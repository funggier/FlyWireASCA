from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from flywire_asca.contracts import CueKind, RetrievalState
from flywire_asca.familiarity import FamiliarityCost, FamiliarityResult, FamiliarityTrace


def test_trace_is_immutable_and_validates_ids_surface_and_evidence():
    trace = FamiliarityTrace(
        "trace-1",
        CueKind.ENTITY,
        " Alice ",
        "person-alice",
        ("ev-1",),
    )
    assert trace.surface_value == " Alice "
    with pytest.raises(FrozenInstanceError):
        trace.region_id = "other"  # type: ignore[misc]

    with pytest.raises(ValueError, match="trace_id"):
        FamiliarityTrace("", CueKind.ENTITY, "Alice", "person-alice")
    with pytest.raises(ValueError, match="region_id"):
        FamiliarityTrace("trace-1", CueKind.ENTITY, "Alice", "")
    with pytest.raises(ValueError, match="surface_value"):
        FamiliarityTrace("trace-1", CueKind.ENTITY, "   ", "region")
    with pytest.raises(ValueError, match="evidence_ids"):
        FamiliarityTrace(
            "trace-1",
            CueKind.ENTITY,
            "Alice",
            "region",
            ("ev-1", "ev-1"),
        )


def test_cost_is_immutable_and_enforces_nonnegative_logical_counts():
    cost = FamiliarityCost(1, 2, 10)
    assert (cost.index_probes, cost.matched_trace_count, cost.total_trace_count) == (1, 2, 10)
    with pytest.raises(FrozenInstanceError):
        cost.index_probes = 2  # type: ignore[misc]
    with pytest.raises(ValueError, match="index_probes"):
        FamiliarityCost(-1, 0, 0)
    with pytest.raises(ValueError, match="matched_trace_count"):
        FamiliarityCost(1, -1, 1)
    with pytest.raises(ValueError, match="total_trace_count"):
        FamiliarityCost(1, 2, 1)


def test_result_contract_allows_only_binary_exact_familiarity_states():
    familiar = FamiliarityResult(
        "cue-1",
        RetrievalState.FAMILIAR,
        1.0,
        ("region-a",),
        ("trace-a",),
        FamiliarityCost(1, 1, 1),
    )
    assert familiar.familiarity_score == 1.0
    with pytest.raises(FrozenInstanceError):
        familiar.familiarity_score = 0.0  # type: ignore[misc]

    unfamiliar = FamiliarityResult(
        "cue-2",
        RetrievalState.UNFAMILIAR,
        0.0,
        (),
        (),
        FamiliarityCost(1, 0, 1),
    )
    assert unfamiliar.candidate_region_ids == ()

    with pytest.raises(ValueError, match="retrieval_state"):
        FamiliarityResult(
            "cue-3",
            RetrievalState.RECALLED,
            1.0,
            ("region-a",),
            ("trace-a",),
            FamiliarityCost(1, 1, 1),
        )
    with pytest.raises(ValueError, match="familiarity_score"):
        FamiliarityResult(
            "cue-4",
            RetrievalState.FAMILIAR,
            0.5,
            ("region-a",),
            ("trace-a",),
            FamiliarityCost(1, 1, 1),
        )
    with pytest.raises(ValueError, match="FAMILIAR"):
        FamiliarityResult(
            "cue-5",
            RetrievalState.FAMILIAR,
            1.0,
            (),
            (),
            FamiliarityCost(1, 0, 1),
        )
    with pytest.raises(ValueError, match="UNFAMILIAR"):
        FamiliarityResult(
            "cue-6",
            RetrievalState.UNFAMILIAR,
            0.0,
            ("region-a",),
            ("trace-a",),
            FamiliarityCost(1, 1, 1),
        )


def test_result_requires_canonical_sorted_unique_ids_and_cost_consistency():
    with pytest.raises(ValueError, match="candidate_region_ids"):
        FamiliarityResult(
            "cue-1",
            RetrievalState.FAMILIAR,
            1.0,
            ("region-b", "region-a"),
            ("trace-a",),
            FamiliarityCost(1, 1, 1),
        )
    with pytest.raises(ValueError, match="matched_trace_ids"):
        FamiliarityResult(
            "cue-1",
            RetrievalState.FAMILIAR,
            1.0,
            ("region-a",),
            ("trace-b", "trace-a"),
            FamiliarityCost(1, 2, 2),
        )
    with pytest.raises(ValueError, match="matched_trace_count"):
        FamiliarityResult(
            "cue-1",
            RetrievalState.FAMILIAR,
            1.0,
            ("region-a",),
            ("trace-a",),
            FamiliarityCost(1, 0, 1),
        )
