from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from flywire_asca.contracts import ObservationKind, ProcedureRef
from flywire_asca.contracts.validation import require_nonempty, require_unique_nonempty


class ProcedureStepKind(str, Enum):
    ACTION = "ACTION"
    CALL_PROCEDURE = "CALL_PROCEDURE"


class OutcomeMatcherKind(str, Enum):
    EXACT = "EXACT"


class ProcedureExecutionMode(str, Enum):
    FLAT = "FLAT"
    CHUNKED = "CHUNKED"
    BLIND_CHUNKED = "BLIND_CHUNKED"


class ProcedureExecutionState(str, Enum):
    READY = "READY"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    INTERRUPTED = "INTERRUPTED"
    FAILED_VALIDATION = "FAILED_VALIDATION"


@dataclass(frozen=True, slots=True)
class ExpectedOutcome:
    expectation_id: str
    observation_kind: ObservationKind
    expected_payload_ref: str
    matcher: OutcomeMatcherKind = OutcomeMatcherKind.EXACT

    def __post_init__(self) -> None:
        require_nonempty("expectation_id", self.expectation_id)
        if not isinstance(self.observation_kind, ObservationKind):
            raise ValueError("observation_kind must be an ObservationKind")
        require_nonempty("expected_payload_ref", self.expected_payload_ref)
        if not isinstance(self.matcher, OutcomeMatcherKind):
            raise ValueError("matcher must be an OutcomeMatcherKind")


@dataclass(frozen=True, slots=True)
class ProcedureStep:
    step_id: str
    kind: ProcedureStepKind
    expected_outcome: ExpectedOutcome
    explanation_memory_ids: tuple[str, ...] = ()
    action_ref: str | None = None
    callee_procedure_id: str | None = None

    def __post_init__(self) -> None:
        require_nonempty("step_id", self.step_id)
        if not isinstance(self.kind, ProcedureStepKind):
            raise ValueError("kind must be a ProcedureStepKind")
        if not isinstance(self.expected_outcome, ExpectedOutcome):
            raise ValueError("expected_outcome must be an ExpectedOutcome")
        require_unique_nonempty("explanation_memory_ids", self.explanation_memory_ids)
        if self.kind is ProcedureStepKind.ACTION:
            require_nonempty("action_ref", self.action_ref)
            if self.callee_procedure_id is not None:
                raise ValueError("callee_procedure_id must be None for ACTION")
        elif self.kind is ProcedureStepKind.CALL_PROCEDURE:
            require_nonempty("callee_procedure_id", self.callee_procedure_id)
            if self.action_ref is not None:
                raise ValueError("action_ref must be None for CALL_PROCEDURE")


@dataclass(frozen=True, slots=True)
class ProcedureDefinition:
    procedure: ProcedureRef
    steps: tuple[ProcedureStep, ...]
    completion_outcome: ExpectedOutcome

    def __post_init__(self) -> None:
        if not isinstance(self.procedure, ProcedureRef):
            raise ValueError("procedure must be a ProcedureRef")
        if not self.steps:
            raise ValueError("steps must not be empty")
        if any(not isinstance(step, ProcedureStep) for step in self.steps):
            raise ValueError("steps must contain only ProcedureStep values")
        ids = tuple(step.step_id for step in self.steps)
        if len(ids) != len(set(ids)):
            raise ValueError("step_id values must be unique within a procedure")
        if not isinstance(self.completion_outcome, ExpectedOutcome):
            raise ValueError("completion_outcome must be an ExpectedOutcome")


@dataclass(frozen=True, slots=True)
class FlattenedPrimitiveStep:
    procedure_id: str
    step_id: str
    call_path: tuple[str, ...]
    primitive_step_path: str
    action_ref: str
    expected_outcome: ExpectedOutcome
    explanation_memory_ids: tuple[str, ...]
