import pytest

from flywire_asca.contracts import Observation, ObservationKind, ProcedureRef
from flywire_asca.procedural_memory import (
    ExpectedOutcome,
    ProcedureDefinition,
    ProcedureLibrary,
    ProcedureStep,
    ProcedureStepKind,
    canonical_explanation_memory_ids,
    verify_outcome,
)


def exp(eid="e", payload="ok", kind=ObservationKind.RESULT):
    return ExpectedOutcome(eid, kind, payload)


def test_exact_verifier_checks_kind_and_payload_and_ignores_expected_match_oracle():
    expected=exp()
    observed=Observation("o1", ObservationKind.RESULT, "ok", expected_match=False)
    snapshot=observed
    result=verify_outcome(expected, observed)
    assert result.expectation_id=="e"
    assert result.observation_id=="o1"
    assert result.matched is True
    assert observed==snapshot

    assert verify_outcome(expected, Observation("o2", ObservationKind.ERROR, "ok", expected_match=True)).matched is False
    assert verify_outcome(expected, Observation("o3", ObservationKind.RESULT, "wrong", expected_match=True)).matched is False


def test_provenance_union_follows_call_path_then_failing_step_unique_first():
    grand=ProcedureDefinition(
        ProcedureRef("grand","grand","1",("g","shared")),
        (ProcedureStep("gs",ProcedureStepKind.ACTION,exp(),("step","shared"),action_ref="ga"),),
        exp("gd","grand-done"),
    )
    child=ProcedureDefinition(
        ProcedureRef("child","child","1",("c","shared")),
        (ProcedureStep("cg",ProcedureStepKind.CALL_PROCEDURE,exp("callg","grand-done"),callee_procedure_id="grand"),),
        exp("cd","child-done"),
    )
    root=ProcedureDefinition(
        ProcedureRef("root","root","1",("r","shared")),
        (ProcedureStep("rc",ProcedureStepKind.CALL_PROCEDURE,exp("callc","child-done"),callee_procedure_id="child"),),
        exp("rd","root-done"),
    )
    lib=ProcedureLibrary((root,child,grand))
    assert canonical_explanation_memory_ids(lib,("root","child","grand"),grand.steps[0]) == (
        "r","shared","c","g","step"
    )
