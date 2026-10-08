from __future__ import annotations

import pytest

from flywire_asca.contracts import Cue, CueKind, RetrievalState
from flywire_asca.familiarity import (
    ExactFamiliarityIndex,
    ExhaustiveFamiliarityBaseline,
    FamiliarityTrace,
)


def _cue(cue_id: str, kind: CueKind, value: str) -> Cue:
    return Cue(cue_id, kind, value, 1.0)


def _observable(result):
    return (
        result.cue_id,
        result.retrieval_state,
        result.familiarity_score,
        result.candidate_region_ids,
        result.matched_trace_ids,
        result.cost.matched_trace_count,
        result.cost.total_trace_count,
    )


def test_known_and_unknown_cues_match_exhaustive_semantics():
    traces = (
        FamiliarityTrace("trace-alice", CueKind.ENTITY, "Alice", "person-alice"),
        FamiliarityTrace("trace-office", CueKind.CONTEXT, "Office", "context-office"),
    )
    exact = ExactFamiliarityIndex(traces)
    exhaustive = ExhaustiveFamiliarityBaseline(traces)

    known = _cue("cue-known", CueKind.ENTITY, " alice ")
    exact_known = exact.assess(known)
    exhaustive_known = exhaustive.assess(known)
    assert exact_known.retrieval_state is RetrievalState.FAMILIAR
    assert exact_known.familiarity_score == 1.0
    assert exact_known.candidate_region_ids == ("person-alice",)
    assert exact_known.matched_trace_ids == ("trace-alice",)
    assert _observable(exact_known) == _observable(exhaustive_known)

    unknown = _cue("cue-unknown", CueKind.ENTITY, "Bob")
    exact_unknown = exact.assess(unknown)
    exhaustive_unknown = exhaustive.assess(unknown)
    assert exact_unknown.retrieval_state is RetrievalState.UNFAMILIAR
    assert exact_unknown.familiarity_score == 0.0
    assert exact_unknown.candidate_region_ids == ()
    assert exact_unknown.matched_trace_ids == ()
    assert _observable(exact_unknown) == _observable(exhaustive_unknown)


def test_same_surface_under_different_cue_kind_does_not_collide():
    traces = (
        FamiliarityTrace("trace-a", CueKind.ENTITY, "A", "person-a"),
    )
    exact = ExactFamiliarityIndex(traces)
    assert exact.assess(_cue("entity-a", CueKind.ENTITY, "A")).retrieval_state is RetrievalState.FAMILIAR
    assert exact.assess(_cue("text-a", CueKind.TEXT, "A")).retrieval_state is RetrievalState.UNFAMILIAR


def test_same_name_ambiguity_preserves_all_regions_and_has_no_identity_winner():
    traces = (
        FamiliarityTrace("trace-primary", CueKind.ENTITY, "A", "person-a-primary"),
        FamiliarityTrace("trace-neighbor", CueKind.ENTITY, "A", "person-a-neighbor"),
    )
    result = ExactFamiliarityIndex(traces).assess(_cue("cue-a", CueKind.ENTITY, "A"))
    assert result.candidate_region_ids == ("person-a-neighbor", "person-a-primary")
    assert result.matched_trace_ids == ("trace-neighbor", "trace-primary")
    assert not hasattr(result, "identity_id")
    assert not hasattr(result, "winner_id")
    assert not hasattr(result, "same_person")


def test_multiple_traces_to_same_region_deduplicate_region_only():
    traces = (
        FamiliarityTrace("trace-1", CueKind.ENTITY, "Alice", "person-alice"),
        FamiliarityTrace("trace-2", CueKind.ENTITY, "ALICE", "person-alice"),
    )
    result = ExactFamiliarityIndex(traces).assess(_cue("cue", CueKind.ENTITY, "alice"))
    assert result.candidate_region_ids == ("person-alice",)
    assert result.matched_trace_ids == ("trace-1", "trace-2")
    assert result.cost.matched_trace_count == 2


def test_duplicate_trace_ids_fail_closed():
    traces = (
        FamiliarityTrace("trace-1", CueKind.ENTITY, "Alice", "person-a"),
        FamiliarityTrace("trace-1", CueKind.ENTITY, "Bob", "person-b"),
    )
    with pytest.raises(ValueError, match="duplicate trace_id"):
        ExactFamiliarityIndex(traces)
    with pytest.raises(ValueError, match="duplicate trace_id"):
        ExhaustiveFamiliarityBaseline(traces)


def test_generator_input_is_materialized_once_and_costs_are_explicit():
    def generate():
        yield FamiliarityTrace("trace-1", CueKind.ENTITY, "Alice", "person-a")
        yield FamiliarityTrace("trace-2", CueKind.ENTITY, "Bob", "person-b")

    exact = ExactFamiliarityIndex(generate())
    exhaustive = ExhaustiveFamiliarityBaseline(generate())

    exact_result = exact.assess(_cue("cue", CueKind.ENTITY, "Alice"))
    exhaustive_result = exhaustive.assess(_cue("cue", CueKind.ENTITY, "Alice"))
    assert exact_result.cost.index_probes == 1
    assert exhaustive_result.cost.index_probes == 2
    assert exact_result.cost.total_trace_count == 2
    assert exhaustive_result.cost.total_trace_count == 2
    assert exact_result.cost.matched_trace_count == exhaustive_result.cost.matched_trace_count == 1


def test_result_ordering_is_independent_of_trace_construction_order():
    traces_a = (
        FamiliarityTrace("trace-z", CueKind.ENTITY, "A", "region-z"),
        FamiliarityTrace("trace-a", CueKind.ENTITY, "a", "region-a"),
        FamiliarityTrace("trace-m", CueKind.ENTITY, "Ａ", "region-m"),
    )
    traces_b = tuple(reversed(traces_a))
    cue = _cue("cue", CueKind.ENTITY, "A")
    left = ExactFamiliarityIndex(traces_a).assess(cue)
    right = ExactFamiliarityIndex(traces_b).assess(cue)
    assert left.candidate_region_ids == right.candidate_region_ids == (
        "region-a",
        "region-m",
        "region-z",
    )
    assert left.matched_trace_ids == right.matched_trace_ids == (
        "trace-a",
        "trace-m",
        "trace-z",
    )
