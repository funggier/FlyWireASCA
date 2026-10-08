from __future__ import annotations

from dataclasses import dataclass

from .enums import ObservationKind
from .validation import require_nonempty, require_unique_nonempty


@dataclass(frozen=True, slots=True)
class ProcedureRef:
    procedure_id: str
    name: str
    version: str
    explanation_memory_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        require_nonempty("procedure_id", self.procedure_id)
        require_nonempty("name", self.name)
        require_nonempty("version", self.version)
        require_unique_nonempty("explanation_memory_ids", self.explanation_memory_ids)


@dataclass(frozen=True, slots=True)
class Observation:
    observation_id: str
    kind: ObservationKind
    payload_ref: str
    expected_match: bool | None = None
    evidence_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        require_nonempty("observation_id", self.observation_id)
        require_nonempty("payload_ref", self.payload_ref)
        if self.expected_match is not None and not isinstance(self.expected_match, bool):
            raise ValueError("expected_match must be bool or None")
        require_unique_nonempty("evidence_ids", self.evidence_ids)
