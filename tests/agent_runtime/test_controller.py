import pytest
from .conftest import api

def test_illegal_transition_and_late_dispatch_fail_closed(clock):
    c=api("control").RunControl.create(api("contracts").AgentRequest("development"),clock=clock)
    machine=api("controller").StateMachine(c)
    with pytest.raises(api("budgets").IntegrityStop):machine.move(api("values").Phase.EXECUTING)
    machine.finish()
    with pytest.raises(api("budgets").IntegrityStop):machine.move(api("values").Phase.INTERPRETING)

def test_model_assist_remembers_its_requesting_phase(clock):
    c=api("control").RunControl.create(api("contracts").AgentRequest("development"),clock=clock)
    machine=api("controller").StateMachine(c)
    c.phase_hook=machine.move
    machine.move(api("values").Phase.INTERPRETING)
    with c.model_assist(api("values").ModelPurpose.INTENT,"prompt"):
        assert c.phase is api("values").Phase.MODEL_ASSIST
    assert c.phase is api("values").Phase.INTERPRETING

def test_pinned_model_port_binds_owning_run_and_shared_transport_gate(clock):
    from .test_model_adapter import FakeTransport
    p=api("adapters.model");c=api("control").RunControl.create(api("contracts").AgentRequest("setup"),clock=clock)
    fake=FakeTransport();identity=p.probe_physical_identity("http://localhost:11434",transport=fake)
    base=p.PinnedModelPort("http://localhost:11434",c,identity,transport=fake)
    actual=api("control").RunControl.create(api("contracts").AgentRequest("actual"),clock=clock)
    bound=base.for_control(actual)
    assert bound.control is actual and base.control is c


def test_model_scope_records_role_requesting_state_and_prompt_before_dispatch(clock):
    c=api("control").RunControl.create(api("contracts").AgentRequest("development"),clock=clock)
    machine=api("controller").StateMachine(c);c.phase_hook=machine.move
    machine.move(api("values").Phase.INTERPRETING)
    with c.model_assist(api("values").ModelPurpose.INTENT,"dev-prompt"):
        scopes=[e for e in c.trace.freeze() if e.kind=="model_scope"]
        assert scopes and scopes[-1].payload["purpose"]=="INTENT"
        assert scopes[-1].payload["requesting_phase"]=="INTERPRETING"
        assert scopes[-1].payload["prompt_fingerprint"]=="dev-prompt"

def test_transition_limit_retains_legal_terminal_unwind(clock):
    c=api("control").RunControl.create(api("contracts").AgentRequest("development"),clock=clock)
    machine=api("controller").StateMachine(c);v=api("values").Phase
    machine.move(v.INTERPRETING);machine.move(v.RESOLVING)
    with pytest.raises(api("budgets").BudgetStop):
        while True:
            for phase in (v.EXECUTING,v.OBSERVING,v.VERIFYING,v.RECOVERING,v.RESOLVING):
                machine.move(phase)
    prior=c.phase;machine.finish()
    assert c.terminal and c.ledger.snapshot().counters["transitions"]<=64
    event=c.trace.freeze()[-1]
    assert event.payload["from"]==prior.value
    chain=tuple(event.payload["unwind"])
    assert chain[-1]=="TERMINAL"
    for target in chain:
        assert v(target) in api("controller").NEXT[prior]
        prior=v(target)


def test_profile_requires_one_transition_for_terminal_publication():
    with pytest.raises(ValueError,match="terminal transition"):
        api("profile").RuntimeProfile(transitions=0)
