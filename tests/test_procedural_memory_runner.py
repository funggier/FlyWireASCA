from __future__ import annotations

import pytest

from flywire_asca.contracts import ObservationKind, ProcedureRef
from flywire_asca.procedural_memory import (
    DeterministicProcedureSimulator,
    ExpectedOutcome,
    ProcedureDefinition,
    ProcedureExecutionMode,
    ProcedureExecutionState,
    ProcedureLibrary,
    ProcedureStep,
    ProcedureStepKind,
    SimulatedActionDefinition,
    SimulatedCompletionProbe,
    SimulatedFailureOverride,
    SimulatedWorldState,
    flatten_procedure,
    run_procedure,
)


def exp(eid, payload, kind=ObservationKind.RESULT):
    return ExpectedOutcome(eid, kind, payload)


def action_step(step_id, action_ref, payload, explanations=()):
    return ProcedureStep(
        step_id,
        ProcedureStepKind.ACTION,
        exp(f"e-{step_id}", payload),
        explanations,
        action_ref=action_ref,
    )


def call_step(step_id, callee, payload, explanations=()):
    return ProcedureStep(
        step_id,
        ProcedureStepKind.CALL_PROCEDURE,
        exp(f"e-{step_id}", payload, ObservationKind.STATE),
        explanations,
        callee_procedure_id=callee,
    )


def fixture():
    grand=ProcedureDefinition(
        ProcedureRef("grand","grand","1",("mem-grand",)),
        (action_step("g-set","act-grand","grand-action",("mem-step-grand",)),),
        exp("grand-done","grand-ready",ObservationKind.STATE),
    )
    child=ProcedureDefinition(
        ProcedureRef("child","child","1",("mem-child",)),
        (
            action_step("c-set","act-child","child-action"),
            call_step("c-grand","grand","grand-ready"),
        ),
        exp("child-done","child-ready",ObservationKind.STATE),
    )
    root=ProcedureDefinition(
        ProcedureRef("root","root","1",("mem-root",)),
        (
            action_step("r-first","act-root-first","root-first"),
            call_step("r-child","child","child-ready",("mem-call-child",)),
            action_step("r-last","act-root-last","root-last"),
        ),
        exp("root-done","root-ready",ObservationKind.STATE),
    )
    lib=ProcedureLibrary((root,child,grand))
    actions=(
        SimulatedActionDefinition("act-root-first",(("root-first","yes"),),ObservationKind.RESULT,"root-first"),
        SimulatedActionDefinition("act-child",(("child","child-ready"),),ObservationKind.RESULT,"child-action"),
        SimulatedActionDefinition("act-grand",(("grand","grand-ready"),),ObservationKind.RESULT,"grand-action"),
        SimulatedActionDefinition("act-root-last",(("root-last","yes"),),ObservationKind.RESULT,"root-last"),
    )
    probes=(
        SimulatedCompletionProbe("child","child",ObservationKind.STATE),
        SimulatedCompletionProbe("grand","grand",ObservationKind.STATE),
    )
    return lib,actions,probes


def simulator(*, failure=()):
    _,actions,probes=fixture()
    return DeterministicProcedureSimulator(
        actions,
        probes,
        SimulatedWorldState((("child","cold"),("grand","cold"))),
        failure,
    )


def primitive_actions(result):
    return tuple(
        item.action_ref
        for item in result.step_results
        if item.primitive_action_executed
    )


def test_flat_matches_flattened_sequence_and_has_no_call_events():
    lib,_,_=fixture()
    sim=simulator()
    result=run_procedure(
        lib,root_procedure_id="root",mode=ProcedureExecutionMode.FLAT,
        executor=sim,execution_id="exec-flat",
    )
    flat=flatten_procedure(lib,"root")
    assert result.state is ProcedureExecutionState.COMPLETED
    assert result.interruption is None
    assert primitive_actions(result)==tuple(x.action_ref for x in flat)
    assert all(x.kind is ProcedureStepKind.ACTION for x in result.step_results)
    assert result.metrics.primitive_action_count==4
    assert result.metrics.procedure_call_count==0
    assert result.metrics.root_visible_dispatch_count==4
    assert result.metrics.total_step_event_count==4
    assert result.metrics.expected_outcome_check_count==4
    assert result.metrics.suppressed_internal_check_count==0
    assert result.metrics.max_runtime_call_depth==3
    assert result.final_world_state_ref==sim.world_state_ref()


def test_chunked_preserves_primitive_sequence_but_reduces_root_visible_dispatch():
    lib,_,_=fixture()
    flat_sim=simulator()
    flat=run_procedure(lib,root_procedure_id="root",mode=ProcedureExecutionMode.FLAT,executor=flat_sim,execution_id="flat")
    chunk_sim=simulator()
    chunk=run_procedure(lib,root_procedure_id="root",mode=ProcedureExecutionMode.CHUNKED,executor=chunk_sim,execution_id="chunk")

    assert chunk.state is ProcedureExecutionState.COMPLETED
    assert primitive_actions(chunk)==primitive_actions(flat)
    assert chunk_sim.world_state()==flat_sim.world_state()
    assert chunk.metrics.primitive_action_count==4
    assert chunk.metrics.procedure_call_count==2
    assert chunk.metrics.root_visible_dispatch_count==3
    assert chunk.metrics.total_step_event_count==6
    assert chunk.metrics.expected_outcome_check_count==6
    assert chunk.metrics.suppressed_internal_check_count==0
    assert chunk.metrics.max_runtime_call_depth==3
    assert [x.kind for x in chunk.step_results].count(ProcedureStepKind.CALL_PROCEDURE)==2


def test_chunked_checked_child_failure_interrupts_exact_primitive_and_no_parent_call_result():
    lib,_,_=fixture()
    fail=SimulatedFailureOverride("root/child/grand::g-set",ObservationKind.ERROR,"boom",True)
    sim=simulator(failure=(fail,))
    result=run_procedure(
        lib,root_procedure_id="root",mode=ProcedureExecutionMode.CHUNKED,
        executor=sim,execution_id="fail-chunk",
    )
    assert result.state is ProcedureExecutionState.INTERRUPTED
    assert result.interruption is not None
    assert result.interruption.failing_procedure_id=="grand"
    assert result.interruption.failing_step_id=="g-set"
    assert result.interruption.call_path==("root","child","grand")
    assert result.interruption.observed.kind is ObservationKind.ERROR
    assert result.interruption.explanation_memory_ids==(
        "mem-root","mem-child","mem-grand","mem-step-grand"
    )
    assert result.interruption.completed_primitive_step_paths==(
        "root::r-first","root/child::c-set","root/child/grand::g-set"
    )
    assert sim.executed_primitive_step_paths()==result.interruption.completed_primitive_step_paths
    assert "root::r-last" not in sim.executed_primitive_step_paths()
    # The unfinished child/grand calls must not synthesize CALL results.
    assert all(
        not (x.kind is ProcedureStepKind.CALL_PROCEDURE and x.step_id in {"c-grand","r-child"})
        for x in result.step_results
    )


def test_flat_failure_localizes_same_originating_primitive():
    lib,_,_=fixture()
    fail=SimulatedFailureOverride("root/child/grand::g-set",ObservationKind.ERROR,"boom",True)
    sim=simulator(failure=(fail,))
    result=run_procedure(
        lib,root_procedure_id="root",mode=ProcedureExecutionMode.FLAT,
        executor=sim,execution_id="fail-flat",
    )
    assert result.state is ProcedureExecutionState.INTERRUPTED
    assert result.interruption.failing_procedure_id=="grand"
    assert result.interruption.failing_step_id=="g-set"
    assert result.interruption.call_path==("root","child","grand")
    assert sim.executed_primitive_step_paths()==(
        "root::r-first","root/child::c-set","root/child/grand::g-set"
    )


def test_blind_chunked_suppresses_internal_check_and_localizes_at_call_boundary():
    lib,_,_=fixture()
    fail=SimulatedFailureOverride("root/child::c-set",ObservationKind.ERROR,"boom",True)
    sim=simulator(failure=(fail,))
    result=run_procedure(
        lib,root_procedure_id="root",mode=ProcedureExecutionMode.BLIND_CHUNKED,
        executor=sim,execution_id="fail-blind",
    )
    assert result.state is ProcedureExecutionState.INTERRUPTED
    internal=next(x for x in result.step_results if x.step_id=="c-set")
    assert internal.verification is None
    assert result.metrics.suppressed_internal_check_count>=1
    assert result.interruption.failing_procedure_id=="root"
    assert result.interruption.failing_step_id=="r-child"
    assert result.interruption.call_path==("root",)
    assert result.interruption.observed.kind is ObservationKind.STATE
    assert result.interruption.observed.payload_ref=="cold"
    assert result.interruption.explanation_memory_ids==("mem-root","mem-call-child")
    assert "root::r-last" not in sim.executed_primitive_step_paths()


def test_blind_success_final_state_matches_other_modes():
    lib,_,_=fixture()
    results=[]
    states=[]
    for mode in ProcedureExecutionMode:
        sim=simulator()
        results.append(run_procedure(lib,root_procedure_id="root",mode=mode,executor=sim,execution_id=f"e-{mode.value}"))
        states.append(sim.world_state())
    assert all(x.state is ProcedureExecutionState.COMPLETED for x in results)
    assert states[0]==states[1]==states[2]
    assert results[2].metrics.suppressed_internal_check_count==2


def test_runner_rejects_blank_execution_unknown_root_and_invalid_executor_before_actions():
    lib,_,_=fixture()
    sim=simulator()
    with pytest.raises(ValueError,match="execution_id"):
        run_procedure(lib,root_procedure_id="root",mode=ProcedureExecutionMode.CHUNKED,executor=sim,execution_id="")
    with pytest.raises(ValueError,match="unknown procedure_id"):
        run_procedure(lib,root_procedure_id="missing",mode=ProcedureExecutionMode.CHUNKED,executor=sim,execution_id="e")
    with pytest.raises(ValueError,match="executor"):
        run_procedure(lib,root_procedure_id="root",mode=ProcedureExecutionMode.CHUNKED,executor=object(),execution_id="e")


def test_runner_is_deterministic_with_fresh_equivalent_simulators():
    lib,_,_=fixture()
    a=run_procedure(lib,root_procedure_id="root",mode=ProcedureExecutionMode.CHUNKED,executor=simulator(),execution_id="same")
    b=run_procedure(lib,root_procedure_id="root",mode=ProcedureExecutionMode.CHUNKED,executor=simulator(),execution_id="same")
    assert a==b
