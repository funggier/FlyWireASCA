from __future__ import annotations

import pytest

from flywire_asca.contracts import (
    ActivationBudget,
    MemoryKind,
    RetrievalState,
    WorkingSetKind,
)
from flywire_asca.selective_activation import (
    SelectiveRetrievalEvidence,
    bounded_union_activation,
    select_working_set,
    validate_a006_budget,
)
from flywire_asca.vector_memory import VectorMemoryHit, VectorMemoryResult


def _budget(
    *,
    memory: int = 4,
    working: int = 3,
    hops: int = 0,
    expansions: int = 0,
    model_tokens: int = 0,
) -> ActivationBudget:
    return ActivationBudget(
        max_memory_nodes=memory,
        max_relation_hops=hops,
        max_working_set_items=working,
        max_model_input_tokens=model_tokens,
        max_expansions=expansions,
    )


def _hit(
    memory_id: str,
    similarity: float,
    *,
    confidence: float = 0.5,
    kind: MemoryKind = MemoryKind.SEMANTIC,
    evidence_ids: tuple[str, ...] = (),
    entity_ids: tuple[str, ...] = (),
    context_tags: tuple[str, ...] = (),
    source_tags: tuple[str, ...] = (),
) -> VectorMemoryHit:
    return VectorMemoryHit(
        memory_id=memory_id,
        similarity=similarity,
        memory_kind=kind,
        proposition_confidence=confidence,
        evidence_ids=evidence_ids,
        entity_ids=entity_ids,
        context_tags=context_tags,
        source_tags=source_tags,
    )


def _result(
    query_id: str,
    hits: tuple[VectorMemoryHit, ...],
    *,
    model: str = "embedder",
    digest: str | None = "digest",
    profile: str = "profile-v1",
) -> VectorMemoryResult:
    count = len(hits)
    return VectorMemoryResult(
        query_id=query_id,
        hits=hits,
        stored_count=max(count, 1),
        metadata_eligible_count=count,
        scored_vector_count=count,
        above_threshold_count=count,
        returned_count=count,
        embedding_model_name=model,
        embedding_model_digest=digest,
        embedding_profile=profile,
    )


def _evidence(cue: str, query: str, *hits: VectorMemoryHit, **kwargs):
    return SelectiveRetrievalEvidence(
        cue,
        _result(query, tuple(hits), **kwargs),
    )


def test_validate_a006_budget_requires_no_graph_no_model_context_profile():
    validate_a006_budget(_budget(memory=4, working=2))

    with pytest.raises(ValueError, match="max_working_set_items"):
        validate_a006_budget(_budget(memory=2, working=3))
    with pytest.raises(ValueError, match="max_relation_hops"):
        validate_a006_budget(_budget(hops=1))
    with pytest.raises(ValueError, match="max_expansions"):
        validate_a006_budget(_budget(expansions=1))
    with pytest.raises(ValueError, match="max_model_input_tokens"):
        validate_a006_budget(_budget(model_tokens=1))


def test_bounded_union_activation_is_deterministic_bounded_and_positive_only():
    assert bounded_union_activation((0.8,)) == pytest.approx(0.8)
    assert bounded_union_activation((0.8, 0.8)) == pytest.approx(0.96)
    assert bounded_union_activation((0.2, 0.5, 1.0)) == pytest.approx(1.0)

    with pytest.raises(ValueError, match="similarities"):
        bounded_union_activation(())
    with pytest.raises(ValueError, match="positive"):
        bounded_union_activation((0.0,))
    with pytest.raises(ValueError, match="positive"):
        bounded_union_activation((-0.1,))
    with pytest.raises(ValueError, match="within"):
        bounded_union_activation((1.1,))
    with pytest.raises(ValueError, match="finite"):
        bounded_union_activation((float("nan"),))


def test_selector_materializes_evidence_once_and_rejects_duplicate_cue_or_query_ids():
    items = [
        _evidence("cue-a", "q-a", _hit("m1", 0.8)),
        _evidence("cue-b", "q-b", _hit("m2", 0.7)),
    ]
    consumed = {"count": 0}

    def generate():
        for item in items:
            consumed["count"] += 1
            yield item

    result = select_working_set(generate(), budget=_budget())
    assert consumed["count"] == 2
    assert result.input_result_count == 2

    with pytest.raises(ValueError, match="source_cue_id"):
        select_working_set(
            (
                _evidence("cue-a", "q-a", _hit("m1", 0.8)),
                _evidence("cue-a", "q-b", _hit("m2", 0.7)),
            ),
            budget=_budget(),
        )

    with pytest.raises(ValueError, match="query_id"):
        select_working_set(
            (
                _evidence("cue-a", "q-same", _hit("m1", 0.8)),
                _evidence("cue-b", "q-same", _hit("m2", 0.7)),
            ),
            budget=_budget(),
        )


def test_selector_rejects_duplicate_memory_in_one_result_and_embedding_identity_mismatch():
    duplicate = _evidence(
        "cue-a",
        "q-a",
        _hit("m1", 0.8),
        _hit("m1", 0.7),
    )
    with pytest.raises(ValueError, match="duplicate memory_id"):
        select_working_set((duplicate,), budget=_budget())

    with pytest.raises(ValueError, match="embedding_model_name"):
        select_working_set(
            (
                _evidence("cue-a", "q-a", _hit("m1", 0.8), model="embed-a"),
                _evidence("cue-b", "q-b", _hit("m2", 0.7), model="embed-b"),
            ),
            budget=_budget(),
        )
    with pytest.raises(ValueError, match="embedding_model_digest"):
        select_working_set(
            (
                _evidence("cue-a", "q-a", _hit("m1", 0.8), digest="a"),
                _evidence("cue-b", "q-b", _hit("m2", 0.7), digest="b"),
            ),
            budget=_budget(),
        )
    with pytest.raises(ValueError, match="embedding_profile"):
        select_working_set(
            (
                _evidence("cue-a", "q-a", _hit("m1", 0.8), profile="a"),
                _evidence("cue-b", "q-b", _hit("m2", 0.7), profile="b"),
            ),
            budget=_budget(),
        )


@pytest.mark.parametrize(
    "field, second",
    [
        ("memory_kind", _hit("m1", 0.7, kind=MemoryKind.EPISODIC)),
        ("proposition_confidence", _hit("m1", 0.7, confidence=0.9)),
        ("evidence_ids", _hit("m1", 0.7, evidence_ids=("e2",))),
        ("entity_ids", _hit("m1", 0.7, entity_ids=("p2",))),
        ("context_tags", _hit("m1", 0.7, context_tags=("c2",))),
        ("source_tags", _hit("m1", 0.7, source_tags=("s2",))),
    ],
)
def test_selector_rejects_conflicting_immutable_metadata_for_same_memory(field, second):
    first_kwargs = {
        "confidence": 0.5,
        "evidence_ids": ("e1",) if field == "evidence_ids" else (),
        "entity_ids": ("p1",) if field == "entity_ids" else (),
        "context_tags": ("c1",) if field == "context_tags" else (),
        "source_tags": ("s1",) if field == "source_tags" else (),
    }
    first = _hit("m1", 0.8, **first_kwargs)
    with pytest.raises(ValueError, match=field):
        select_working_set(
            (
                _evidence("cue-a", "q-a", first),
                _evidence("cue-b", "q-b", second),
            ),
            budget=_budget(),
        )


def test_selector_filters_nonpositive_support_and_uses_multi_query_bounded_union():
    result = select_working_set(
        (
            _evidence(
                "cue-z",
                "q-z",
                _hit("target", 0.6, confidence=0.1),
                _hit("zero", 0.0),
                _hit("negative", -0.4),
            ),
            _evidence(
                "cue-a",
                "q-a",
                _hit("target", 0.6, confidence=0.1),
                _hit("one-off", 0.8, confidence=0.99),
            ),
        ),
        budget=_budget(memory=4, working=4),
    )
    assert [support.memory_id for support in result.supports] == [
        "target",
        "one-off",
    ]
    target = result.supports[0]
    assert target.source_cue_ids == ("cue-a", "cue-z")
    assert target.similarities == pytest.approx((0.6, 0.6))
    assert target.support_count == 2
    assert target.max_similarity == pytest.approx(0.6)
    assert target.activation == pytest.approx(0.84)
    assert target.proposition_confidence == pytest.approx(0.1)
    assert result.unique_candidate_count == 4
    assert result.positive_candidate_count == 2
    assert [entry.ref_id for entry in result.working_set.entries] == [
        "target",
        "one-off",
    ]
    assert result.working_set.entries[0].reason == "multi_cue_convergence"
    assert result.working_set.entries[1].reason == "single_cue_support"
    assert all(state.hop == 0 for state in result.activation_states)


def test_selector_ranking_ignores_confidence_and_uses_memory_id_as_final_tiebreak():
    result = select_working_set(
        (
            _evidence(
                "cue-a",
                "q-a",
                _hit("m-b", 0.8, confidence=0.99),
                _hit("m-a", 0.8, confidence=0.01),
            ),
        ),
        budget=_budget(memory=2, working=2),
    )
    assert [support.memory_id for support in result.supports] == ["m-a", "m-b"]
    assert [support.proposition_confidence for support in result.supports] == [
        0.01,
        0.99,
    ]


def test_selector_applies_strict_memory_budget_and_reports_boundary_tie():
    result = select_working_set(
        (
            _evidence(
                "cue",
                "q",
                _hit("m-a", 0.8),
                _hit("m-b", 0.8),
                _hit("m-c", 0.7),
            ),
        ),
        budget=_budget(memory=1, working=1),
    )
    assert [support.memory_id for support in result.supports] == [
        "m-a",
        "m-b",
        "m-c",
    ]
    assert [state.node_id for state in result.activation_states] == ["m-a"]
    assert [entry.ref_id for entry in result.working_set.entries] == ["m-a"]
    assert result.dropped_by_memory_budget_count == 2
    assert result.dropped_by_working_set_budget_count == 0
    assert result.memory_budget_boundary_tie is True
    assert result.working_set_boundary_tie is False
    assert result.working_set.retrieval_state is RetrievalState.PARTIAL_RECALL


def test_selector_applies_strict_working_set_budget_and_reports_boundary_tie():
    result = select_working_set(
        (
            _evidence(
                "cue",
                "q",
                _hit("m-a", 0.8),
                _hit("m-b", 0.8),
                _hit("m-c", 0.7),
            ),
        ),
        budget=_budget(memory=3, working=1),
    )
    assert [state.node_id for state in result.activation_states] == [
        "m-a",
        "m-b",
        "m-c",
    ]
    assert [entry.ref_id for entry in result.working_set.entries] == ["m-a"]
    assert result.dropped_by_memory_budget_count == 0
    assert result.dropped_by_working_set_budget_count == 2
    assert result.memory_budget_boundary_tie is False
    assert result.working_set_boundary_tie is True
    assert result.working_set.retrieval_state is RetrievalState.PARTIAL_RECALL


def test_selector_retrieval_state_is_insufficient_or_recalled_when_no_budget_drop():
    no_positive = select_working_set(
        (_evidence("cue", "q", _hit("m0", 0.0), _hit("mn", -0.2)),),
        budget=_budget(),
    )
    assert no_positive.supports == ()
    assert no_positive.activation_states == ()
    assert no_positive.working_set.entries == ()
    assert no_positive.working_set.retrieval_state is RetrievalState.INSUFFICIENT_EVIDENCE
    assert no_positive.unique_candidate_count == 2
    assert no_positive.positive_candidate_count == 0

    recalled = select_working_set(
        (_evidence("cue", "q", _hit("m1", 0.8), _hit("m2", 0.7)),),
        budget=_budget(memory=2, working=2),
    )
    assert recalled.working_set.retrieval_state is RetrievalState.RECALLED
    assert recalled.dropped_by_memory_budget_count == 0
    assert recalled.dropped_by_working_set_budget_count == 0
    assert all(
        entry.kind is WorkingSetKind.MEMORY
        for entry in recalled.working_set.entries
    )

def test_selector_rejects_empty_evidence_without_embedding_identity():
    with pytest.raises(ValueError, match="evidence"):
        select_working_set((), budget=_budget())
