"""Bilingual schema binding then one metered unresolved-intent proposal."""
from dataclasses import dataclass
from collections.abc import Mapping
import re
import unicodedata
from .values import TaskKind,ModelPurpose,TerminalReason,canonical_bytes
from .semantics import TaskIntent,SpanBinding,Interpretation
from .goals import TASK_KINDS,validate_parameters
from .broker import strict_json_object
from .prompts import render_role_prompt

NUMBER=r"[-+]?\d+(?:\.\d+)?"
NUMBER_PATTERN=re.compile(r"(?<![a-z0-9])"+NUMBER+r"(?![a-z0-9])")
FIELD_ALIASES={
"office":("office","สำนักงาน"),"temperature_limit":("temperature limit","อุณหภูมิ"),
"supplier":("supplier","ผู้จัดหา"),"status":("status","สถานะ"),"phone":("phone","โทรศัพท์"),
"readings":("readings","ค่าที่บันทึก"),"items":("shipments","รายการจัดส่ง"),
"quantity":("quantity","tray","ถาด","จำนวน"),
}
OP_ALIASES={"sum":("sum","add","บวก","ผลรวม"),"sort":("sort","ascending","เรียง","น้อยไปมาก"),
"filter":("keep","filter","เก็บ","เฉพาะ"),"group":("group","จัดกลุ่ม"),
"format":("format","จัดรูปแบบ"),"select":("show","names","ชื่อ")}
RELATION_ALIASES={"WORKS_AT":("work","works","working","employ","employed","employment","ทำงาน"),"CAUSED_BY":("cause","caused","causes","causing","สาเหตุ"),
"OCCURRED_BEFORE":("after","before","หลัง","ก่อน"),"PART_OF":("part of","ส่วนหนึ่ง"),
"USED_FOR":("used for","ใช้ทำ","ใช้สำหรับ")}
ACTION_ALIASES={"pack":("pack","แพ็ก","แพ็ค"),"approve":("approve","อนุมัติ"),
"prepare":("prepare","calibrate","เตรียม","สอบเทียบ"),"reconcile":("reconcile","ปรับยอด"),
"set":("set","ตั้งค่า")}

@dataclass(frozen=True,slots=True)
class NormalizedText:
    text:str
    spans:tuple
    def original_span(self,start,end):
        if not 0<=start<end<=len(self.text):raise ValueError("normalized span")
        return min(p[0] for p in self.spans[start:end]),max(p[1] for p in self.spans[start:end])

def normalize_with_spans(text):
    out=[];spans=[];i=0
    while i<len(text):
        start=i;i+=1
        while i<len(text) and unicodedata.combining(text[i]):i+=1
        piece=unicodedata.normalize("NFKC",text[start:i]).casefold()
        for char in piece:
            if char.isspace():
                if out and out[-1]==" ":
                    spans[-1]=(spans[-1][0],i)
                else:out.append(" ");spans.append((start,i))
            else:out.append(char);spans.append((start,i))
    return NormalizedText("".join(out),tuple(spans))

def _number(text):
    return float(text) if "." in text else int(text)

def _has(text,words):
    words=tuple(normalize_with_spans(word).text for word in words)
    return any((bool(re.search(r"\b"+re.escape(word)+r"\b",text)) if word.isascii() and word.isalpha()
                else word in text) for word in words)

def _entities(text,schemas):
    exact=[];named=[]
    for entity in schemas.entities:
        if re.search(r"(?<![a-z0-9_-])"+re.escape(entity["id"].casefold())+r"(?![a-z0-9_-])",text):
            exact.append(entity)
        if re.search(r"(?<![a-z0-9_-])"+re.escape(entity["name"].casefold())+r"(?![a-z0-9_-])",text):
            named.append(entity)
    if any(e["id"]!=e["name"] for e in exact):return tuple(exact)
    return tuple({e["id"]:e for e in named or exact}.values())

def request_control(request,schemas):
    text=normalize_with_spans(request.text).text
    if _has(text,("email","delete","อีเมล","ลบไฟล์","ลบไฟล์ชื่อ")):
        return Interpretation(unsupported=TerminalReason.UNSUPPORTED_CAPABILITY.value)
    entities=_entities(text,schemas)
    by_name={}
    for e in entities:by_name.setdefault(e["name"],[]).append(e)
    if any(len(group)>1 for group in by_name.values()):
        return Interpretation(clarification="Specify which distinct entity named "+next(k for k,v in by_name.items() if len(v)>1))
    if _has(text,ACTION_ALIASES["set"]) and _has(text,("tray","ถาด")) and not any(e["kind"]=="tray" for e in entities):
        return Interpretation(clarification="Specify the tray to update")
    return None

def _thresholds(text):
    patterns=[("ge",r"(?:at least|ไม่น้อยกว่า|ตั้งแต่)\s*("+NUMBER+r")"),
              ("le",r"(?:at most|ไม่เกิน)\s*("+NUMBER+r")"),
              ("lt",r"(?:below|less than|ต่ำกว่า)\s*("+NUMBER+r")"),
              ("gt",r"(?:above|more than|มากกว่า)\s*("+NUMBER+r")")]
    values=[]
    for comparison,pattern in patterns:
        for match in re.finditer(unicodedata.normalize("NFKC",pattern).casefold(),text):values.append((comparison,_number(match.group(1)),match.span(1)))
    return sorted(values,key=lambda v:v[2][0])

def deterministic_intent(request,schemas):
    stopped=request_control(request,schemas)
    if stopped:return stopped
    normalized=normalize_with_spans(request.text);text=normalized.text
    entities=_entities(text,schemas)
    principal=next((e for e in entities if e["kind"] not in ("dataset","purpose","organization")),None)
    thresholds=_thresholds(text)
    numeric=[(m,_number(m.group())) for m in NUMBER_PATTERN.finditer(text)
             if not any(start<=m.start()<end for _,_,(start,end) in thresholds)]
    spans=[]
    def span(name,value,start=0,end=None):
        end=len(text) if end is None else end
        a,b=normalized.original_span(start,end);spans.append(SpanBinding(name,value,a,b))
    def result(task,parameters):
        validate_parameters(task,parameters,schemas)
        if not spans:span("task",task)
        return Interpretation(intent=TaskIntent(TASK_KINDS[task],
            {"task":task,"parameters":parameters,"spans":tuple(spans)}))
    if principal:
        entity=principal["id"]
        found=re.search(re.escape(entity.casefold()),text)
        if found:span("entity",entity,found.start(),found.end())
        action=None
        for candidate,kinds in (("pack",("order",)),("approve",("invoice",)),
                                ("prepare",("bench",)),("reconcile",("bin",)),("set",("tray",))):
            if principal["kind"] in kinds and _has(text,ACTION_ALIASES[candidate]):
                action=candidate;break
        if action in ("pack","approve","prepare","reconcile"):return result(action,{"entity":entity})
        if action=="set":
            if any(op=="ge" for op,_,_ in thresholds) and any(op=="le" for op,_,_ in thresholds):
                lo=next(v for op,v,_ in thresholds if op=="ge")
                hi=next(v for op,v,_ in thresholds if op=="le")
                for op,value,(a,b) in thresholds:span("min" if op=="ge" else "max",value,a,b)
                return result("state_range",{"entity":entity,"field":"quantity","min":lo,"max":hi})
            if not numeric:return Interpretation(clarification="Specify the numeric state value")
            if _has(text,("sum","ผลรวม","บวก")):
                cut=re.search(r"(?:then|แล้ว)",text)
                input_values=[value for m,value in numeric if cut is None or m.start()<cut.start()]
                value={"sum":input_values}
                if cut:
                    tail=[v for m,v in numeric if m.start()>=cut.start()]
                    if tail:value["verify"]=tail[-1]
            else:value=numeric[0][1]
            span("value",value)
            return result("set",{"entity":entity,"field":"quantity","value":value})
    is_composition=_has(text,OP_ALIASES["group"]) or _has(text,("names only","เฉพาะชื่อ","costing","ราคา"))
    data_transform=(_has(text,("readings","ค่าที่บันทึก")) and _has(text,OP_ALIASES["filter"]))
    transform=not principal or is_composition or data_transform
    if transform:
        operations=[];outputs=[]
        source=None
        if _has(text,("shipments","รายการจัดส่ง")):
            source={"entity":"shipments","field":"items"}
        elif _has(text,("components","ชิ้นส่วน")) and _has(text,("names","ชื่อ","cost","ราคา")):
            source={"collection":"component"}
            if _has(text,("approved","อนุมัติ")):operations.append({"op":"filter","field":"approved","comparison":"eq","value":True})
        elif principal and data_transform:source={"entity":principal["id"],"field":"readings"}
        elif numeric:source={"literal":[value for _,value in numeric]}
        if source is not None:
            span("source",source)
            if thresholds:
                comparison,value,(a,b)=thresholds[0]
                field="cost" if "collection" in source else None
                operations.append({"op":"filter","field":field,"comparison":comparison,"value":value})
                span("threshold",value,a,b)
            if _has(text,OP_ALIASES["sort"]):
                operations.append({"op":"sort","field":"cost" if "collection" in source else None});outputs.append("list")
            if _has(text,OP_ALIASES["group"]):
                operations.append({"op":"group","key":"destination","value":"quantity"});outputs=["map"]
            elif _has(text,OP_ALIASES["format"]):
                operations.append({"op":"format","separator":","});outputs=["value"]
            elif _has(text,("names only","เฉพาะชื่อ","showing names")):
                operations.append({"op":"select","fields":["name"]});outputs=["names"]
            elif _has(text,OP_ALIASES["sum"]):
                operations.append({"op":"sum"});outputs.append("sum" if "list" in outputs else "value")
            elif operations and not outputs:outputs=["list"]
            if operations:return result("transform",{"source":source,"operations":operations,"outputs":outputs})
    if principal:
        relations=[relation for relation,words in RELATION_ALIASES.items() if _has(text,words)]
        if relations:
            return result("relation",{"entity":principal["id"],"relations":relations,
                "top_level":_has(text,("top-level","ระดับบนสุด"))})
        for field,aliases in FIELD_ALIASES.items():
            if _has(text,aliases):return result("fact",{"entity":principal["id"],"field":field})
    return None

def _span_matches(value,fragment,schemas):
    text=normalize_with_spans(fragment).text.strip()
    if isinstance(value,Mapping):
        if set(value)=={"literal"}:return _span_matches(value["literal"],fragment,schemas)
        if set(value)=={"entity","field"}:
            return _span_matches(value["entity"],fragment,schemas) and _span_matches(value["field"],fragment,schemas)
        if set(value)=={"collection"}:return _has(text,("component","components","ชิ้นส่วน")) and value["collection"]=="component"
        if set(value) in ({"sum"},{"sum","verify"}):
            numbers=[_number(m.group()) for m in NUMBER_PATTERN.finditer(text)]
            return all(v in numbers for v in value["sum"]) and ("verify" not in value or value["verify"] in numbers)
        return False
    if isinstance(value,(tuple,list)):
        if value and all(isinstance(v,str) and v in RELATION_ALIASES for v in value):
            return all(_has(text,RELATION_ALIASES[v]) for v in value)
        return tuple(value)==tuple(_number(m.group()) for m in NUMBER_PATTERN.finditer(text))
    if isinstance(value,(int,float)) and not isinstance(value,bool):
        return value in tuple(_number(m.group()) for m in NUMBER_PATTERN.finditer(text))
    if isinstance(value,str):
        if value.casefold() in text:return True
        if value in FIELD_ALIASES:return _has(text,FIELD_ALIASES[value])
        return any(e["id"]==value and e["name"].casefold() in text for e in schemas.entities)
    return False

def validate_intent_proposal(raw,request,schemas):
    if not isinstance(raw,Mapping):raise ValueError("intent object required")
    if set(raw)=={"status","reason"}:
        stopped=request_control(request,schemas)
        if stopped is None:raise ValueError("unverified intent stop")
        status="NEEDS_CLARIFICATION" if stopped.clarification else "UNSUPPORTED"
        reason="AMBIGUOUS_INPUT" if stopped.clarification else "UNSUPPORTED_CAPABILITY"
        if raw["status"]!=status or raw["reason"]!=reason:raise ValueError("contradictory stop")
        return stopped
    if set(raw)!={"kind","task","parameters","spans"}:raise ValueError("closed intent schema")
    validate_parameters(raw["task"],raw["parameters"],schemas)
    if TaskKind(raw["kind"])!=TASK_KINDS[raw["task"]]:raise ValueError("kind mismatch")
    stopped=request_control(request,schemas)
    if stopped:return stopped
    spans=[]
    if not isinstance(raw["spans"],(tuple,list)) or not raw["spans"]:raise ValueError("original bindings required")
    for entry in raw["spans"]:
        if not isinstance(entry,Mapping) or set(entry)!={"name","value","start","end"}:raise ValueError("span schema")
        start,end=entry["start"],entry["end"]
        if (isinstance(start,bool) or isinstance(end,bool) or not isinstance(start,int) or not isinstance(end,int)
            or not 0<=start<end<=len(request.text) or not _span_matches(entry["value"],request.text[start:end],schemas)):
            raise ValueError("invalid original binding")
        spans.append(SpanBinding(entry["name"],entry["value"],start,end))
    for name,value in raw["parameters"].items():
        if name in ("operations","outputs","top_level"):continue
        if not any(s.name==name and (canonical_bytes(s.value)==canonical_bytes(value) or (name=="source" and isinstance(value,Mapping) and canonical_bytes(s.value)==canonical_bytes(value.get("literal")))) for s in spans):
            # Field names may use the same grounded entity/source span.
            if name=="field" and any(_span_matches(value,request.text[s.original_start:s.original_end],schemas) for s in spans):continue
            raise ValueError("unbound material parameter "+name)
    if raw["task"]=="transform":
        normalized=normalize_with_spans(request.text).text
        for op in raw["parameters"]["operations"]:
            if not _has(normalized,OP_ALIASES[op["op"]]):raise ValueError("unbound requested operator")
            if op["op"]=="filter" and isinstance(op["value"],(int,float)) and not isinstance(op["value"],bool):
                if not any(_span_matches(op["value"],request.text[s.original_start:s.original_end],schemas) for s in spans):
                    raise ValueError("unbound threshold")
    return Interpretation(intent=TaskIntent(TaskKind(raw["kind"]),
        {"task":raw["task"],"parameters":raw["parameters"],"spans":tuple(spans)}))

class Interpreter:
    def __init__(self,schemas,broker):self.schemas=schemas;self.broker=broker
    def interpret(self,request,*,control):
        control.check_dispatch()
        found=deterministic_intent(request,self.schemas)
        if found:return found
        prompt=render_role_prompt(ModelPurpose.INTENT,{"text":request.text,"task_schemas":self.schemas.tasks,
                                  "entities":tuple({"id":e["id"],"name":e["name"],"kind":e["kind"]} for e in self.schemas.entities)})
        response=self.broker.generate(ModelPurpose.INTENT,prompt,control=control,max_output_tokens=1024)
        if response.error:return Interpretation(failure=response.error)
        try:return validate_intent_proposal(strict_json_object(response.response.content),request,self.schemas)
        except (ValueError,TypeError,KeyError):return Interpretation(failure=TerminalReason.INVALID_PLAN.value)
