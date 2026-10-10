from __future__ import annotations

from flywire_asca.contracts import AssociationEdge, MemoryKind, MemoryRecord, RelationType
from flywire_asca.embedding import (
    EmbeddingDescriptor,
    EmbeddingInputKind,
    EmbeddingResponse,
    normalize_embedding_values,
)
from flywire_asca.relational_activation import (
    HybridRecallRequest,
    RelationalActivationPolicy,
    StructuralNeed,
    TargetFreeRelationIndex,
    run_hybrid_recall,
)
from flywire_asca.vector_memory import (
    ExactVectorMemoryIndex,
    VectorMemoryDocument,
    VectorMemoryQuery,
)


class _Adapter:
    def inspect(self):
        return EmbeddingDescriptor(
            backend_name="fixture",
            backend_version="1",
            model_name="fixture",
            model_digest="fixture-v1",
            architecture="fixture",
            parameter_count=0,
            parameter_size=None,
            quantization=None,
            context_length=16,
            embedding_dimension=2,
            capabilities=("embedding",),
        )

    def embed(self, request):
        table = {
            "seed text": (1.0, 0.0),
            "target text": (0.0, 1.0),
            "query": (1.0, 0.0),
        }
        vectors = tuple(
            normalize_embedding_values(table[text], expected_dimension=2)
            for text in request.texts
        )
        return EmbeddingResponse(
            request_id=request.request_id,
            model_name="fixture",
            model_digest="fixture-v1",
            vectors=vectors,
            input_count=len(vectors),
            prompt_tokens=0,
            total_duration_ns=0,
            load_duration_ns=0,
        )


def _runtime():
    seed = MemoryRecord("seed", MemoryKind.SEMANTIC, "content:seed", 1.0)
    target = MemoryRecord("target", MemoryKind.SEMANTIC, "content:target", 1.0)
    vector = ExactVectorMemoryIndex(
        (
            VectorMemoryDocument(seed, "seed text"),
            VectorMemoryDocument(target, "target text"),
        ),
        _Adapter(),
        embedding_profile="a013-test",
    )
    relation = TargetFreeRelationIndex(
        (seed, target),
        (
            AssociationEdge(
                "edge",
                "seed",
                "target",
                RelationType.WORKS_AT,
                0.9,
                0.9,
                ("evidence:edge",),
            ),
        ),
    )
    return vector, relation


def _request(policy, structural_need):
    return HybridRecallRequest(
        request_id=f"req:{policy.value}",
        policy=policy,
        vector_query=VectorMemoryQuery(
            "query",
            "query",
            top_k=1,
            minimum_similarity=0.9,
        ),
        structural_need=structural_need,
        default_relation_scope=(RelationType.WORKS_AT,),
    )


def test_vector_only_does_not_invoke_relation():
    vector, relation = _runtime()
    result = run_hybrid_recall(
        _request(
            RelationalActivationPolicy.VECTOR_ONLY,
            StructuralNeed((RelationType.WORKS_AT,), True),
        ),
        vector_index=vector,
        relation_index=relation,
    )
    assert result.initial_memory_ids == ("seed",)
    assert result.final_memory_ids == ("seed",)
    assert result.relation_invoked is False


def test_always_relation_invokes_even_without_structural_need():
    vector, relation = _runtime()
    result = run_hybrid_recall(
        _request(
            RelationalActivationPolicy.ALWAYS_RELATION,
            StructuralNeed(),
        ),
        vector_index=vector,
        relation_index=relation,
    )
    assert result.relation_invoked is True
    assert result.final_memory_ids == ("seed", "target")


def test_signal_gated_relation_invokes_only_with_explicit_structural_need():
    vector, relation = _runtime()
    off = run_hybrid_recall(
        _request(
            RelationalActivationPolicy.SIGNAL_GATED_RELATION,
            StructuralNeed(),
        ),
        vector_index=vector,
        relation_index=relation,
    )
    on = run_hybrid_recall(
        _request(
            RelationalActivationPolicy.SIGNAL_GATED_RELATION,
            StructuralNeed((RelationType.WORKS_AT,), True),
        ),
        vector_index=vector,
        relation_index=relation,
    )
    assert off.relation_invoked is False
    assert off.final_memory_ids == ("seed",)
    assert on.relation_invoked is True
    assert on.final_memory_ids == ("seed", "target")
