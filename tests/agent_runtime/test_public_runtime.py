import pytest,json
from dataclasses import replace
from .conftest import api
from .test_knowledge_adapter import Embedding

class Identity:
    def inspect(self):
        p=api("profile")
        return api("contracts").PhysicalIdentity("qwen3.5:4b",p.GENERATION_DIGEST,
            "qwen3-embedding:0.6b",p.EMBEDDING_DIGEST,1024,"0.32.15",{"portable":True})

class Bounds:
    def bound(self,prompt):return api("contracts").PromptBound(3000,"development-only-certificate")

class Model:
    def __init__(self,handler=None):self.calls=[];self.handler=handler
    def generate(self,request,*,deadline,cancellation):
        self.calls.append(request)
        if self.handler:return self.handler(request,deadline,cancellation)
        raise AssertionError("unnecessary generation in development deterministic task")

def build(configuration,clock,*,model=None):
    model=model or Model()
    ports=api("ports").RuntimePorts(model,Embedding(),Bounds(),Identity(),clock)
    runtime=api("factory").build_stage_a_runtime(configuration,ports)
    return runtime,model

@pytest.mark.parametrize("text",[
 "Please add 13 and 2 for a development check.",
 "ช่วยบวก 13 กับ 2 สำหรับตรวจระบบ",
 "Please report Nira office for this development check.",
 "Please pack order O1 and seal it securely.",
 "Which company does Ada work for in this development check?",
 "กรุณาบอกว่าสำนักงานของ Nira อยู่ที่ไหน",
])
def test_public_text_runs_own_complete_lifecycle(text,configuration,clock):
    runtime,model=build(configuration,clock)
    result=runtime.run(text)
    assert result.status is api("values").TerminalStatus.SUCCEEDED
    assert result.verification.passed and result.interpreted_goal
    assert result.metrics.strategy_attempts>=1
    assert result.metrics.model_invocations==0 and not model.calls
    assert result.trace[-1].kind=="terminal"
    assert runtime.setup_metrics.document_embedding_calls==2

def test_fresh_runs_do_not_reuse_goal_state_or_result_cache(configuration,clock):
    runtime,_=build(configuration,clock)
    first=runtime.run("Please pack order O1 and seal it securely.")
    second=runtime.run("Please pack order O1 and seal it securely.")
    assert first.run_id!=second.run_id
    assert first.final_state_ref!=second.final_state_ref
    assert first.data==second.data
    assert configuration.initial_state.values["O1"]["status"]=="pending"
    assert first.metrics.strategy_attempts==second.metrics.strategy_attempts==1
    assert not runtime._knowledge.cache

@pytest.mark.parametrize("value",[
 {"text":"Add13 and2","structural_need":{}},{"text":"Add13 and2","procedure_id":"pack"},
 {"text":"Add13 and2","expected_answer_ids":["gold"]},"",{"text":5},
])
def test_invalid_public_fields_are_rejected_without_task_dispatch(value,configuration,clock):
    runtime,model=build(configuration,clock)
    result=runtime.run(value)
    assert result.status is api("values").TerminalStatus.REJECTED
    assert result.reason is api("values").TerminalReason.INVALID_INPUT
    assert result.metrics.model_invocations==0 and not model.calls

def test_all_terminal_controls_are_typed(configuration,clock):
    runtime,_=build(configuration,clock)
    for text,status in [("Who does Alex work for?","NEEDS_CLARIFICATION"),
                        ("Please email this invoice.","UNSUPPORTED"),
                        ("Set tray T1 to at least9 and at most3.","BOUNDED_FAILURE")]:
        assert runtime.run(text).status.value==status

def test_cancellation_and_deadline_publish_once_without_late_dispatch(configuration,clock):
    runtime,_=build(configuration,clock)
    token=api("control").Cancellation();token.cancel()
    result=runtime.run("Please add13 and2.",cancellation=token)
    assert result.status is api("values").TerminalStatus.CANCELLED
    assert result.metrics.strategy_attempts==0
    limited=replace(configuration,profile=replace(configuration.profile,transitions=2))
    run,_=build(limited,clock)
    stopped=run.run("Please add13 and2.")
    assert stopped.status is api("values").TerminalStatus.BOUNDED_FAILURE
    assert stopped.metrics.reservations.get("transitions",0)<=2
    assert stopped.trace[-1].kind=="terminal"

def test_terminal_latch_is_write_once():
    latch=api("controller").TerminalLatch()
    c=api("contracts");v=api("values")
    one=c.AgentResult("r","run",v.TerminalStatus.CANCELLED,v.TerminalReason.CANCELLED)
    two=c.AgentResult("r","another",v.TerminalStatus.REJECTED,v.TerminalReason.INVALID_INPUT)
    assert latch.publish(one) is one and latch.publish(two) is one


def test_self_contained_task_skips_acquiring_phase(configuration,clock):
    runtime,_=build(configuration,clock)
    result=runtime.run("Please add 13 and 2 for a development check.")
    phases=[e.payload["to"] for e in result.trace if e.kind=="phase"]
    assert result.status.value=="SUCCEEDED" and "ACQUIRING" not in phases

def test_request_deadline_prevents_next_dispatch(configuration,clock):
    runtime,_=build(configuration,clock);components=runtime._components
    def delayed(control):
        parts=components(control);original=parts.interpreter.interpret
        def interpret(request,*,control):
            found=original(request,control=control);clock.value+=180;return found
        parts.interpreter.interpret=interpret;return parts
    runtime._components=delayed
    result=runtime.run("Please add 13 and 2 for a development check.")
    assert result.status.value=="BOUNDED_FAILURE" and result.reason.value=="DEADLINE_EXCEEDED"
    assert result.metrics.strategy_attempts==0 and result.trace[-1].kind=="terminal"

def test_request_mutation_fails_before_execution(configuration,clock):
    runtime,_=build(configuration,clock);components=runtime._components
    def corrupt(control):
        parts=components(control);original=parts.acquirer.acquire
        def acquire(*args,**kwargs):
            found=original(*args,**kwargs);control.request=api("contracts").AgentRequest("Wrong task");return found
        parts.acquirer.acquire=acquire;return parts
    runtime._components=corrupt
    result=runtime.run("Please add 13 and 2 for a development check.")
    assert result.status.value=="REJECTED" and result.metrics.strategy_attempts==0
    assert result.metrics.integrity_failures==1

def test_identity_drift_terminates_without_recovery(configuration,clock):
    def wrong(request,deadline,cancellation):
        identity=replace(Identity().inspect(),model_digest="0"*64)
        return api("contracts").BrokerModelResponse(request.subrequest_id,identity,"{}",api("contracts").Usage(20,2,True))
    runtime,_=build(configuration,clock,model=Model(wrong))
    result=runtime.run("Compute something useful from this unspecified development instruction.")
    assert result.status.value=="REJECTED" and result.reason.value=="IDENTITY_MISMATCH"
    assert result.metrics.recovery_rounds==0 and result.metrics.model_invocations==1


def test_late_callback_cannot_dispatch_after_terminal(configuration,clock):
    runtime,_=build(configuration,clock);components=runtime._components;captured=[]
    def capture(control):
        captured.append(control);return components(control)
    runtime._components=capture
    result=runtime.run("Please add 13 and 2 for a development check.")
    c=captured[-1];before=c.ledger.snapshot();trace=c.trace.freeze()
    with pytest.raises(api("budgets").IntegrityStop):
        c.event("late",{})
    assert c.ledger.snapshot()==before and c.trace.freeze()==trace and c.terminal
    assert result.trace[-1].kind=="terminal"


def test_normalized_thai_threshold_cannot_silently_drop_filter(configuration,clock):
    runtime,_=build(configuration,clock)
    result=runtime.run("ช่วยเก็บตัวเลข 10, 20, 60 ที่ต่ำกว่า 30 แล้วเรียงและหาผลรวม")
    assert result.status.value=="SUCCEEDED"
    assert result.data["list"]==(10,20) and result.data["sum"]==30

def test_publicly_absent_fact_stops_as_missing_evidence(configuration,clock):
    runtime,_=build(configuration,clock)
    result=runtime.run("Report Nira temperature limit for this development evidence check.")
    assert result.status.value=="BOUNDED_FAILURE" and result.reason.value=="MISSING_EVIDENCE"
    assert result.metrics.recovery_rounds==0

def test_low_confidence_relation_has_typed_bounded_failure(configuration,clock):
    runtime,_=build(configuration,clock)
    result=runtime.run("Development evidence check: identify the cause of Echo using the recorded relation.")
    assert result.status.value=="BOUNDED_FAILURE" and result.reason.value=="INSUFFICIENT_CONFIDENCE"
    assert result.metrics.recovery_rounds==0 and result.metrics.relation_invocations==1
