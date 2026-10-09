from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from flywire_asca.contracts import Cue, WorkingSet
from flywire_asca.contracts.validation import require_nonempty, require_unique_nonempty
from flywire_asca.familiarity import FamiliarityResult
from flywire_asca.model import ModelResponse
from flywire_asca.procedural_memory import (
    ProcedureExecutionMode,
    ProcedureExecutionResult,
    ProcedureExecutionState,
)
from flywire_asca.selective_activation import SelectiveWorkingSetResult
from flywire_asca.uncertainty_expansion import (
    ExpansionRunResult,
    ExpansionScope,
)
from flywire_asca.vector_memory import VectorMemoryResult


class CognitiveLoopPhase(str, Enum):
    FAMILIARITY = "FAMILIARITY"
    INITIAL_EXPANSION = "INITIAL_EXPANSION"
    PROCEDURE_EXECUTION = "PROCEDURE_EXECUTION"
    RECOVERY_EXPANSION = "RECOVERY_EXPANSION"
    MODEL_FALLBACK = "MODEL_FALLBACK"
    TERMINAL = "TERMINAL"


class RecoveryCause(str, Enum):
    PROCEDURE_OUTCOME_MISMATCH = "PROCEDURE_OUTCOME_MISMATCH"


class LoopPolicy(str, Enum):
    NO_PROCEDURE_RECOVERY = "NO_PROCEDURE_RECOVERY"
    MISMATCH_DRIVEN_RECOVERY = "MISMATCH_DRIVEN_RECOVERY"
    ALWAYS_MAX_SCOPE = "ALWAYS_MAX_SCOPE"


class ModelUsePolicy(str, Enum):
    DISABLED = "DISABLED"
    TERMINAL_ONLY = "TERMINAL_ONLY"


class CognitiveTerminationReason(str, Enum):
    PROCEDURE_COMPLETED = "PROCEDURE_COMPLETED"
    RECOVERED_AFTER_MISMATCH = "RECOVERED_AFTER_MISMATCH"
    PROCEDURE_MISMATCH_EXHAUSTED = "PROCEDURE_MISMATCH_EXHAUSTED"


class CognitiveTraceEventKind(str, Enum):
    FAMILIARITY_ASSESSED = "FAMILIARITY_ASSESSED"
    INITIAL_EXPANSION_SCOPE_EVALUATED = "INITIAL_EXPANSION_SCOPE_EVALUATED"
    INITIAL_EXPANSION_TERMINATED = "INITIAL_EXPANSION_TERMINATED"
    ROOT_PROCEDURE_SELECTED = "ROOT_PROCEDURE_SELECTED"
    PROCEDURE_ATTEMPT_STARTED = "PROCEDURE_ATTEMPT_STARTED"
    PROCEDURE_COMPLETED = "PROCEDURE_COMPLETED"
    PROCEDURE_MISMATCH_OBSERVED = "PROCEDURE_MISMATCH_OBSERVED"
    RECOVERY_SCOPE_FORCED = "RECOVERY_SCOPE_FORCED"
    MODEL_FALLBACK_INVOKED = "MODEL_FALLBACK_INVOKED"
    TERMINAL_STATE_REACHED = "TERMINAL_STATE_REACHED"


def _require_nonnegative_int(name: str, value: int) -> None:
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise ValueError(f"{name} must be a nonnegative integer")


def _require_optional_nonempty(name: str, value: str | None) -> None:
    if value is not None:
        require_nonempty(name, value)


@dataclass(frozen=True, slots=True)
class CognitiveLoopRequest:
    loop_id: str
    goal_text: str
    familiarity_cue: Cue
    root_procedure_id: str
    policy: LoopPolicy
    model_use_policy: ModelUsePolicy

    def __post_init__(self) -> None:
        require_nonempty("loop_id", self.loop_id)
        require_nonempty("goal_text", self.goal_text)
        if not isinstance(self.familiarity_cue, Cue):
            raise ValueError("familiarity_cue must be a Cue")
        require_nonempty("root_procedure_id", self.root_procedure_id)
        if not isinstance(self.policy, LoopPolicy):
            raise ValueError("policy must be a LoopPolicy")
        if not isinstance(self.model_use_policy, ModelUsePolicy):
            raise ValueError("model_use_policy must be a ModelUsePolicy")


@dataclass(frozen=True, slots=True)
class IntegratedScopeEvaluation:
    scope: ExpansionScope
    retrieval_results: tuple[VectorMemoryResult, ...]
    working_set_result: SelectiveWorkingSetResult

    def __post_init__(self) -> None:
        if not isinstance(self.scope, ExpansionScope):
            raise ValueError("scope must be an ExpansionScope")
        if not self.retrieval_results:
            raise ValueError("retrieval_results must not be empty")
        if any(
            not isinstance(result, VectorMemoryResult)
            for result in self.retrieval_results
        ):
            raise ValueError(
                "retrieval_results must contain only VectorMemoryResult values"
            )
        query_ids = tuple(result.query_id for result in self.retrieval_results)
        if len(query_ids) != len(set(query_ids)):
            raise ValueError("retrieval_results contain duplicate query_id values")
        if not isinstance(self.working_set_result, SelectiveWorkingSetResult):
            raise ValueError(
                "working_set_result must be a SelectiveWorkingSetResult"
            )


@dataclass(frozen=True, slots=True)
class IntegratedExpansionResult:
    run: ExpansionRunResult
    evaluations: tuple[IntegratedScopeEvaluation, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.run, ExpansionRunResult):
            raise ValueError("run must be an ExpansionRunResult")
        if not self.evaluations:
            raise ValueError("evaluations must not be empty")
        if any(
            not isinstance(item, IntegratedScopeEvaluation)
            for item in self.evaluations
        ):
            raise ValueError(
                "evaluations must contain only IntegratedScopeEvaluation values"
            )
        if len(self.evaluations) != len(self.run.rounds):
            raise ValueError("evaluation count must equal expansion run round count")
        for evaluation, round_result in zip(self.evaluations, self.run.rounds):
            if evaluation.scope != round_result.scope:
                raise ValueError("evaluation scope must equal expansion round scope")
            if evaluation.working_set_result != round_result.working_set_result:
                raise ValueError(
                    "evaluation working_set_result must equal expansion round result"
                )


@dataclass(frozen=True, slots=True)
class CognitiveProcedureAttempt:
    attempt_index: int
    execution_id: str
    scope: ExpansionScope
    working_set_memory_ids: tuple[str, ...]
    execution: ProcedureExecutionResult
    recovery_cause: RecoveryCause | None
    initial_world_state_ref: str

    def __post_init__(self) -> None:
        _require_nonnegative_int("attempt_index", self.attempt_index)
        require_nonempty("execution_id", self.execution_id)
        if not isinstance(self.scope, ExpansionScope):
            raise ValueError("scope must be an ExpansionScope")
        require_unique_nonempty(
            "working_set_memory_ids",
            self.working_set_memory_ids,
        )
        if not isinstance(self.execution, ProcedureExecutionResult):
            raise ValueError("execution must be a ProcedureExecutionResult")
        if self.execution.execution_id != self.execution_id:
            raise ValueError(
                "execution_id must equal execution.execution_id"
            )
        if self.execution.mode is not ProcedureExecutionMode.CHUNKED:
            raise ValueError("execution mode must be CHUNKED")
        if self.attempt_index == 0:
            if self.recovery_cause is not None:
                raise ValueError("attempt 0 recovery_cause must be None")
        elif self.recovery_cause is not RecoveryCause.PROCEDURE_OUTCOME_MISMATCH:
            raise ValueError(
                "recovery_cause for replay must be PROCEDURE_OUTCOME_MISMATCH"
            )
        require_nonempty("initial_world_state_ref", self.initial_world_state_ref)


@dataclass(frozen=True, slots=True)
class CognitiveTraceEvent:
    sequence: int
    kind: CognitiveTraceEventKind
    refs: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        _require_nonnegative_int("sequence", self.sequence)
        if not isinstance(self.kind, CognitiveTraceEventKind):
            raise ValueError("kind must be a CognitiveTraceEventKind")
        require_unique_nonempty("refs", self.refs)


@dataclass(frozen=True, slots=True)
class CognitiveLoopResult:
    loop_id: str
    policy: LoopPolicy
    familiarity: FamiliarityResult
    initial_expansion: IntegratedExpansionResult
    scope_evaluations: tuple[IntegratedScopeEvaluation, ...]
    procedure_attempts: tuple[CognitiveProcedureAttempt, ...]
    termination_reason: CognitiveTerminationReason
    final_working_set: WorkingSet
    final_world_state_ref: str | None
    model_response: ModelResponse | None
    trace: tuple[CognitiveTraceEvent, ...]

    def __post_init__(self) -> None:
        require_nonempty("loop_id", self.loop_id)
        if not isinstance(self.policy, LoopPolicy):
            raise ValueError("policy must be a LoopPolicy")
        if not isinstance(self.familiarity, FamiliarityResult):
            raise ValueError("familiarity must be a FamiliarityResult")
        if not isinstance(self.initial_expansion, IntegratedExpansionResult):
            raise ValueError(
                "initial_expansion must be an IntegratedExpansionResult"
            )
        if not self.scope_evaluations or any(
            not isinstance(item, IntegratedScopeEvaluation)
            for item in self.scope_evaluations
        ):
            raise ValueError(
                "scope_evaluations must contain IntegratedScopeEvaluation values"
            )
        if tuple(self.scope_evaluations[: len(self.initial_expansion.evaluations)]) != (
            self.initial_expansion.evaluations
        ):
            raise ValueError(
                "scope_evaluations must begin with initial expansion evaluations"
            )
        if not self.procedure_attempts or any(
            not isinstance(item, CognitiveProcedureAttempt)
            for item in self.procedure_attempts
        ):
            raise ValueError(
                "procedure_attempts must contain CognitiveProcedureAttempt values"
            )

        indices = tuple(item.attempt_index for item in self.procedure_attempts)
        if indices != tuple(range(len(self.procedure_attempts))):
            raise ValueError("procedure attempt indices must be contiguous from 0")
        execution_ids = tuple(item.execution_id for item in self.procedure_attempts)
        if len(execution_ids) != len(set(execution_ids)):
            raise ValueError("procedure attempt execution_id values must be unique")
        scope_indices = tuple(item.scope.round_index for item in self.procedure_attempts)
        if any(
            current < previous
            for previous, current in zip(scope_indices, scope_indices[1:])
        ):
            raise ValueError("procedure attempt scope indices must not regress")
        for item in self.procedure_attempts[:-1]:
            if item.execution.state is ProcedureExecutionState.COMPLETED:
                raise ValueError("procedure attempt cannot occur after COMPLETED")

        if not isinstance(self.termination_reason, CognitiveTerminationReason):
            raise ValueError(
                "termination_reason must be a CognitiveTerminationReason"
            )
        final_attempt = self.procedure_attempts[-1]
        if self.termination_reason is CognitiveTerminationReason.PROCEDURE_COMPLETED:
            if final_attempt.execution.state is not ProcedureExecutionState.COMPLETED:
                raise ValueError("PROCEDURE_COMPLETED requires completed final attempt")
        elif (
            self.termination_reason
            is CognitiveTerminationReason.RECOVERED_AFTER_MISMATCH
        ):
            if len(self.procedure_attempts) < 2:
                raise ValueError(
                    "RECOVERED_AFTER_MISMATCH requires at least two attempts"
                )
            if final_attempt.execution.state is not ProcedureExecutionState.COMPLETED:
                raise ValueError(
                    "RECOVERED_AFTER_MISMATCH requires completed final attempt"
                )
        elif (
            self.termination_reason
            is CognitiveTerminationReason.PROCEDURE_MISMATCH_EXHAUSTED
        ):
            if final_attempt.execution.state is not ProcedureExecutionState.INTERRUPTED:
                raise ValueError(
                    "PROCEDURE_MISMATCH_EXHAUSTED requires interrupted final attempt"
                )

        if not isinstance(self.final_working_set, WorkingSet):
            raise ValueError("final_working_set must be a WorkingSet")
        _require_optional_nonempty(
            "final_world_state_ref",
            self.final_world_state_ref,
        )
        if self.model_response is not None and not isinstance(
            self.model_response,
            ModelResponse,
        ):
            raise ValueError("model_response must be a ModelResponse or None")
        if not self.trace or any(
            not isinstance(item, CognitiveTraceEvent) for item in self.trace
        ):
            raise ValueError("trace must contain CognitiveTraceEvent values")
        sequences = tuple(item.sequence for item in self.trace)
        if sequences != tuple(range(len(self.trace))):
            raise ValueError("trace sequence values must be contiguous from 0")
