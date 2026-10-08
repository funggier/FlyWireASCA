from __future__ import annotations

import math

import pytest

from flywire_asca.contracts import (
    AssociationEdge,
    Cue,
    CueKind,
    EvidenceRef,
    MemoryKind,
    MemoryRecord,
    RelationType,
    RetrievalState,
)


def test_contract_enums_freeze_required_v01_vocabulary():
    assert [state.value for state in RetrievalState] == [
        "UNFAMILIAR",
        "FAMILIAR",
        "KNOWN_BUT_NOT_RECALLED",
        "PARTIAL_RECALL",
        "RECALLED",
        "CONFLICTING_RECALL",
        "INSUFFICIENT_EVIDENCE",
    ]
    assert RelationType.SAME_PERSON.value == "same_person"
    assert RelationType.SAME_NAME.value == "same_name"
    assert RelationType.SIMILAR_TO.value == "similar_to"
    assert RelationType.SAME_PERSON is not RelationType.SAME_NAME


def test_evidence_and_memory_probability_fields_validate_closed_unit_interval():
    evidence = EvidenceRef("ev-1", "fixture://source", 0.8)
    memory = MemoryRecord(
        memory_id="mem-1",
        kind=MemoryKind.SEMANTIC,
        content_ref="fixture://memory/1",
        proposition_confidence=0.6,
        evidence_ids=("ev-1",),
    )
    cue = Cue(
        cue_id="cue-1",
        kind=CueKind.TEXT,
        value="บริษัทที่ A ย้ายไปปีที่แล้ว",
        confidence=0.7,
        evidence_ids=("ev-1",),
    )
    assert evidence.confidence == 0.8
    assert memory.proposition_confidence == 0.6
    assert cue.confidence == 0.7

    with pytest.raises(ValueError, match="confidence"):
        EvidenceRef("ev-bad", "fixture://source", 1.01)
    with pytest.raises(ValueError, match="proposition_confidence"):
        MemoryRecord("mem-bad", MemoryKind.SEMANTIC, "fixture://m", -0.01)
    with pytest.raises(ValueError, match="confidence"):
        Cue("cue-bad", CueKind.TEXT, "x", float("nan"))


def test_contract_ids_and_references_must_be_nonempty_and_unique_where_repeated():
    with pytest.raises(ValueError, match="evidence_id"):
        EvidenceRef("", "fixture://source", 1.0)
    with pytest.raises(ValueError, match="memory_id"):
        MemoryRecord("", MemoryKind.EPISODIC, "fixture://m", 1.0)
    with pytest.raises(ValueError, match="evidence_ids"):
        Cue(
            "cue-1",
            CueKind.ENTITY,
            "A",
            1.0,
            evidence_ids=("ev-1", "ev-1"),
        )


def test_association_keeps_activation_strength_separate_from_truth_confidence():
    edge = AssociationEdge(
        edge_id="edge-1",
        source_id="mem-person-a",
        target_id="mem-name-a",
        relation=RelationType.SAME_NAME,
        activation_weight=0.95,
        proposition_confidence=0.25,
        evidence_ids=("ev-1",),
    )
    assert edge.activation_weight == 0.95
    assert edge.proposition_confidence == 0.25
    assert edge.relation is RelationType.SAME_NAME

    inhibitory = AssociationEdge(
        edge_id="edge-2",
        source_id="mem-a",
        target_id="mem-b",
        relation=RelationType.SIMILAR_TO,
        activation_weight=-0.4,
        proposition_confidence=0.9,
    )
    assert inhibitory.activation_weight == -0.4

    with pytest.raises(ValueError, match="activation_weight"):
        AssociationEdge(
            "edge-bad",
            "mem-a",
            "mem-b",
            RelationType.SIMILAR_TO,
            math.inf,
            0.5,
        )


def test_public_memory_contracts_are_immutable():
    memory = MemoryRecord(
        "mem-1",
        MemoryKind.SEMANTIC,
        "fixture://memory/1",
        0.5,
    )
    with pytest.raises((AttributeError, TypeError)):
        memory.proposition_confidence = 0.9  # type: ignore[misc]
