from __future__ import annotations

import pytest

from flywire_asca.contracts import Observation, ObservationKind, ProcedureRef


def test_procedure_ref_preserves_lazy_explanation_links():
    procedure = ProcedureRef(
        procedure_id="proc-close-door",
        name="close door",
        version="1",
        explanation_memory_ids=("mem-mosquito-reason",),
    )
    assert procedure.explanation_memory_ids == ("mem-mosquito-reason",)

    with pytest.raises(ValueError, match="procedure_id"):
        ProcedureRef("", "close door", "1")


def test_observation_is_an_explicit_interruptible_loop_input():
    observation = Observation(
        observation_id="obs-1",
        kind=ObservationKind.STATE,
        payload_ref="fixture://road/barrier",
        expected_match=False,
        evidence_ids=("ev-road-1",),
    )
    assert observation.expected_match is False
    assert observation.kind is ObservationKind.STATE

    with pytest.raises(ValueError, match="evidence_ids"):
        Observation(
            "obs-2",
            ObservationKind.RESULT,
            "fixture://result",
            None,
            ("ev-1", "ev-1"),
        )
