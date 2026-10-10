from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import math

from flywire_asca.contracts import RelationType
from flywire_asca.contracts.validation import require_nonempty


MAX_HOPS = 3
MAX_VISITED_NODES = 8
MAX_SCANNED_EDGES = 32


class ArchitectureDecision(str, Enum):
    EXPLICIT_RELATION_TRAVERSAL_JUSTIFIED = "EXPLICIT_RELATION_TRAVERSAL_JUSTIFIED"
    VECTOR_METADATA_REMAINS_SUFFICIENT = "VECTOR_METADATA_REMAINS_SUFFICIENT"
    MIXED = "MIXED"


class ComparisonVariant(str, Enum):
    VECTOR_METADATA = "VECTOR_METADATA"
    BOUNDED_RELATION = "BOUNDED_RELATION"


class TraversalTermination(str, Enum):
    TARGET_FOUND = "TARGET_FOUND"
    FRONTIER_EXHAUSTED = "FRONTIER_EXHAUSTED"
    HOP_BUDGET_EXHAUSTED = "HOP_BUDGET_EXHAUSTED"
    NODE_BUDGET_EXHAUSTED = "NODE_BUDGET_EXHAUSTED"
    EDGE_BUDGET_EXHAUSTED = "EDGE_BUDGET_EXHAUSTED"


def _canonical_strings(name: str, values: tuple[str, ...], *, nonempty: bool = False) -> tuple[str, ...]:
    parsed: list[str] = []
    for value in values:
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{name} must contain only nonempty strings")
        parsed.append(value)
    result = tuple(sorted(set(parsed)))
    if nonempty and not result:
        raise ValueError(f"{name} must not be empty")
    return result


def _positive_int(name: str, value: int, maximum: int) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or not 1 <= value <= maximum:
        raise ValueError(f"{name} must be an integer within [1, {maximum}]")
    return value


@dataclass(frozen=True, slots=True)
class TraversalRequest:
    seed_memory_ids: tuple[str, ...]
    target_memory_ids: tuple[str, ...]
    allowed_relations: tuple[RelationType, ...]
    max_hops: int = MAX_HOPS
    max_visited_nodes: int = MAX_VISITED_NODES
    max_scanned_edges: int = MAX_SCANNED_EDGES
    minimum_proposition_confidence: float = 0.5

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "seed_memory_ids",
            _canonical_strings("seed_memory_ids", self.seed_memory_ids, nonempty=True),
        )
        object.__setattr__(
            self,
            "target_memory_ids",
            _canonical_strings("target_memory_ids", self.target_memory_ids, nonempty=True),
        )
        for relation in self.allowed_relations:
            if not isinstance(relation, RelationType):
                raise ValueError("allowed_relations must contain only RelationType values")
        relations = tuple(sorted(set(self.allowed_relations), key=lambda item: item.value))
        if not relations:
            raise ValueError("allowed_relations must not be empty")
        object.__setattr__(self, "allowed_relations", relations)
        _positive_int("max_hops", self.max_hops, MAX_HOPS)
        _positive_int("max_visited_nodes", self.max_visited_nodes, MAX_VISITED_NODES)
        _positive_int("max_scanned_edges", self.max_scanned_edges, MAX_SCANNED_EDGES)
        if self.max_visited_nodes < len(self.seed_memory_ids):
            raise ValueError("max_visited_nodes must cover all seed_memory_ids")
        value = self.minimum_proposition_confidence
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            raise ValueError("minimum_proposition_confidence must be within [0, 1]")
        value = float(value)
        if not math.isfinite(value) or not 0.0 <= value <= 1.0:
            raise ValueError("minimum_proposition_confidence must be within [0, 1]")
        object.__setattr__(self, "minimum_proposition_confidence", value)


@dataclass(frozen=True, slots=True)
class RelationPathEvidence:
    target_memory_id: str
    memory_ids: tuple[str, ...]
    edge_ids: tuple[str, ...]
    evidence_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        require_nonempty("target_memory_id", self.target_memory_id)
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
        if self.target_memory_id != self.memory_ids[-1]:
            raise ValueError("target_memory_id must equal final memory_ids entry")
        object.__setattr__(
            self,
            "evidence_ids",
            _canonical_strings("evidence_ids", self.evidence_ids),
        )

    @property
    def hop_count(self) -> int:
        return len(self.edge_ids)


@dataclass(frozen=True, slots=True)
class TraversalResult:
    visited_memory_ids: tuple[str, ...]
    discovered_target_ids: tuple[str, ...]
    paths: tuple[RelationPathEvidence, ...]
    scanned_edge_count: int
    max_hop_reached: int
    termination: TraversalTermination

    def __post_init__(self) -> None:
        for value in self.visited_memory_ids:
            require_nonempty("visited_memory_id", value)
        if len(set(self.visited_memory_ids)) != len(self.visited_memory_ids):
            raise ValueError("visited_memory_ids must be unique")
        discovered = _canonical_strings(
            "discovered_target_ids", self.discovered_target_ids
        )
        object.__setattr__(self, "discovered_target_ids", discovered)
        if any(not isinstance(path, RelationPathEvidence) for path in self.paths):
            raise ValueError("paths must contain only RelationPathEvidence values")
        path_targets = tuple(sorted(path.target_memory_id for path in self.paths))
        if path_targets != discovered:
            raise ValueError("paths must exactly cover discovered_target_ids")
        if not isinstance(self.scanned_edge_count, int) or isinstance(self.scanned_edge_count, bool) or self.scanned_edge_count < 0:
            raise ValueError("scanned_edge_count must be a nonnegative integer")
        if not isinstance(self.max_hop_reached, int) or isinstance(self.max_hop_reached, bool) or self.max_hop_reached < 0:
            raise ValueError("max_hop_reached must be a nonnegative integer")
        if not isinstance(self.termination, TraversalTermination):
            raise ValueError("termination must be a TraversalTermination")
        if self.termination is TraversalTermination.TARGET_FOUND and not discovered:
            raise ValueError("TARGET_FOUND requires discovered targets and paths")
        if discovered and self.termination is not TraversalTermination.TARGET_FOUND:
            raise ValueError("discovered targets require TARGET_FOUND termination")
