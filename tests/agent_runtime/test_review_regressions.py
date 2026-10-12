"""Fresh review reproductions; development inputs, no frozen task oracle."""
import pytest
from dataclasses import replace
from .conftest import api
from .test_public_runtime import build
from .test_verification import probe,make_candidate,verdict

@pytest.mark.parametrize("text",[
 "Keep 2, 5, 8, 12 above 3 and below 10, then sort.",
 "Keep 2, 5, 8, 12 below 10 and above 3, then sort.",
 "เก็บ 2, 5, 8, 12 ที่มากกว่า 3 และต่ำกว่า 10 แล้วเรียง",
])
def test_every_recognized_filter_reaches_verified_result(text,configuration,clock):
    runtime,_=build(configuration,clock)
    result=runtime.run(text)
    assert result.status.value=="SUCCEEDED"
    assert result.data["list"]==(5,8)
    assert len(result.interpreted_goal.parameters["operations"])==3

def test_explicit_semicolon_is_not_replaced_by_default_comma(configuration,clock):
    runtime,_=build(configuration,clock)
    result=runtime.run("Format 13, 2, 7 separated by a semicolon.")
    assert result.status.value=="SUCCEEDED"
    assert result.data["value"]=="13;2;7"

@pytest.mark.parametrize("text",[
 "Format 13, 2, 7 with semicolons and calculate their sum.",
 "Sort 13, 2, 7 in descending order.",
])
def test_unsupported_transform_modifier_cannot_publish_partial_success(text,configuration,clock):
    runtime,_=build(configuration,clock)
    result=runtime.run(text)
    assert result.status.value!="SUCCEEDED"
    assert not result.verification or not result.verification.passed

def test_model_intent_cannot_drop_second_recognized_threshold(schemas):
    text="Keep 2, 5, 8, 12 above 3 and below 10, then sort."
    request=api("contracts").AgentRequest(text)
    start=text.index("2");end=text.index(" above")
    low=text.index("3 and")
    raw={"kind":"TRANSFORM","task":"transform","parameters":{
        "source":{"literal":[2,5,8,12]},
        "operations":[{"op":"filter","field":None,"comparison":"gt","value":3},{"op":"sort","field":None}],
        "outputs":["list"]},"spans":[
        {"name":"source","value":{"literal":[2,5,8,12]},"start":start,"end":end},
        {"name":"threshold","value":3,"start":low,"end":low+1}]}
    with pytest.raises(ValueError):
        api("interpretation").validate_intent_proposal(raw,request,schemas)

def test_single_output_rejects_unverified_extra_claims(configuration,registry,schemas,clock):
    goal,context,c,attempt=probe("transform",{"source":{"literal":[13,2,7]},
        "operations":[{"op":"sum"}],"outputs":["value"]},configuration,registry,schemas,clock)
    candidate=make_candidate(goal,context,attempt,{"value":22,"extra_claim":"Nira office is South"})
    checked=verdict(goal,candidate,c,configuration)
    assert not checked.passed
    rendered=api("rendering").render_result_data(candidate,checked)
    assert "extra_claim" not in rendered and "Nira office is South" not in rendered

@pytest.mark.parametrize("interruption",["cancel","deadline"])
def test_terminal_arbitration_rechecks_after_rendering(interruption,configuration,clock,monkeypatch):
    runtime,_=build(configuration,clock)
    cancellation=api("control").Cancellation()
    module=api("controller");render=module.render_result_data
    def interrupted(*args,**kwargs):
        answer=render(*args,**kwargs)
        if interruption=="cancel":cancellation.cancel()
        else:clock.value=1000
        return answer
    monkeypatch.setattr(module,"render_result_data",interrupted)
    result=runtime.run("Add 13 and 2.",cancellation=cancellation)
    assert result.status.value=="CANCELLED" if interruption=="cancel" else result.reason.value=="DEADLINE_EXCEEDED"
    terminals=[e for e in result.trace if e.kind=="terminal"]
    assert len(terminals)==1 and terminals[0].payload["status"]==result.status.value

def test_cancellation_acceptance_is_serialized_with_success_publication(configuration,clock,monkeypatch):
    import threading
    runtime,_=build(configuration,clock);token=api("control").Cancellation()
    module=api("controller");finish=module.StateMachine.finish
    accepted=[];workers=[]
    def concurrent_finish(machine):
        entered=threading.Event()
        def cancel():
            entered.set();token.cancel();accepted.append(machine.control.terminal)
        worker=threading.Thread(target=cancel);workers.append(worker);worker.start()
        assert entered.wait(1)
        finish(machine)
    monkeypatch.setattr(module.StateMachine,"finish",concurrent_finish)
    result=runtime.run("Add 13 and 2.",cancellation=token)
    for worker in workers:worker.join(1)
    assert accepted==[True]
    assert result.status.value=="SUCCEEDED"

def test_resealed_zero_vector_work_cannot_override_public_eligible_documents(configuration,clock):
    from project_asca.evaluation.evidence import _event_replay
    runtime,_=build(configuration,clock)
    result=runtime.run("Please report Nira office for this development check.")
    assert result.status.value=="SUCCEEDED" and result.metrics.counters["vectors_scored"]>0
    assert _event_replay(result,configuration)
    counters={**dict(result.metrics.counters),"vectors_scored":0}
    reported={**dict(result.metrics.reported),"vectors_scored":0}
    trace=tuple(replace(e,payload={**dict(e.payload),"vectors_scored":0,"eligible_vectors":0})
        if e.kind=="retrieval" else e for e in result.trace)
    changed=replace(result,trace=trace,metrics=replace(result.metrics,counters=counters,reported=reported))
    with pytest.raises(ValueError):
        _event_replay(changed,configuration)

@pytest.mark.parametrize(("text","expected"),[
    ("Format 13, 2, 7 separated by tabs.","13\t2\t7"),
    ("Format 13, 2, 7 separated by ';'.","13;2;7"),
])
def test_explicit_tab_and_quoted_separator_publish_exact_requested_format(configuration,clock,text,expected):
    runtime,_=build(configuration,clock)
    result=runtime.run(text)
    assert result.status.value=="SUCCEEDED"
    assert result.data["value"]==expected
