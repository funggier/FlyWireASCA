from dataclasses import replace,asdict
from .conftest import api
from .test_public_runtime import build,Model,Identity

def test_real_missing_policy_recovery_keeps_ledger_and_fresh_execution(configuration,clock):
    public=api("values").thaw_json(configuration.public)
    public["facts"] += [["dev-flag","I1","requires_department",True],["dev-approval","I1","department_approval",True]]
    configuration=api("domain").load_public_configuration(public,asdict(configuration.profile))
    runtime,_=build(configuration,clock)
    original=runtime._knowledge.search;calls=0
    def missing_then_complete(query,*,control):
        nonlocal calls
        result=original(query,control=control)
        if query.index_kind=="memory":
            calls+=1
            if calls==1:return replace(result,hits=tuple(h for h in result.hits if h.evidence.payload.get("field")!="department_approval"))
        return result
    runtime._knowledge.search=missing_then_complete
    result=runtime.run("Please approve invoice I1 under its valid limit policy.")
    assert result.status is api("values").TerminalStatus.SUCCEEDED
    assert 1<=result.metrics.recovery_rounds<=2
    assert result.metrics.strategy_attempts<=3 and result.metrics.actual_retrieval_queries<=6
    action_events=[e for e in result.trace if e.kind=="action"]
    ids={e.payload["execution_id"] for e in action_events}
    assert len(ids)>=2 and any(not e.payload["executed"] for e in action_events)
    assert result.interpreted_goal.goal_id==result.verification.goal_id

def test_unchanged_context_and_plan_is_no_progress(configuration,clock):
    public=api("values").thaw_json(configuration.public)
    public["facts"] += [["dev-flag","I1","requires_department",True],["dev-approval","I1","department_approval",True]]
    configuration=api("domain").load_public_configuration(public,asdict(configuration.profile))
    runtime,_=build(configuration,clock)
    original=runtime._knowledge.search
    def always_missing(query,*,control):
        result=original(query,control=control)
        return replace(result,hits=tuple(h for h in result.hits if h.evidence.payload.get("field")!="department_approval"))
    runtime._knowledge.search=always_missing
    result=runtime.run("Please approve invoice I1 under its valid limit policy.")
    assert result.status is api("values").TerminalStatus.BOUNDED_FAILURE
    assert result.reason is api("values").TerminalReason.NO_PROGRESS
    assert result.metrics.recovery_rounds<=2 and result.metrics.strategy_attempts<=3

def test_progress_fingerprints_ignore_opaque_plan_ids_and_item_order(configuration,registry,schemas,clock):
    from .test_execution import plan_for
    plan,goal,context,c=plan_for("Please pack order O1 and seal it securely.",configuration,registry,schemas,clock)
    recovery=api("recovery")
    other=replace(plan.proposal,plan_id="another opaque identity",revision=7)
    assert recovery.plan_fingerprint(plan.proposal)==recovery.plan_fingerprint(other)
    ordered=replace(context,items=tuple(reversed(context.items)),canonical_bytes=0,fingerprint="")
    assert recovery.context_fingerprint(context)==recovery.context_fingerprint(ordered)

def test_model_assist_resumes_requesting_state_without_claiming_success(configuration,clock):
    c=api("contracts")
    def malformed(request,deadline,cancellation):
        return c.BrokerModelResponse(request.subrequest_id,Identity().inspect(),"not JSON",c.Usage(17,3,True))
    model=Model(malformed);runtime,_=build(configuration,clock,model=model)
    result=runtime.run("Compute something useful from this unspecified development instruction.")
    assert result.status is api("values").TerminalStatus.BOUNDED_FAILURE
    phases=[e.payload["to"] for e in result.trace if e.kind=="phase"]
    index=phases.index("MODEL_ASSIST")
    assert phases[index+1]=="INTERPRETING"
    assert result.metrics.model_invocations==1 and not result.verification


def test_two_real_recovery_rounds_share_three_attempt_and_query_budgets(configuration,clock):
    public=api("values").thaw_json(configuration.public)
    public["facts"] += [["dev-flag","I1","requires_department",True],["dev-approval","I1","department_approval",True]]
    config=api("domain").load_public_configuration(public,asdict(configuration.profile))
    runtime,_=build(config,clock);original=runtime._knowledge.search;rounds=0
    def staged(query,*,control):
        nonlocal rounds
        result=original(query,control=control)
        if query.index_kind=="memory":
            rounds+=1
            missing=({"requires_department","department_approval"} if rounds==1 else
                     {"department_approval"} if rounds==2 else set())
            return replace(result,hits=tuple(h for h in result.hits if h.evidence.payload.get("field") not in missing))
        return result
    runtime._knowledge.search=staged
    result=runtime.run("Please approve invoice I1 under its valid limit policy.")
    assert result.status.value=="SUCCEEDED" and result.metrics.recovery_rounds==2
    assert result.metrics.strategy_attempts==3 and result.metrics.actual_retrieval_queries==6
    ids={e.payload["execution_id"] for e in result.trace if e.kind=="action"}
    assert len(ids)==3 and result.metrics.model_invocations==0

def test_failed_stored_plan_can_repair_to_compatible_composed_plan(configuration,clock):
    public=api("values").thaw_json(configuration.public)
    public["facts"].append(["dev-package","O1","required_package","protective"])
    config=api("domain").load_public_configuration(public,asdict(configuration.profile))
    def repair(request,deadline,cancellation):
        import json
        proposal={"type":"bounded-steps","bindings":{},"steps":[
          {"id":"p","capability":"package","version":"1","inputs":{"entity":{"source":"literal","value":"O1"}}},
          {"id":"k","capability":"pack","version":"1","inputs":{"entity":{"source":"literal","value":"O1"}}},
          {"id":"s","capability":"seal","version":"1","inputs":{"entity":{"source":"literal","value":"O1"}}}]}
        return api("contracts").BrokerModelResponse(request.subrequest_id,Identity().inspect(),
            json.dumps(proposal),api("contracts").Usage(80,60,True))
    model=Model(repair);runtime,_=build(config,clock,model=model)
    result=runtime.run("Please pack order O1 and seal it securely.")
    assert result.status.value=="SUCCEEDED" and result.metrics.recovery_rounds==1
    assert len(model.calls)==1 and runtime.model_records[-1]["purpose"]=="PLAN_REPAIR"
    assert result.data["state"]["package"]=="protective"
    assert len({e.payload["execution_id"] for e in result.trace if e.kind=="action"})==2


def test_malformed_repairs_consume_attempts_and_stop_at_bounds(configuration,clock):
    public=api("values").thaw_json(configuration.public)
    public["facts"].append(["dev-package","O1","required_package","protective"])
    config=api("domain").load_public_configuration(public,asdict(configuration.profile))
    def malformed(request,deadline,cancellation):
        return api("contracts").BrokerModelResponse(request.subrequest_id,Identity().inspect(),
             "{broken",api("contracts").Usage(80,5,True))
    runtime,model=build(config,clock,model=Model(malformed))
    result=runtime.run("Please pack order O1 and seal it securely.")
    assert result.status.value=="BOUNDED_FAILURE"
    assert 2<=result.metrics.strategy_attempts<=3 and 1<=len(model.calls)<=2
    assert result.metrics.recovery_rounds<=2
