import pytest
from dataclasses import replace
from .conftest import api
from .test_interpretation import NoBroker

def probe(task,parameters,configuration,registry,schemas,clock,*,executor=None):
    s=api("semantics");v=api("values");p=api("plans")
    text="Development verifier probe "+task+" "+str(parameters)
    request=api("contracts").AgentRequest(text)
    intent=s.TaskIntent(api("goals").TASK_KINDS[task],
        {"task":task,"parameters":parameters,"spans":(s.SpanBinding("source",text,0,len(text)),)})
    goal=api("goals").GoalCompiler().compile(intent,request,schemas)
    selected=[]
    entity=parameters.get("entity") or parameters.get("source",{}).get("entity")
    for f in configuration.knowledge.facts:
        if f["subject"]==entity:
            selected.append(s.EvidenceRecord(f["id"],v.EvidenceKind.STORED_FACT,f["id"],configuration.knowledge.snapshot_id,f))
    for row in configuration.catalog.procedures:
        if row["task"]==task:
            selected.append(s.EvidenceRecord("catalog:"+row["id"],v.EvidenceKind.CATALOG_ENTRY,
                                            "catalog:"+row["id"],configuration.knowledge.snapshot_id,row))
    c=api("control").RunControl.create(request,clock=clock)
    paths=()
    if task=="relation":
        from .test_knowledge_adapter import knowledge
        k,_,_=knowledge(configuration)
        paths=k.expand((entity,),s.RouteDecision("DECIDED_RELATIONAL",tuple(parameters["relations"]),True),control=c).paths
    context=api("adapters.selection").assemble_context(goal,tuple(selected),paths,
                                             snapshot=configuration.knowledge,capacity=24)
    candidate=api("strategy").StrategyResolver(configuration.catalog,registry,NoBroker()).resolve(
                goal,context,previous=None,deficits=(),control=c).candidate
    validated=api("strategy").validate_plan(candidate,goal,context,catalog=configuration.catalog,registry=registry,control=c)
    assert validated.plan
    attempt=api("execution").execute_attempt(validated.plan,goal,context,initial=configuration.initial_state,
        catalog=configuration.catalog,registry=registry,authorization=api("capabilities").StageAAuthorization(),
        control=c,executor=executor or api("adapters.procedures").ProcedureExecutionAdapter())
    return goal,context,c,attempt

def make_candidate(goal,context,attempt,data):
    return api("verification").CompletionCandidate(data,tuple(i.evidence_id for i in context.items
       if i.kind is not api("values").EvidenceKind.USER_INPUT),attempt,evidence=context.items)

def verdict(goal,candidate,c,configuration,*,final=None,snapshot=None):
    c.phase=api("values").Phase.VERIFYING
    return api("verification").verify_completion(goal,candidate,knowledge=configuration.knowledge,
         final_state=final if final is not None else candidate.attempt.final_state,
         control_snapshot=snapshot or c.snapshot())

def state_data(goal,attempt):
    entity=goal.parameters["entity"]
    return {"entity":entity,"state":attempt.final_state.values[entity]}

def test_completed_procedure_with_unmet_goal(configuration,registry,schemas,clock):
    class Unsealed:
        def execute(self,*args,**kwargs):
            result=api("adapters.procedures").ProcedureExecutionAdapter().execute(*args,**kwargs)
            values={**dict(result.final_state.values),"O1":{**dict(result.final_state.values["O1"]),"sealed":False}}
            state=api("semantics").StateSnapshot("state:"+api("values").fingerprint(
                {"execution":result.execution_id,"revision":result.final_state.revision,"values":values}),
                result.final_state.revision,values)
            return replace(result,final_state=state,observations=result.observations[:-1]+
                           (replace(result.observations[-1],state_ref=state.snapshot_id),))
    goal,context,c,attempt=probe("pack",{"entity":"O1"},configuration,registry,schemas,clock,executor=Unsealed())
    assert attempt.procedure_state=="COMPLETED"
    candidate=make_candidate(goal,context,attempt,state_data(goal,attempt))
    checked=verdict(goal,candidate,c,configuration)
    assert not checked.passed and any(p.status=="FAIL" for p in checked.predicates)

def test_all_postconditions_require_fresh_final_state(configuration,registry,schemas,clock):
    goal,context,c,attempt=probe("pack",{"entity":"O1"},configuration,registry,schemas,clock)
    candidate=make_candidate(goal,context,attempt,state_data(goal,attempt))
    assert verdict(goal,candidate,c,configuration).passed
    stale=replace(attempt.final_state,revision=attempt.final_state.revision+1)
    assert not verdict(goal,candidate,c,configuration,final=stale).passed

@pytest.mark.parametrize("mutation",["run","execution","capability","version","revision","missing"])
def test_observation_identity_and_revision_fail_closed(mutation,configuration,registry,schemas,clock):
    goal,context,c,attempt=probe("pack",{"entity":"O1"},configuration,registry,schemas,clock)
    changes={"run":{"run_id":"another"},"execution":{"execution_id":"another"},
             "capability":{"capability_id":"sum"},"version":{"capability_version":"wrong"},
             "revision":{"state_revision":999}}
    observations=() if mutation=="missing" else (replace(attempt.observations[0],**changes[mutation]),)+attempt.observations[1:]
    bad=replace(attempt,observations=observations)
    assert not verdict(goal,make_candidate(goal,context,bad,state_data(goal,bad)),c,configuration).passed

def test_factual_value_needs_authoritative_selected_evidence(configuration,registry,schemas,clock):
    goal,context,c,attempt=probe("fact",{"entity":"Nira","field":"office"},configuration,registry,schemas,clock)
    value=next(f["value"] for f in configuration.knowledge.facts if f["subject"]=="Nira" and f["field"]=="office")
    candidate=make_candidate(goal,context,attempt,value)
    assert verdict(goal,candidate,c,configuration).passed
    assert not verdict(goal,replace(candidate,data="invented office"),c,configuration).passed
    assert not verdict(goal,replace(candidate,data={"value":value,"extra_claim":"invented"}),c,configuration).passed
    assert not verdict(goal,replace(candidate,evidence_refs=()),c,configuration).passed

def test_hypothesis_cannot_ground_factual_answer(configuration,registry,schemas,clock):
    goal,context,c,attempt=probe("fact",{"entity":"Nira","field":"office"},configuration,registry,schemas,clock)
    value=attempt.output
    candidate=make_candidate(goal,context,attempt,value)
    items=tuple(replace(i,kind=api("values").EvidenceKind.HYPOTHESIS) if i.payload.get("field")=="office" else i
                for i in candidate.evidence)
    assert not verdict(goal,replace(candidate,evidence=items),c,configuration).passed

def test_transform_recomputes_both_requested_outputs(configuration,registry,schemas,clock):
    parameters={"source":{"literal":[13,2,7]},"operations":[{"op":"sort"},{"op":"sum"}],"outputs":["list","sum"]}
    goal,context,c,attempt=probe("transform",parameters,configuration,registry,schemas,clock)
    candidate=make_candidate(goal,context,attempt,{"list":[2,7,13],"sum":22})
    assert verdict(goal,candidate,c,configuration).passed
    for data in ({"sum":22},{"list":[2,7,13],"sum":21},{"list":[2,13,7],"sum":22}):
        assert not verdict(goal,replace(candidate,data=data),c,configuration).passed

def test_relation_proof_cannot_reverse_or_omit_constituents(configuration,registry,schemas,clock):
    goal,context,c,attempt=probe("relation",{"entity":"Ada","relations":["WORKS_AT"]},configuration,registry,schemas,clock)
    paths=tuple({k:p.payload[k] for k in ("node_ids","edge_ids","evidence_ids")}
                for p in context.items if p.payload.get("record_kind")=="path")
    candidate=make_candidate(goal,context,attempt,{"paths":paths})
    assert verdict(goal,candidate,c,configuration).passed
    wrong={**paths[0],"node_ids":tuple(reversed(paths[0]["node_ids"]))}
    assert not verdict(goal,replace(candidate,data={"paths":[wrong]}),c,configuration).passed
    records=tuple(i for i in candidate.evidence if i.payload.get("record_kind")!="edge_evidence")
    assert not verdict(goal,replace(candidate,evidence=records),c,configuration).passed

def test_empty_goal_and_invalid_control_never_pass(configuration,registry,schemas,clock):
    goal,context,c,attempt=probe("pack",{"entity":"O1"},configuration,registry,schemas,clock)
    candidate=make_candidate(goal,context,attempt,state_data(goal,attempt))
    for snap in (replace(c.snapshot(),integrity=False),replace(c.snapshot(),terminal=True)):
        assert not verdict(goal,candidate,c,configuration,snapshot=snap).passed
    object.__setattr__(goal,"predicates",())
    assert not verdict(goal,candidate,c,configuration).passed

def test_equal_goal_cannot_reuse_another_runs_verification(configuration,registry,schemas,clock):
    first=probe("pack",{"entity":"O1"},configuration,registry,schemas,clock)
    second=probe("pack",{"entity":"O1"},configuration,registry,schemas,clock)
    g,ctx,c,attempt=first;candidate=make_candidate(g,ctx,attempt,state_data(g,attempt))
    assert g.goal_id==second[0].goal_id
    assert not verdict(g,candidate,second[2],configuration).passed


def test_budget_accounting_and_late_cancellation_block_success(configuration,registry,schemas,clock):
    goal,context,c,attempt=probe("pack",{"entity":"O1"},configuration,registry,schemas,clock)
    candidate=make_candidate(goal,context,attempt,state_data(goal,attempt))
    c.phase=api("values").Phase.VERIFYING
    metrics=c.snapshot().metrics
    forged=replace(metrics,counters={**dict(metrics.counters),"primitive_actions":metrics.action_reservations+1})
    assert not verdict(goal,candidate,c,configuration,snapshot=replace(c.snapshot(),metrics=forged)).passed
    clock.value=c.ledger.deadline
    assert not verdict(goal,candidate,c,configuration).passed
    clock.value=0;c.cancellation.cancel()
    assert not verdict(goal,candidate,c,configuration).passed

def test_candidate_builder_keeps_outputs_and_source_records(configuration,registry,schemas,clock):
    parameters={"source":{"literal":[13,2,7]},"operations":[{"op":"sort"},{"op":"sum"}],"outputs":["list","sum"]}
    goal,context,c,attempt=probe("transform",parameters,configuration,registry,schemas,clock)
    candidate=api("verification").candidate_from_attempt(goal,context,attempt)
    assert candidate.data["list"]==(2,7,13) and candidate.data["sum"]==22
    assert verdict(goal,candidate,c,configuration).passed
