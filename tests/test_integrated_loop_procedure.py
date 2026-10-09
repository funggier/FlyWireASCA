from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from flywire_asca.contracts import ObservationKind, ProcedureRef
from flywire_asca.integrated_loop import (
    ActionMemoryRequirement,
    ContextBoundProcedureExecutorFactory,
)
from flywire_asca.procedural_memory import (
    ExpectedOutcome,
    ProcedureDefinition,
    ProcedureExecutionMode,
    ProcedureExecutionState,
    ProcedureLibrary,
    ProcedureStep,
    ProcedureStepKind,
    SimulatedActionDefinition,
    SimulatedWorldState,
    run_procedure,
)


def _expected(expectation_id: str, payload: str) -> ExpectedOutcome:
    return ExpectedOutcome(expectation_id, ObservationKind.RESULT, payload)


def _library() -> ProcedureLibrary:
    return ProcedureLibrary(
        (
            ProcedureDefinition(
                ProcedureRef("root", "root", "1"),
                (
                    ProcedureStep(
                        "prepare",
                        ProcedureStepKind.ACTION,
                        _expected("prepare-ok", "prepared"),
                        action_ref="prepare-action",
                    ),
                    ProcedureStep(
                        "finish",
                        ProcedureStepKind.ACTION,
                        _expected("finish-ok", "done"),
                        action_ref="finish-action",
                    ),
                ),
                _expected("root-done", "done"),
            ),
        )
    )


def _factory() -> ContextBoundProcedureExecutorFactory:
    return ContextBoundProcedureExecutorFactory(
        action_definitions=(
            SimulatedActionDefinition(
                "prepare-action",
                (("phase", "prepared"),),
                ObservationKind.RESULT,
                "prepared",
            ),
            SimulatedActionDefinition(
                "finish-action",
                (("done", "yes"),),
                ObservationKind.RESULT,
                "done",
            ),
        ),
        completion_probes=(),
        initial_state=SimulatedWorldState((("phase", "initial"),)),
        requirements=(
            ActionMemoryRequirement(
                "finish-action",
                ("mem-finish",),
                ObservationKind.RESULT,
                "missing-memory",
            ),
        ),
    )


def test_action_memory_requirement_is_frozen_and_fail_closed():
    requirement = ActionMemoryRequirement(
        "action",
        ("mem-a", "mem-b"),
        ObservationKind.RESULT,
        "missing",
    )
    assert requirement.required_memory_ids == ("mem-a", "mem-b")
    with pytest.raises(FrozenInstanceError):
        requirement.action_ref = "other"  # type: ignore[misc]
    with pytest.raises(ValueError, match="action_ref"):
        ActionMemoryRequirement("", ("mem",), ObservationKind.RESULT, "missing")
    with pytest.raises(ValueError, match="required_memory_ids"):
        ActionMemoryRequirement("action", (), ObservationKind.RESULT, "missing")
    with pytest.raises(ValueError, match="required_memory_ids"):
        ActionMemoryRequirement(
            "action",
            ("mem", "mem"),
            ObservationKind.RESULT,
            "missing",
        )
    with pytest.raises(ValueError, match="failure_observation_kind"):
        ActionMemoryRequirement("action", ("mem",), "RESULT", "missing")  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="failure_payload_ref"):
        ActionMemoryRequirement("action", ("mem",), ObservationKind.RESULT, "")


def test_factory_rejects_duplicate_or_unknown_requirement_action_refs():
    action = SimulatedActionDefinition(
        "action",
        (),
        ObservationKind.RESULT,
        "ok",
    )
    req = ActionMemoryRequirement(
        "action",
        ("mem",),
        ObservationKind.RESULT,
        "missing",
    )
    with pytest.raises(ValueError, match="requirement.*action_ref"):
        ContextBoundProcedureExecutorFactory(
            (action,),
            (),
            SimulatedWorldState(()),
            (req, req),
        )
    with pytest.raises(ValueError, match="unknown.*action_ref"):
        ContextBoundProcedureExecutorFactory(
            (action,),
            (),
            SimulatedWorldState(()),
            (
                ActionMemoryRequirement(
                    "other",
                    ("mem",),
                    ObservationKind.RESULT,
                    "missing",
                ),
            ),
        )


def test_missing_memory_returns_deterministic_mismatch_without_state_write():
    factory = _factory()
    executor = factory.create(available_memory_ids=(), execution_id="exec-0")

    result = run_procedure(
        _library(),
        root_procedure_id="root",
        mode=ProcedureExecutionMode.CHUNKED,
        executor=executor,
        execution_id="exec-0",
    )

    assert result.state is ProcedureExecutionState.INTERRUPTED
    assert result.interruption is not None
    assert result.interruption.failing_step_id == "finish"
    assert result.interruption.observed.kind is ObservationKind.RESULT
    assert result.interruption.observed.payload_ref == "missing-memory"
    assert executor.world_state().get("phase") == "prepared"
    assert executor.world_state().get("done") is None
    assert executor.executed_primitive_step_paths() == ("root::prepare",)
    assert result.interruption.completed_primitive_step_paths == ("root::prepare",)


def test_missing_memory_observation_id_is_stable_for_same_execution_and_path():
    factory = _factory()
    first = factory.create(available_memory_ids=(), execution_id="same")
    second = factory.create(available_memory_ids=(), execution_id="same")

    first_result = run_procedure(
        _library(),
        root_procedure_id="root",
        mode=ProcedureExecutionMode.CHUNKED,
        executor=first,
        execution_id="same",
    )
    second_result = run_procedure(
        _library(),
        root_procedure_id="root",
        mode=ProcedureExecutionMode.CHUNKED,
        executor=second,
        execution_id="same",
    )

    assert first_result.interruption is not None
    assert second_result.interruption is not None
    assert (
        first_result.interruption.observed.observation_id
        == second_result.interruption.observed.observation_id
    )
    assert first_result == second_result


def test_available_memory_delegates_normal_action_and_completes():
    factory = _factory()
    executor = factory.create(
        available_memory_ids=("mem-finish",),
        execution_id="exec-ok",
    )
    result = run_procedure(
        _library(),
        root_procedure_id="root",
        mode=ProcedureExecutionMode.CHUNKED,
        executor=executor,
        execution_id="exec-ok",
    )
    assert result.state is ProcedureExecutionState.COMPLETED
    assert executor.world_state().get("phase") == "prepared"
    assert executor.world_state().get("done") == "yes"


def test_each_factory_create_returns_fresh_executor_from_same_initial_snapshot():
    factory = _factory()
    failed = factory.create(available_memory_ids=(), execution_id="exec-0")
    assert failed.initial_world_state_ref == factory.initial_world_state_ref
    first = run_procedure(
        _library(),
        root_procedure_id="root",
        mode=ProcedureExecutionMode.CHUNKED,
        executor=failed,
        execution_id="exec-0",
    )
    assert first.state is ProcedureExecutionState.INTERRUPTED
    assert failed.world_state().get("phase") == "prepared"

    replay = factory.create(
        available_memory_ids=("mem-finish",),
        execution_id="exec-1",
    )
    assert replay is not failed
    assert replay.initial_world_state_ref == factory.initial_world_state_ref
    assert replay.world_state().get("phase") == "initial"
    assert replay.world_state().get("done") is None

    second = run_procedure(
        _library(),
        root_procedure_id="root",
        mode=ProcedureExecutionMode.CHUNKED,
        executor=replay,
        execution_id="exec-1",
    )
    assert second.state is ProcedureExecutionState.COMPLETED
    assert replay.world_state().get("done") == "yes"


def test_factory_create_validates_execution_id_and_available_memory_ids():
    factory = _factory()
    with pytest.raises(ValueError, match="execution_id"):
        factory.create(available_memory_ids=(), execution_id="")
    with pytest.raises(ValueError, match="available_memory_ids"):
        factory.create(
            available_memory_ids=("mem", "mem"),
            execution_id="exec",
        )
