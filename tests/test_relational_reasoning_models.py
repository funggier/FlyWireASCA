from __future__ import annotations

from dataclasses import replace

import pytest

from flywire_asca.contracts import RelationType
from flywire_asca.relational_reasoning import (
    ArchitectureDecision,
    RelationPathEvidence,
    TraversalRequest,
    TraversalResult,
    TraversalTermination,
)


def test_traversal_request_canonicalizes_ids_relations_and_validates_bounds():
    request = TraversalRequest(
        seed_memory_ids=("seed-b", "seed-a", "seed-a"),
        target_memory_ids=("target",),
        allowed_relations=(RelationType.WORKS_AT, RelationType.PART_OF, RelationType.WORKS_AT),
        max_hops=2,
        max_visited_nodes=7,
        max_scanned_edges=20,
        minimum_proposition_confidence=0.5,
    )
    assert request.seed_memory_ids == ("seed-a", "seed-b")
    assert request.target_memory_ids == ("target",)
    assert request.allowed_relations == (RelationType.PART_OF, RelationType.WORKS_AT)

    with pytest.raises(ValueError, match="max_hops"):
        replace(request, max_hops=0)
    with pytest.raises(ValueError, match="max_hops"):
        replace(request, max_hops=4)
    with pytest.raises(ValueError, match="max_visited_nodes"):
        replace(request, max_visited_nodes=0)
    with pytest.raises(ValueError, match="max_visited_nodes"):
        replace(request, max_visited_nodes=9)
    with pytest.raises(ValueError, match="max_scanned_edges"):
        replace(request, max_scanned_edges=33)
    with pytest.raises(ValueError, match="minimum_proposition_confidence"):
        replace(request, minimum_proposition_confidence=1.1)


def test_path_evidence_requires_exact_hop_shape_and_unique_evidence():
    path = RelationPathEvidence(
        target_memory_id="target",
        memory_ids=("seed", "mid", "target"),
        edge_ids=("e1", "e2"),
        evidence_ids=("ev2", "ev1", "ev1"),
    )
    assert path.hop_count == 2
    assert path.evidence_ids == ("ev1", "ev2")

    with pytest.raises(ValueError, match="edge_ids"):
        replace(path, edge_ids=("e1",))


def test_traversal_result_rejects_count_and_target_inconsistency():
    path = RelationPathEvidence("target", ("seed", "target"), ("e1",), ("ev1",))
    result = TraversalResult(
        visited_memory_ids=("seed", "target"),
        discovered_target_ids=("target",),
        paths=(path,),
        scanned_edge_count=1,
        max_hop_reached=1,
        termination=TraversalTermination.TARGET_FOUND,
    )
    assert result.discovered_target_ids == ("target",)

    with pytest.raises(ValueError, match="TARGET_FOUND"):
        replace(result, discovered_target_ids=(), paths=())
    with pytest.raises(ValueError, match="paths"):
        replace(result, paths=())


def test_architecture_decision_vocabulary_is_exact():
    assert tuple(item.value for item in ArchitectureDecision) == (
        "EXPLICIT_RELATION_TRAVERSAL_JUSTIFIED",
        "VECTOR_METADATA_REMAINS_SUFFICIENT",
        "MIXED",
    )
