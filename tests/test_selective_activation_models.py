from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from flywire_asca.contracts import (
    ActivationBudget,
    ActivationState,
    MemoryKind,
    RetrievalState,
    WorkingSet,
    WorkingSetEntry,
    WorkingSetKind,
)
from flywire_asca.selective_activation import (
    MemoryActivationSupport,
    SelectiveMode,
    SelectiveRetrievalEvidence,
    SelectiveWorkingSetResult,
)
from flywire_asca.vector_memory import VectorMemoryHit, VectorMemoryResult


def _hit(
    memory_id: str,
    *,
    similarity: float = 0.8,
    confidence: float = 0.4,
    evidence_ids: tuple[str, ...] = (),
    entity_ids: tuple[str, ...] = (),
    context_tags: tuple[str, ...] = (),
    source_tags: tuple[str, ...] = (),
) -> VectorMemoryHit:
    return VectorMemoryHit(
        memory_id=memory_id,
        similarity=similarity,
        memory_kind=MemoryKind.SEMANTIC,
        proposition_confidence=confidence,
        evidence_ids=evidence_ids,
        entity_ids=entity_ids,
        context_tags=context_tags,
        source_tags=source_tags,
    )


def _result(
    query_id: str = "q1",
    hits: tuple[VectorMemoryHit, ...] = (),
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
        embedding_model_name="embedder",
        embedding_model_digest="digest",
        embedding_profile="profile-v1",
    )


def _budget() -> ActivationBudget:
    return ActivationBudget(
        max_memory_nodes=3,
        max_relation_hops=0,
        max_working_set_items=2,
        max_model_input_tokens=0,
        max_expansions=0,
    )


def _support(
    memory_id: str = "m1",
    *,
    cues: tuple[str, ...] = ("cue-a",),
    similarities: tuple[float, ...] = (0.8,),
    activation: float = 0.8,
) -> MemoryActivationSupport:
    return MemoryActivationSupport(
        memory_id=memory_id,
        source_cue_ids=cues,
        similarities=similarities,
        support_count=len(cues),
        max_similarity=max(similarities),
        activation=activation,
        memory_kind=MemoryKind.SEMANTIC,
        proposition_confidence=0.4,
        evidence_ids=("e2", "e1", "e1"),
        entity_ids=("person-b", "person-a", "person-a"),
        context_tags=("work", "office", "work"),
        source_tags=("note", "chat", "chat"),
    )


def test_selective_mode_vocabulary_is_exact():
    assert tuple(mode.value for mode in SelectiveMode) == (
        "SELECTIVE_CONVERGENCE",
        "SINGLE_BEST",
        "EXHAUSTIVE",
    )


def test_selective_retrieval_evidence_is_frozen_and_validates_runtime_types():
    value = SelectiveRetrievalEvidence(
        "cue-a",
        _result("q1", (_hit("m1"),)),
    )
    assert value.source_cue_id == "cue-a"
    with pytest.raises(FrozenInstanceError):
        value.source_cue_id = "changed"  # type: ignore[misc]

    with pytest.raises(ValueError, match="source_cue_id"):
        SelectiveRetrievalEvidence("", _result())
    with pytest.raises(ValueError, match="result"):
        SelectiveRetrievalEvidence("cue", object())  # type: ignore[arg-type]


def test_activation_support_canonicalizes_cue_similarity_pairs_and_metadata():
    support = MemoryActivationSupport(
        memory_id="m1",
        source_cue_ids=("cue-z", "cue-a"),
        similarities=(0.7, 0.9),
        support_count=2,
        max_similarity=0.9,
        activation=0.97,
        memory_kind=MemoryKind.SEMANTIC,
        proposition_confidence=0.25,
        evidence_ids=("e2", "e1", "e1"),
        entity_ids=("b", "a", "a"),
        context_tags=("z", "x", "x"),
        source_tags=("s2", "s1", "s1"),
    )
    assert support.source_cue_ids == ("cue-a", "cue-z")
    assert support.similarities == pytest.approx((0.9, 0.7))
    assert support.evidence_ids == ("e1", "e2")
    assert support.entity_ids == ("a", "b")
    assert support.context_tags == ("x", "z")
    assert support.source_tags == ("s1", "s2")


@pytest.mark.parametrize(
    "kwargs, match",
    [
        ({"source_cue_ids": ("cue", "cue"), "similarities": (0.8, 0.7)}, "source_cue_ids"),
        ({"source_cue_ids": ("cue-a",), "similarities": (0.0,)}, "similarities"),
        ({"source_cue_ids": ("cue-a",), "similarities": (-0.1,)}, "similarities"),
        ({"source_cue_ids": ("cue-a",), "similarities": (1.1,)}, "similarities"),
        ({"source_cue_ids": ("cue-a",), "similarities": (float("nan"),)}, "similarities"),
        ({"source_cue_ids": ("cue-a",), "similarities": (0.8,), "support_count": 2}, "support_count"),
        ({"source_cue_ids": ("cue-a",), "similarities": (0.8,), "max_similarity": 0.7}, "max_similarity"),
        ({"source_cue_ids": ("cue-a",), "similarities": (0.8,), "activation": 1.1}, "activation"),
        ({"source_cue_ids": (), "similarities": (), "support_count": 0, "max_similarity": 0.0}, "source_cue_ids"),
    ],
)
def test_activation_support_rejects_invalid_support_contract(kwargs, match):
    base = dict(
        memory_id="m1",
        source_cue_ids=("cue-a",),
        similarities=(0.8,),
        support_count=1,
        max_similarity=0.8,
        activation=0.8,
        memory_kind=MemoryKind.SEMANTIC,
        proposition_confidence=0.4,
        evidence_ids=(),
        entity_ids=(),
        context_tags=(),
        source_tags=(),
    )
    base.update(kwargs)
    with pytest.raises(ValueError, match=match):
        MemoryActivationSupport(**base)


def test_activation_support_validates_memory_kind_and_confidence():
    base = dict(
        memory_id="m1",
        source_cue_ids=("cue-a",),
        similarities=(0.8,),
        support_count=1,
        max_similarity=0.8,
        activation=0.8,
        memory_kind=MemoryKind.SEMANTIC,
        proposition_confidence=0.4,
        evidence_ids=(),
        entity_ids=(),
        context_tags=(),
        source_tags=(),
    )
    with pytest.raises(ValueError, match="memory_kind"):
        MemoryActivationSupport(**dict(base, memory_kind="semantic"))  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="proposition_confidence"):
        MemoryActivationSupport(**dict(base, proposition_confidence=1.1))


def test_selective_result_accepts_consistent_counts_and_is_frozen():
    budget = _budget()
    support = _support()
    state = ActivationState("m1", 0.8, 0, ("cue-a",))
    entry = WorkingSetEntry(
        "m1",
        WorkingSetKind.MEMORY,
        0.8,
        "single_cue_support",
    )
    working_set = WorkingSet((entry,), RetrievalState.RECALLED, budget)
    result = SelectiveWorkingSetResult(
        working_set=working_set,
        activation_states=(state,),
        supports=(support,),
        input_result_count=1,
        input_hit_count=1,
        unique_candidate_count=1,
        positive_candidate_count=1,
        activated_candidate_count=1,
        selected_count=1,
        dropped_by_memory_budget_count=0,
        dropped_by_working_set_budget_count=0,
        memory_budget_boundary_tie=False,
        working_set_boundary_tie=False,
        embedding_model_name="embedder",
        embedding_model_digest="digest",
        embedding_profile="profile-v1",
    )
    assert result.selected_count == 1
    with pytest.raises(FrozenInstanceError):
        result.selected_count = 2  # type: ignore[misc]


@pytest.mark.parametrize(
    "field, value, match",
    [
        ("input_result_count", -1, "input_result_count"),
        ("input_hit_count", 0, "input_hit_count"),
        ("unique_candidate_count", 0, "unique_candidate_count"),
        ("positive_candidate_count", 0, "positive_candidate_count"),
        ("activated_candidate_count", 0, "activated_candidate_count"),
        ("selected_count", 0, "selected_count"),
        ("dropped_by_memory_budget_count", 1, "dropped_by_memory_budget_count"),
        ("dropped_by_working_set_budget_count", 1, "dropped_by_working_set_budget_count"),
    ],
)
def test_selective_result_rejects_count_invariant_mismatches(field, value, match):
    budget = _budget()
    support = _support()
    state = ActivationState("m1", 0.8, 0, ("cue-a",))
    working_set = WorkingSet(
        (WorkingSetEntry("m1", WorkingSetKind.MEMORY, 0.8, "single_cue_support"),),
        RetrievalState.RECALLED,
        budget,
    )
    kwargs = dict(
        working_set=working_set,
        activation_states=(state,),
        supports=(support,),
        input_result_count=1,
        input_hit_count=1,
        unique_candidate_count=1,
        positive_candidate_count=1,
        activated_candidate_count=1,
        selected_count=1,
        dropped_by_memory_budget_count=0,
        dropped_by_working_set_budget_count=0,
        memory_budget_boundary_tie=False,
        working_set_boundary_tie=False,
        embedding_model_name="embedder",
        embedding_model_digest="digest",
        embedding_profile="profile-v1",
    )
    kwargs[field] = value
    with pytest.raises(ValueError, match=match):
        SelectiveWorkingSetResult(**kwargs)


def test_selective_result_validates_types_and_embedding_identity():
    budget = _budget()
    empty_ws = WorkingSet((), RetrievalState.INSUFFICIENT_EVIDENCE, budget)
    with pytest.raises(ValueError, match="activation_states"):
        SelectiveWorkingSetResult(
            empty_ws,
            (object(),),  # type: ignore[arg-type]
            (),
            0, 0, 0, 0, 1, 0, 0, 1, False, False,
            "embedder", "digest", "profile-v1",
        )
    with pytest.raises(ValueError, match="embedding_model_name"):
        SelectiveWorkingSetResult(
            empty_ws, (), (),
            0, 0, 0, 0, 0, 0, 0, 0, False, False,
            "", None, "profile-v1",
        )
    with pytest.raises(ValueError, match="embedding_profile"):
        SelectiveWorkingSetResult(
            empty_ws, (), (),
            0, 0, 0, 0, 0, 0, 0, 0, False, False,
            "embedder", None, "",
        )
