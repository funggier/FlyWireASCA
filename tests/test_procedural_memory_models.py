from dataclasses import FrozenInstanceError
import pytest

from flywire_asca.contracts import ObservationKind, ProcedureRef
from flywire_asca.procedural_memory import (
    ExpectedOutcome,
    OutcomeMatcherKind,
    ProcedureDefinition,
    ProcedureExecutionMode,
    ProcedureExecutionState,
    ProcedureStep,
    ProcedureStepKind,
)


def _expected(eid="exp", payload="ok"):
    return ExpectedOutcome(eid, ObservationKind.RESULT, payload)


def _proc(pid="p", explanations=()):
    return ProcedureRef(pid, pid, "1", explanations)


def test_enum_vocabularies_are_exact():
    assert tuple(x.value for x in ProcedureStepKind) == ("ACTION", "CALL_PROCEDURE")
    assert tuple(x.value for x in OutcomeMatcherKind) == ("EXACT",)
    assert tuple(x.value for x in ProcedureExecutionMode) == ("FLAT", "CHUNKED", "BLIND_CHUNKED")
    assert tuple(x.value for x in ProcedureExecutionState) == (
        "READY", "RUNNING", "COMPLETED", "INTERRUPTED", "FAILED_VALIDATION"
    )


def test_expected_outcome_is_frozen_and_validated():
    item = _expected()
    assert item.matcher is OutcomeMatcherKind.EXACT
    with pytest.raises(FrozenInstanceError):
        item.expected_payload_ref = "x"
    with pytest.raises(ValueError, match="expectation_id"):
        ExpectedOutcome("", ObservationKind.RESULT, "ok")
    with pytest.raises(ValueError, match="expected_payload_ref"):
        ExpectedOutcome("e", ObservationKind.RESULT, "")
    with pytest.raises(ValueError, match="observation_kind"):
        ExpectedOutcome("e", "result", "ok")  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="matcher"):
        ExpectedOutcome("e", ObservationKind.RESULT, "ok", "EXACT")  # type: ignore[arg-type]


def test_action_and_call_steps_are_discriminated_and_explanations_unique():
    action = ProcedureStep("s", ProcedureStepKind.ACTION, _expected(), ("m1",), action_ref="a")
    assert action.action_ref == "a"
    with pytest.raises(ValueError, match="callee_procedure_id"):
        ProcedureStep("s", ProcedureStepKind.ACTION, _expected(), action_ref="a", callee_procedure_id="p")
    with pytest.raises(ValueError, match="action_ref"):
        ProcedureStep("s", ProcedureStepKind.ACTION, _expected())
    call = ProcedureStep("s", ProcedureStepKind.CALL_PROCEDURE, _expected(), callee_procedure_id="child")
    assert call.callee_procedure_id == "child"
    with pytest.raises(ValueError, match="action_ref"):
        ProcedureStep("s", ProcedureStepKind.CALL_PROCEDURE, _expected(), action_ref="a", callee_procedure_id="child")
    with pytest.raises(ValueError, match="callee_procedure_id"):
        ProcedureStep("s", ProcedureStepKind.CALL_PROCEDURE, _expected())
    with pytest.raises(ValueError, match="explanation_memory_ids"):
        ProcedureStep("s", ProcedureStepKind.ACTION, _expected(), ("m1", "m1"), action_ref="a")


def test_procedure_definition_requires_steps_unique_ids_and_completion_outcome():
    definition = ProcedureDefinition(
        _proc(),
        (ProcedureStep("s", ProcedureStepKind.ACTION, _expected(), action_ref="a"),),
        _expected("done", "done"),
    )
    assert definition.procedure.procedure_id == "p"
    with pytest.raises(ValueError, match="steps"):
        ProcedureDefinition(_proc(), (), _expected("done", "done"))
    dup = ProcedureStep("s", ProcedureStepKind.ACTION, _expected(), action_ref="a")
    with pytest.raises(ValueError, match="step_id"):
        ProcedureDefinition(_proc(), (dup, dup), _expected("done", "done"))
