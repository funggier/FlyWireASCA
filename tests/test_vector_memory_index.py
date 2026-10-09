from __future__ import annotations

from types import SimpleNamespace

import pytest

from flywire_asca.contracts import MemoryKind, MemoryRecord
from flywire_asca.embedding import (
    EmbeddingDescriptor,
    EmbeddingInputKind,
    EmbeddingRequest,
    EmbeddingResponse,
    normalize_embedding_values,
)
from flywire_asca.vector_memory import (
    ExactVectorMemoryIndex,
    VectorMemoryDocument,
    VectorMemoryQuery,
)


def _memory(
    memory_id: str,
    *,
    kind: MemoryKind = MemoryKind.SEMANTIC,
    confidence: float = 0.8,
    evidence_ids: tuple[str, ...] = (),
) -> MemoryRecord:
    return MemoryRecord(memory_id, kind, f"content:{memory_id}", confidence, evidence_ids)


def _doc(
    memory_id: str,
    text: str,
    *,
    kind: MemoryKind = MemoryKind.SEMANTIC,
    confidence: float = 0.8,
    evidence_ids: tuple[str, ...] = (),
    entity_ids: tuple[str, ...] = (),
    context_tags: tuple[str, ...] = (),
    source_tags: tuple[str, ...] = (),
) -> VectorMemoryDocument:
    return VectorMemoryDocument(
        _memory(memory_id, kind=kind, confidence=confidence, evidence_ids=evidence_ids),
        text,
        entity_ids,
        context_tags,
        source_tags,
    )


class FakeEmbeddingAdapter:
    def __init__(self, vectors_by_text, *, digest="digest", dimension=2):
        self.vectors_by_text = vectors_by_text
        self.requests: list[EmbeddingRequest] = []
        self.descriptor = EmbeddingDescriptor(
            backend_name="fake",
            backend_version="1",
            model_name="fake-embedder",
            model_digest=digest,
            architecture="fake",
            parameter_count=None,
            parameter_size=None,
            quantization=None,
            context_length=8192,
            embedding_dimension=dimension,
            capabilities=("embedding",),
        )

    def inspect(self):
        return self.descriptor

    def embed(self, request):
        self.requests.append(request)
        vectors = tuple(
            normalize_embedding_values(
                self.vectors_by_text[text],
                expected_dimension=self.descriptor.embedding_dimension,
            )
            for text in request.texts
        )
        return EmbeddingResponse(
            request.request_id,
            self.descriptor.model_name,
            self.descriptor.model_digest,
            vectors,
            len(vectors),
            None,
            None,
            None,
        )


def test_document_and_query_contracts_validate_and_canonicalize_metadata():
    doc = _doc(
        "m1",
        " memory ",
        entity_ids=("entity-b", "entity-a", "entity-a"),
        context_tags=("work", "office", "work"),
        source_tags=("note", "chat", "chat"),
    )
    assert doc.entity_ids == ("entity-a", "entity-b")
    assert doc.context_tags == ("office", "work")
    assert doc.source_tags == ("chat", "note")

    query = VectorMemoryQuery(
        "q1",
        " question ",
        top_k=3,
        minimum_similarity=0.25,
        allowed_memory_kinds=(MemoryKind.SEMANTIC, MemoryKind.EPISODIC, MemoryKind.SEMANTIC),
        required_entity_ids=("b", "a", "a"),
        required_context_tags=("z", "x", "x"),
        required_source_tags=("s2", "s1"),
    )
    assert query.allowed_memory_kinds == (MemoryKind.EPISODIC, MemoryKind.SEMANTIC)
    assert query.required_entity_ids == ("a", "b")
    assert query.required_context_tags == ("x", "z")
    assert query.required_source_tags == ("s1", "s2")

    with pytest.raises(ValueError, match="retrieval_text"):
        _doc("m2", " ")
    with pytest.raises(ValueError, match="top_k"):
        VectorMemoryQuery("q", "x", top_k=0)
    with pytest.raises(ValueError, match="minimum_similarity"):
        VectorMemoryQuery("q", "x", minimum_similarity=2.0)


def test_index_rejects_duplicate_memory_ids_and_materializes_generator_once():
    docs = [_doc("m1", "one"), _doc("m2", "two")]
    adapter = FakeEmbeddingAdapter({"one": (1.0, 0.0), "two": (0.0, 1.0)})

    consumed = {"count": 0}
    def generator():
        for doc in docs:
            consumed["count"] += 1
            yield doc

    index = ExactVectorMemoryIndex(generator(), adapter, embedding_profile="fake-v1")
    assert consumed["count"] == 2
    assert index.document_count == 2
    assert len(adapter.requests) == 1
    assert adapter.requests[0].input_kind is EmbeddingInputKind.DOCUMENT

    with pytest.raises(ValueError, match="duplicate memory_id"):
        ExactVectorMemoryIndex(
            (_doc("dup", "one"), _doc("dup", "two")),
            adapter,
            embedding_profile="fake-v1",
        )


def test_index_rejects_adapter_count_or_dimension_contract_violation():
    doc = _doc("m1", "one")

    class BadCountAdapter(FakeEmbeddingAdapter):
        def embed(self, request):
            self.requests.append(request)
            return SimpleNamespace(
                input_count=0,
                vectors=(),
                model_name="fake-embedder",
                model_digest="digest",
            )

    with pytest.raises(ValueError, match="count"):
        ExactVectorMemoryIndex(
            (doc,),
            BadCountAdapter({"one": (1.0, 0.0)}),
            embedding_profile="fake-v1",
        )

    class BadDimensionAdapter(FakeEmbeddingAdapter):
        def embed(self, request):
            self.requests.append(request)
            return SimpleNamespace(
                input_count=1,
                vectors=(normalize_embedding_values((1.0, 0.0, 0.0)),),
                model_name="fake-embedder",
                model_digest="digest",
            )

    with pytest.raises(ValueError, match="dimension"):
        ExactVectorMemoryIndex(
            (doc,),
            BadDimensionAdapter({"one": (1.0, 0.0)}),
            embedding_profile="fake-v1",
        )


def test_exact_cosine_ranking_is_score_desc_then_memory_id_tie_break():
    docs = (
        _doc("m-b", "b"),
        _doc("m-a", "a"),
        _doc("m-c", "c"),
    )
    adapter = FakeEmbeddingAdapter(
        {
            "a": (1.0, 0.0),
            "b": (1.0, 0.0),
            "c": (0.0, 1.0),
            "query": (1.0, 0.0),
        }
    )
    index = ExactVectorMemoryIndex(docs, adapter, embedding_profile="fake-v1")
    result = index.search(
        VectorMemoryQuery("q", "query", top_k=3, minimum_similarity=-1.0)
    )
    assert [hit.memory_id for hit in result.hits] == ["m-a", "m-b", "m-c"]
    assert [hit.similarity for hit in result.hits] == pytest.approx([1.0, 1.0, 0.0])
    assert result.stored_count == 3
    assert result.metadata_eligible_count == 3
    assert result.scored_vector_count == 3
    assert result.above_threshold_count == 3
    assert result.returned_count == 3
    assert result.embedding_model_name == "fake-embedder"
    assert result.embedding_model_digest == "digest"
    assert result.embedding_profile == "fake-v1"


def test_metadata_filters_apply_before_scoring_with_all_required_and_semantics():
    docs = (
        _doc(
            "m1", "one",
            kind=MemoryKind.SEMANTIC,
            entity_ids=("alice", "team"),
            context_tags=("office", "project-x"),
            source_tags=("chat", "note"),
        ),
        _doc(
            "m2", "two",
            kind=MemoryKind.EPISODIC,
            entity_ids=("alice",),
            context_tags=("office",),
            source_tags=("chat",),
        ),
        _doc(
            "m3", "three",
            kind=MemoryKind.SEMANTIC,
            entity_ids=("bob", "team"),
            context_tags=("office", "project-x"),
            source_tags=("note",),
        ),
    )
    adapter = FakeEmbeddingAdapter(
        {
            "one": (1.0, 0.0),
            "two": (1.0, 0.0),
            "three": (1.0, 0.0),
            "query": (1.0, 0.0),
        }
    )
    index = ExactVectorMemoryIndex(docs, adapter, embedding_profile="fake-v1")
    result = index.search(
        VectorMemoryQuery(
            "q",
            "query",
            allowed_memory_kinds=(MemoryKind.SEMANTIC,),
            required_entity_ids=("alice", "team"),
            required_context_tags=("office", "project-x"),
            required_source_tags=("note",),
        )
    )
    assert [hit.memory_id for hit in result.hits] == ["m1"]
    assert result.metadata_eligible_count == 1
    assert result.scored_vector_count == 1


def test_ambiguity_is_preserved_without_entity_filter_and_filter_can_constrain_it():
    docs = (
        _doc("somchai-a", "Somchai works at company A", confidence=0.4, entity_ids=("person-a",)),
        _doc("somchai-b", "Somchai works at company B", confidence=0.9, entity_ids=("person-b",)),
    )
    adapter = FakeEmbeddingAdapter(
        {
            "Somchai works at company A": (1.0, 0.0),
            "Somchai works at company B": (1.0, 0.0),
            "Somchai works where": (1.0, 0.0),
        }
    )
    index = ExactVectorMemoryIndex(docs, adapter, embedding_profile="fake-v1")

    ambiguous = index.search(
        VectorMemoryQuery("q1", "Somchai works where", top_k=5, minimum_similarity=0.5)
    )
    assert [hit.memory_id for hit in ambiguous.hits] == ["somchai-a", "somchai-b"]
    assert [hit.proposition_confidence for hit in ambiguous.hits] == [0.4, 0.9]

    filtered = index.search(
        VectorMemoryQuery(
            "q2",
            "Somchai works where",
            required_entity_ids=("person-b",),
            top_k=5,
            minimum_similarity=0.5,
        )
    )
    assert [hit.memory_id for hit in filtered.hits] == ["somchai-b"]


def test_threshold_counts_before_topk_and_no_hit_is_valid():
    docs = (
        _doc("m1", "one", evidence_ids=("e1",)),
        _doc("m2", "two"),
        _doc("m3", "three"),
    )
    adapter = FakeEmbeddingAdapter(
        {
            "one": (1.0, 0.0),
            "two": (0.8, 0.6),
            "three": (0.0, 1.0),
            "query": (1.0, 0.0),
            "none": (-1.0, 0.0),
        }
    )
    index = ExactVectorMemoryIndex(docs, adapter, embedding_profile="fake-v1")
    result = index.search(
        VectorMemoryQuery("q", "query", top_k=1, minimum_similarity=0.5)
    )
    assert [hit.memory_id for hit in result.hits] == ["m1"]
    assert result.above_threshold_count == 2
    assert result.returned_count == 1
    assert result.hits[0].evidence_ids == ("e1",)

    no_hit = index.search(
        VectorMemoryQuery("q2", "none", top_k=2, minimum_similarity=0.5)
    )
    assert no_hit.hits == ()
    assert no_hit.above_threshold_count == 0
    assert no_hit.returned_count == 0
    assert no_hit.scored_vector_count == 3
