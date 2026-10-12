import pytest
from dataclasses import replace
from .conftest import api
from .test_verification import probe,make_candidate,verdict,state_data

def verified(configuration,registry,schemas,clock):
    goal,context,c,attempt=probe("pack",{"entity":"O1"},configuration,registry,schemas,clock)
    candidate=make_candidate(goal,context,attempt,state_data(goal,attempt))
    checked=verdict(goal,candidate,c,configuration)
    assert checked.passed
    return goal,c,candidate,checked

def test_render_is_deterministic_and_binds_exact_verified_data(configuration,registry,schemas,clock):
    goal,c,candidate,checked=verified(configuration,registry,schemas,clock)
    render=api("rendering").render_result_data
    assert render(candidate,checked,language="en")==render(candidate,checked,language="en")
    assert "packed" in render(candidate,checked,language="th")
    with pytest.raises(ValueError):render(replace(candidate,data="unverified claim"),checked,language="en")

def test_non_success_render_does_not_claim_completion(configuration,registry,schemas,clock):
    goal,c,candidate,checked=verified(configuration,registry,schemas,clock)
    failed=replace(checked,integrity=False)
    text=api("rendering").render_result_data(candidate,failed,language="en")
    assert "unverified" in text.casefold() or "not verified" in text.casefold()
    assert "succeeded" not in text.casefold()

def test_success_publication_binds_run_goal_predicates_and_data(configuration,registry,schemas,clock):
    goal,c,candidate,checked=verified(configuration,registry,schemas,clock)
    contract=api("contracts");values=api("values")
    kwargs=dict(request_id=c.request.request_id,run_id=c.run_id,status=values.TerminalStatus.SUCCEEDED,
      reason=values.TerminalReason.VERIFIED,interpreted_goal=goal,data=candidate.data,verification=checked,
      final_state_ref=candidate.attempt.final_state.snapshot_id)
    assert contract.AgentResult(**kwargs).status is values.TerminalStatus.SUCCEEDED
    for wrong in ({"run_id":"another"},{"data":"swapped"},{"verification":replace(checked,predicates=checked.predicates[:1])}):
        with pytest.raises(ValueError):contract.AgentResult(**{**kwargs,**wrong})


def test_renderer_cannot_accept_another_run_record(configuration,registry,schemas,clock):
    goal,c,candidate,checked=verified(configuration,registry,schemas,clock)
    with pytest.raises(ValueError):
        api("rendering").render_result_data(candidate,replace(checked,run_id="another"),language="en")
