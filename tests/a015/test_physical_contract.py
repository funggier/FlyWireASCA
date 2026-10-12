import pytest
from .conftest import api
from tests.agent_runtime.test_public_runtime import build
def test_runtime_exposes_bounded_verification_artifacts_with_no_cross_run_cache(configuration,clock):
    runtime,_=build(configuration,clock)
    result=runtime.run("Please add 13 and 2 for a development check.")
    assert result.status.value=="SUCCEEDED"
    refs=result.artifacts
    assert result.verification.candidate_fingerprint in refs
    candidate=refs[result.verification.candidate_fingerprint]
    assert candidate.attempt.execution_id==result.verification.execution_id
    assert api("values").fingerprint(candidate.data)==result.verification.data_fingerprint
    events=[e for e in result.trace if e.kind=="verification"]
    assert events[-1].payload["control_ref"] in refs
    second=runtime.run("Please add 17 and 2 for a development check.")
    assert result.run_id!=second.run_id and not runtime._knowledge.cache
    assert result.verification.candidate_fingerprint not in second.artifacts
def test_artifact_admission_shares_trace_budget_and_blocks_oversize(clock):
    c=api("control").RunControl.create(api("contracts").AgentRequest("development"),clock=clock)
    ref=c.capture({"observed":"value"})
    assert c.trace.artifacts()[ref]["observed"]=="value"
    with pytest.raises(api("budgets").BudgetStop):c.capture({"value":"x"*65536})
    c.terminal=True
    with pytest.raises(api("budgets").IntegrityStop):c.capture({"late":True})
def test_raw_model_record_retains_prompt_settings_and_response_identity(configuration,clock):
    from .conftest import direct_for
    text="Please add 13 and 2 for a development check."
    runner,_=direct_for(configuration,clock,{"type":"structured-answer","data":15,"evidence_ids":[]},text)
    result=runner.run(text);record=runner.model_records[-1]
    assert record["prompt"] and api("values").fingerprint(record["prompt"])==record["prompt_fingerprint"]
    assert record["response_subrequest_id"]==record["subrequest_id"]
    assert record["response_identity"].model_digest==api("profile").GENERATION_DIGEST
    assert record["request_parameters"]["temperature"]==0
    assert record["request_parameters"]["context_limit"]==8192
    assert record["request_parameters"]["thinking"] is False
def test_schedule_calls_each_runner_once_with_plain_text_and_keeps_failures(workload,clock):
    from project_asca.evaluation.physical import execute_schedule
    from project_asca.evaluation.schedule import trial_schedule
    class Runner:
        def __init__(self,prefix):self.calls=[];self.model_records=[];self.prefix=prefix
        def run(self,text):
            assert isinstance(text,str)
            self.calls.append(text)
            return api("contracts").AgentResult(self.prefix+str(len(self.calls)),self.prefix+"run"+str(len(self.calls)),
                api("values").TerminalStatus.BOUNDED_FAILURE,api("values").TerminalReason.NO_VALID_PLAN)
    unified=Runner("u");direct=Runner("d");observed=[]
    trials=execute_schedule(workload,unified,direct,trial_schedule(workload),clock=clock,on_trial=observed.append)
    assert len(trials)==len(observed)==384 and len(unified.calls)==len(direct.calls)==192
    assert len({t.result.run_id for t in trials})==384
    assert all(t.result.status.value=="BOUNDED_FAILURE" for t in trials)
    assert all(t.result.run_id!=t.case_id for t in trials)
