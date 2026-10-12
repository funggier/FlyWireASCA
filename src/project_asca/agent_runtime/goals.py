"""Closed trusted task templates; no model-supplied predicates or success grants."""
from dataclasses import dataclass
from collections.abc import Mapping
import math
from .values import TaskKind,PredicateOperator,EffectClass,fingerprint,canonical_bytes,freeze_json
from .semantics import GoalContract,GoalPredicate,SpanBinding

@dataclass(frozen=True,slots=True)
class TaskSchemaRegistry:
    configuration:object
    tasks:Mapping
    entities:tuple
    @classmethod
    def from_public(cls,configuration):
        return cls(configuration,configuration.task_schemas,configuration.knowledge.entities)
    def candidates(self,name):
        return tuple(e for e in self.entities if e["id"].casefold()==name.casefold() or e["name"].casefold()==name.casefold())

TASK_KINDS={"fact":TaskKind.FACT,"relation":TaskKind.RELATION,"transform":TaskKind.TRANSFORM,
            "pack":TaskKind.STATE_GOAL,"approve":TaskKind.STATE_GOAL,"prepare":TaskKind.STATE_GOAL,
            "reconcile":TaskKind.STATE_GOAL,"set":TaskKind.STATE_GOAL,"state_range":TaskKind.STATE_GOAL}
OP_FIELDS={"filter":{"op","field","comparison","value"},"sort":{"op","field"},
           "group":{"op","key","value"},"sum":{"op"},"format":{"op","separator"},"select":{"op","fields"}}
RELATIONS={"WORKS_AT","CAUSED_BY","OCCURRED_BEFORE","PART_OF","USED_FOR"}

def _bounded(value,depth=0):
    if depth>8:raise ValueError("semantic nesting limit")
    if isinstance(value,(tuple,list)):
        if len(value)>256:raise ValueError("semantic array limit")
        for item in value:_bounded(item,depth+1)
    elif isinstance(value,Mapping):
        for item in value.values():_bounded(item,depth+1)
    elif isinstance(value,float) and not math.isfinite(value):raise ValueError("finite parameters")
    elif value is not None and not isinstance(value,(str,int,float,bool)):raise ValueError("JSON parameters")

def validate_parameters(task,parameters,schemas):
    if task not in TASK_KINDS or not isinstance(parameters,Mapping):raise ValueError("task schema")
    allowed=set(schemas.tasks[task])
    if set(parameters)-allowed:raise ValueError("unknown semantic parameter")
    optional={"top_level"} if task=="relation" else set()
    if allowed-set(parameters)-optional:raise ValueError("missing material parameter")
    _bounded(parameters)
    if len(canonical_bytes(parameters))>65536:raise ValueError("semantic byte limit")
    if "entity" in parameters:
        candidates=schemas.candidates(parameters["entity"])
        if len(candidates)!=1:raise ValueError("unknown/disputed entity")
        if candidates[0]["id"]!=parameters["entity"]:raise ValueError("canonical entity binding required")
    if task=="relation":
        relations=parameters["relations"]
        if not isinstance(relations,(tuple,list)) or not relations or set(relations)-RELATIONS:
            raise ValueError("relation schema")
        if "top_level" in parameters and not isinstance(parameters["top_level"],bool):raise ValueError("top-level type")
    if task in ("fact","set","state_range") and (not isinstance(parameters["field"],str) or not parameters["field"]):
        raise ValueError("field parameter")
    if task=="transform":
        source=parameters["source"]
        if not isinstance(source,Mapping) or set(source) not in ({"literal"},{"entity","field"},{"collection"}):
            raise ValueError("source schema")
        if "literal" in source and (not isinstance(source["literal"],(tuple,list)) or any(
             isinstance(v,bool) or not isinstance(v,(int,float)) for v in source["literal"])):
            raise ValueError("numeric source")
        if "entity" in source and len(schemas.candidates(source["entity"]))!=1:raise ValueError("source entity")
        operations=parameters["operations"]
        if not isinstance(operations,(tuple,list)) or not 0<len(operations)<=32:raise ValueError("finite operations")
        for op in operations:
            if not isinstance(op,Mapping) or op.get("op") not in OP_FIELDS or set(op)-OP_FIELDS[op["op"]]:
                raise ValueError("operation schema")
            if op["op"]=="filter" and (op.get("comparison") not in ("lt","le","ge","gt","eq") or "value" not in op):
                raise ValueError("filter schema")
            if op["op"]=="group" and not {"key","value"}<=set(op):raise ValueError("group schema")
            if op["op"]=="format" and not isinstance(op.get("separator"),str):raise ValueError("format schema")
            if op["op"]=="select" and not isinstance(op.get("fields"),(tuple,list)):raise ValueError("select schema")
        outputs=parameters["outputs"]
        if not isinstance(outputs,(tuple,list)) or not outputs or set(outputs)-{"value","list","sum","map","names"}:
            raise ValueError("output schema")
    if task=="set":
        value=parameters["value"]
        if isinstance(value,Mapping):
            if set(value) not in ({"sum"},{"sum","verify"}) or not isinstance(value["sum"],(tuple,list)):
                raise ValueError("state expression schema")
            for item in tuple(value["sum"])+((value["verify"],) if "verify" in value else ()):
                if isinstance(item,bool) or not isinstance(item,(int,float)) or not math.isfinite(item):
                    raise ValueError("state numeric expression")
    if task=="state_range":
        for key in ("min","max"):
            v=parameters[key]
            if isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v):raise ValueError("numeric range")

class GoalCompiler:
    def compile(self,intent,request,schemas):
        if set(intent.bindings)!={"task","parameters","spans"}:raise ValueError("intent binding schema")
        task=intent.bindings["task"];params=intent.bindings["parameters"]
        validate_parameters(task,params,schemas)
        if intent.kind!=TASK_KINDS[task]:raise ValueError("task kind mismatch")
        spans=intent.bindings["spans"]
        for span in spans:
            if not isinstance(span,SpanBinding) or not 0<=span.original_start<span.original_end<=len(request.text):
                raise ValueError("original span required")
        if not spans:raise ValueError("material original-span bindings required")
        predicates=[];refs=[]
        def add(operator,arguments):
            predicates.append(GoalPredicate("p"+str(len(predicates)+1),operator,arguments))
        if task=="fact":
            add(PredicateOperator.FACT_EQUALS,{"entity":params["entity"],"field":params["field"]})
            refs.append(params["entity"]+"."+params["field"])
        elif task=="relation":
            for relation in params["relations"]:
                add(PredicateOperator.RELATION_PATH,{"entity":params["entity"],"relation":relation,
                                                     "top_level":params.get("top_level",False)})
                refs.append("relation:"+params["entity"]+":"+relation)
        elif task=="transform":
            outputs=set(params["outputs"])
            ops={op["op"] for op in params["operations"]}
            if "sort" in ops and "sum" in ops:outputs.update(("list","sum"))
            for output in sorted(outputs):
                add(PredicateOperator.TRANSFORM_RESULT,{"source":params["source"],
                    "operations":params["operations"],"output":output})
            source=params["source"]
            if "entity" in source:refs.append(source["entity"]+"."+source["field"])
            elif "collection" in source:refs.append("collection:"+source["collection"])
        else:
            entity=params["entity"]
            required={"pack":{"status":"packed","sealed":True},"approve":{"status":"approved"},
                      "prepare":{"calibrated":True,"ready":True},"reconcile":{"checked":True}}.get(task,{})
            for field,value in required.items():
                add(PredicateOperator.STATE_EQUALS,{"entity":entity,"field":field,"value":value})
            if task=="reconcile":
                add(PredicateOperator.STATE_EQUALS,{"entity":entity,"field":"quantity","fact_field":"recorded_count"})
                refs.append(entity+".recorded_count")
            if task in ("approve","prepare","pack","reconcile"):
                add(PredicateOperator.POLICY_VALID,{"entity":entity,"task":task})
                if task=="approve":refs.extend((entity+".amount",entity+".limit"))
                if task=="prepare":refs.append(entity+".calibration_policy")
            if task=="set":
                value=params["value"]
                add(PredicateOperator.STATE_EQUALS,{"entity":entity,"field":params["field"],
                    "value":{"sum":value["sum"]} if isinstance(value,Mapping) else value})
                if isinstance(value,Mapping) and "verify" in value:
                    add(PredicateOperator.STATE_EQUALS,{"entity":entity,"field":params["field"],"value":value["verify"]})
            if task=="state_range":
                add(PredicateOperator.STATE_RANGE,dict(params))
        accepted={"task":task,**dict(params),"spans":spans}
        return GoalContract("goal:"+fingerprint({"request":request.text,"parameters":accepted}),intent.kind,
                            accepted,tuple(predicates),tuple(refs),
                            (EffectClass.PURE,EffectClass.IN_MEMORY) if intent.kind is TaskKind.STATE_GOAL else (EffectClass.PURE,))
