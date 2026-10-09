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

@dataclass(frozen=True, slots=True)
class OutcomeVerification:
    expectation_id: str
    observation_id: str
    matched: bool

    def __post_init__(self) -> None:
        require_nonempty("expectation_id", self.expectation_id)
        require_nonempty("observation_id", self.observation_id)
        if not isinstance(self.matched, bool):
            raise ValueError("matched must be bool")


@dataclass(frozen=True, slots=True)
class SimulatedWorldState:
    values: tuple[tuple[str, str], ...]

    def __post_init__(self) -> None:
        normalized = tuple(self.values)
        keys: list[str] = []
        for item in normalized:
            if not isinstance(item, tuple) or len(item) != 2:
                raise ValueError("values must contain (key, value) pairs")
            key, value = item
            require_nonempty("key", key)
            if not isinstance(value, str):
                raise ValueError("world-state value must be a string")
            keys.append(key)
        if len(keys) != len(set(keys)):
            raise ValueError("world-state keys must be unique")
        object.__setattr__(self, "values", tuple(sorted(normalized)))

    def get(self, key: str) -> str | None:
        require_nonempty("key", key)
        return dict(self.values).get(key)


@dataclass(frozen=True, slots=True)
class SimulatedActionDefinition:
    action_ref: str
    writes: tuple[tuple[str, str], ...]
    observation_kind: ObservationKind
    success_payload_ref: str

    def __post_init__(self) -> None:
        require_nonempty("action_ref", self.action_ref)
        if not isinstance(self.observation_kind, ObservationKind):
            raise ValueError("observation_kind must be an ObservationKind")
        require_nonempty("success_payload_ref", self.success_payload_ref)
        keys: list[str] = []
        for item in self.writes:
            if not isinstance(item, tuple) or len(item) != 2:
                raise ValueError("writes must contain (key, value) pairs")
            key, value = item
            require_nonempty("write key", key)
            if not isinstance(value, str):
                raise ValueError("write value must be a string")
            keys.append(key)
        if len(keys) != len(set(keys)):
            raise ValueError("write keys must be unique within an action definition")


@dataclass(frozen=True, slots=True)
class SimulatedCompletionProbe:
    procedure_id: str
    state_key: str
    observation_kind: ObservationKind

    def __post_init__(self) -> None:
        require_nonempty("procedure_id", self.procedure_id)
        require_nonempty("state_key", self.state_key)
        if not isinstance(self.observation_kind, ObservationKind):
            raise ValueError("observation_kind must be an ObservationKind")


@dataclass(frozen=True, slots=True)
class SimulatedFailureOverride:
    primitive_step_path: str
    observation_kind: ObservationKind
    payload_ref: str
    suppress_writes: bool = True

    def __post_init__(self) -> None:
        require_nonempty("primitive_step_path", self.primitive_step_path)
        if not isinstance(self.observation_kind, ObservationKind):
            raise ValueError("observation_kind must be an ObservationKind")
        require_nonempty("payload_ref", self.payload_ref)
        if not isinstance(self.suppress_writes, bool):
            raise ValueError("suppress_writes must be bool")

@dataclass(frozen=True, slots=True)
class ProcedureExecutionMetrics:
    primitive_action_count: int
    procedure_call_count: int
    root_visible_dispatch_count: int
    total_step_event_count: int
    expected_outcome_check_count: int
    suppressed_internal_check_count: int
    max_runtime_call_depth: int

    def __post_init__(self) -> None:
        for name in (
            "primitive_action_count",
            "procedure_call_count",
            "root_visible_dispatch_count",
            "total_step_event_count",
            "expected_outcome_check_count",
            "suppressed_internal_check_count",
            "max_runtime_call_depth",
        ):
            value = getattr(self, name)
            if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                raise ValueError(f"{name} must be a nonnegative integer")


@dataclass(frozen=True, slots=True)
class StepExecutionResult:
    procedure_id: str
    step_id: str
    call_path: tuple[str, ...]
    kind: ProcedureStepKind
    observation: object
    expected_outcome: ExpectedOutcome
    verification: OutcomeVerification | None
    primitive_action_executed: bool
    action_ref: str | None = None

    def __post_init__(self) -> None:
        require_nonempty("procedure_id", self.procedure_id)
        require_nonempty("step_id", self.step_id)
        if not self.call_path or self.call_path[-1] != self.procedure_id:
            raise ValueError("call_path must end with procedure_id")
        if not isinstance(self.kind, ProcedureStepKind):
            raise ValueError("kind must be a ProcedureStepKind")
        if not isinstance(self.expected_outcome, ExpectedOutcome):
            raise ValueError("expected_outcome must be an ExpectedOutcome")
        if self.verification is not None and not isinstance(self.verification, OutcomeVerification):
            raise ValueError("verification must be OutcomeVerification or None")
        if not isinstance(self.primitive_action_executed, bool):
            raise ValueError("primitive_action_executed must be bool")
        if self.kind is ProcedureStepKind.ACTION:
            require_nonempty("action_ref", self.action_ref)
            if not self.primitive_action_executed:
                raise ValueError("ACTION result must record primitive execution")
        elif self.action_ref is not None:
            raise ValueError("CALL_PROCEDURE result action_ref must be None")


@dataclass(frozen=True, slots=True)
class ProcedureInterruption:
    root_procedure_id: str
    failing_procedure_id: str
    failing_step_id: str
    call_path: tuple[str, ...]
    expected_outcome: ExpectedOutcome
    observed: object
    explanation_memory_ids: tuple[str, ...]
    completed_primitive_step_paths: tuple[str, ...]

    def __post_init__(self) -> None:
        require_nonempty("root_procedure_id", self.root_procedure_id)
        require_nonempty("failing_procedure_id", self.failing_procedure_id)
        require_nonempty("failing_step_id", self.failing_step_id)
        if not self.call_path or self.call_path[-1] != self.failing_procedure_id:
            raise ValueError("interruption call_path must end with failing_procedure_id")
        require_unique_nonempty("explanation_memory_ids", self.explanation_memory_ids)


@dataclass(frozen=True, slots=True)
class ProcedureExecutionResult:
    execution_id: str
    root_procedure_id: str
    mode: ProcedureExecutionMode
    state: ProcedureExecutionState
    step_results: tuple[StepExecutionResult, ...]
    interruption: ProcedureInterruption | None
    final_world_state_ref: str | None
    metrics: ProcedureExecutionMetrics

    def __post_init__(self) -> None:
        require_nonempty("execution_id", self.execution_id)
        require_nonempty("root_procedure_id", self.root_procedure_id)
        if not isinstance(self.mode, ProcedureExecutionMode):
            raise ValueError("mode must be a ProcedureExecutionMode")
        if not isinstance(self.state, ProcedureExecutionState):
            raise ValueError("state must be a ProcedureExecutionState")
        if any(not isinstance(item, StepExecutionResult) for item in self.step_results):
            raise ValueError("step_results must contain StepExecutionResult values")
        if self.state is ProcedureExecutionState.INTERRUPTED:
            if not isinstance(self.interruption, ProcedureInterruption):
                raise ValueError("INTERRUPTED requires interruption evidence")
        elif self.interruption is not None:
            raise ValueError("non-INTERRUPTED result must not contain interruption")
        if not isinstance(self.metrics, ProcedureExecutionMetrics):
            raise ValueError("metrics must be ProcedureExecutionMetrics")
