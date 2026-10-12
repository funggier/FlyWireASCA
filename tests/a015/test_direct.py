import json,pytest
from .conftest import api,direct_for
from tests.agent_runtime.test_public_runtime import Identity,Bounds,Model
def test_direct_is_one_shot_with_complete_public_data(configuration,clock,monkeypatch):
    text="Please add 13 and 2 for a development check."
    runner,model=direct_for(configuration,clock,{"type":"structured-answer","data":15,"evidence_ids":[]},text)
    for unit,name,method in (("interpretation","Interpreter","interpret"),("context","ContextAcquirer","acquire"),
                            ("strategy","StrategyResolver","resolve"),("recovery","RecoveryEngine","decide")):
        monkeypatch.setattr(getattr(api(unit),name),method,lambda *a,**k:pytest.fail("selective orchestration used in direct path"))
    result=runner.run(text)
    assert result.status.value=="SUCCEEDED" and result.data==15 and len(model.calls)==1
    assert json.loads(model.calls[0].prompt.messages[-1].content)["public"]==api("values").thaw_json(configuration.public)
    assert result.metrics.actual_retrieval_queries==result.metrics.relation_invocations==0
    assert result.metrics.active_context_peak is None
    assert runner.model_records[-1]["purpose"]=="DIRECT_SOLUTION"
def test_direct_invalid_prose_is_not_executed_or_repaired(configuration,clock):
    from project_asca.evaluation.direct import DirectPinnedRunner
    def prose(request,deadline,cancellation):
        return api("contracts").BrokerModelResponse(request.subrequest_id,Identity().inspect(),"Done, I packed the order.",api("contracts").Usage(60,8,True))
    model=Model(prose);broker=api("broker").ModelBroker(model,Bounds(),Identity().inspect())
    result=DirectPinnedRunner(configuration,broker,clock=clock).run("Please pack order O1 and seal it securely.")
    assert result.status.value=="BOUNDED_FAILURE" and result.reason.value=="INVALID_PLAN"
    assert len(model.calls)==1 and result.metrics.primitive_actions==0
    assert configuration.initial_state.values["O1"]["status"]=="pending"
def test_direct_executes_valid_public_root_by_id_once(configuration,clock,monkeypatch):
    text="Please pack order O1 and seal it securely."
    runner,_=direct_for(configuration,clock,{"type":"stored-root","root":"pack","bindings":{"entity":"O1"}},text)
    monkeypatch.setattr(api("strategy").StrategyResolver,"resolve",lambda *a,**k:pytest.fail("ranked a root"))
    result=runner.run(text)
    assert result.status.value=="SUCCEEDED" and result.data["state"]["sealed"] is True
    assert result.metrics.strategy_attempts==1 and result.metrics.recovery_rounds==0
def test_direct_cannot_turn_answer_prose_into_state_effect(configuration,clock):
    text="Please pack order O1 and seal it securely."
    runner,_=direct_for(configuration,clock,{"type":"structured-answer","data":{"entity":"O1","state":{"status":"packed","sealed":True}},"evidence_ids":[]},text)
    result=runner.run(text)
    assert result.status.value!="SUCCEEDED" and result.metrics.recovery_rounds==0
    assert configuration.initial_state.values["O1"]["status"]=="pending"
def test_direct_bad_plan_has_no_hidden_repair(configuration,clock):
    text="Please pack order O1 and seal it securely."
    runner,model=direct_for(configuration,clock,{"type":"stored-root","root":"unknown","bindings":{"entity":"O1"}},text)
    result=runner.run(text)
    assert result.status.value=="BOUNDED_FAILURE" and result.metrics.strategy_attempts==1
    assert result.metrics.primitive_actions==0 and len(model.calls)==1
def test_direct_valid_grounded_relation_uses_public_proof_only(configuration,clock):
    text="Which company does Ada work for in this development check?"
    edge=next(e for e in configuration.knowledge.edges if e["source"]=="Ada" and e["relation"]=="WORKS_AT")
    data={"paths":[{"node_ids":[edge["source"],edge["target"]],"edge_ids":[edge["id"]],"evidence_ids":["evidence:"+edge["id"]]}]}
    runner,_=direct_for(configuration,clock,{"type":"structured-answer","data":data,"evidence_ids":[edge["id"]]},text)
    result=runner.run(text)
    assert result.status.value=="SUCCEEDED" and result.verification.passed
    assert result.metrics.relation_invocations==0 and result.metrics.actual_retrieval_queries==0
