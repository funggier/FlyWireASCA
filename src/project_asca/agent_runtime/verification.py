"""Independent semantic completion, bound to trusted execution and evidence."""
from dataclasses import dataclass
from collections.abc import Mapping
from decimal import Decimal
import math
from .values import FrozenRecord,TaskKind,EffectClass,EvidenceKind,PredicateOperator,Phase,canonical_bytes,fingerprint
from .semantics import GoalContract,EvidenceRecord,PredicateVerdict,VerificationRecord
from .plans import CapabilityDescriptor

@dataclass(frozen=True,slots=True)
class CompletionCandidate(FrozenRecord):
    data:object
    evidence_refs:tuple[str,...]
    attempt:object=None
    evidence:tuple[EvidenceRecord,...]=()
    def __post_init__(self):
        super(CompletionCandidate,self).__post_init__()
        if len(canonical_bytes(self.data))>65536 or len(self.evidence)>256:
            raise ValueError("completion candidate bound")
        if len(set(self.evidence_refs))!=len(self.evidence_refs):raise ValueError("duplicate evidence reference")

class Unresolved(ValueError):pass
class ProvenanceError(ValueError):pass

def _same(a,b):
    if isinstance(a,bool) or isinstance(b,bool):return type(a) is type(b) and a==b
    if isinstance(a,(int,float)) and isinstance(b,(int,float)):return _number(a)==_number(b)
    if isinstance(a,Mapping) and isinstance(b,Mapping):
        return set(a)==set(b) and all(_same(a[k],b[k]) for k in a)
    if isinstance(a,(tuple,list)) and isinstance(b,(tuple,list)):
        return len(a)==len(b) and all(_same(x,y) for x,y in zip(a,b))
    return type(a) is type(b) and a==b

def _number(v):
    if isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v):raise ValueError("finite numeric value")
    return Decimal(str(v))

def _total(values):
    n=sum((_number(v) for v in values),Decimal(0))
    answer=int(n) if n==n.to_integral_value() else float(n)
    if isinstance(answer,float) and not math.isfinite(answer):raise ValueError("finite result")
    return answer

def _compare(a,op,b):
    if op=="eq":return _same(a,b)
    x,y=_number(a),_number(b)
    if op=="lt":return x<y
    if op=="le":return x<=y
    if op=="ge":return x>=y
    if op=="gt":return x>y
    raise ValueError("comparison operator")

def _records(candidate,knowledge):
    result={}
    for record in candidate.evidence:
        if not isinstance(record,EvidenceRecord) or record.evidence_id in result:
            raise ProvenanceError("typed unique evidence")
        result[record.evidence_id]=record
    if any(ref not in result for ref in candidate.evidence_refs):raise ProvenanceError("unbound evidence reference")
    return {ref:result[ref] for ref in candidate.evidence_refs}

def _fact(knowledge,records,entity,field):
    facts=[f for f in knowledge.facts if f["subject"]==entity and f["field"]==field]
    if len(facts)!=1:raise Unresolved(entity+"."+field)
    fact=facts[0]
    matches=[r for r in records.values() if r.origin_id==fact["id"] and r.payload.get("field")==field]
    if not matches:raise Unresolved(entity+"."+field)
    for r in matches:
        if (r.kind not in (EvidenceKind.STORED_FACT,EvidenceKind.VECTOR_HIT)
            or r.snapshot_id!=knowledge.snapshot_id or fact["confidence"]<.5
            or canonical_bytes(r.payload)!=canonical_bytes(fact)):
            raise ProvenanceError("factual identity/version/confidence")
    return fact["value"]

def _registry(knowledge):
    if not knowledge.capabilities:raise ProvenanceError("capability metadata missing")
    descriptors=tuple(CapabilityDescriptor(c["id"],c["version"],{"required":c["inputs"]},
         {"bounded_json":True},effect_class=EffectClass(c["effect"])) for c in knowledge.capabilities)
    if len({d.capability_id for d in descriptors})!=len(descriptors):raise ProvenanceError("duplicate registry identity")
    return {d.capability_id:d for d in descriptors},fingerprint(descriptors)

def _control_and_observations(goal,candidate,knowledge,state,snapshot):
    if (not snapshot.integrity or snapshot.terminal or snapshot.cancelled
        or Phase(snapshot.phase) is not Phase.VERIFYING or not math.isfinite(snapshot.observed_at)
        or not math.isfinite(snapshot.deadline) or snapshot.observed_at>=snapshot.deadline):
        raise ProvenanceError("control/deadline/cancellation")
    if not snapshot.limits:raise ProvenanceError("budget authority missing")
    for resource,value in snapshot.metrics.reservations.items():
        if (resource not in snapshot.limits or isinstance(value,bool) or not isinstance(value,int)
            or value<0 or value>snapshot.limits[resource]):raise ProvenanceError("budget violation")
    counter_resources={"primitive_actions":"actions","primitive_action_attempts":"actions",
        "model_invocations":"model_calls","actual_retrieval_queries":"retrieval_queries",
        "vectors_scored":"vectors_scored","relation_invocations":"relation_invocations",
        "relation_visit_events":"relation_visits","strategy_attempts":"strategy_attempts",
        "recovery_rounds":"recovery_rounds","transitions":"transitions"}
    for counter,resource in counter_resources.items():
        value=snapshot.metrics.counters.get(counter,0)
        if isinstance(value,bool) or not isinstance(value,int) or value<0 or value>snapshot.metrics.reservations.get(resource,0):
            raise ProvenanceError("actual work exceeds budget accounting")
    if snapshot.metrics.integrity_failures:raise ProvenanceError("integrity failure")
    attempt=candidate.attempt;receipt=snapshot.execution_receipt
    if attempt is None or state is None or receipt is None:raise Unresolved("fresh observation/receipt/state required")
    registry,registry_fp=_registry(knowledge)
    if (receipt.run_id!=snapshot.run_id or receipt.goal_fingerprint!=fingerprint(goal)
        or receipt.capability_fingerprint!=registry_fp or receipt.execution_id!=attempt.execution_id
        or receipt.final_state_ref!=state.snapshot_id or receipt.final_state_revision!=state.revision
        or receipt.observation_fingerprint!=fingerprint(attempt.observations)
        or canonical_bytes(state)!=canonical_bytes(attempt.final_state)
        or attempt.procedure_state!="COMPLETED"
        or not attempt.observations or len(attempt.observations)!=len(receipt.expected_steps)):
        raise ProvenanceError("execution receipt identity")
    if state.snapshot_id!="state:"+fingerprint({"execution":attempt.execution_id,"revision":state.revision,"values":state.values}):
        raise ProvenanceError("fresh state hash")
    revision=0;seen=set()
    for expected,observation in zip(receipt.expected_steps,attempt.observations):
        step,capability,version=expected
        descriptor=registry.get(capability)
        if (descriptor is None or descriptor.version!=version or descriptor.effect_class not in goal.effect_scope
            or observation.run_id!=snapshot.run_id or observation.attempt_id!=receipt.attempt_id
            or observation.execution_id!=receipt.execution_id or observation.step_id!=step
            or (observation.capability_id,observation.capability_version)!=(capability,version)
            or step in seen or not observation.executed or observation.error is not None):
            raise ProvenanceError("observation identity/capability/effect")
        seen.add(step)
        if descriptor.effect_class is EffectClass.IN_MEMORY:revision+=1
        if observation.state_revision!=revision:raise ProvenanceError("state revision")
    if revision!=state.revision or attempt.observations[-1].state_ref!=state.snapshot_id:
        raise ProvenanceError("final observation revision")
    if snapshot.metrics.primitive_actions<len(attempt.observations):raise ProvenanceError("missing executed-action accounting")
    return tuple(fingerprint(o) for o in attempt.observations)

def _relation(goal,predicate,candidate,knowledge,records):
    if not isinstance(candidate.data,Mapping) or set(candidate.data)!={"paths"}:return False
    paths=candidate.data["paths"]
    if not isinstance(paths,(tuple,list)) or not paths:return False
    edges={e["id"]:e for e in knowledge.edges};nodes={e["id"]:e for e in knowledge.entities}
    matched=False
    for path in paths:
        if not isinstance(path,Mapping) or set(path)!={"node_ids","edge_ids","evidence_ids"}:return False
        ns,es,evs=path["node_ids"],path["edge_ids"],path["evidence_ids"]
        if not es or len(es)>3 or len(ns)!=len(es)+1 or len(set(ns))!=len(ns) or len(set(es))!=len(es):
            raise ProvenanceError("finite directed path")
        if ns[0]!=goal.parameters["entity"]:raise ProvenanceError("relation entity identity")
        authoritative={}
        for node in ns:
            if node not in nodes:raise ProvenanceError("unknown relation node")
            authoritative["node:"+node]=(node,{"record_kind":"node",**dict(nodes[node])})
        relations=[]
        for index,edge_id in enumerate(es):
            edge=edges.get(edge_id)
            if (edge is None or edge["source"]!=ns[index] or edge["target"]!=ns[index+1] or edge["confidence"]<.5):
                raise ProvenanceError("edge direction/confidence")
            relations.append(edge["relation"])
            authoritative["edge:"+edge_id]=(edge_id,{"record_kind":"edge",**dict(edge)})
            eid="evidence:"+edge_id
            authoritative[eid]=(edge_id,{"record_kind":"edge_evidence","id":eid,"edge_id":edge_id,
                                         "confidence":edge["confidence"],"version":edge["version"]})
        if tuple(evs)!=tuple("evidence:"+e for e in es):raise ProvenanceError("edge evidence order")
        wrappers=[r for r in records.values() if r.payload.get("record_kind")=="path"
            and all(_same(r.payload.get(k),path[k]) for k in path)]
        if not wrappers:raise Unresolved("selected complete path")
        for wrapper in wrappers:
            if (wrapper.kind is not EvidenceKind.RELATION_PATH or wrapper.snapshot_id!=knowledge.snapshot_id
                or set(wrapper.constituent_ids)!=set(authoritative)):
                raise ProvenanceError("path wrapper identity/constituents")
        for identifier,(origin,payload) in authoritative.items():
            record=records.get(identifier)
            if record is None:raise Unresolved("missing path constituent "+identifier)
            if (record.origin_id!=origin or record.snapshot_id!=knowledge.snapshot_id
                or record.kind is not EvidenceKind.RELATION_PATH or canonical_bytes(record.payload)!=canonical_bytes(payload)):
                raise ProvenanceError("path constituent identity/version")
        relation=predicate.arguments["relation"]
        if all(r==relation for r in relations):
            if predicate.arguments.get("top_level") and any(e["source"]==ns[-1] and e["relation"]==relation
                                                          and e["confidence"]>=.5 for e in knowledge.edges):
                continue
            matched=True
        elif any(r not in goal.parameters["relations"] for r in relations):
            raise ProvenanceError("unsupported relation claim")
    return matched

def _source(source,knowledge,records):
    if "literal" in source:return source["literal"]
    if "entity" in source:return _fact(knowledge,records,source["entity"],source["field"])
    rows=[]
    for entity in knowledge.entities:
        if entity["kind"]!=source["collection"]:continue
        row={"name":entity["name"]}
        for fact in knowledge.facts:
            if fact["subject"]==entity["id"]:row[fact["field"]]=_fact(knowledge,records,entity["id"],fact["field"])
        rows.append(row)
    return rows

def _transform(parameters,knowledge,records):
    current=_source(parameters["source"],knowledge,records);last_list=current if isinstance(current,(list,tuple)) else None
    for op in parameters["operations"]:
        kind=op["op"]
        if not isinstance(current,(tuple,list)) or len(current)>256:raise ValueError("finite input sequence")
        field=op.get("field");key=lambda item:item if field is None else item[field]
        if kind=="filter":current=[item for item in current if _compare(key(item),op["comparison"],op["value"])]
        elif kind=="sort":
            keys=[key(item) for item in current]
            if all(isinstance(v,str) for v in keys):current=sorted(current,key=key)
            else:
                for v in keys:_number(v)
                current=sorted(current,key=lambda item:_number(key(item)))
        elif kind=="sum":current=_total(current)
        elif kind=="group":
            grouped={}
            for item in current:
                group=item[op["key"]]
                if not isinstance(group,str):raise ValueError("group key")
                grouped.setdefault(group,[]).append(item[op["value"]])
            current={group:_total(grouped[group]) for group in sorted(grouped)}
        elif kind=="select":current=[{field:item[field] for field in op["fields"]} for item in current]
        elif kind=="format":
            def scalar(v):
                if v is None:return "null"
                if isinstance(v,bool):return "true" if v else "false"
                if isinstance(v,(int,float)):_number(v)
                if isinstance(v,(str,int,float)):return str(v)
                raise ValueError("scalar format")
            current=op["separator"].join(scalar(v) for v in current)
        else:raise ValueError("unsupported transformation")
        if len(canonical_bytes(current))>65536:raise ValueError("intermediate byte limit")
        if isinstance(current,(list,tuple)):last_list=current
    names=tuple(item["name"] if isinstance(item,Mapping) and set(item)=={"name"} else item
                for item in last_list) if last_list is not None else None
    return {"value":current,"list":last_list,"sum":current,"map":current,"names":names}

def _policy(goal,knowledge,records,state):
    task=goal.parameters["task"];entity=goal.parameters["entity"]
    fact=lambda field:_fact(knowledge,records,entity,field)
    declared=lambda field:any(f["subject"]==entity and f["field"]==field for f in knowledge.facts)
    if task=="approve":
        return _compare(fact("amount"),"le",fact("limit")) and (
            not declared("requires_department") or fact("requires_department") is not True or fact("department_approval") is True)
    if task=="prepare":
        policy=fact("calibration_policy")
        if policy=="basic":return True
        if policy=="reference":_number(fact("reference_setting"));return True
        return False
    if task=="reconcile":
        _number(fact("recorded_count"))
        return not declared("requires_revision") or fact("requires_revision") is not True or isinstance(fact("count_revision"),str)
    if task=="pack":
        return not declared("required_package") or state.values[entity]["package"]==fact("required_package")
    return False

def verify_completion(goal,candidate,*,knowledge,final_state,control_snapshot):
    predicates=[];observation_refs=();integrity=True
    try:
        if not isinstance(goal,GoalContract) or not goal.predicates:raise ProvenanceError("nonempty accepted goal")
        observation_refs=_control_and_observations(goal,candidate,knowledge,final_state,control_snapshot)
        records=_records(candidate,knowledge)
        entity=goal.parameters.get("entity")
        if entity is not None and not any(e["id"]==entity for e in knowledge.entities):raise ProvenanceError("goal entity identity")
        expected_outputs=tuple(p.arguments["output"] for p in goal.predicates if p.operator is PredicateOperator.TRANSFORM_RESULT)
        transformed=_transform(goal.parameters,knowledge,records) if goal.kind is TaskKind.TRANSFORM else {}
        if len(expected_outputs)>1 and (not isinstance(candidate.data,Mapping) or set(candidate.data)!=set(expected_outputs)):
            raise ValueError("all requested outputs required")
        if len(expected_outputs)==1 and isinstance(candidate.data,Mapping):
            output=expected_outputs[0]
            if not _same(candidate.data,transformed[output]) and set(candidate.data)!={output}:
                raise ValueError("unsupported additional output claim")
        if goal.kind is TaskKind.STATE_GOAL and not _same(candidate.data,{"entity":entity,"state":final_state.values[entity]}):
            raise ValueError("unsupported state claim")
        allowed={TaskKind.FACT:{PredicateOperator.FACT_EQUALS},TaskKind.RELATION:{PredicateOperator.RELATION_PATH},
                 TaskKind.TRANSFORM:{PredicateOperator.TRANSFORM_RESULT},
                 TaskKind.STATE_GOAL:{PredicateOperator.STATE_EQUALS,PredicateOperator.STATE_RANGE,PredicateOperator.POLICY_VALID}}
        for p in goal.predicates:
            args=p.arguments
            if p.operator not in allowed[goal.kind]:raise ValueError("inapplicable predicate")
            if p.operator is PredicateOperator.FACT_EQUALS:
                claimed=candidate.data["value"] if isinstance(candidate.data,Mapping) and set(candidate.data)=={"value"} else candidate.data
                passed=_same(claimed,_fact(knowledge,records,args["entity"],args["field"]))
            elif p.operator is PredicateOperator.RELATION_PATH:passed=_relation(goal,p,candidate,knowledge,records)
            elif p.operator is PredicateOperator.TRANSFORM_RESULT:
                output=args["output"]
                claimed=candidate.data[output] if isinstance(candidate.data,Mapping) and output in candidate.data else candidate.data
                passed=_same(claimed,transformed[output])
            elif p.operator is PredicateOperator.POLICY_VALID:passed=_policy(goal,knowledge,records,final_state)
            elif p.operator is PredicateOperator.STATE_RANGE:
                value=final_state.values[args["entity"]][args["field"]]
                passed=_compare(value,"ge",args["min"]) and _compare(value,"le",args["max"])
            else:
                expected=_fact(knowledge,records,args["entity"],args["fact_field"]) if "fact_field" in args else args["value"]
                if isinstance(expected,Mapping) and set(expected)=={"sum"}:expected=_total(expected["sum"])
                passed=_same(final_state.values[args["entity"]][args["field"]],expected)
            predicates.append(PredicateVerdict(p.predicate_id,"PASS" if passed else "FAIL",
                              candidate.evidence_refs,"independent trusted semantic check"))
    except (ProvenanceError,Unresolved,ValueError,TypeError,KeyError,AttributeError,OverflowError) as exc:
        if isinstance(exc,ProvenanceError):integrity=False
        status="UNRESOLVED" if isinstance(exc,Unresolved) else "FAIL"
        predicates=[PredicateVerdict(p.predicate_id,status,(),str(exc)) for p in getattr(goal,"predicates",())]
    return VerificationRecord(goal.goal_id,tuple(predicates),observation_refs,
       final_state.snapshot_id if final_state is not None else None,integrity,
       control_snapshot.run_id,candidate.attempt.execution_id if candidate.attempt else None,
       fingerprint(goal),fingerprint(candidate),fingerprint(candidate.data))

def candidate_from_attempt(goal,context,attempt):
    records=context.items if hasattr(context,"items") and not isinstance(context,Mapping) else tuple(context)
    refs=tuple(r.evidence_id for r in records if r.kind is not EvidenceKind.USER_INPUT)
    if goal.kind is TaskKind.STATE_GOAL:data={"entity":goal.parameters["entity"],"state":attempt.final_state.values[goal.parameters["entity"]]}
    elif goal.kind is TaskKind.RELATION:
        data={"paths":tuple({k:r.payload[k] for k in ("node_ids","edge_ids","evidence_ids")}
                            for r in records if r.payload.get("record_kind")=="path")}
    elif goal.kind is TaskKind.TRANSFORM:
        outputs=tuple(p.arguments["output"] for p in goal.predicates)
        list_result=next((o.result for o in reversed(attempt.observations) if o.executed and isinstance(o.result,(tuple,list))),None)
        values={"value":attempt.output,"sum":attempt.output,"map":attempt.output,"list":list_result,
                "names":tuple(v["name"] if isinstance(v,Mapping) and set(v)=={"name"} else v for v in list_result) if list_result is not None else None}
        data={output:values[output] for output in outputs}
    else:data=attempt.output
    return CompletionCandidate(data,refs,attempt,tuple(records))
