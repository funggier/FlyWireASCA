"""Shared direct runner must reject extra claims and late terminal success."""
import pytest
from .conftest import direct_for,api

def test_direct_structured_answer_rejects_unverified_fields(configuration,clock):
    text="Add 13 and 2."
    runner,_=direct_for(configuration,clock,{"type":"structured-answer",
        "data":{"value":15,"extra_claim":"Nira office is South"},"evidence_ids":[]},text)
    result=runner.run(text)
    assert result.status.value!="SUCCEEDED"
    assert result.metrics.model_invocations==1

@pytest.mark.parametrize("interruption",["cancel","deadline"])
def test_direct_terminal_arbitration_rechecks_rendering(interruption,configuration,clock,monkeypatch):
    import project_asca.evaluation.direct as module
    text="Add 13 and 2.";cancellation=api("control").Cancellation()
    runner,_=direct_for(configuration,clock,{"type":"structured-answer","data":{"value":15},"evidence_ids":[]},text)
    render=module.render_result_data
    def interrupted(*args,**kwargs):
        answer=render(*args,**kwargs)
        if interruption=="cancel":cancellation.cancel()
        else:clock.value=1000
        return answer
    monkeypatch.setattr(module,"render_result_data",interrupted)
    result=runner.run(text,cancellation=cancellation)
    assert result.status.value=="CANCELLED" if interruption=="cancel" else result.reason.value=="DEADLINE_EXCEEDED"
    assert len([e for e in result.trace if e.kind=="terminal"])==1
