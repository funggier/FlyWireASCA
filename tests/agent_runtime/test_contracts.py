from dataclasses import FrozenInstanceError
import pytest
from .conftest import api

def test_utf8_limit_and_unknown_request_fields():
    parse = api("contracts").parse_agent_request
    assert parse({"text": "ก" * 2730 + "ab"}).text == "ก" * 2730 + "ab"
    with pytest.raises(ValueError): parse({"text": "ก" * 2731})
    for key in ("StructuralNeed", "procedure_id", "expected_answer_ids", "policy", "benchmark"):
        with pytest.raises(ValueError): parse({"text":"sum 1 and 2",key:"injected"})

@pytest.mark.parametrize("text", ["", "  ", None, 42, True, chr(0xD800)])
def test_invalid_text_fails_closed(text):
    with pytest.raises(ValueError): api("contracts").parse_agent_request({"text":text})

def test_request_is_immutable_and_preserves_original():
    c=api("contracts"); r=c.AgentRequest("  บวก 3 กับ 4  ",request_id="opaque")
    assert r.text == "  บวก 3 กับ 4  " and r.request_id == "opaque"
    with pytest.raises(FrozenInstanceError): r.text="changed"
    with pytest.raises(ValueError): c.AgentRequest("work",language_hint="fr")

def test_nested_state_is_detached_and_immutable():
    s=api("semantics"); raw={"tray":{"quantity":1},"items":[1,2]}
    snapshot=s.StateSnapshot("initial",0,raw)
    raw["tray"]["quantity"]=999
    assert snapshot.values["tray"]["quantity"]==1
    with pytest.raises(TypeError): snapshot.values["tray"]["quantity"]=2
    assert snapshot.values["items"] == (1,2)

def test_empty_predicates_do_not_pass():
    s=api("semantics")
    assert not s.VerificationRecord("g",(),(),None,True).passed

def test_contradictory_success_is_rejected():
    c=api("contracts"); s=api("semantics")
    verification=s.VerificationRecord("g",(),(),None,True)
    with pytest.raises(ValueError):
        c.AgentResult(request_id="r",run_id="run",status=c.TerminalStatus.SUCCEEDED,
                      reason=c.TerminalReason.VERIFIED,verification=verification)

def test_profile_pins_global_and_per_attempt_limits(profile):
    assert (profile.model_calls,profile.prompt_tokens,profile.output_tokens)==(4,32768,2048)
    assert (profile.retrieval_queries,profile.vectors_scored)==(6,1536)
    assert (profile.context_items,profile.context_bytes)==(24,16384)
    assert (profile.relation_visits,profile.relation_edges)==(24,96)
    assert (profile.actions_per_attempt,profile.actions,profile.call_depth)==(32,96,8)
    assert (profile.transitions,profile.trace_events,profile.trace_bytes)==(64,256,262144)
    assert (profile.state_bytes,profile.deadline_seconds,profile.model_call_seconds)==(65536,180,120)

def test_oversized_state_and_invalid_goal_code():
    s=api("semantics")
    with pytest.raises(ValueError): s.StateSnapshot("s",0,{"large":"x"*65536})
    with pytest.raises(ValueError): s.GoalPredicate("p","eval",{"code":"open('x')"})

def test_plan_preflight_action_and_depth_limits():
    p=api("plans"); s=api("semantics")
    steps=tuple(p.PlanStep(str(i),"sum","1",{}) for i in range(33))
    with pytest.raises(ValueError): p.ActionProposal("p",0,steps,{},None)
    proposal=p.ActionProposal("p",0,(),{},"root")
    with pytest.raises(ValueError): p.ValidatedPlan(proposal,"g","cap",1,9)
