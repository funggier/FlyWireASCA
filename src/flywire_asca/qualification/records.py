"""Immutable normalized A011 records; importing this module executes no qualification."""
from __future__ import annotations

from dataclasses import dataclass, fields
from enum import Enum
import math
import re
from collections.abc import Mapping
from types import MappingProxyType, UnionType
from typing import TypeAlias, get_args, get_origin, get_type_hints, Union

JsonValue: TypeAlias = None | bool | int | float | str | Mapping[str, "JsonValue"] | tuple["JsonValue", ...]
JsonObject: TypeAlias = Mapping[str, JsonValue]


class QualificationError(ValueError):
    def __init__(self, code: str, message: str):
        self.code = code
        super().__init__(message)


class GateStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    BLOCKED = "BLOCKED"
    NOT_RUN = "NOT_RUN"


class EngineeringVerdict(str, Enum):
    ENGINEERING_QUALIFIED = "ENGINEERING_QUALIFIED"
    ENGINEERING_NOT_QUALIFIED = "ENGINEERING_NOT_QUALIFIED"
    QUALIFICATION_BLOCKED = "QUALIFICATION_BLOCKED"


class Scope(str, Enum):
    PORTABLE_ONLY = "PORTABLE_ONLY"
    FULL_SYSTEM = "FULL_SYSTEM"


class ResearchOutcome(str, Enum):
    SUPPORTED = "SUPPORTED"
    NOT_SUPPORTED = "NOT_SUPPORTED"


class EvidenceRole(str, Enum):
    PHYSICAL_PRIMARY = "PHYSICAL_PRIMARY"
    PORTABLE_PRIMARY = "PORTABLE_PRIMARY"
    PHYSICAL_SECONDARY = "PHYSICAL_SECONDARY"


class Freshness(str, Enum):
    FRESH_PORTABLE = "FRESH_PORTABLE"
    FRESH_PHYSICAL = "FRESH_PHYSICAL"


PORTABLE_GATE_IDS = (
    "P00_PROFILE_SOURCE", "P01_TESTS", "P02_ARCHITECTURE", "P03_REPOSITORY",
    "P04_A003", "P05_A008", "P06_A009", "P07_A010",
    "P08_FROZEN_AUDIT", "P09_PACK_VALIDATION",
)
PHYSICAL_GATE_IDS = (
    "H00_PREREQUISITES", "H01_A004", "H02_A005", "H03_A006",
    "H04_A007", "H05_A009", "H06_A010", "H07_FULL_VALIDATION",
)
RESEARCH_OUTCOMES = {
    "A006": ResearchOutcome.NOT_SUPPORTED, "A007": ResearchOutcome.SUPPORTED,
    "A008": ResearchOutcome.SUPPORTED, "A009": ResearchOutcome.SUPPORTED,
    "A010": ResearchOutcome.NOT_SUPPORTED,
}
REASON_CODES = frozenset((
    "PROFILE_DRIFT", "IDENTITY_DRIFT", "REPLAY_DRIFT", "EVIDENCE_INVALID",
    "SOURCE_MISMATCH", "QUALIFIER_FAILED", "PREREQUISITE_UNAVAILABLE",
    "MODEL_MISSING", "ARTIFACT_WRITE_FAILED",
))
BLOCKER_CODES = frozenset(("PREREQUISITE_UNAVAILABLE", "MODEL_MISSING"))
CLAIMS_BOUNDARY = (
    "Project-internal qualification of the declared ASCA v0.x profile.",
    "A006-A010 research outcomes are reported separately by milestone.",
    "No external certification or aggregate intelligence/performance claim.",
)


def freeze_json(value):
    if value is None or type(value) in (bool, int, str):
        return value
    if type(value) is float and math.isfinite(value):
        return value
    if isinstance(value, Mapping):
        if not all(type(key) is str for key in value):
            raise QualificationError("EVIDENCE_INVALID", "JSON object keys must be strings")
        return MappingProxyType({key: freeze_json(item) for key, item in value.items()})
    if type(value) in (tuple, list):
        return tuple(freeze_json(item) for item in value)
    raise QualificationError("EVIDENCE_INVALID", "Not a finite JSON value")


def _typed(value, hint):
    origin, args = get_origin(hint), get_args(hint)
    if origin in (Union, UnionType):
        for option in args:
            try:
                return _typed(value, option)
            except QualificationError:
                pass
        raise QualificationError("EVIDENCE_INVALID", "Wrong union value type")
    if origin is tuple:
        if type(value) not in (tuple, list):
            raise QualificationError("EVIDENCE_INVALID", "Expected a sequence")
        return tuple(_typed(item, args[0]) for item in value)
    if hint is type(None):
        if value is None:
            return None
    elif isinstance(hint, type) and type(value) is hint:
        return value
    raise QualificationError("EVIDENCE_INVALID", f"Wrong primitive/record type for {hint}")


class _ImmutableRecord:
    def __post_init__(self):
        hints = get_type_hints(type(self))
        for field in fields(self):
            value = getattr(self, field.name)
            if isinstance(self, FrozenCheck) and field.name in ("expected", "observed"):
                value = freeze_json(value)
            elif isinstance(self, PhysicalEnvironment) and field.name in ("terminal", "embedding"):
                if value is not None:
                    value = freeze_json(value)
                    if not isinstance(value, Mapping) or set(value) != {"model", "digest", "dimension"}:
                        raise QualificationError("EVIDENCE_INVALID", "Runtime descriptor keys differ")
                    if type(value["model"]) is not str or not _hex(value["digest"], 64):
                        raise QualificationError("EVIDENCE_INVALID", "Invalid runtime identity")
                    dim = value["dimension"]
                    if (field.name == "terminal" and dim is not None) or (
                        field.name == "embedding" and (type(dim) is not int or dim <= 0)):
                        raise QualificationError("EVIDENCE_INVALID", "Invalid runtime dimension")
            else:
                value = _typed(value, hints[field.name])
            object.__setattr__(self, field.name, value)
        for field in fields(self):
            value = getattr(self, field.name)
            if field.name in {"sha256", "expected_sha256", "protected_sha256", "profile_sha256",
                              "fixture_fingerprint", "payload_sha256"} and value is not None:
                if not _hex(value, 64):
                    raise QualificationError("EVIDENCE_INVALID", f"Malformed hash: {field.name}")
            if field.name in {"commit", "source_commit", "qualifier_blob"} and value is not None:
                if not _hex(value, 40):
                    raise QualificationError("EVIDENCE_INVALID", f"Malformed Git identity: {field.name}")
            if field.name in {"byte_length", "run_index"} and value < 0:
                raise QualificationError("EVIDENCE_INVALID", f"Negative {field.name}")


def _hex(value, length):
    return type(value) is str and re.fullmatch(f"[0-9a-f]{{{length}}}", value) is not None


@dataclass(frozen=True)
class Reason(_ImmutableRecord):
    code: str
    gate_id: str
    message: str
    evidence_refs: tuple[str, ...]


@dataclass(frozen=True)
class ProfileIdentity(_ImmutableRecord):
    id: str
    schema_version: int
    sha256: str
    expected_sha256: str
    expected_identity_source: str


@dataclass(frozen=True)
class SourceSnapshot(_ImmutableRecord):
    commit: str | None
    clean: bool | None
    protected_sha256: str | None
    profile_sha256: str | None
    captured_at: str


@dataclass(frozen=True)
class SourceIdentity(_ImmutableRecord):
    repository: str
    commit: str | None
    protected_sha256: str | None
    before: SourceSnapshot
    after: SourceSnapshot


@dataclass(frozen=True)
class GateEvidence(_ImmutableRecord):
    gate_id: str
    scope: Scope
    status: GateStatus
    command: tuple[str, ...] | None
    started_at: str | None
    finished_at: str | None
    exit_code: int | None
    artifacts: tuple[str, ...]
    errors: tuple[Reason, ...]
    cause_ids: tuple[str, ...]


@dataclass(frozen=True)
class FrozenCheck(_ImmutableRecord):
    identity: str
    expected: JsonValue
    observed: JsonValue
    status: GateStatus
    evidence_refs: tuple[str, ...]


@dataclass(frozen=True)
class ResearchObservation(_ImmutableRecord):
    outcome: ResearchOutcome
    role: EvidenceRole
    freshness: Freshness
    evidence_ref: str


@dataclass(frozen=True)
class ResearchEvidence(_ImmutableRecord):
    milestone: str
    expected_outcome: ResearchOutcome
    observations: tuple[ResearchObservation, ...]
    historical_refs: tuple[str, ...]


@dataclass(frozen=True)
class ReplayObservation(_ImmutableRecord):
    milestone: str
    run_index: int
    fixture_version: str
    fixture_fingerprint: str
    payload_sha256: str
    qualifier_blob: str
    source_commit: str
    profile_sha256: str
    evidence_ref: str


@dataclass(frozen=True)
class ReplayIdentity(_ImmutableRecord):
    pack_id: str
    source_commit: str | None
    profile_sha256: str
    observations: tuple[ReplayObservation, ...]


@dataclass(frozen=True)
class PhysicalEnvironment(_ImmutableRecord):
    hostname: str
    platform: str
    python_version: str
    ollama_version: str | None
    endpoint: str
    terminal: JsonObject | None
    embedding: JsonObject | None
    evidence_refs: tuple[str, ...]


@dataclass(frozen=True)
class ArtifactRecord(_ImmutableRecord):
    path: str
    kind: str
    sha256: str
    byte_length: int


@dataclass(frozen=True)
class QualificationPack(_ImmutableRecord):
    schema_version: int
    profile: ProfileIdentity
    source: SourceIdentity
    scope: Scope
    is_final: bool
    portable_status: GateStatus
    engineering_verdict: EngineeringVerdict | None
    gates: tuple[GateEvidence, ...]
    frozen_checks: tuple[FrozenCheck, ...]
    research_evidence: tuple[ResearchEvidence, ...]
    replay_identity: ReplayIdentity
    physical_environment: PhysicalEnvironment | None
    errors: tuple[Reason, ...]
    blockers: tuple[Reason, ...]
    artifact_index: tuple[ArtifactRecord, ...]
    claims_boundary: tuple[str, ...]
