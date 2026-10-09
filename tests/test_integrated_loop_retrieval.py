from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from flywire_asca.contracts import MemoryKind, MemoryRecord
from flywire_asca.embedding import (
    EmbeddingDescriptor,
    EmbeddingInputKind,
    EmbeddingResponse,
    normalize_embedding_values,
)
from flywire_asca.integrated_loop import (
    IntegratedRetrievalContext,
    IntegratedRetrievalCue,
    IntegratedRetrievalCueTier,
    evaluate_integrated_scope,
    run_initial_integrated_expansion,
)
from flywire_asca.selective_activation import (
    SelectiveWorkingSetResult,
    bounded_union_activation,
)
from flywire_asca.uncertainty_expansion import (
    ExpansionPolicy,
    ExpansionTerminationReason,
    build_a007_primary_profile,
)
from flywire_asca.vector_memory import (
    ExactVectorMemoryIndex,
    VectorMemoryDocument,
    VectorMemoryQuery,
)


class FakeEmbeddingAdapter:
    def __init__(self, vectors: dict[str, tuple[float, float]]) -> None:
        self.vectors = vectors
        self.requests = []

    def inspect(self) -> EmbeddingDescriptor:
        return EmbeddingDescriptor(
            backend_name="fake",
            backend_version="1",
            model_name="a009-fake-embedder",
            model_digest="a009-fake-digest",
            architecture="fixture",
            parameter_count=0,
            parameter_size=None,
            quantization=None,
            context_length=1024,
            embedding_dimension=2,
            capabilities=("embedding",),
        )

    def embed(self, request):
        self.requests.append(request)
        vectors = tuple(
            normalize_embedding_values(self.vectors[text], expected_dimension=2)
            for text in request.texts
        )
        return EmbeddingResponse(
            request_id=request.request_id,
            model_name="a009-fake-embedder",
            model_digest="a009-fake-digest",
            vectors=vectors,
            input_count=len(vectors),
            prompt_tokens=0,
            total_duration_ns=0,
            load_duration_ns=0,
        )


class RecordingIndex(ExactVectorMemoryIndex):
    def __init__(self, *args, **kwargs):
        self.queries: list[VectorMemoryQuery] = []
        super().__init__(*args, **kwargs)

    def search(self, query: VectorMemoryQuery):
        self.queries.append(query)
        return super().search(query)


def _document(memory_id: str, text: str) -> VectorMemoryDocument:
    return VectorMemoryDocument(
        MemoryRecord(
            memory_id,
            MemoryKind.SEMANTIC,
            f"content:{memory_id}",
            1.0,
        ),
        text,
    )


def _context(
    *,
    threshold: float = 0.8,
    cue_vectors: dict[str, tuple[float, float]] | None = None,
) -> tuple[IntegratedRetrievalContext, RecordingIndex]:
    cue_vectors = cue_vectors or {
        "cue-0": (0.8, 0.6),
        "cue-1": (0.9, 0.4358898943540673),
        "cue-2": (0.6, 0.8),
    }
    adapter = FakeEmbeddingAdapter(
        {
            "memory-alpha": (1.0, 0.0),
            "memory-beta": (0.0, 1.0),
            **cue_vectors,
        }
    )
    index = RecordingIndex(
        (
            _document("mem-alpha", "memory-alpha"),
            _document("mem-beta", "memory-beta"),
        ),
        adapter,
        embedding_profile="a009-test",
    )
    context = IntegratedRetrievalContext(
        index=index,
        cue_tiers=(
            IntegratedRetrievalCueTier(
                0,
                (IntegratedRetrievalCue("source-0", "query-0", "cue-0"),),
            ),
            IntegratedRetrievalCueTier(
                1,
                (IntegratedRetrievalCue("source-1", "query-1", "cue-1"),),
            ),
            IntegratedRetrievalCueTier(
                2,
                (IntegratedRetrievalCue("source-2", "query-2", "cue-2"),),
            ),
        ),
        minimum_similarity=threshold,
    )
    return context, index


def test_retrieval_cue_and_tier_contracts_are_frozen_and_fail_closed():
    cue = IntegratedRetrievalCue("source", "query", "text")
    tier = IntegratedRetrievalCueTier(0, (cue,))
    assert tier.cues == (cue,)
    with pytest.raises(FrozenInstanceError):
        cue.query_text = "other"  # type: ignore[misc]
    with pytest.raises(ValueError, match="source_cue_id"):
        IntegratedRetrievalCue("", "query", "text")
    with pytest.raises(ValueError, match="query_id"):
        IntegratedRetrievalCue("source", "", "text")
    with pytest.raises(ValueError, match="query_text"):
        IntegratedRetrievalCue("source", "query", "")
    with pytest.raises(ValueError, match="tier_index"):
        IntegratedRetrievalCueTier(-1, (cue,))
    with pytest.raises(ValueError, match="cues"):
        IntegratedRetrievalCueTier(0, ())


def test_context_requires_contiguous_tiers_unique_ids_and_real_index():
    context, index = _context()
    assert isinstance(context.index, ExactVectorMemoryIndex)
    assert tuple(tier.tier_index for tier in context.cue_tiers) == (0, 1, 2)

    cue0 = IntegratedRetrievalCue("source", "query", "cue-0")
    cue1_same_source = IntegratedRetrievalCue("source", "query-1", "cue-1")
    cue1_same_query = IntegratedRetrievalCue("source-1", "query", "cue-1")
    with pytest.raises(ValueError, match="contiguous"):
        IntegratedRetrievalContext(
            index,
            (
                IntegratedRetrievalCueTier(0, (cue0,)),
                IntegratedRetrievalCueTier(2, (IntegratedRetrievalCue("s2", "q2", "cue-2"),)),
            ),
            0.8,
        )
    with pytest.raises(ValueError, match="source_cue_id"):
        IntegratedRetrievalContext(
            index,
            (
                IntegratedRetrievalCueTier(0, (cue0,)),
                IntegratedRetrievalCueTier(1, (cue1_same_source,)),
            ),
            0.8,
        )
    with pytest.raises(ValueError, match="query_id"):
        IntegratedRetrievalContext(
            index,
            (
                IntegratedRetrievalCueTier(0, (cue0,)),
                IntegratedRetrievalCueTier(1, (cue1_same_query,)),
            ),
            0.8,
        )
    with pytest.raises(ValueError, match="index"):
        IntegratedRetrievalContext(object(), (IntegratedRetrievalCueTier(0, (cue0,)),), 0.8)  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="minimum_similarity"):
        IntegratedRetrievalContext(index, (IntegratedRetrievalCueTier(0, (cue0,)),), 2.0)


@pytest.mark.parametrize(
    ("round_index", "expected_queries", "expected_top_k"),
    ((0, 1, 12), (1, 2, 24), (2, 3, 32)),
)
def test_scope_evaluator_uses_enabled_tiers_scope_top_k_and_fixed_threshold(
    round_index: int,
    expected_queries: int,
    expected_top_k: int,
):
    context, index = _context(threshold=0.8)
    scope = build_a007_primary_profile().scopes[round_index]
    evaluation = evaluate_integrated_scope(context, scope)

    assert isinstance(evaluation.working_set_result, SelectiveWorkingSetResult)
    assert len(evaluation.retrieval_results) == expected_queries
    new_queries = index.queries[-expected_queries:]
    assert tuple(query.top_k for query in new_queries) == (expected_top_k,) * expected_queries
    assert tuple(query.minimum_similarity for query in new_queries) == (0.8,) * expected_queries
    assert tuple(result.query_id for result in evaluation.retrieval_results) == tuple(
        f"query-{index}" for index in range(expected_queries)
    )
    assert evaluation.working_set_result.working_set.entries[0].ref_id == "mem-alpha"
    alpha = next(
        support
        for support in evaluation.working_set_result.supports
        if support.memory_id == "mem-alpha"
    )
    assert alpha.activation == alpha.max_similarity
    if alpha.support_count > 1:
        assert alpha.activation != bounded_union_activation(alpha.similarities)


def test_signal_driven_stops_without_speculatively_evaluating_later_scope():
    context, index = _context()
    result = run_initial_integrated_expansion(
        context,
        profile=build_a007_primary_profile(),
        policy=ExpansionPolicy.SIGNAL_DRIVEN,
    )
    assert tuple(item.scope.round_index for item in result.evaluations) == (0,)
    assert result.run.termination_reason is ExpansionTerminationReason.CONTROLLER_STOP
    assert tuple(query.query_id for query in index.queries) == ("query-0",)


def test_signal_driven_expands_only_until_structural_state_recovers():
    context, index = _context(
        threshold=0.8,
        cue_vectors={
            "cue-0": (0.0, -1.0),
            "cue-1": (1.0, 0.0),
            "cue-2": (1.0, 0.0),
        },
    )
    result = run_initial_integrated_expansion(
        context,
        profile=build_a007_primary_profile(),
        policy=ExpansionPolicy.SIGNAL_DRIVEN,
    )
    assert tuple(item.scope.round_index for item in result.evaluations) == (0, 1)
    assert result.run.termination_reason is ExpansionTerminationReason.CONTROLLER_STOP
    assert tuple(query.query_id for query in index.queries) == (
        "query-0",
        "query-0",
        "query-1",
    )


def test_always_expand_evaluates_exactly_all_frozen_scopes():
    context, _ = _context()
    result = run_initial_integrated_expansion(
        context,
        profile=build_a007_primary_profile(),
        policy=ExpansionPolicy.ALWAYS_EXPAND,
    )
    assert tuple(item.scope.round_index for item in result.evaluations) == (0, 1, 2)
    assert result.run.termination_reason is ExpansionTerminationReason.POLICY_MAX_SCOPE


def test_scope_evaluator_rejects_request_for_more_tiers_than_context_has():
    context, _ = _context()
    bad_scope = build_a007_primary_profile().scopes[2]
    short = IntegratedRetrievalContext(
        context.index,
        context.cue_tiers[:2],
        context.minimum_similarity,
    )
    with pytest.raises(ValueError, match="enabled_cue_tier_count"):
        evaluate_integrated_scope(short, bad_scope)
