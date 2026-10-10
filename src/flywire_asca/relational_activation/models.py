from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import math

from flywire_asca.contracts import RelationType
from flywire_asca.contracts.validation import require_nonempty
from flywire_asca.relational_reasoning import (
    MAX_HOPS,
    MAX_SCANNED_EDGES,
    MAX_VISITED_NODES,
)
from flywire_asca.vector_memory import VectorMemoryQuery, VectorMemoryResult


class RelationalActivationPolicy(str, Enum):
    VECTOR_ONLY = "VECTOR_ONLY"
    ALWAYS_RELATION = "ALWAYS_RELATION"
    SIGNAL_GATED_RELATION = "SIGNAL_GATED_RELATION"


class RelationalActivationDecision(str, Enum):
    SIGNAL_GATED_RELATION_JUSTIFIED = "SIGNAL_GATED_RELATION_JUSTIFIED"
    ALWAYS_RELATION_PREFERRED = "ALWAYS_RELATION_PREFERRED"
    RELATION_INTEGRATION_NOT_JUSTIFIED = "RELATION_INTEGRATION_NOT_JUSTIFIED"
    MIXED = "MIXED"


class ExpansionTermination(str, Enum):
    FRONTIER_EXHAUSTED = "FRONTIER_EXHAUSTED"
    HOP_BUDGET_EXHAUSTED = "HOP_BUDGET_EXHAUSTED"
    NODE_BUDGET_EXHAUSTED = "NODE_BUDGET_EXHAUSTED"
    EDGE_BUDGET_EXHAUSTED = "EDGE_BUDGET_EXHAUSTED"


def _canonical_strings(
    name: str,
    values: tuple[str, ...],
    *,
    nonempty: bool = False,
) -> tuple[str, ...]:
    parsed: list[str] = []
    for value in values:
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{name} must contain only nonempty strings")
        parsed.append(value)
    result = tuple(sorted(set(parsed)))
    if nonempty and not result:
        raise ValueError(f"{name} must not be empty")
    return result


def _canonical_relations(
    name: str,
    values: tuple[RelationType, ...],
    *,
    nonempty: bool = False,
) -> tuple[RelationType, ...]:
    if any(not isinstance(value, RelationType) for value in values):
        raise ValueError(f"{name} must contain only RelationType values")
    result = tuple(sorted(set(values), key=lambda value: value.value))
    if nonempty and not result:
        raise ValueError(f"{name} must not be empty")
    return result


def _positive_int(name: str, value: int, maximum: int) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or not 1 <= value <= maximum:
        raise ValueError(f"{name} must be an integer within [1, {maximum}]")
    return value


def _probability(name: str, value: float) -> float:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise ValueError(f"{name} must be within [0, 1]")
    parsed = float(value)
    if not math.isfinite(parsed) or not 0.0 <= parsed <= 1.0:
        raise ValueError(f"{name} must be within [0, 1]")
    return parsed


@dataclass(frozen=True, slots=True)
class StructuralNeed:
    required_relations: tuple[RelationType, ...] = ()
    requires_path_provenance: bool = False

    def __post_init__(self) -> None:
        relations = _canonical_relations("required_relations", self.required_relations)
        object.__setattr__(self, "required_relations", relations)
        if not isinstance(self.requires_path_provenance, bool):
            raise ValueError("requires_path_provenance must be a boolean")
        if self.requires_path_provenance and not relations:
            raise ValueError(
                "requires_path_provenance requires at least one required relation"
            )

    @property
    def active(self) -> bool:
        return bool(self.required_relations)


@dataclass(frozen=True, slots=True)
class ExpansionRequest:
    seed_memory_ids: tuple[str, ...]
    allowed_relations: tuple[RelationType, ...]
    max_hops: int = MAX_HOPS
    max_visited_nodes: int = MAX_VISITED_NODES
    max_scanned_edges: int = MAX_SCANNED_EDGES
    minimum_proposition_confidence: float = 0.5

    def __post_init__(self) -> None:
        seeds = _canonical_strings(
            "seed_memory_ids", self.seed_memory_ids, nonempty=True
        )
        relations = _canonical_relations(
            "allowed_relations", self.allowed_relations, nonempty=True
        )
        object.__setattr__(self, "seed_memory_ids", seeds)
        object.__setattr__(self, "allowed_relations", relations)
        _positive_int("max_hops", self.max_hops, MAX_HOPS)
        _positive_int("max_visited_nodes", self.max_visited_nodes, MAX_VISITED_NODES)
        _positive_int("max_scanned_edges", self.max_scanned_edges, MAX_SCANNED_EDGES)
        if self.max_visited_nodes < len(seeds):
            raise ValueError("max_visited_nodes must cover all seed_memory_ids")
        object.__setattr__(
            self,
            "minimum_proposition_confidence",
            _probability(
                "minimum_proposition_confidence",
                self.minimum_proposition_confidence,
            ),
        )


@dataclass(frozen=True, slots=True)
class ExpansionPathEvidence:
    reached_memory_id: str
    memory_ids: tuple[str, ...]
    edge_ids: tuple[str, ...]
    evidence_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        require_nonempty("reached_memory_id", self.reached_memory_id)
        if not self.memory_ids:
            raise ValueError("memory_ids must not be empty")
        for value in self.memory_ids:
            require_nonempty("memory_id", value)
        if len(set(self.memory_ids)) != len(self.memory_ids):
            raise ValueError("memory_ids must not contain a cycle")
        for value in self.edge_ids:
            require_nonempty("edge_id", value)
        if len(self.edge_ids) != len(self.memory_ids) - 1:
            raise ValueError("edge_ids length must equal len(memory_ids) - 1")
        if len(set(self.edge_ids)) != len(self.edge_ids):
            raise ValueError("edge_ids must be unique within a path")
        if self.reached_memory_id != self.memory_ids[-1]:
            raise ValueError("reached_memory_id must equal final memory_ids entry")
        object.__setattr__(
            self,
            "evidence_ids",
            _canonical_strings("evidence_ids", self.evidence_ids),
        )

    @property
    def hop_count(self) -> int:
        return len(self.edge_ids)


@dataclass(frozen=True, slots=True)
class ExpansionResult:
    seed_memory_ids: tuple[str, ...]
    visited_memory_ids: tuple[str, ...]
    paths: tuple[ExpansionPathEvidence, ...]
    scanned_edge_count: int
    max_hop_reached: int
    termination: ExpansionTermination

    def __post_init__(self) -> None:
        seeds = _canonical_strings("seed_memory_ids", self.seed_memory_ids, nonempty=True)
        object.__setattr__(self, "seed_memory_ids", seeds)
        if not self.visited_memory_ids:
            raise ValueError("visited_memory_ids must not be empty")
        for value in self.visited_memory_ids:
            require_nonempty("visited_memory_id", value)
        if len(set(self.visited_memory_ids)) != len(self.visited_memory_ids):
            raise ValueError("visited_memory_ids must be unique")
        if not set(seeds).issubset(self.visited_memory_ids):
            raise ValueError("visited_memory_ids must contain all seeds")
        if any(not isinstance(path, ExpansionPathEvidence) for path in self.paths):
            raise ValueError("paths must contain only ExpansionPathEvidence values")
        reached = tuple(path.reached_memory_id for path in self.paths)
        expected = tuple(
            memory_id
            for memory_id in self.visited_memory_ids
            if memory_id not in set(seeds)
        )
        if reached != expected:
            raise ValueError("paths must exactly cover reached non-seed memories")
        if (
            not isinstance(self.scanned_edge_count, int)
            or isinstance(self.scanned_edge_count, bool)
            or self.scanned_edge_count < 0
        ):
            raise ValueError("scanned_edge_count must be a nonnegative integer")
        if (
            not isinstance(self.max_hop_reached, int)
            or isinstance(self.max_hop_reached, bool)
            or self.max_hop_reached < 0
        ):
            raise ValueError("max_hop_reached must be a nonnegative integer")
        if not isinstance(self.termination, ExpansionTermination):
            raise ValueError("termination must be an ExpansionTermination")


DEFAULT_RELATION_SCOPE = tuple(RelationType)


@dataclass(frozen=True, slots=True)
class HybridRecallRequest:
    request_id: str
    policy: RelationalActivationPolicy
    vector_query: VectorMemoryQuery
    structural_need: StructuralNeed
    default_relation_scope: tuple[RelationType, ...] = DEFAULT_RELATION_SCOPE
    max_hops: int = MAX_HOPS
    max_visited_nodes: int = MAX_VISITED_NODES
    max_scanned_edges: int = MAX_SCANNED_EDGES
    minimum_proposition_confidence: float = 0.5

    def __post_init__(self) -> None:
        require_nonempty("request_id", self.request_id)
        if not isinstance(self.policy, RelationalActivationPolicy):
            raise ValueError("policy must be a RelationalActivationPolicy")
        if not isinstance(self.vector_query, VectorMemoryQuery):
            raise ValueError("vector_query must be a VectorMemoryQuery")
        if not isinstance(self.structural_need, StructuralNeed):
            raise ValueError("structural_need must be a StructuralNeed")
        object.__setattr__(
            self,
            "default_relation_scope",
            _canonical_relations(
                "default_relation_scope",
                self.default_relation_scope,
                nonempty=True,
            ),
        )
        _positive_int("max_hops", self.max_hops, MAX_HOPS)
        _positive_int("max_visited_nodes", self.max_visited_nodes, MAX_VISITED_NODES)
        _positive_int("max_scanned_edges", self.max_scanned_edges, MAX_SCANNED_EDGES)
        object.__setattr__(
            self,
            "minimum_proposition_confidence",
            _probability(
                "minimum_proposition_confidence",
                self.minimum_proposition_confidence,
            ),
        )


@dataclass(frozen=True, slots=True)
class HybridRecallResult:
    request_id: str
    policy: RelationalActivationPolicy
    structural_activation_requested: bool
    relation_invoked: bool
    vector_result: VectorMemoryResult
    initial_memory_ids: tuple[str, ...]
    final_memory_ids: tuple[str, ...]
    expansion_result: ExpansionResult | None

    def __post_init__(self) -> None:
        require_nonempty("request_id", self.request_id)
        if not isinstance(self.policy, RelationalActivationPolicy):
            raise ValueError("policy must be a RelationalActivationPolicy")
        if not isinstance(self.structural_activation_requested, bool):
            raise ValueError("structural_activation_requested must be a boolean")
        if not isinstance(self.relation_invoked, bool):
            raise ValueError("relation_invoked must be a boolean")
        if not isinstance(self.vector_result, VectorMemoryResult):
            raise ValueError("vector_result must be a VectorMemoryResult")
        initial = _canonical_strings("initial_memory_ids", self.initial_memory_ids)
        object.__setattr__(self, "initial_memory_ids", initial)
        if self.expansion_result is not None and not isinstance(
            self.expansion_result, ExpansionResult
        ):
            raise ValueError("expansion_result must be an ExpansionResult or None")
        if self.relation_invoked != (self.expansion_result is not None):
            raise ValueError("relation_invoked must match expansion_result presence")
        final = tuple(self.final_memory_ids)
        if any(not isinstance(value, str) or not value.strip() for value in final):
            raise ValueError("final_memory_ids must contain only nonempty strings")
        if len(set(final)) != len(final):
            raise ValueError("final_memory_ids must be unique")
        object.__setattr__(self, "final_memory_ids", final)
        if self.expansion_result is None:
            if set(final) != set(initial):
                raise ValueError(
                    "without relation expansion final_memory_ids must equal initial IDs"
                )
        else:
            if tuple(self.expansion_result.visited_memory_ids) != final:
                raise ValueError(
                    "final_memory_ids must equal expansion visited_memory_ids"
                )
