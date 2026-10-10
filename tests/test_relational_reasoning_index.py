from __future__ import annotations

from dataclasses import replace

import pytest

from flywire_asca.contracts import (
    AssociationEdge,
    MemoryKind,
    MemoryRecord,
    RelationType,
)
from flywire_asca.relational_reasoning import (
    BoundedRelationIndex,
    TraversalRequest,
    TraversalTermination,
)


def _memory(memory_id: str) -> MemoryRecord:
    return MemoryRecord(memory_id, MemoryKind.SEMANTIC, f"content:{memory_id}", 0.9)


def _edge(
    edge_id: str,
    source_id: str,
    target_id: str,
    relation: RelationType,
    *,
    weight: float = 0.8,
    confidence: float = 0.9,
    evidence_ids: tuple[str, ...] = (),
) -> AssociationEdge:
    return AssociationEdge(
        edge_id,
        source_id,
        target_id,
        relation,
        weight,
        confidence,
        evidence_ids,
    )


def _request(
    *,
    seeds=("seed",),
    targets=("target",),
    relations=(RelationType.WORKS_AT,),
    max_hops=3,
    max_nodes=8,
    max_edges=32,
    confidence=0.5,
) -> TraversalRequest:
    return TraversalRequest(
        seed_memory_ids=seeds,
        target_memory_ids=targets,
        allowed_relations=relations,
        max_hops=max_hops,
        max_visited_nodes=max_nodes,
        max_scanned_edges=max_edges,
        minimum_proposition_confidence=confidence,
    )


def test_index_rejects_duplicate_ids_and_unknown_endpoints():
    memories = (_memory("seed"), _memory("target"))
    duplicate = (
        _edge("e1", "seed", "target", RelationType.WORKS_AT),
        _edge("e1", "seed", "target", RelationType.WORKS_AT),
    )
    with pytest.raises(ValueError, match="duplicate edge_id"):
        BoundedRelationIndex(memories, duplicate)

    with pytest.raises(ValueError, match="unknown target_id"):
        BoundedRelationIndex(
            memories,
            (_edge("e2", "seed", "missing", RelationType.WORKS_AT),),
        )


def test_directed_relation_traversal_records_exact_path_and_evidence():
    memories = (_memory("seed"), _memory("target"))
    index = BoundedRelationIndex(
        memories,
        (
            _edge(
                "e-work",
                "seed",
                "target",
                RelationType.WORKS_AT,
                evidence_ids=("ev-work",),
            ),
        ),
    )
    result = index.traverse(_request())
    assert result.termination is TraversalTermination.TARGET_FOUND
    assert result.discovered_target_ids == ("target",)
    assert result.visited_memory_ids == ("seed", "target")
    assert result.scanned_edge_count == 1
    assert result.max_hop_reached == 1
    assert result.paths[0].memory_ids == ("seed", "target")
    assert result.paths[0].edge_ids == ("e-work",)
    assert result.paths[0].evidence_ids == ("ev-work",)

    reverse = index.traverse(
        _request(seeds=("target",), targets=("seed",))
    )
    assert reverse.discovered_target_ids == ()
    assert reverse.termination is TraversalTermination.FRONTIER_EXHAUSTED


def test_relation_allowlist_and_confidence_are_fail_closed():
    memories = (_memory("seed"), _memory("target"))
    edge = _edge(
        "e",
        "seed",
        "target",
        RelationType.PART_OF,
        confidence=0.49,
    )
    index = BoundedRelationIndex(memories, (edge,))

    wrong_relation = index.traverse(
        _request(relations=(RelationType.WORKS_AT,), confidence=0.4)
    )
    assert wrong_relation.discovered_target_ids == ()

    low_confidence = index.traverse(
        _request(relations=(RelationType.PART_OF,), confidence=0.5)
    )
    assert low_confidence.discovered_target_ids == ()


def test_two_hop_path_is_bounded_and_cycle_safe():
    memories = tuple(_memory(item) for item in ("seed", "mid", "target"))
    index = BoundedRelationIndex(
        memories,
        (
            _edge("e1", "seed", "mid", RelationType.PART_OF),
            _edge("e2", "mid", "seed", RelationType.PART_OF),
            _edge("e3", "mid", "target", RelationType.PART_OF),
        ),
    )
    result = index.traverse(
        _request(relations=(RelationType.PART_OF,), max_hops=2)
    )
    assert result.discovered_target_ids == ("target",)
    assert result.paths[0].memory_ids == ("seed", "mid", "target")
    assert result.paths[0].edge_ids == ("e1", "e3")
    assert result.visited_memory_ids == ("seed", "mid", "target")
    assert len(result.visited_memory_ids) == len(set(result.visited_memory_ids))

    hop_limited = index.traverse(
        _request(relations=(RelationType.PART_OF,), max_hops=1)
    )
    assert hop_limited.discovered_target_ids == ()
    assert hop_limited.termination is TraversalTermination.HOP_BUDGET_EXHAUSTED


def test_node_and_edge_budgets_terminate_explicitly():
    memories = tuple(_memory(item) for item in ("seed", "a", "b", "target"))
    index = BoundedRelationIndex(
        memories,
        (
            _edge("e-a", "seed", "a", RelationType.WORKS_AT, weight=0.9),
            _edge("e-b", "seed", "b", RelationType.WORKS_AT, weight=0.8),
            _edge("e-target", "a", "target", RelationType.WORKS_AT),
        ),
    )

    node_limited = index.traverse(_request(max_nodes=1))
    assert node_limited.termination is TraversalTermination.NODE_BUDGET_EXHAUSTED

    edge_limited = index.traverse(_request(max_edges=1))
    assert edge_limited.termination is TraversalTermination.EDGE_BUDGET_EXHAUSTED


def test_frontier_priority_is_weight_then_confidence_then_edge_id():
    memories = tuple(_memory(item) for item in ("seed", "a", "b", "target"))
    index = BoundedRelationIndex(
        memories,
        (
            _edge("z", "seed", "a", RelationType.WORKS_AT, weight=0.7, confidence=0.8),
            _edge("a", "seed", "b", RelationType.WORKS_AT, weight=0.9, confidence=0.7),
            _edge("to-target", "b", "target", RelationType.WORKS_AT),
        ),
    )
    result = index.traverse(_request(max_nodes=3))
    assert result.visited_memory_ids[:2] == ("seed", "b")
