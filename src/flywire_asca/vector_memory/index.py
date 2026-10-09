from __future__ import annotations

from collections.abc import Iterable
import math

from flywire_asca.embedding import (
    EmbeddingAdapter,
    EmbeddingInputKind,
    EmbeddingRequest,
    EmbeddingVector,
)
from flywire_asca.contracts.validation import require_nonempty

from .models import (
    VectorMemoryDocument,
    VectorMemoryHit,
    VectorMemoryQuery,
    VectorMemoryResult,
)


def _contains_all(values: tuple[str, ...], required: tuple[str, ...]) -> bool:
    return set(required).issubset(values)


def _cosine(left: EmbeddingVector, right: EmbeddingVector) -> float:
    if left.dimension != right.dimension:
        raise ValueError("embedding dimension mismatch during vector scoring")
    score = sum(a * b for a, b in zip(left.values, right.values))
    if not math.isfinite(score):
        raise ValueError("cosine similarity must be finite")
    return max(-1.0, min(1.0, score))


class ExactVectorMemoryIndex:
    def __init__(
        self,
        documents: Iterable[VectorMemoryDocument],
        adapter: EmbeddingAdapter,
        *,
        embedding_profile: str,
    ) -> None:
        require_nonempty("embedding_profile", embedding_profile)
        document_tuple = tuple(documents)
        if any(not isinstance(doc, VectorMemoryDocument) for doc in document_tuple):
            raise ValueError("documents must contain only VectorMemoryDocument values")
        memory_ids = tuple(doc.memory.memory_id for doc in document_tuple)
        if len(set(memory_ids)) != len(memory_ids):
            raise ValueError("duplicate memory_id values are not allowed")

        descriptor = adapter.inspect()
        response = adapter.embed(
            EmbeddingRequest(
                "vector-memory-index-build",
                EmbeddingInputKind.DOCUMENT,
                tuple(doc.retrieval_text for doc in document_tuple),
            )
        ) if document_tuple else None

        vectors: tuple[EmbeddingVector, ...]
        if response is None:
            vectors = ()
        else:
            if (
                getattr(response, "input_count", None) != len(document_tuple)
                or len(getattr(response, "vectors", ())) != len(document_tuple)
            ):
                raise ValueError("document embedding count mismatch")
            vectors = tuple(response.vectors)
            if any(
                vector.dimension != descriptor.embedding_dimension
                for vector in vectors
            ):
                raise ValueError("document embedding dimension mismatch")
            if getattr(response, "model_name", None) != descriptor.model_name:
                raise ValueError("document embedding model mismatch")
            if getattr(response, "model_digest", None) != descriptor.model_digest:
                raise ValueError("document embedding digest mismatch")

        self._documents = document_tuple
        self._vectors = vectors
        self._adapter = adapter
        self._descriptor = descriptor
        self._embedding_profile = embedding_profile

    @property
    def document_count(self) -> int:
        return len(self._documents)

    def _eligible(self, doc: VectorMemoryDocument, query: VectorMemoryQuery) -> bool:
        if (
            query.allowed_memory_kinds
            and doc.memory.kind not in query.allowed_memory_kinds
        ):
            return False
        if not _contains_all(doc.entity_ids, query.required_entity_ids):
            return False
        if not _contains_all(doc.context_tags, query.required_context_tags):
            return False
        if not _contains_all(doc.source_tags, query.required_source_tags):
            return False
        return True

    def search(self, query: VectorMemoryQuery) -> VectorMemoryResult:
        if not isinstance(query, VectorMemoryQuery):
            raise ValueError("query must be a VectorMemoryQuery")

        query_response = self._adapter.embed(
            EmbeddingRequest(
                f"vector-memory-query:{query.query_id}",
                EmbeddingInputKind.QUERY,
                (query.query_text,),
            )
        )
        if (
            getattr(query_response, "input_count", None) != 1
            or len(getattr(query_response, "vectors", ())) != 1
        ):
            raise ValueError("query embedding count mismatch")
        query_vector = query_response.vectors[0]
        if query_vector.dimension != self._descriptor.embedding_dimension:
            raise ValueError("query embedding dimension mismatch")
        if getattr(query_response, "model_name", None) != self._descriptor.model_name:
            raise ValueError("query embedding model mismatch")
        if getattr(query_response, "model_digest", None) != self._descriptor.model_digest:
            raise ValueError("query embedding digest mismatch")

        eligible: list[tuple[VectorMemoryDocument, EmbeddingVector]] = [
            (doc, vector)
            for doc, vector in zip(self._documents, self._vectors)
            if self._eligible(doc, query)
        ]
        scored: list[tuple[float, VectorMemoryDocument]] = [
            (_cosine(query_vector, vector), doc)
            for doc, vector in eligible
        ]
        above = [
            (score, doc)
            for score, doc in scored
            if score >= query.minimum_similarity
        ]
        above.sort(key=lambda item: (-item[0], item[1].memory.memory_id))
        selected = above[: query.top_k]

        hits = tuple(
            VectorMemoryHit(
                memory_id=doc.memory.memory_id,
                similarity=score,
                memory_kind=doc.memory.kind,
                proposition_confidence=doc.memory.proposition_confidence,
                evidence_ids=doc.memory.evidence_ids,
                entity_ids=doc.entity_ids,
                context_tags=doc.context_tags,
                source_tags=doc.source_tags,
            )
            for score, doc in selected
        )
        return VectorMemoryResult(
            query_id=query.query_id,
            hits=hits,
            stored_count=len(self._documents),
            metadata_eligible_count=len(eligible),
            scored_vector_count=len(scored),
            above_threshold_count=len(above),
            returned_count=len(hits),
            embedding_model_name=self._descriptor.model_name,
            embedding_model_digest=self._descriptor.model_digest,
            embedding_profile=self._embedding_profile,
        )
