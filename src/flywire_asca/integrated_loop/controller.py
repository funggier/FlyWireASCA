from __future__ import annotations

import json
from typing import Protocol

from flywire_asca.familiarity import ExactFamiliarityIndex
from flywire_asca.model import (
    ModelAdapter,
    ModelMessage,
    ModelRequest,
    ModelResponse,
    ModelRole,
)
from flywire_asca.procedural_memory import (
    ProcedureExecutionMode,
    ProcedureExecutionState,
    ProcedureLibrary,
    run_procedure,
)
from flywire_asca.uncertainty_expansion import (
    ExpansionPolicy,
    ExpansionProfile,
)

from .models import (
    CognitiveLoopRequest,
    CognitiveLoopResult,
    CognitiveProcedureAttempt,
    CognitiveTerminationReason,
    CognitiveTraceEvent,
    CognitiveTraceEventKind,
    LoopPolicy,
    ModelUsePolicy,
    RecoveryCause,
)
from .procedure import ContextBoundProcedureExecutorFactory
from .retrieval import (
    IntegratedRetrievalContext,
    evaluate_integrated_scope,
    run_initial_integrated_expansion,
)


class MemoryContextProvider(Protocol):
    def resolve(self, memory_id: str) -> str | None: ...


def _event(
    trace: list[CognitiveTraceEvent],
    kind: CognitiveTraceEventKind,
    *refs: str,
) -> None:
    trace.append(
        CognitiveTraceEvent(
            sequence=len(trace),
            kind=kind,
            refs=tuple(refs),
        )
    )


def _working_set_ids(evaluation) -> tuple[str, ...]:
    return tuple(
        entry.ref_id
        for entry in evaluation.working_set_result.working_set.entries
    )


def _run_attempt(
    *,
    request: CognitiveLoopRequest,
    attempt_index: int,
    evaluation,
    procedure_library: ProcedureLibrary,
    procedure_executor_factory: ContextBoundProcedureExecutorFactory,
    recovery_cause: RecoveryCause | None,
):
    execution_id = f"{request.loop_id}:procedure-attempt:{attempt_index}"
    memory_ids = _working_set_ids(evaluation)
    executor = procedure_executor_factory.create(
        available_memory_ids=memory_ids,
        execution_id=execution_id,
    )
    execution = run_procedure(
        procedure_library,
        root_procedure_id=request.root_procedure_id,
        mode=ProcedureExecutionMode.CHUNKED,
        executor=executor,
        execution_id=execution_id,
    )
    return CognitiveProcedureAttempt(
        attempt_index=attempt_index,
        execution_id=execution_id,
        scope=evaluation.scope,
        working_set_memory_ids=memory_ids,
        execution=execution,
        recovery_cause=recovery_cause,
        initial_world_state_ref=executor.initial_world_state_ref,
    )


def _terminal_model_request(
    *,
    request: CognitiveLoopRequest,
    familiarity,
    final_evaluation,
    final_attempt: CognitiveProcedureAttempt,
    memory_context_provider: MemoryContextProvider | None,
) -> ModelRequest:
    interruption = final_attempt.execution.interruption
    if interruption is None:
        raise ValueError(
            "terminal model fallback requires procedure interruption evidence"
        )
    memory_ids = final_attempt.working_set_memory_ids
    memory_context = []
    for memory_id in memory_ids:
        resolved = (
            memory_context_provider.resolve(memory_id)
            if memory_context_provider is not None
            else None
        )
        memory_context.append(
            {
                "memory_id": memory_id,
                "text": resolved,
            }
        )
    payload = {
        "role": "terminal_diagnostic_fallback_only",
        "goal": request.goal_text,
        "familiarity_state": familiarity.retrieval_state.value,
        "final_scope_index": final_evaluation.scope.round_index,
        "working_set": memory_context,
        "failing_procedure_id": interruption.failing_procedure_id,
        "failing_step_id": interruption.failing_step_id,
        "call_path": interruption.call_path,
        "expected_payload_ref": (
            interruption.expected_outcome.expected_payload_ref
        ),
        "observed_payload_ref": getattr(
            interruption.observed,
            "payload_ref",
            None,
        ),
        "control_boundary": (
            "diagnostic text only; do not choose retrieval scope, procedure, "
            "verification, replay, or termination"
        ),
    }
    return ModelRequest(
        request_id=f"{request.loop_id}:terminal-model",
        messages=(
            ModelMessage(
                ModelRole.SYSTEM,
                "Produce a diagnostic/fallback explanation only. "
                "You do not control the cognitive loop.",
            ),
            ModelMessage(
                ModelRole.USER,
                json.dumps(
                    payload,
                    ensure_ascii=False,
                    sort_keys=True,
                    separators=(",", ":"),
                ),
            ),
        ),
        max_output_tokens=256,
        context_limit=8192,
        temperature=0.0,
        seed=0,
        thinking=False,
    )


def run_cognitive_loop(
    request: CognitiveLoopRequest,
    *,
    familiarity_index: ExactFamiliarityIndex,
    retrieval_context: IntegratedRetrievalContext,
    expansion_profile: ExpansionProfile,
    procedure_library: ProcedureLibrary,
    procedure_executor_factory: ContextBoundProcedureExecutorFactory,
    model_adapter: ModelAdapter | None = None,
    memory_context_provider: MemoryContextProvider | None = None,
) -> CognitiveLoopResult:
    if not isinstance(request, CognitiveLoopRequest):
        raise ValueError("request must be a CognitiveLoopRequest")
    if not isinstance(familiarity_index, ExactFamiliarityIndex):
        raise ValueError("familiarity_index must be an ExactFamiliarityIndex")
    if not isinstance(retrieval_context, IntegratedRetrievalContext):
        raise ValueError(
            "retrieval_context must be an IntegratedRetrievalContext"
        )
    if not isinstance(expansion_profile, ExpansionProfile):
        raise ValueError("expansion_profile must be an ExpansionProfile")
    if len(expansion_profile.scopes) > 3:
        raise ValueError("A009 supports at most three expansion scopes")
    if any(scope.round_index > 2 for scope in expansion_profile.scopes):
        raise ValueError("A009 scope round_index must not exceed 2")
    if not isinstance(procedure_library, ProcedureLibrary):
        raise ValueError("procedure_library must be a ProcedureLibrary")
    if not isinstance(
        procedure_executor_factory,
        ContextBoundProcedureExecutorFactory,
    ):
        raise ValueError(
            "procedure_executor_factory must be a "
            "ContextBoundProcedureExecutorFactory"
        )
    procedure_library.get(request.root_procedure_id)

    trace: list[CognitiveTraceEvent] = []
    familiarity = familiarity_index.assess(request.familiarity_cue)
    _event(
        trace,
        CognitiveTraceEventKind.FAMILIARITY_ASSESSED,
        f"cue:{familiarity.cue_id}",
        f"state:{familiarity.retrieval_state.value}",
    )

    initial_policy = (
        ExpansionPolicy.ALWAYS_EXPAND
        if request.policy is LoopPolicy.ALWAYS_MAX_SCOPE
        else ExpansionPolicy.SIGNAL_DRIVEN
    )
    initial_expansion = run_initial_integrated_expansion(
        retrieval_context,
        profile=expansion_profile,
        policy=initial_policy,
    )
    scope_evaluations = list(initial_expansion.evaluations)
    for evaluation in initial_expansion.evaluations:
        _event(
            trace,
            CognitiveTraceEventKind.INITIAL_EXPANSION_SCOPE_EVALUATED,
            f"scope:{evaluation.scope.round_index}",
        )
    _event(
        trace,
        CognitiveTraceEventKind.INITIAL_EXPANSION_TERMINATED,
        f"reason:{initial_expansion.run.termination_reason.value}",
    )
    _event(
        trace,
        CognitiveTraceEventKind.ROOT_PROCEDURE_SELECTED,
        f"procedure:{request.root_procedure_id}",
        "route:EXPLICIT_ROOT_PROCEDURE",
    )

    attempts: list[CognitiveProcedureAttempt] = []
    current = scope_evaluations[-1]
    _event(
        trace,
        CognitiveTraceEventKind.PROCEDURE_ATTEMPT_STARTED,
        f"execution:{request.loop_id}:procedure-attempt:0",
        f"scope:{current.scope.round_index}",
    )
    attempt = _run_attempt(
        request=request,
        attempt_index=0,
        evaluation=current,
        procedure_library=procedure_library,
        procedure_executor_factory=procedure_executor_factory,
        recovery_cause=None,
    )
    attempts.append(attempt)

    if attempt.execution.state is ProcedureExecutionState.COMPLETED:
        _event(
            trace,
            CognitiveTraceEventKind.PROCEDURE_COMPLETED,
            f"execution:{attempt.execution_id}",
        )
        termination = CognitiveTerminationReason.PROCEDURE_COMPLETED
    else:
        _event(
            trace,
            CognitiveTraceEventKind.PROCEDURE_MISMATCH_OBSERVED,
            f"execution:{attempt.execution_id}",
            f"procedure:{attempt.execution.interruption.failing_procedure_id}",
            f"step:{attempt.execution.interruption.failing_step_id}",
        )
        termination = CognitiveTerminationReason.PROCEDURE_MISMATCH_EXHAUSTED

        if request.policy is LoopPolicy.MISMATCH_DRIVEN_RECOVERY:
            current_index = current.scope.round_index
            while (
                attempts[-1].execution.state
                is ProcedureExecutionState.INTERRUPTED
                and current_index + 1 < len(expansion_profile.scopes)
                and len(attempts) < 3
            ):
                next_scope = expansion_profile.scopes[current_index + 1]
                if next_scope.round_index != current_index + 1:
                    raise ValueError(
                        "recovery scope must be exactly the next declared scope"
                    )
                _event(
                    trace,
                    CognitiveTraceEventKind.RECOVERY_SCOPE_FORCED,
                    f"scope:{next_scope.round_index}",
                    "cause:PROCEDURE_OUTCOME_MISMATCH",
                )
                current = evaluate_integrated_scope(
                    retrieval_context,
                    next_scope,
                )
                scope_evaluations.append(current)
                attempt_index = len(attempts)
                execution_id = (
                    f"{request.loop_id}:procedure-attempt:{attempt_index}"
                )
                _event(
                    trace,
                    CognitiveTraceEventKind.PROCEDURE_ATTEMPT_STARTED,
                    f"execution:{execution_id}",
                    f"scope:{current.scope.round_index}",
                )
                attempt = _run_attempt(
                    request=request,
                    attempt_index=attempt_index,
                    evaluation=current,
                    procedure_library=procedure_library,
                    procedure_executor_factory=procedure_executor_factory,
                    recovery_cause=RecoveryCause.PROCEDURE_OUTCOME_MISMATCH,
                )
                attempts.append(attempt)
                current_index = current.scope.round_index
                if attempt.execution.state is ProcedureExecutionState.COMPLETED:
                    _event(
                        trace,
                        CognitiveTraceEventKind.PROCEDURE_COMPLETED,
                        f"execution:{attempt.execution_id}",
                    )
                    termination = (
                        CognitiveTerminationReason.RECOVERED_AFTER_MISMATCH
                    )
                    break
                _event(
                    trace,
                    CognitiveTraceEventKind.PROCEDURE_MISMATCH_OBSERVED,
                    f"execution:{attempt.execution_id}",
                    f"procedure:{attempt.execution.interruption.failing_procedure_id}",
                    f"step:{attempt.execution.interruption.failing_step_id}",
                )

    model_response: ModelResponse | None = None
    if (
        termination
        is CognitiveTerminationReason.PROCEDURE_MISMATCH_EXHAUSTED
        and request.model_use_policy is ModelUsePolicy.TERMINAL_ONLY
    ):
        if model_adapter is None or not callable(
            getattr(model_adapter, "generate", None)
        ):
            raise ValueError(
                "TERMINAL_ONLY exhaustion requires a model adapter"
            )
        model_request = _terminal_model_request(
            request=request,
            familiarity=familiarity,
            final_evaluation=scope_evaluations[-1],
            final_attempt=attempts[-1],
            memory_context_provider=memory_context_provider,
        )
        response = model_adapter.generate(model_request)
        if not isinstance(response, ModelResponse):
            raise ValueError("model adapter must return a ModelResponse")
        if response.request_id != model_request.request_id:
            raise ValueError(
                "model response request_id must match terminal request_id"
            )
        model_response = response
        _event(
            trace,
            CognitiveTraceEventKind.MODEL_FALLBACK_INVOKED,
            f"request:{model_request.request_id}",
        )

    _event(
        trace,
        CognitiveTraceEventKind.TERMINAL_STATE_REACHED,
        f"reason:{termination.value}",
    )
    final_attempt = attempts[-1]
    final_evaluation = scope_evaluations[-1]
    return CognitiveLoopResult(
        loop_id=request.loop_id,
        policy=request.policy,
        familiarity=familiarity,
        initial_expansion=initial_expansion,
        scope_evaluations=tuple(scope_evaluations),
        procedure_attempts=tuple(attempts),
        termination_reason=termination,
        final_working_set=final_evaluation.working_set_result.working_set,
        final_world_state_ref=final_attempt.execution.final_world_state_ref,
        model_response=model_response,
        trace=tuple(trace),
    )
