"""Validated immutable public deployment data, without evaluator metadata."""
from dataclasses import dataclass
from collections.abc import Mapping
from .values import FrozenRecord,freeze_json,canonical_bytes,fingerprint
from .profile import RuntimeProfile
from .semantics import KnowledgeSnapshot,StateSnapshot
from .plans import StrategyCatalog,StrategyDescriptor

@dataclass(frozen=True,slots=True)
class PublicConfiguration(FrozenRecord):
    public:Mapping
    profile:RuntimeProfile
    knowledge:KnowledgeSnapshot
    initial_state:StateSnapshot
    catalog:StrategyCatalog
    capabilities:tuple
    task_schemas:Mapping
    dependency_reachable:bool

def load_public_configuration(public,profile):
    allowed={"version","defaults","columns","entities","facts","edges","initial",
             "capabilities","procedures","task_schemas","limits","bindings"}
    if not isinstance(public,Mapping) or set(public)!=allowed:
        raise ValueError("closed public configuration")
    public=freeze_json(public)
    try:p=RuntimeProfile(**dict(profile))
    except TypeError as exc:raise ValueError("unknown runtime profile field") from exc
    if len(canonical_bytes(public["initial"]))>p.state_bytes:raise ValueError("initial state bound")
    def records(name):
        columns=public["columns"][name];result=[]
        if len(set(columns))!=len(columns):raise ValueError("duplicate table columns")
        for row in public[name]:
            if name=="entities":
                if len(row) not in (2,3):raise ValueError("entity table arity")
                item={"id":row[0],"kind":row[1],"name":row[2] if len(row)==3 else row[0]}
            else:
                if len(row)!=len(columns):raise ValueError("table arity "+name)
                item=dict(zip(columns,row))
            item["version"]=public["defaults"]["version"]
            if name=="facts":item["confidence"]=public["defaults"]["confidence"]
            if name=="procedures":
                steps=[]
                for step in item["steps"]:
                    if isinstance(step,str):
                        steps.append(("call",step[5:]) if step.startswith("call:") else (step,{"entity":"$entity"}))
                    else:steps.append(step)
                item["steps"]=steps
            result.append(freeze_json(item))
        if len({r["id"] for r in result})!=len(result):raise ValueError("duplicate "+name+" identity")
        return tuple(result)
    entities=records("entities");facts=records("facts");edges=records("edges")
    caps=records("capabilities");procedures=records("procedures")
    ids={e["id"] for e in entities}
    if any(not isinstance(e["id"],str) or not e["id"] for e in entities):raise ValueError("entity ID")
    if any(f["subject"] not in ids for f in facts):raise ValueError("unknown fact subject")
    if len({(f["subject"],f["field"]) for f in facts})!=len(facts):raise ValueError("duplicate fact field")
    relations={"WORKS_AT","CAUSED_BY","OCCURRED_BEFORE","PART_OF","USED_FOR"}
    if any(e["source"] not in ids or e["target"] not in ids or e["relation"] not in relations
           or not 0<=e["confidence"]<=1 or not 0<=e["activation_weight"]<=1 for e in edges):
        raise ValueError("edge identity/type/confidence")
    if any(c["effect"] not in ("PURE","IN_MEMORY") for c in caps):raise ValueError("public effect class")
    initial=public["initial"]
    if set(initial)!={"by_kind","overrides"} or set(initial["overrides"])-ids:raise ValueError("initial schema")
    initial_values={e["id"]:dict(initial["by_kind"][e["kind"]]) for e in entities if e["kind"] in initial["by_kind"]}
    for entity,values in initial["overrides"].items():
        if entity not in initial_values:raise ValueError("unknown state override")
        initial_values[entity].update(values)
    cap_ids={c["id"] for c in caps};by_root={r["id"]:r for r in procedures}
    def cost(root,active=()):
        if root in active or len(active)>=8:raise ValueError("recursive/deep procedure")
        total=0
        for op,arg in by_root[root]["steps"]:
            if op=="call":
                if arg not in by_root:raise ValueError("missing child root")
                total+=cost(arg,active+(root,))
            elif op in cap_ids:total+=1
            else:raise ValueError("unknown capability")
        if not 0<total<=32:raise ValueError("procedure bound")
        return total
    descriptors=tuple(StrategyDescriptor(r["id"],r["version"],("STATE_GOAL",),r["id"],
        {"inputs":("entity",),"output":"state"},effects=(r["task"],),
        goal_compatibility={"task":r["task"]},evidence_requirements=tuple(r["evidence"]),
        cost=cost(r["id"]),description={"en":r["description"][0],"th":r["description"][1]}) for r in procedures)
    fields={(f["subject"],f["field"]) for f in facts}
    reachable=all((entity,required) in fields for entity,flag,required in
        ((f["subject"],f["field"],"department_approval" if f["field"]=="requires_department" else "count_revision")
         for f in facts if f["field"] in ("requires_department","requires_revision") and f["value"]))
    reachable=reachable and all((f["subject"],"reference_setting") in fields for f in facts
                                if f["field"]=="calibration_policy" and f["value"]=="reference")
    if not reachable:raise ValueError("declared policy dependency unreachable")
    if len(facts)+len(entities)+len(descriptors)>p.indexed_records:raise ValueError("search universe limit")
    digest=fingerprint(public)
    snapshot=KnowledgeSnapshot("public:"+digest,entities,facts,edges,facts,caps)
    state=StateSnapshot("initial:"+fingerprint(initial_values),0,initial_values)
    return PublicConfiguration(public,p,snapshot,state,StrategyCatalog(descriptors,procedures),
                               caps,public["task_schemas"],reachable)
