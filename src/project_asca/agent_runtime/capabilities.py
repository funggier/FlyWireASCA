"""Trusted finite operation semantics; facts are usable only when context-bound."""
from dataclasses import dataclass
from decimal import Decimal,InvalidOperation
from collections.abc import Mapping
import math
from .values import FrozenRecord,EffectClass,EvidenceKind,canonical_bytes,fingerprint,freeze_json
from .plans import CapabilityDescriptor,AuthorizationDecision,ValueBinding

@dataclass(frozen=True,slots=True)
class CapabilityOutcome(FrozenRecord):
    executed:bool
    result:object
    error:str|None
    state:object
    unmet_evidence:tuple[str,...]=()

class CapabilityRegistry:
    def __init__(self,configuration):
        self.configuration=configuration
        self.descriptors={c["id"]:CapabilityDescriptor(c["id"],c["version"],
            {"required":c["inputs"]},{"bounded_json":True},effect_class=EffectClass(c["effect"]))
            for c in configuration.capabilities}
        self.fact_catalog={f["id"]:f for f in configuration.knowledge.facts}
        self.fingerprint=fingerprint(tuple(self.descriptors.values()))
    @classmethod
    def from_public(cls,configuration):return cls(configuration)
    def get(self,capability_id,version):
        descriptor=self.descriptors.get(capability_id)
        if descriptor is None or descriptor.version!=version:raise ValueError("unregistered capability/version")
        return descriptor

class StageAAuthorization:
    def authorize(self,capability,*,control):
        control.check_dispatch()
        return AuthorizationDecision(capability.effect_class in (EffectClass.PURE,EffectClass.IN_MEMORY),
                                     "Stage A pure/in-memory registry scope")

class MissingEvidence(ValueError):
    def __init__(self,reference):
        self.reference=reference
        super().__init__("MISSING_EVIDENCE")

def bound_fact(context,registry,entity,field):
    ref=entity+"."+field
    for item in context.items:
        p=item.payload
        if p.get("subject")==entity and p.get("field")==field:
            if item.kind not in (EvidenceKind.STORED_FACT,EvidenceKind.VECTOR_HIT):
                raise ValueError("PROVENANCE_INVALID")
            authoritative=registry.fact_catalog.get(item.origin_id)
            if (item.snapshot_id!=context.snapshot_id or authoritative is None
                or dict(p)!=dict(authoritative) or p.get("version")!=registry.configuration.public["defaults"]["version"]
                or p.get("confidence",0)<.5):
                raise ValueError("PROVENANCE_INVALID")
            return p["value"]
    raise MissingEvidence(ref)

def _binding(value,bindings,context):
    if isinstance(value,Mapping) and "source" in value:
        if set(value)-{"source","reference","value"}:raise ValueError("binding fields")
        value=ValueBinding(**dict(value))
    if not isinstance(value,ValueBinding):return value
    if value.source=="literal":return value.value
    if value.source in ("request","step"):
        key=value.reference if value.source=="request" else "step:"+value.reference
        if key not in bindings:raise ValueError("unavailable/forward binding")
        return bindings[key]
    for item in context.items:
        if value.reference in (item.evidence_id,item.origin_id):
            if item.kind is EvidenceKind.HYPOTHESIS:raise ValueError("PROVENANCE_INVALID")
            return item.payload.get("value",item.payload)
    raise MissingEvidence(value.reference)

def _number(value):
    if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value):
        raise ValueError("finite numeric value required")
    return Decimal(str(value))

def _sum(items):
    total=sum((_number(v) for v in items),Decimal(0))
    result=int(total) if total==total.to_integral_value() else float(total)
    if isinstance(result,float) and not math.isfinite(result):raise ValueError("numeric overflow")
    return result

def _items(value):
    if not isinstance(value,(tuple,list)) or len(value)>256:raise ValueError("bounded array required")
    return value

def _field(item,key):
    return item if key is None else item[key]

def _compare(a,op,b):
    if op=="eq":
        if isinstance(a,bool)!=isinstance(b,bool):return False
        return a==b
    a=_number(a);b=_number(b)
    if op=="lt":return a<b
    if op=="le":return a<=b
    if op=="ge":return a>=b
    if op=="gt":return a>b
    raise ValueError("comparison operator")

def execute_operation(step,bindings,*,context,session,registry):
    try:
        descriptor=registry.get(step.capability_id,step.capability_version)
        if descriptor.effect_class not in (EffectClass.PURE,EffectClass.IN_MEMORY):
            raise ValueError("UNSUPPORTED_CAPABILITY")
        args={k:_binding(v,bindings,context) for k,v in step.inputs.items()}
        required=set(descriptor.input_schema["required"])
        optional={"field"} if step.capability_id in ("filter","sort") else set()
        if set(args)-required or required-set(args)-optional:raise ValueError("capability input schema")
        if len(canonical_bytes(args))>65536:raise ValueError("intermediate byte limit")
        op=step.capability_id;result=None
        if op in ("select","filter","sort","group","sum","format"):
            items=_items(args["items"])
            if op=="select":
                fields=_items(args["fields"])
                result=[{key:item[key] for key in fields} for item in items]
            elif op=="filter":
                result=[item for item in items if _compare(_field(item,args.get("field")),args["op"],args["value"])]
            elif op=="sort":
                key=args.get("field");keys=[_field(item,key) for item in items]
                numeric=all(not isinstance(k,bool) and isinstance(k,(int,float)) for k in keys)
                strings=all(isinstance(k,str) for k in keys)
                if not numeric and not strings:raise ValueError("homogeneous sort keys")
                if numeric:
                    for k in keys:_number(k)
                result=sorted(items,key=lambda item:_field(item,key))
            elif op=="group":
                result={}
                for item in items:
                    key=item[args["key"]]
                    if not isinstance(key,str):raise ValueError("string group key")
                    result.setdefault(key,[]).append(item[args["value"]])
                result={key:_sum(result[key]) for key in sorted(result)}
            elif op=="sum":result=_sum(items)
            elif op=="format":
                separator=args["separator"]
                if not isinstance(separator,str):raise ValueError("separator")
                def scalar(v):
                    if v is None:return "null"
                    if isinstance(v,bool):return "true" if v else "false"
                    if isinstance(v,(int,float)):_number(v);return str(v)
                    if isinstance(v,str):return v
                    raise ValueError("scalar format")
                result=separator.join(scalar(v) for v in items)
        elif op=="assert":
            if not _compare(args["actual"],args["op"],args["value"]):raise ValueError("OBSERVED_MISMATCH")
            result=args["actual"]
        elif op=="set":
            session.set_values(args["entity"],{args["field"]:args["value"]})
            result=args["value"]
        else:
            entity=args["entity"]
            fact=lambda field:bound_fact(context,registry,entity,field)
            def declared(field):
                return any(f["subject"]==entity and f["field"]==field for f in registry.fact_catalog.values())
            if op in ("policy","approve"):
                if not _compare(fact("amount"),"le",fact("limit")):raise ValueError("PRECONDITION_UNSATISFIED")
                if declared("requires_department"):
                    if fact("requires_department") and fact("department_approval") is not True:
                        raise ValueError("PRECONDITION_UNSATISFIED")
                if op=="approve":session.set_values(entity,{"status":"approved"})
                result=True
            elif op=="calibrate":
                policy=fact("calibration_policy")
                if policy=="reference":_number(fact("reference_setting"))
                elif policy!="basic":raise ValueError("PRECONDITION_UNSATISFIED")
                session.set_values(entity,{"calibrated":True});result=True
            elif op=="ready":
                if session.snapshot().values[entity]["calibrated"] is not True:raise ValueError("PRECONDITION_UNSATISFIED")
                session.set_values(entity,{"ready":True});result=True
            elif op=="reconcile":
                quantity=fact("recorded_count");_number(quantity)
                if declared("requires_revision") and fact("requires_revision"):
                    if not isinstance(fact("count_revision"),str):raise ValueError("PRECONDITION_UNSATISFIED")
                session.set_values(entity,{"quantity":quantity,"checked":True});result=quantity
            elif op=="package":
                package=fact("required_package")
                if not isinstance(package,str):raise ValueError("PRECONDITION_UNSATISFIED")
                session.set_values(entity,{"package":package});result=package
            elif op=="pack":
                if declared("required_package") and session.snapshot().values[entity]["package"]!=fact("required_package"):
                    raise ValueError("PRECONDITION_UNSATISFIED")
                session.set_values(entity,{"status":"packed"});result=True
            elif op=="seal":
                if session.snapshot().values[entity]["status"]!="packed":raise ValueError("PRECONDITION_UNSATISFIED")
                session.set_values(entity,{"sealed":True});result=True
            else:raise ValueError("unregistered operation semantics")
        if len(canonical_bytes(result))>65536:raise ValueError("result byte bound")
        return CapabilityOutcome(True,freeze_json(result),None,session.snapshot())
    except MissingEvidence as exc:
        return CapabilityOutcome(False,None,"MISSING_EVIDENCE",session.snapshot(),(exc.reference,))
    except (ValueError,TypeError,KeyError,InvalidOperation,OverflowError) as exc:
        error=str(exc) if str(exc) in ("PROVENANCE_INVALID","PRECONDITION_UNSATISFIED","OBSERVED_MISMATCH",
                                     "UNSUPPORTED_CAPABILITY") else "INVALID_PLAN"
        return CapabilityOutcome(False,None,error,session.snapshot())
