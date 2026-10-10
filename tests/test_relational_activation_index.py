from __future__ import annotations

from flywire_asca.contracts import AssociationEdge, MemoryKind, MemoryRecord, RelationType
from flywire_asca.relational_activation import (
    ExpansionRequest,
    ExpansionTermination,
    TargetFreeRelationIndex,
)


def _memory(memory_id: str) -> MemoryRecord:
    return MemoryRecord(memory_id, MemoryKind.SEMANTIC, f"content:{memory_id}", 1.0)


def _edge(
    edge_id: str,
    source: str,
    target: str,
    relation: RelationType,
    *,
    weight: float = 0.8,
    confidence: float = 0.9,
) -> AssociationEdge:
    return AssociationEdge(
        edge_id,
        source,
        target,
        relation,
        weight,
        confidence,
        (f"evidence:{edge_id}",),
    )


def test_target_free_expansion_reaches_two_hops_with_exact_provenance():
    memories = tuple(_memory(value) for value in ("seed", "mid", "whole"))
    index = TargetFreeRelationIndex(
        memories,
        (
            _edge("e1", "seed", "mid", RelationType.PART_OF),
            _edge("e2", "mid", "whole", RelationType.PART_OF),
        ),
    )
    result = index.expand(
        ExpansionRequest(("seed",), (RelationType.PART_OF,))
    )
    assert result.visited_memory_ids == ("seed", "mid", "whole")
    assert result.scanned_edge_count == 2
    assert result.max_hop_reached == 2
    assert result.termination is ExpansionTermination.FRONTIER_EXHAUSTED
    assert [path.reached_memory_id for path in result.paths] == ["mid", "whole"]
    assert result.paths[-1].memory_ids == ("seed", "mid", "whole")
    assert result.paths[-1].edge_ids == ("e1", "e2")
    assert result.paths[-1].evidence_ids == ("evidence:e1", "evidence:e2")


def test_target_free_expansion_is_cycle_safe_and_has_no_duplicate_visits():
    memories = tuple(_memory(value) for value in ("seed", "mid"))
    index = TargetFreeRelationIndex(
        memories,
        (
            _edge("forward", "seed", "mid", RelationType.PART_OF),
            _edge("back", "mid", "seed", RelationType.PART_OF),
        ),
    )
    result = index.expand(
        ExpansionRequest(("seed",), (RelationType.PART_OF,))
    )
    assert result.visited_memory_ids == ("seed", "mid")
    assert len(set(result.visited_memory_ids)) == 2
    assert result.scanned_edge_count == 2


def test_target_free_expansion_filters_relation_and_confidence():
    memories = tuple(_memory(value) for value in ("seed", "wrong", "low"))
    index = TargetFreeRelationIndex(
        memories,
        (
            _edge("wrong", "seed", "wrong", RelationType.PART_OF),
            _edge(
                "low",
                "seed",
                "low",
                RelationType.WORKS_AT,
                confidence=0.49,
            ),
        ),
    )
    result = index.expand(
        ExpansionRequest(
            ("seed",),
            (RelationType.WORKS_AT,),
            minimum_proposition_confidence=0.5,
        )
    )
    assert result.visited_memory_ids == ("seed",)
    assert result.scanned_edge_count == 2
    assert result.paths == ()


def test_target_free_expansion_preserves_a012_edge_ordering():
    memories = tuple(_memory(value) for value in ("seed", "a", "b", "c"))
    index = TargetFreeRelationIndex(
        memories,
        (
            _edge("edge-c", "seed", "c", RelationType.SIMILAR_TO, weight=0.7),
            _edge("edge-b", "seed", "b", RelationType.SIMILAR_TO, weight=0.9, confidence=0.8),
            _edge("edge-a", "seed", "a", RelationType.SIMILAR_TO, weight=0.9, confidence=0.95),
        ),
    )
    result = index.expand(
        ExpansionRequest(("seed",), (RelationType.SIMILAR_TO,))
    )
    assert result.visited_memory_ids == ("seed", "a", "b", "c")


def test_target_free_expansion_honors_edge_budget_without_inventing_nodes():
    memories = tuple(_memory(value) for value in ("seed", "a", "b"))
    index = TargetFreeRelationIndex(
        memories,
        (
            _edge("a", "seed", "a", RelationType.SIMILAR_TO),
            _edge("b", "seed", "b", RelationType.SIMILAR_TO),
        ),
    )
    result = index.expand(
        ExpansionRequest(
            ("seed",),
            (RelationType.SIMILAR_TO,),
            max_scanned_edges=1,
        )
    )
    assert result.scanned_edge_count == 1
    assert result.visited_memory_ids == ("seed", "a")
    assert result.termination is ExpansionTermination.EDGE_BUDGET_EXHAUSTED
