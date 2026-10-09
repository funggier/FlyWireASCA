from __future__ import annotations

from dataclasses import dataclass
import math

from flywire_asca.contracts import MemoryKind, MemoryRecord
from flywire_asca.contracts.validation import require_nonempty, require_probability


def _canonical_strings(name: str, values: tuple[str, ...]) -> tuple[str, ...]:
    normalized: list[str] = []
    for value in values:
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{name} must contain only nonempty strings")
        normalized.append(value)
    return tuple(sorted(set(normalized)))


def _canonical_memory_kinds(values: tuple[MemoryKind, ...]) -> tuple[MemoryKind, ...]:
    for value in values:
        if not isinstance(value, MemoryKind):
            raise ValueError("allowed_memory_kinds must contain only MemoryKind values")
    return tuple(sorted(set(values), key=lambda value: value.value))


@dataclass(frozen=True, slots=True)
class VectorMemoryDocument:
    memory: MemoryRecord
    retrieval_text: str
    entity_ids: tuple[str, ...] = ()
    context_tags: tuple[str, ...] = ()
    source_tags: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.memory, MemoryRecord):
            raise ValueError("memory must be a MemoryRecord")
        require_nonempty("retrieval_text", self.retrieval_text)
        object.__setattr__(
            self,
            "entity_ids",
            _canonical_strings("entity_ids", self.entity_ids),
        )
        object.__setattr__(
            self,
            "context_tags",
            _canonical_strings("context_tags", self.context_tags),
        )
        object.__setattr__(
            self,
            "source_tags",
            _canonical_strings("source_tags", self.source_tags),
        )


@dataclass(frozen=True, slots=True)
class VectorMemoryQuery:
    query_id: str
    query_text: str
    top_k: int = 5
    minimum_similarity: float = 0.0
    allowed_memory_kinds: tuple[MemoryKind, ...] = ()
    required_entity_ids: tuple[str, ...] = ()
    required_context_tags: tuple[str, ...] = ()
    required_source_tags: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        require_nonempty("query_id", self.query_id)
        require_nonempty("query_text", self.query_text)
        if (
            not isinstance(self.top_k, int)
            or isinstance(self.top_k, bool)
            or self.top_k <= 0
        ):
            raise ValueError("top_k must be a positive integer")
        if (
            not isinstance(self.minimum_similarity, (int, float))
            or isinstance(self.minimum_similarity, bool)
        ):
            raise ValueError("minimum_similarity must be finite and within [-1, 1]")
        similarity = float(self.minimum_similarity)
        if not math.isfinite(similarity) or not -1.0 <= similarity <= 1.0:
            raise ValueError("minimum_similarity must be finite and within [-1, 1]")
        object.__setattr__(self, "minimum_similarity", similarity)
        object.__setattr__(
            self,
            "allowed_memory_kinds",
            _canonical_memory_kinds(self.allowed_memory_kinds),
        )
        object.__setattr__(
            self,
            "required_entity_ids",
            _canonical_strings("required_entity_ids", self.required_entity_ids),
        )
        object.__setattr__(
            self,
            "required_context_tags",
            _canonical_strings("required_context_tags", self.required_context_tags),
        )
        object.__setattr__(
            self,
            "required_source_tags",
            _canonical_strings("required_source_tags", self.required_source_tags),
        )


@dataclass(frozen=True, slots=True)
class VectorMemoryHit:
    memory_id: str
    similarity: float
    memory_kind: MemoryKind
    proposition_confidence: float
    evidence_ids: tuple[str, ...]
    entity_ids: tuple[str, ...]
    context_tags: tuple[str, ...]
    source_tags: tuple[str, ...]

    def __post_init__(self) -> None:
        require_nonempty("memory_id", self.memory_id)
        if (
            not isinstance(self.similarity, (int, float))
            or isinstance(self.similarity, bool)
        ):
            raise ValueError("similarity must be finite and within [-1, 1]")
        similarity = float(self.similarity)
        if not math.isfinite(similarity) or not -1.0 <= similarity <= 1.0:
            raise ValueError("similarity must be finite and within [-1, 1]")
        object.__setattr__(self, "similarity", similarity)
        if not isinstance(self.memory_kind, MemoryKind):
            raise ValueError("memory_kind must be a MemoryKind")
        require_probability("proposition_confidence", self.proposition_confidence)
        object.__setattr__(
            self,
            "evidence_ids",
            _canonical_strings("evidence_ids", self.evidence_ids),
        )
        object.__setattr__(
            self,
            "entity_ids",
            _canonical_strings("entity_ids", self.entity_ids),
        )
        object.__setattr__(
            self,
            "context_tags",
            _canonical_strings("context_tags", self.context_tags),
        )
        object.__setattr__(
            self,
            "source_tags",
            _canonical_strings("source_tags", self.source_tags),
        )


@dataclass(frozen=True, slots=True)
class VectorMemoryResult:
    query_id: str
    hits: tuple[VectorMemoryHit, ...]
    stored_count: int
    metadata_eligible_count: int
    scored_vector_count: int
    above_threshold_count: int
    returned_count: int
    embedding_model_name: str
    embedding_model_digest: str | None
    embedding_profile: str

    def __post_init__(self) -> None:
        require_nonempty("query_id", self.query_id)
        if any(not isinstance(hit, VectorMemoryHit) for hit in self.hits):
            raise ValueError("hits must contain only VectorMemoryHit values")
        for name in (
            "stored_count",
            "metadata_eligible_count",
            "scored_vector_count",
            "above_threshold_count",
            "returned_count",
        ):
            value = getattr(self, name)
            if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                raise ValueError(f"{name} must be a nonnegative integer")
        if self.returned_count != len(self.hits):
            raise ValueError("returned_count must equal len(hits)")
        if not (
            self.returned_count
            <= self.above_threshold_count
            <= self.scored_vector_count
            <= self.metadata_eligible_count
            <= self.stored_count
        ):
            raise ValueError("result counts must be monotonically bounded")
        require_nonempty("embedding_model_name", self.embedding_model_name)
        if self.embedding_model_digest is not None:
            require_nonempty("embedding_model_digest", self.embedding_model_digest)
        require_nonempty("embedding_profile", self.embedding_profile)
