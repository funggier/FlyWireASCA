"""Disclosed scripted engineering replay; never physical capability or cost evidence."""
from dataclasses import dataclass
import json,time
from collections.abc import Mapping
from project_asca.agent_runtime.contracts import PhysicalIdentity,BrokerModelResponse,EmbeddingBatch,Usage,AgentRequest
from project_asca.agent_runtime.control import MonotonicClock
from project_asca.agent_runtime.ports import RuntimePorts
from project_asca.agent_runtime.broker import ModelBroker
from project_asca.agent_runtime.domain import load_public_configuration
from project_asca.agent_runtime.factory import build_stage_a_runtime
from project_asca.agent_runtime.goals import TaskSchemaRegistry
from project_asca.agent_runtime.interpretation import deterministic_intent,normalize_with_spans,_has,RELATION_ALIASES
from project_asca.agent_runtime.values import TaskKind,RunVariant,thaw_json,fingerprint
from . import oracle
from .direct import DirectPinnedRunner,justified_stop
from .fixture import bounds_from_workload
from .freeze import validate_freeze
@dataclass(frozen=True,slots=True)
class PortableQualification:
    evidence_kind:str
    physical:bool
    scripted_usage:bool
    architecture_outcome:object
    freeze_valid:bool
    engineering_valid:bool
    trials:tuple
    totals:object
    setup:object
    limitations:tuple
class PortableIdentity:
    def __init__(self,identity):self.identity=identity
    def inspect(self):return self.identity
class ScriptedEmbedding:
    def __init__(self,identity):self.identity=identity
    def embed(self,texts,*,deadline,cancellation):
        return EmbeddingBatch(self.identity.embedding_name,self.identity.embedding_digest,1024,
                              tuple((1.0,)+(0.0,)*1023 for _ in texts),0,{"scripted":True})
def wire_interpretation(text,configuration):
    found=deterministic_intent(AgentRequest(text),TaskSchemaRegistry.from_public(configuration))
    if found is None:return None,None
    if found.intent is None:
        return {"status":"NEEDS_CLARIFICATION" if found.clarification else "UNSUPPORTED",
                "reason":"AMBIGUOUS_INPUT" if found.clarification else "UNSUPPORTED_CAPABILITY"},None
    b=found.intent.bindings;p=thaw_json(b["parameters"])
    return {"kind":found.intent.kind.value,"task":b["task"],"parameters":p,
            "spans":[{"name":k,"value":v,"start":0,"end":len(text)} for k,v in p.items()
                     if k not in ("operations","outputs","top_level")]},p
def scripted_plan(task,p,facts):
    steps=[]
    def add(cap,args):
        identifier="s"+str(len(steps)+1)
        steps.append({"id":identifier,"capability":cap,"version":"1","inputs":args})
        return {"source":"step","reference":identifier}
    def lit(v):return {"source":"literal","value":v}
    entity=p.get("entity");ent={"entity":lit(entity)}
    declared=lambda name:any(f["subject"]==entity and f["field"]==name for f in facts)
    if task=="pack":
        if declared("required_package"):add("package",ent)
        add("pack",ent);add("seal",ent)
    elif task=="approve":add("policy",ent);add("approve",ent)
    elif task=="prepare":add("calibrate",ent);add("ready",ent)
    elif task=="reconcile":add("reconcile",ent)
    elif task in ("set","state_range"):
        value=p.get("value",p.get("min"))
        if isinstance(value,Mapping):
            current=add("sum",{"items":lit(value["sum"])})
        else:current=lit(value)
        add("set",{"entity":lit(entity),"field":lit(p["field"]),"value":current})
        if isinstance(value,Mapping) and "verify" in value:add("assert",{"actual":current,"op":lit("eq"),"value":lit(value["verify"])})
    elif task=="transform":
        source=p["source"]
        if "literal" in source:values=source["literal"]
        elif "entity" in source:
            values=next(f["value"] for f in facts if f["subject"]==source["entity"] and f["field"]==source["field"])
        else:
            groups={}
            for f in facts:
                if f["field"] in ("cost","approved"):
                    groups.setdefault(f["subject"],{"name":f["subject"]})[f["field"]]=f["value"]
            values=list(groups.values())
        current=lit(values)
        for op in p["operations"]:
            name=op["op"];args={"items":current}
            if name=="filter":args.update(field=lit(op.get("field")),op=lit(op["comparison"]),value=lit(op["value"]))
            elif name=="sort":args["field"]=lit(op.get("field"))
            elif name=="group":args.update(key=lit(op["key"]),value=lit(op["value"]))
            elif name=="format":args["separator"]=lit(op["separator"])
            elif name=="select":args["fields"]=lit(op["fields"])
            current=add(name,args)
    return {"type":"bounded-steps","steps":steps,"bindings":{}}
def scripted_paths(entity,relations,edges,top_level):
    paths=[]
    def walk(nodes,used):
        if len(used)>=3:return
        for e in edges:
            if (e["source"]!=nodes[-1] or e["relation"] not in relations or e["confidence"]<.5
                or e["target"] in nodes):continue
            ns=nodes+[e["target"]];es=used+[e["id"]]
            terminal=not any(x["source"]==ns[-1] and x["relation"]==e["relation"] and x["confidence"]>=.5 for x in edges)
            if not top_level or terminal:paths.append({"node_ids":ns,"edge_ids":es,"evidence_ids":["evidence:"+x for x in es]})
            walk(ns,es)
    walk([entity],[])
    return paths
class ScriptedModel:
    def __init__(self,configuration,identity):self.configuration=configuration;self.identity=identity
    def generate(self,request,*,deadline,cancellation):
        prompt=request.prompt;role=prompt.template_id;cfg=self.configuration
        if role=="a014-router":
            text=normalize_with_spans(prompt.messages[-1].content).text
            relations=[r.lower() for r,a in RELATION_ALIASES.items() if _has(text,a)]
            body={"requires_relation":bool(relations),"required_relations":relations,"requires_path_provenance":bool(relations)}
        else:
            payload=json.loads(prompt.messages[-1].content)
            if role=="a015-intent-v1":
                body,_=wire_interpretation(payload["text"],cfg);body=body or {}
            elif role in ("a015-plan_proposal-v1","a015-plan_repair-v1"):
                p=payload["goal"]["parameters"]
                facts=[r["payload"] for r in payload["context"]["items"] if "subject" in r["payload"] and "field" in r["payload"]]
                body=scripted_plan(p["task"],p,facts)
            elif role=="a015-direct-v1":
                intent,p=wire_interpretation(payload["text"],cfg)
                if intent is None:body={}
                elif p is None:body={"intent":intent,"proposal":{"type":"stop",**intent}}
                else:
                    from project_asca.agent_runtime.goals import GoalCompiler
                    from project_asca.agent_runtime.interpretation import validate_intent_proposal
                    found=validate_intent_proposal(intent,AgentRequest(payload["text"]),TaskSchemaRegistry.from_public(cfg))
                    goal=GoalCompiler().compile(found.intent,AgentRequest(payload["text"]),TaskSchemaRegistry.from_public(cfg))
                    stop=justified_stop(goal,cfg)
                    if stop:proposal={"type":"stop","status":"BOUNDED_FAILURE","reason":stop.value}
                    elif intent["task"]=="fact":
                        fact=next(f for f in cfg.knowledge.facts if f["subject"]==p["entity"] and f["field"]==p["field"])
                        proposal={"type":"structured-answer","data":fact["value"],"evidence_ids":[fact["id"]]}
                    elif intent["task"]=="relation":
                        paths=scripted_paths(p["entity"],p["relations"],cfg.knowledge.edges,p.get("top_level",False))
                        proposal={"type":"structured-answer","data":{"paths":paths},
                                  "evidence_ids":list(dict.fromkeys(e for path in paths for e in path["edge_ids"]))}
                    else:proposal=scripted_plan(intent["task"],p,cfg.knowledge.facts)
                    body={"intent":intent,"proposal":proposal}
            else:body={}
        return BrokerModelResponse(request.subrequest_id,self.identity,json.dumps(body,ensure_ascii=False),
                                   Usage(64,min(128,request.max_output_tokens),True),{"scripted":True},transport_dispatches=0)
def run_portable_qualification(workload):
    cfg=load_public_configuration(workload.public,workload.profile)
    identity=PhysicalIdentity(**workload.certificate["identity"]);bounds=bounds_from_workload(workload)
    freeze=validate_freeze(workload,bounds);clock=MonotonicClock()
    model=ScriptedModel(cfg,identity)
    runtime=build_stage_a_runtime(cfg,RuntimePorts(model,ScriptedEmbedding(identity),bounds,PortableIdentity(identity),clock))
    direct=DirectPinnedRunner(cfg,ModelBroker(model,bounds,identity),clock=clock);trials=[]
    for case in workload.cases:
        for variant,runner in ((RunVariant.UNIFIED_RUNTIME,runtime),(RunVariant.DIRECT_PINNED_MODEL,direct)):
            first=len(runner.model_records);start=clock.now();result=runner.run(case.text);wall=max(0.0,clock.now()-start)
            records=tuple(runner.model_records[first:])
            verdict=oracle.evaluate_trial(case,workload.oracle[case.case_id],result)
            trials.append(oracle.RawTrial(case.case_id,variant,1,fingerprint(case.text),result,verdict,records,wall))
    totals=oracle.aggregate_trials(tuple(trials))
    engineering=freeze.valid and all(v.false_success==0 and v.controls_correct==16 and v.bounded_failures_correct==8 for v in totals.variants.values()) and not any(t.result.status.value=="SUCCEEDED" and t.result.metrics.integrity_failures for t in trials)
    return PortableQualification("PORTABLE_ENGINEERING",False,True,None,freeze.valid,engineering,tuple(trials),totals,
         runtime.setup_metrics,("Scripted generation/constant embedding vectors; no physical capability claim.",
                                "Fake usage cannot support token savings or research preference.",
                                "Frozen cases are evaluated only after terminal publication; task misses remain visible."))
