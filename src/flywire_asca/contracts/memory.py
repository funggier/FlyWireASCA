from __future__ import annotations

from dataclasses import dataclass

from .enums import CueKind, MemoryKind, RelationType
from .validation import (
    require_finite,
    require_nonempty,
    require_probability,
    require_unique_nonempty,
)


@dataclass(frozen=True, slots=True)
class EvidenceRef:
    evidence_id: str
    source: str
    confidence: float

    def __post_init__(self) -> None:
        require_nonempty("evidence_id", self.evidence_id)
        require_nonempty("source", self.source)
        require_probability("confidence", self.confidence)


@dataclass(frozen=True, slots=True)
class Cue:
    cue_id: str
    kind: CueKind
    value: str
    confidence: float
    evidence_ids: tuple[str, ...] = ()
    context_tags: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        require_nonempty("cue_id", self.cue_id)
        require_nonempty("value", self.value)
        require_probability("confidence", self.confidence)
        require_unique_nonempty("evidence_ids", self.evidence_ids)
        require_unique_nonempty("context_tags", self.context_tags)


@dataclass(frozen=True, slots=True)
class MemoryRecord:
    memory_id: str
    kind: MemoryKind
    content_ref: str
    proposition_confidence: float
    evidence_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        require_nonempty("memory_id", self.memory_id)
        require_nonempty("content_ref", self.content_ref)
        require_probability("proposition_confidence", self.proposition_confidence)
        require_unique_nonempty("evidence_ids", self.evidence_ids)


@dataclass(frozen=True, slots=True)
class AssociationEdge:
    edge_id: str
    source_id: str
    target_id: str
    relation: RelationType
    activation_weight: float
    proposition_confidence: float
    evidence_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        require_nonempty("edge_id", self.edge_id)
        require_nonempty("source_id", self.source_id)
        require_nonempty("target_id", self.target_id)
        require_finite("activation_weight", self.activation_weight)
        require_probability("proposition_confidence", self.proposition_confidence)
        require_unique_nonempty("evidence_ids", self.evidence_ids)
