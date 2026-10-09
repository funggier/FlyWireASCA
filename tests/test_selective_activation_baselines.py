from __future__ import annotations

import pytest

from flywire_asca.contracts import ActivationBudget, RetrievalState
from flywire_asca.selective_activation import (
    SelectiveRetrievalEvidence,
    select_exhaustive,
    select_single_best,
    select_working_set,
)
from flywire_asca.vector_memory import VectorMemoryHit, VectorMemoryResult
from flywire_asca.contracts import MemoryKind


def _budget(memory=4, working=3):
    return ActivationBudget(memory, 0, working, 0, 0)


def _hit(memory_id, similarity, *, confidence=0.5):
    return VectorMemoryHit(
        memory_id=memory_id,
        similarity=similarity,
        memory_kind=MemoryKind.SEMANTIC,
        proposition_confidence=confidence,
        evidence_ids=("e",),
        entity_ids=("entity",),
        context_tags=("ctx",),
        source_tags=("src",),
    )


def _ev(cue, query, *hits):
    count=len(hits)
    return SelectiveRetrievalEvidence(
        cue,
        VectorMemoryResult(
            query_id=query,
            hits=tuple(hits),
            stored_count=max(count, 1),
            metadata_eligible_count=count,
            scored_vector_count=count,
            above_threshold_count=count,
            returned_count=count,
            embedding_model_name="embedder",
            embedding_model_digest="digest",
            embedding_profile="profile-v1",
        ),
    )


def test_single_best_uses_max_similarity_without_convergence_or_support_count_boost():
    evidence=(
        _ev("cue-a","q-a",_hit("multi",0.6),_hit("one-off",0.7)),
        _ev("cue-b","q-b",_hit("multi",0.6)),
    )
    selective=select_working_set(evidence,budget=_budget(memory=2,working=2))
    single=select_single_best(evidence,budget=_budget(memory=2,working=2))

    assert [s.memory_id for s in selective.supports] == ["multi","one-off"]
    assert selective.supports[0].activation == pytest.approx(0.84)

    assert [s.memory_id for s in single.supports] == ["one-off","multi"]
    by_id={s.memory_id:s for s in single.supports}
    assert by_id["multi"].activation == pytest.approx(0.6)
    assert by_id["multi"].support_count == 2
    assert by_id["one-off"].activation == pytest.approx(0.7)


def test_single_best_tie_ignores_support_count_and_reports_boundary_tie():
    evidence=(
        _ev("cue-a","q-a",_hit("m-a",0.8),_hit("m-b",0.8)),
        _ev("cue-b","q-b",_hit("m-a",0.5)),
    )
    result=select_single_best(evidence,budget=_budget(memory=2,working=1))
    assert [s.memory_id for s in result.supports] == ["m-a","m-b"]
    assert result.supports[0].support_count == 2
    assert result.supports[1].support_count == 1
    assert result.working_set_boundary_tie is True
    assert result.working_set.retrieval_state is RetrievalState.PARTIAL_RECALL


def test_single_best_reuses_selector_validation_path():
    duplicate=(
        _ev("cue","q1",_hit("m1",0.8)),
        _ev("cue","q2",_hit("m2",0.7)),
    )
    with pytest.raises(ValueError,match="source_cue_id"):
        select_single_best(duplicate,budget=_budget())


def test_exhaustive_keeps_every_positive_candidate_and_expands_budget_exactly():
    evidence=(
        _ev("cue-a","q-a",_hit("m1",0.8),_hit("m2",0.0),_hit("m3",-0.2)),
        _ev("cue-b","q-b",_hit("m4",0.7),_hit("m1",0.6)),
    )
    result=select_exhaustive(evidence)

    assert [s.memory_id for s in result.supports] == ["m1","m4"]
    assert [s.node_id for s in result.activation_states] == ["m1","m4"]
    assert [e.ref_id for e in result.working_set.entries] == ["m1","m4"]
    assert result.working_set.budget == ActivationBudget(2,0,2,0,0)
    assert result.dropped_by_memory_budget_count == 0
    assert result.dropped_by_working_set_budget_count == 0
    assert result.working_set.retrieval_state is RetrievalState.RECALLED


def test_exhaustive_zero_positive_uses_declared_minimal_budget():
    result=select_exhaustive(
        (_ev("cue","q",_hit("m0",0.0),_hit("mn",-0.1)),)
    )
    assert result.supports == ()
    assert result.activation_states == ()
    assert result.working_set.entries == ()
    assert result.working_set.budget == ActivationBudget(1,0,1,0,0)
    assert result.working_set.retrieval_state is RetrievalState.INSUFFICIENT_EVIDENCE


def test_all_modes_preserve_support_provenance_and_embedding_identity():
    evidence=(
        _ev("cue-b","q-b",_hit("m1",0.6)),
        _ev("cue-a","q-a",_hit("m1",0.7)),
    )
    selective=select_working_set(evidence,budget=_budget(memory=1,working=1))
    single=select_single_best(evidence,budget=_budget(memory=1,working=1))
    exhaustive=select_exhaustive(evidence)

    supports=[result.supports[0] for result in (selective,single,exhaustive)]
    for support in supports:
        assert support.source_cue_ids == ("cue-a","cue-b")
        assert support.similarities == pytest.approx((0.7,0.6))
        assert support.support_count == 2
        assert support.max_similarity == pytest.approx(0.7)
        assert support.memory_kind is MemoryKind.SEMANTIC
        assert support.proposition_confidence == pytest.approx(0.5)
        assert support.evidence_ids == ("e",)
        assert support.entity_ids == ("entity",)
        assert support.context_tags == ("ctx",)
        assert support.source_tags == ("src",)

    assert selective.supports[0].activation == pytest.approx(0.88)
    assert single.supports[0].activation == pytest.approx(0.7)
    assert exhaustive.supports[0].activation == pytest.approx(0.88)

    for result in (selective,single,exhaustive):
        assert result.embedding_model_name == "embedder"
        assert result.embedding_model_digest == "digest"
        assert result.embedding_profile == "profile-v1"
