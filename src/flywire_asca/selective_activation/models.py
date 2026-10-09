from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import math

from flywire_asca.contracts import (
    ActivationState,
    MemoryKind,
    WorkingSet,
)
from flywire_asca.contracts.validation import (
    require_nonempty,
    require_probability,
)
from flywire_asca.vector_memory import VectorMemoryResult


class SelectiveMode(str, Enum):
    SELECTIVE_CONVERGENCE = "SELECTIVE_CONVERGENCE"
    SINGLE_BEST = "SINGLE_BEST"
    EXHAUSTIVE = "EXHAUSTIVE"


def _canonical_strings(name: str, values: tuple[str, ...]) -> tuple[str, ...]:
    normalized: list[str] = []
    for value in values:
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{name} must contain only nonempty strings")
        normalized.append(value)
    return tuple(sorted(set(normalized)))


def _require_nonnegative_int(name: str, value: int) -> None:
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise ValueError(f"{name} must be a nonnegative integer")


def _require_unit_interval(name: str, value: float) -> float:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise ValueError(f"{name} must be finite and within [0, 1]")
    numeric = float(value)
    if not math.isfinite(numeric) or not 0.0 <= numeric <= 1.0:
        raise ValueError(f"{name} must be finite and within [0, 1]")
    return numeric


@dataclass(frozen=True, slots=True)
class SelectiveRetrievalEvidence:
    source_cue_id: str
    result: VectorMemoryResult

    def __post_init__(self) -> None:
        require_nonempty("source_cue_id", self.source_cue_id)
        if not isinstance(self.result, VectorMemoryResult):
            raise ValueError("result must be a VectorMemoryResult")


@dataclass(frozen=True, slots=True)
class MemoryActivationSupport:
    memory_id: str
    source_cue_ids: tuple[str, ...]
    similarities: tuple[float, ...]
    support_count: int
    max_similarity: float
    activation: float
    memory_kind: MemoryKind
    proposition_confidence: float
    evidence_ids: tuple[str, ...]
    entity_ids: tuple[str, ...]
    context_tags: tuple[str, ...]
    source_tags: tuple[str, ...]

    def __post_init__(self) -> None:
        require_nonempty("memory_id", self.memory_id)
        if not self.source_cue_ids:
            raise ValueError("source_cue_ids must not be empty")
        if len(self.source_cue_ids) != len(self.similarities):
            raise ValueError(
                "source_cue_ids and similarities must have equal length"
            )

        pairs: list[tuple[str, float]] = []
        seen: set[str] = set()
        for cue_id, similarity in zip(self.source_cue_ids, self.similarities):
            require_nonempty("source_cue_ids", cue_id)
            if cue_id in seen:
                raise ValueError("source_cue_ids must be unique")
            seen.add(cue_id)
            value = _require_unit_interval("similarities", similarity)
            if value <= 0.0:
                raise ValueError("similarities must contain only values in (0, 1]")
            pairs.append((cue_id, value))
        pairs.sort(key=lambda item: item[0])

        if (
            not isinstance(self.support_count, int)
            or isinstance(self.support_count, bool)
            or self.support_count != len(pairs)
        ):
            raise ValueError(
                "support_count must equal len(source_cue_ids) and len(similarities)"
            )
        expected_max = max(value for _, value in pairs)
        observed_max = _require_unit_interval(
            "max_similarity",
            self.max_similarity,
        )
        if observed_max != expected_max:
            raise ValueError("max_similarity must equal max(similarities)")

        activation = _require_unit_interval("activation", self.activation)
        if not isinstance(self.memory_kind, MemoryKind):
            raise ValueError("memory_kind must be a MemoryKind")
        require_probability(
            "proposition_confidence",
            self.proposition_confidence,
        )

        object.__setattr__(
            self,
            "source_cue_ids",
            tuple(cue_id for cue_id, _ in pairs),
        )
        object.__setattr__(
            self,
            "similarities",
            tuple(value for _, value in pairs),
        )
        object.__setattr__(self, "max_similarity", observed_max)
        object.__setattr__(self, "activation", activation)
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
class SelectiveWorkingSetResult:
    working_set: WorkingSet
    activation_states: tuple[ActivationState, ...]
    supports: tuple[MemoryActivationSupport, ...]
    input_result_count: int
    input_hit_count: int
    unique_candidate_count: int
    positive_candidate_count: int
    activated_candidate_count: int
    selected_count: int
    dropped_by_memory_budget_count: int
    dropped_by_working_set_budget_count: int
    memory_budget_boundary_tie: bool
    working_set_boundary_tie: bool
    embedding_model_name: str
    embedding_model_digest: str | None
    embedding_profile: str

    def __post_init__(self) -> None:
        if not isinstance(self.working_set, WorkingSet):
            raise ValueError("working_set must be a WorkingSet")
        if any(
            not isinstance(state, ActivationState)
            for state in self.activation_states
        ):
            raise ValueError(
                "activation_states must contain only ActivationState values"
            )
        if any(
            not isinstance(support, MemoryActivationSupport)
            for support in self.supports
        ):
            raise ValueError(
                "supports must contain only MemoryActivationSupport values"
            )

        for name in (
            "input_result_count",
            "input_hit_count",
            "unique_candidate_count",
            "positive_candidate_count",
            "activated_candidate_count",
            "selected_count",
            "dropped_by_memory_budget_count",
            "dropped_by_working_set_budget_count",
        ):
            _require_nonnegative_int(name, getattr(self, name))

        if self.input_hit_count < self.unique_candidate_count:
            raise ValueError(
                "input_hit_count must be >= unique_candidate_count"
            )
        if self.unique_candidate_count < self.positive_candidate_count:
            raise ValueError(
                "unique_candidate_count must be >= positive_candidate_count"
            )
        if self.positive_candidate_count != len(self.supports):
            raise ValueError(
                "positive_candidate_count must equal len(supports)"
            )
        if self.activated_candidate_count != len(self.activation_states):
            raise ValueError(
                "activated_candidate_count must equal len(activation_states)"
            )
        if self.selected_count != len(self.working_set.entries):
            raise ValueError(
                "selected_count must equal len(working_set.entries)"
            )
        if (
            self.dropped_by_memory_budget_count
            != self.positive_candidate_count - self.activated_candidate_count
        ):
            raise ValueError(
                "dropped_by_memory_budget_count must equal "
                "positive_candidate_count - activated_candidate_count"
            )
        if (
            self.dropped_by_working_set_budget_count
            != self.activated_candidate_count - self.selected_count
        ):
            raise ValueError(
                "dropped_by_working_set_budget_count must equal "
                "activated_candidate_count - selected_count"
            )
        if not isinstance(self.memory_budget_boundary_tie, bool):
            raise ValueError("memory_budget_boundary_tie must be a boolean")
        if not isinstance(self.working_set_boundary_tie, bool):
            raise ValueError("working_set_boundary_tie must be a boolean")

        state_ids = tuple(state.node_id for state in self.activation_states)
        if len(set(state_ids)) != len(state_ids):
            raise ValueError("activation_states contain duplicate node_id values")
        support_ids = tuple(support.memory_id for support in self.supports)
        if len(set(support_ids)) != len(support_ids):
            raise ValueError("supports contain duplicate memory_id values")
        if not set(state_ids).issubset(support_ids):
            raise ValueError("activation_states must reference support memory IDs")
        entry_ids = tuple(entry.ref_id for entry in self.working_set.entries)
        if not set(entry_ids).issubset(state_ids):
            raise ValueError(
                "working_set entries must reference activation state node IDs"
            )

        require_nonempty("embedding_model_name", self.embedding_model_name)
        if self.embedding_model_digest is not None:
            require_nonempty(
                "embedding_model_digest",
                self.embedding_model_digest,
            )
        require_nonempty("embedding_profile", self.embedding_profile)
