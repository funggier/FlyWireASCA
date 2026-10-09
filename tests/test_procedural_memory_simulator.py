import pytest

from flywire_asca.contracts import ObservationKind
from flywire_asca.procedural_memory import (
    DeterministicProcedureSimulator,
    SimulatedActionDefinition,
    SimulatedCompletionProbe,
    SimulatedFailureOverride,
    SimulatedWorldState,
)


def action(ref="a", writes=(("x","1"),), kind=ObservationKind.RESULT, payload="ok"):
    return SimulatedActionDefinition(ref,writes,kind,payload)


def test_world_state_is_canonical_and_validated():
    state=SimulatedWorldState((("z","9"),("a","1")))
    assert state.values == (("a","1"),("z","9"))
    assert state.get("a")=="1"
    assert state.get("missing") is None
    with pytest.raises(ValueError,match="unique"):
        SimulatedWorldState((("x","1"),("x","2")))
    with pytest.raises(ValueError,match="key"):
        SimulatedWorldState((("","1"),))


def test_simulator_rejects_duplicate_registry_entries_and_ambiguous_writes():
    with pytest.raises(ValueError,match="action_ref"):
        DeterministicProcedureSimulator((action("a"),action("a")),(),SimulatedWorldState(()))
    p=SimulatedCompletionProbe("p","x",ObservationKind.RESULT)
    with pytest.raises(ValueError,match="procedure_id"):
        DeterministicProcedureSimulator((action(),),(p,p),SimulatedWorldState(()))
    with pytest.raises(ValueError,match="write"):
        SimulatedActionDefinition("a",(("x","1"),("x","2")),ObservationKind.RESULT,"ok")


def test_execute_action_mutates_state_logs_path_and_is_deterministic():
    kwargs=dict(
        action_definitions=(action("set-x",(("x","ready"),),payload="set"),),
        completion_probes=(SimulatedCompletionProbe("child","x",ObservationKind.STATE),),
        initial_state=SimulatedWorldState((("base","yes"),)),
    )
    first=DeterministicProcedureSimulator(**kwargs)
    obs=first.execute_action(action_ref="set-x",execution_id="exec",call_path=("root","child"),step_id="s1")
    assert obs.kind is ObservationKind.RESULT
    assert obs.payload_ref=="set"
    assert first.world_state().values == (("base","yes"),("x","ready"))
    assert first.executed_primitive_step_paths()==("root/child::s1",)
    completion=first.observe_procedure_completion(procedure_id="child",execution_id="exec",call_path=("root","child"))
    assert completion.kind is ObservationKind.STATE
    assert completion.payload_ref=="ready"

    second=DeterministicProcedureSimulator(**kwargs)
    obs2=second.execute_action(action_ref="set-x",execution_id="exec",call_path=("root","child"),step_id="s1")
    completion2=second.observe_procedure_completion(procedure_id="child",execution_id="exec",call_path=("root","child"))
    assert obs2==obs
    assert completion2==completion
    assert second.world_state()==first.world_state()
    assert second.world_state_ref()==first.world_state_ref()


def test_unknown_action_and_missing_probe_fail_before_mutating_state():
    sim=DeterministicProcedureSimulator((action("known"),),(),SimulatedWorldState((("x","0"),)))
    before=sim.world_state()
    with pytest.raises(ValueError,match="action_ref"):
        sim.execute_action(action_ref="missing",execution_id="e",call_path=("root",),step_id="s")
    assert sim.world_state()==before
    with pytest.raises(ValueError,match="completion probe"):
        sim.observe_procedure_completion(procedure_id="child",execution_id="e",call_path=("root","child"))


def test_completion_probe_fails_when_state_key_missing():
    sim=DeterministicProcedureSimulator(
        (action(),),
        (SimulatedCompletionProbe("child","missing",ObservationKind.STATE),),
        SimulatedWorldState(()),
    )
    with pytest.raises(ValueError,match="state key"):
        sim.observe_procedure_completion(procedure_id="child",execution_id="e",call_path=("root","child"))


def test_failure_override_can_suppress_or_apply_writes():
    base=dict(
        action_definitions=(action("set",(("x","ready"),),payload="normal"),),
        completion_probes=(),
        initial_state=SimulatedWorldState((("x","old"),)),
    )
    suppressed=DeterministicProcedureSimulator(
        **base,
        failure_overrides=(SimulatedFailureOverride("root/child::s",ObservationKind.ERROR,"boom",True),),
    )
    obs=suppressed.execute_action(action_ref="set",execution_id="e",call_path=("root","child"),step_id="s")
    assert obs.kind is ObservationKind.ERROR and obs.payload_ref=="boom"
    assert suppressed.world_state().get("x")=="old"

    applied=DeterministicProcedureSimulator(
        **base,
        failure_overrides=(SimulatedFailureOverride("root/child::s",ObservationKind.ERROR,"boom",False),),
    )
    obs2=applied.execute_action(action_ref="set",execution_id="e",call_path=("root","child"),step_id="s")
    assert obs2.kind is ObservationKind.ERROR
    assert applied.world_state().get("x")=="ready"


def test_world_state_ref_is_stable_sha256_hex():
    a=DeterministicProcedureSimulator((action(),),(),SimulatedWorldState((("b","2"),("a","1"))))
    b=DeterministicProcedureSimulator((action(),),(),SimulatedWorldState((("a","1"),("b","2"))))
    assert a.world_state_ref()==b.world_state_ref()
    assert len(a.world_state_ref())==64
    int(a.world_state_ref(),16)
