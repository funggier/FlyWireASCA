from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass

from flywire_asca.contracts import AssociationEdge, MemoryRecord

from .models import (
    ExpansionPathEvidence,
    ExpansionRequest,
    ExpansionResult,
    ExpansionTermination,
)


@dataclass(frozen=True, slots=True)
class _PathState:
    memory_ids: tuple[str, ...]
    edge_ids: tuple[str, ...]
    evidence_ids: tuple[str, ...]


class TargetFreeRelationIndex:
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
                raise ValueError(
                    f"edge {edge.edge_id} has unknown source_id {edge.source_id}"
                )
            if edge.target_id not in known:
                raise ValueError(
                    f"edge {edge.edge_id} has unknown target_id {edge.target_id}"
                )

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

    def _result(
        self,
        *,
        seeds: tuple[str, ...],
        visited_order: list[str],
        path_by_memory: dict[str, _PathState],
        scanned: int,
        max_hop_reached: int,
        termination: ExpansionTermination,
    ) -> ExpansionResult:
        seed_set = set(seeds)
        paths = tuple(
            ExpansionPathEvidence(
                reached_memory_id=memory_id,
                memory_ids=path_by_memory[memory_id].memory_ids,
                edge_ids=path_by_memory[memory_id].edge_ids,
                evidence_ids=path_by_memory[memory_id].evidence_ids,
            )
            for memory_id in visited_order
            if memory_id not in seed_set
        )
        return ExpansionResult(
            seed_memory_ids=seeds,
            visited_memory_ids=tuple(visited_order),
            paths=paths,
            scanned_edge_count=scanned,
            max_hop_reached=max_hop_reached,
            termination=termination,
        )

    def expand(self, request: ExpansionRequest) -> ExpansionResult:
        if not isinstance(request, ExpansionRequest):
            raise ValueError("request must be an ExpansionRequest")
        for memory_id in request.seed_memory_ids:
            if memory_id not in self._memory_ids:
                raise ValueError(f"unknown seed memory_id {memory_id}")

        seeds = request.seed_memory_ids
        visited_order = list(seeds)
        visited = set(seeds)
        path_by_memory = {
            memory_id: _PathState((memory_id,), (), ())
            for memory_id in seeds
        }
        frontier = list(seeds)
        scanned = 0
        max_hop_reached = 0

        for hop in range(1, request.max_hops + 1):
            next_frontier: list[str] = []
            for source_id in frontier:
                source_path = path_by_memory[source_id]
                for edge in self._outgoing.get(source_id, ()):
                    if scanned >= request.max_scanned_edges:
                        return self._result(
                            seeds=seeds,
                            visited_order=visited_order,
                            path_by_memory=path_by_memory,
                            scanned=scanned,
                            max_hop_reached=max_hop_reached,
                            termination=ExpansionTermination.EDGE_BUDGET_EXHAUSTED,
                        )
                    scanned += 1
                    if edge.relation not in request.allowed_relations:
                        continue
                    if (
                        edge.proposition_confidence
                        < request.minimum_proposition_confidence
                    ):
                        continue
                    target_id = edge.target_id
                    if target_id in visited:
                        continue
                    if len(visited) >= request.max_visited_nodes:
                        return self._result(
                            seeds=seeds,
                            visited_order=visited_order,
                            path_by_memory=path_by_memory,
                            scanned=scanned,
                            max_hop_reached=max_hop_reached,
                            termination=ExpansionTermination.NODE_BUDGET_EXHAUSTED,
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
            if not next_frontier:
                return self._result(
                    seeds=seeds,
                    visited_order=visited_order,
                    path_by_memory=path_by_memory,
                    scanned=scanned,
                    max_hop_reached=max_hop_reached,
                    termination=ExpansionTermination.FRONTIER_EXHAUSTED,
                )
            frontier = next_frontier

        return self._result(
            seeds=seeds,
            visited_order=visited_order,
            path_by_memory=path_by_memory,
            scanned=scanned,
            max_hop_reached=max_hop_reached,
            termination=ExpansionTermination.HOP_BUDGET_EXHAUSTED,
        )
