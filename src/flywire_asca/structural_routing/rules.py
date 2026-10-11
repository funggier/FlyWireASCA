from __future__ import annotations

import re
import unicodedata

from flywire_asca.contracts import RelationType
from flywire_asca.relational_activation import StructuralNeed

from .models import (
    RoutingInferenceSource,
    RoutingInferenceStatus,
    RoutingPolicy,
    StructuralRoutingRequest,
    StructuralRoutingResult,
)


_WHERE_WORK = re.compile(r"\bwhere\b.*\bwork\b")

_RAW_DIRECT_MARKERS = (
    "stated directly",
    "directly stated",
    "ระบุไว้โดยตรง",
    "บอกไว้โดยตรง",
)

_RAW_RELATION_CUES: tuple[tuple[RelationType, tuple[str, ...]], ...] = (
    (RelationType.WORKS_AT, ("works at", "work for", "ทำงานที่", "ทำงานให้")),
    (
        RelationType.CAUSED_BY,
        ("what caused", "caused by", "cause of", "สาเหตุของ", "เกิดจาก"),
    ),
    (
        RelationType.OCCURRED_BEFORE,
        (
            "happened after",
            "happened before",
            "occurred after",
            "occurred before",
            "เกิดหลัง",
            "เกิดก่อน",
        ),
    ),
    (RelationType.PART_OF, ("part of", "เป็นส่วนหนึ่งของ")),
    (RelationType.USED_FOR, ("used for", "ใช้ทำอะไร", "ใช้สำหรับ")),
)


def normalize_routing_text(text: str) -> str:
    if not isinstance(text, str):
        raise ValueError("text must be a string")
    return " ".join(unicodedata.normalize("NFKC", text).casefold().split())


_DIRECT_MARKERS = tuple(
    normalize_routing_text(value) for value in _RAW_DIRECT_MARKERS
)
_RELATION_CUES = tuple(
    (relation, tuple(normalize_routing_text(cue) for cue in cues))
    for relation, cues in _RAW_RELATION_CUES
)


def _relational_result(
    request: StructuralRoutingRequest,
    relations: tuple[RelationType, ...],
) -> StructuralRoutingResult:
    return StructuralRoutingResult(
        request_id=request.request_id,
        policy=RoutingPolicy.RULE_ONLY,
        status=RoutingInferenceStatus.DECIDED_RELATIONAL,
        source=RoutingInferenceSource.RULE,
        structural_need=StructuralNeed(relations, requires_path_provenance=True),
        model_invoked=False,
        rule_evidence_ids=tuple(
            f"rule:relation:{relation.value.replace('_', '-')}"
            for relation in relations
        ),
    )


def route_by_rules(request: StructuralRoutingRequest) -> StructuralRoutingResult:
    if not isinstance(request, StructuralRoutingRequest):
        raise ValueError("request must be a StructuralRoutingRequest")

    text = normalize_routing_text(request.query_text)
    if any(marker in text for marker in _DIRECT_MARKERS):
        return StructuralRoutingResult(
            request_id=request.request_id,
            policy=RoutingPolicy.RULE_ONLY,
            status=RoutingInferenceStatus.DECIDED_NON_RELATIONAL,
            source=RoutingInferenceSource.RULE,
            structural_need=StructuralNeed(),
            model_invoked=False,
            rule_evidence_ids=("rule:direct:stated-directly",),
        )

    matched: set[RelationType] = set()
    if _WHERE_WORK.search(text):
        matched.add(RelationType.WORKS_AT)
    for relation, cues in _RELATION_CUES:
        if any(cue in text for cue in cues):
            matched.add(relation)

    if matched:
        ordered = tuple(sorted(matched, key=lambda relation: relation.value))
        return _relational_result(request, ordered)

    return StructuralRoutingResult(
        request_id=request.request_id,
        policy=RoutingPolicy.RULE_ONLY,
        status=RoutingInferenceStatus.ABSTAINED,
        source=RoutingInferenceSource.FAIL_CLOSED,
        structural_need=StructuralNeed(),
        model_invoked=False,
        rule_evidence_ids=(),
    )
