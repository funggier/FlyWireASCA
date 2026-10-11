from __future__ import annotations

import pytest

from flywire_asca.contracts import RelationType
from flywire_asca.structural_routing import (
    RoutingInferenceSource,
    RoutingInferenceStatus,
    RoutingPolicy,
    StructuralRoutingRequest,
)
from flywire_asca.structural_routing.rules import normalize_routing_text, route_by_rules


@pytest.mark.parametrize(
    "query,relation",
    [
        ("Where does Ada work?", RelationType.WORKS_AT),
        ("Alex คนนี้ทำงานที่ไหน?", RelationType.WORKS_AT),
        ("What caused this failure?", RelationType.CAUSED_BY),
        ("เหตุนี้เกิดจากอะไร?", RelationType.CAUSED_BY),
        ("Which event happened after Alpha?", RelationType.OCCURRED_BEFORE),
        ("เหตุการณ์นี้เกิดก่อนเหตุการณ์ใด?", RelationType.OCCURRED_BEFORE),
        ("Which system is this part of?", RelationType.PART_OF),
        ("ชิ้นนี้เป็นส่วนหนึ่งของระบบใด?", RelationType.PART_OF),
        ("What is this used for?", RelationType.USED_FOR),
        ("เครื่องมือนี้ใช้สำหรับอะไร?", RelationType.USED_FOR),
    ],
)
def test_rule_router_recognizes_each_relation_family_in_english_and_thai(query, relation):
    result = route_by_rules(StructuralRoutingRequest("req", query))
    assert result.policy is RoutingPolicy.RULE_ONLY
    assert result.status is RoutingInferenceStatus.DECIDED_RELATIONAL
    assert result.source is RoutingInferenceSource.RULE
    assert result.structural_need.required_relations == (relation,)
    assert result.structural_need.requires_path_provenance is True
    assert result.model_invoked is False
    assert result.rule_evidence_ids == (f"rule:relation:{relation.value.replace('_', '-')}",)


@pytest.mark.parametrize(
    "query",
    [
        "What cause is stated directly?",
        "สาเหตุที่ระบุไว้โดยตรงคืออะไร?",
        "What part of the cause is directly stated?",
    ],
)
def test_direct_recall_marker_wins_before_relation_cues(query):
    result = route_by_rules(StructuralRoutingRequest("req", query))
    assert result.status is RoutingInferenceStatus.DECIDED_NON_RELATIONAL
    assert result.source is RoutingInferenceSource.RULE
    assert result.structural_need.active is False
    assert result.rule_evidence_ids == ("rule:direct:stated-directly",)


@pytest.mark.parametrize(
    "query",
    [
        "Identify this Alex's employer.",
        "Ada สังกัดบริษัทใด?",
        "คาลิเปอร์มีหน้าที่อะไร?",
    ],
)
def test_conservative_paraphrases_abstain_instead_of_guessing(query):
    result = route_by_rules(StructuralRoutingRequest("req", query))
    assert result.status is RoutingInferenceStatus.ABSTAINED
    assert result.source is RoutingInferenceSource.FAIL_CLOSED
    assert result.structural_need.active is False
    assert result.rule_evidence_ids == ()


def test_normalization_is_nfkc_casefolded_and_whitespace_collapsed():
    assert normalize_routing_text("  ＷＨＥＲＥ   does\tAda   work?  ") == "where does ada work?"
    result = route_by_rules(
        StructuralRoutingRequest("req", "  ＷＨＥＲＥ   does\tAda   work?  ")
    )
    assert result.structural_need.required_relations == (RelationType.WORKS_AT,)


def test_mixed_language_query_can_emit_sorted_relation_union():
    result = route_by_rules(
        StructuralRoutingRequest(
            "req",
            "What caused this component และมันเป็นส่วนหนึ่งของระบบใด?",
        )
    )
    assert result.status is RoutingInferenceStatus.DECIDED_RELATIONAL
    assert result.structural_need.required_relations == (
        RelationType.CAUSED_BY,
        RelationType.PART_OF,
    )
    assert result.rule_evidence_ids == (
        "rule:relation:caused-by",
        "rule:relation:part-of",
    )


def test_same_name_language_does_not_infer_identity_relations():
    result = route_by_rules(
        StructuralRoutingRequest("req", "Do these two people have the same name?")
    )
    assert result.status is RoutingInferenceStatus.ABSTAINED
    assert RelationType.SAME_NAME not in result.structural_need.required_relations
    assert RelationType.SAME_PERSON not in result.structural_need.required_relations


def test_directly_stated_variant_is_also_a_strong_negative():
    result = route_by_rules(
        StructuralRoutingRequest("req", "Which cause is directly stated here?")
    )
    assert result.status is RoutingInferenceStatus.DECIDED_NON_RELATIONAL
    assert result.rule_evidence_ids == ("rule:direct:stated-directly",)


def test_thai_told_directly_variant_is_a_strong_negative():
    result = route_by_rules(
        StructuralRoutingRequest("req", "ข้อใดบอกไว้โดยตรงในข้อความนี้?")
    )
    assert result.status is RoutingInferenceStatus.DECIDED_NON_RELATIONAL
    assert result.rule_evidence_ids == ("rule:direct:stated-directly",)
