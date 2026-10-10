from __future__ import annotations

from dataclasses import fields

import pytest

from flywire_asca.contracts import RelationType
from flywire_asca.relational_activation import (
    ExpansionRequest,
    HybridRecallRequest,
    RelationalActivationPolicy,
    StructuralNeed,
)
from flywire_asca.vector_memory import VectorMemoryQuery


def test_structural_need_is_typed_canonical_and_target_free():
    need = StructuralNeed(
        (RelationType.WORKS_AT, RelationType.CAUSED_BY, RelationType.WORKS_AT),
        requires_path_provenance=True,
    )
    assert need.required_relations == (
        RelationType.CAUSED_BY,
        RelationType.WORKS_AT,
    )
    assert need.active is True
    assert all("target" not in field.name.lower() for field in fields(StructuralNeed))


def test_structural_need_rejects_provenance_without_relation_semantics():
    with pytest.raises(ValueError, match="requires_path_provenance"):
        StructuralNeed((), requires_path_provenance=True)


def test_expansion_request_has_no_target_or_expected_answer_field():
    names = {field.name for field in fields(ExpansionRequest)}
    assert not any("target" in name or "expected" in name for name in names)
    request = ExpansionRequest(
        ("seed-b", "seed-a"),
        (RelationType.PART_OF,),
    )
    assert request.seed_memory_ids == ("seed-a", "seed-b")


def test_hybrid_recall_request_has_no_target_or_expected_answer_field():
    names = {field.name for field in fields(HybridRecallRequest)}
    assert not any("target" in name or "expected" in name for name in names)
    request = HybridRecallRequest(
        request_id="req-1",
        policy=RelationalActivationPolicy.SIGNAL_GATED_RELATION,
        vector_query=VectorMemoryQuery("q-1", "query"),
        structural_need=StructuralNeed((RelationType.WORKS_AT,), True),
    )
    assert request.structural_need.active is True


@pytest.mark.parametrize(
    "kwargs,match",
    (
        ({"max_hops": 4}, "max_hops"),
        ({"max_visited_nodes": 9}, "max_visited_nodes"),
        ({"max_scanned_edges": 33}, "max_scanned_edges"),
        ({"minimum_proposition_confidence": 1.1}, "minimum_proposition_confidence"),
    ),
)
def test_expansion_request_enforces_a012_ceiling(kwargs, match):
    with pytest.raises(ValueError, match=match):
        ExpansionRequest(
            ("seed",),
            (RelationType.PART_OF,),
            **kwargs,
        )
