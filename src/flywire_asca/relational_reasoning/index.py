from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass

from flywire_asca.contracts import AssociationEdge, MemoryRecord

from .models import (
    RelationPathEvidence,
    TraversalRequest,
    TraversalResult,
    TraversalTermination,
)


@dataclass(frozen=True, slots=True)
class _PathState:
    memory_ids: tuple[str, ...]
    edge_ids: tuple[str, ...]
    evidence_ids: tuple[str, ...]


class BoundedRelationIndex:
    def __init__(
        self,
        memories: Iterable[MemoryRecord],
        edges: Iterable[AssociationEdge],
    ) -> None:
        memory_tuple = tuple(memories)
        if any(not isinstance(item, MemoryRecord) for item in memory_tuple):
            raise ValueError("memories must contain only MemoryRecord values")
        memory_ids = tuple(item.memory_id for item in memory_tuple)
        if len(set(memory_ids)) != len(memory_ids):
            raise ValueError("duplicate memory_id values are not allowed")
        known = set(memory_ids)

        edge_tuple = tuple(edges)
        if any(not isinstance(item, AssociationEdge) for item in edge_tuple):
            raise ValueError("edges must contain only AssociationEdge values")
        edge_ids = tuple(item.edge_id for item in edge_tuple)
        if len(set(edge_ids)) != len(edge_ids):
            raise ValueError("duplicate edge_id values are not allowed")
        for edge in edge_tuple:
            if edge.source_id not in known:
                raise ValueError(f"edge {edge.edge_id} has unknown source_id {edge.source_id}")
            if edge.target_id not in known:
                raise ValueError(f"edge {edge.edge_id} has unknown target_id {edge.target_id}")

        outgoing: dict[str, list[AssociationEdge]] = defaultdict(list)
        for edge in edge_tuple:
            outgoing[edge.source_id].append(edge)

        self._memory_ids = frozenset(memory_ids)
        self._outgoing = {
            source: tuple(
                sorted(
                    values,
                    key=lambda edge: (
                        -edge.activation_weight,
                        -edge.proposition_confidence,
                        edge.edge_id,
                    ),
                )
            )
            for source, values in outgoing.items()
        }

    def traverse(self, request: TraversalRequest) -> TraversalResult:
        if not isinstance(request, TraversalRequest):
            raise ValueError("request must be a TraversalRequest")
        for memory_id in request.seed_memory_ids:
            if memory_id not in self._memory_ids:
                raise ValueError(f"unknown seed memory_id {memory_id}")
        for memory_id in request.target_memory_ids:
            if memory_id not in self._memory_ids:
                raise ValueError(f"unknown target memory_id {memory_id}")

        targets = set(request.target_memory_ids)
        visited_order = list(request.seed_memory_ids)
        visited = set(visited_order)
        path_by_memory = {
            memory_id: _PathState((memory_id,), (), ())
            for memory_id in request.seed_memory_ids
        }
        found = targets.intersection(visited)
        if found:
            paths = tuple(
                RelationPathEvidence(
                    target_memory_id=target,
                    memory_ids=path_by_memory[target].memory_ids,
                    edge_ids=path_by_memory[target].edge_ids,
                    evidence_ids=path_by_memory[target].evidence_ids,
                )
                for target in sorted(found)
            )
            return TraversalResult(
                tuple(visited_order),
                tuple(sorted(found)),
                paths,
                0,
                0,
                TraversalTermination.TARGET_FOUND,
            )

        frontier = list(request.seed_memory_ids)
        scanned = 0
        max_hop_reached = 0

        for hop in range(1, request.max_hops + 1):
            next_frontier: list[str] = []
            for source_id in frontier:
                source_path = path_by_memory[source_id]
                for edge in self._outgoing.get(source_id, ()):
                    if scanned >= request.max_scanned_edges:
                        return TraversalResult(
                            tuple(visited_order),
                            (),
                            (),
                            scanned,
                            max_hop_reached,
                            TraversalTermination.EDGE_BUDGET_EXHAUSTED,
                        )
                    scanned += 1
                    if edge.relation not in request.allowed_relations:
                        continue
                    if edge.proposition_confidence < request.minimum_proposition_confidence:
                        continue
                    target_id = edge.target_id
                    if target_id in visited:
                        continue
                    if len(visited) >= request.max_visited_nodes:
                        return TraversalResult(
                            tuple(visited_order),
                            (),
                            (),
                            scanned,
                            max_hop_reached,
                            TraversalTermination.NODE_BUDGET_EXHAUSTED,
                        )
                    visited.add(target_id)
                    visited_order.append(target_id)
                    next_frontier.append(target_id)
                    max_hop_reached = hop
                    combined_evidence = tuple(
                        sorted(set(source_path.evidence_ids + edge.evidence_ids))
                    )
                    path_by_memory[target_id] = _PathState(
                        source_path.memory_ids + (target_id,),
                        source_path.edge_ids + (edge.edge_id,),
                        combined_evidence,
                    )
                    found = targets.intersection(visited)
                    if found == targets:
                        paths = tuple(
                            RelationPathEvidence(
                                target_memory_id=target,
                                memory_ids=path_by_memory[target].memory_ids,
                                edge_ids=path_by_memory[target].edge_ids,
                                evidence_ids=path_by_memory[target].evidence_ids,
                            )
                            for target in sorted(found)
                        )
                        return TraversalResult(
                            tuple(visited_order),
                            tuple(sorted(found)),
                            paths,
                            scanned,
                            max_hop_reached,
                            TraversalTermination.TARGET_FOUND,
                        )
            if not next_frontier:
                return TraversalResult(
                    tuple(visited_order),
                    (),
                    (),
                    scanned,
                    max_hop_reached,
                    TraversalTermination.FRONTIER_EXHAUSTED,
                )
            frontier = next_frontier

        return TraversalResult(
            tuple(visited_order),
            (),
            (),
            scanned,
            max_hop_reached,
            TraversalTermination.HOP_BUDGET_EXHAUSTED,
        )
