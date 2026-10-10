from __future__ import annotations

from dataclasses import replace

from flywire_asca.contracts.validation import require_nonempty
from flywire_asca.familiarity import ExactFamiliarityIndex
from flywire_asca.integrated_loop import (
    CognitiveLoopRequest,
    CognitiveLoopResult,
    CognitiveTraceEventKind,
    ContextBoundProcedureExecutorFactory,
    IntegratedRetrievalContext,
    LoopPolicy,
    MemoryContextProvider,
    evaluate_integrated_scope,
    run_initial_integrated_expansion,
)
from flywire_asca.integrated_loop import controller as integrated_controller
from flywire_asca.model import ModelAdapter
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

from .models import ComparisonRunResult, ComparisonVariant


def _same_name_preserved(
    expected_ids: tuple[str, ...],
    selected_ids: tuple[str, ...],
) -> bool:
    return True if not expected_ids else set(expected_ids).issubset(selected_ids)


def _evaluation_metrics(evaluations):
    return {
        "query_count": sum(len(item.retrieval_results) for item in evaluations),
        "stored_count_sum": sum(
            result.stored_count
            for item in evaluations
            for result in item.retrieval_results
        ),
        "metadata_eligible_count_sum": sum(
            result.metadata_eligible_count
            for item in evaluations
            for result in item.retrieval_results
        ),
        "scored_vector_count_sum": sum(
            result.scored_vector_count
            for item in evaluations
            for result in item.retrieval_results
        ),
        "above_threshold_count_sum": sum(
            result.above_threshold_count
            for item in evaluations
            for result in item.retrieval_results
        ),
        "returned_count_sum": sum(
            result.returned_count
            for item in evaluations
            for result in item.retrieval_results
        ),
        "cumulative_unique_candidate_count": sum(
            item.working_set_result.unique_candidate_count for item in evaluations
        ),
        "cumulative_activated_candidate_count": sum(
            item.working_set_result.activated_candidate_count for item in evaluations
        ),
        "cumulative_selected_count": sum(
            item.working_set_result.selected_count for item in evaluations
        ),
        "peak_selected_count": max(
            item.working_set_result.selected_count for item in evaluations
        ),
    }


def normalize_a009_result(
    case_id: str,
    variant: ComparisonVariant,
    result: CognitiveLoopResult,
    *,
    expected_final_world_state_ref: str,
    same_name_expected_ids: tuple[str, ...] = (),
) -> ComparisonRunResult:
    if not isinstance(result, CognitiveLoopResult):
        raise ValueError("result must be a CognitiveLoopResult")
    require_nonempty(
        "expected_final_world_state_ref", expected_final_world_state_ref
    )
    if variant not in {
        ComparisonVariant.ASCA_PRIMARY,
        ComparisonVariant.ASCA_ALWAYS_MAX_SCOPE,
        ComparisonVariant.ASCA_FAMILIARITY_DISABLED,
    }:
        raise ValueError("variant is not an A009-backed comparison variant")

    evaluations = result.scope_evaluations
    metrics = _evaluation_metrics(evaluations)
    attempts = result.procedure_attempts
    selected_ids = tuple(entry.ref_id for entry in result.final_working_set.entries)
    success = attempts[-1].execution.state is ProcedureExecutionState.COMPLETED
    mismatch_count = sum(
        item.execution.state is ProcedureExecutionState.INTERRUPTED
        for item in attempts
    )
    recovery_count = sum(
        item.kind is CognitiveTraceEventKind.RECOVERY_SCOPE_FORCED
        for item in result.trace
    )
    trace_signature = tuple(
        (item.kind.value, item.refs)
        for item in result.trace
        if item.kind is not CognitiveTraceEventKind.FAMILIARITY_ASSESSED
    )
    return ComparisonRunResult(
        variant=variant,
        case_id=case_id,
        procedure_success=success,
        final_state_correct=(
            success
            and result.final_world_state_ref == expected_final_world_state_ref
        ),
        final_world_state_ref=result.final_world_state_ref,
        evaluated_scope_indices=tuple(
            item.scope.round_index for item in evaluations
        ),
        final_selected_memory_ids=selected_ids,
        procedure_attempt_count=len(attempts),
        execution_ids=tuple(item.execution_id for item in attempts),
        procedure_states=tuple(item.execution.state.value for item in attempts),
        mismatch_count=mismatch_count,
        forced_recovery_scope_count=recovery_count,
        same_name_identity_preserved=_same_name_preserved(
            same_name_expected_ids,
            selected_ids,
        ),
        trace_signature=trace_signature,
        **metrics,
    )


def _run_a009_variant(
    *,
    variant: ComparisonVariant,
    policy: LoopPolicy,
    request: CognitiveLoopRequest,
    familiarity_index: ExactFamiliarityIndex,
    retrieval_context: IntegratedRetrievalContext,
    expansion_profile: ExpansionProfile,
    procedure_library: ProcedureLibrary,
    procedure_executor_factory: ContextBoundProcedureExecutorFactory,
    model_adapter: ModelAdapter | None = None,
    memory_context_provider: MemoryContextProvider | None = None,
    expected_final_world_state_ref: str,
    same_name_expected_ids: tuple[str, ...] = (),
) -> ComparisonRunResult:
    normalized_request = replace(request, policy=policy)
    raw = integrated_controller.run_cognitive_loop(
        normalized_request,
        familiarity_index=familiarity_index,
        retrieval_context=retrieval_context,
        expansion_profile=expansion_profile,
        procedure_library=procedure_library,
        procedure_executor_factory=procedure_executor_factory,
        model_adapter=model_adapter,
        memory_context_provider=memory_context_provider,
    )
    return normalize_a009_result(
        request.loop_id.removeprefix("a009:").split(":", 1)[0]
        if request.loop_id.startswith("a009:")
        else request.loop_id,
        variant,
        raw,
        expected_final_world_state_ref=expected_final_world_state_ref,
        same_name_expected_ids=same_name_expected_ids,
    )


def run_asca_primary(
    *,
    request: CognitiveLoopRequest,
    familiarity_index: ExactFamiliarityIndex,
    retrieval_context: IntegratedRetrievalContext,
    expansion_profile: ExpansionProfile,
    procedure_library: ProcedureLibrary,
    procedure_executor_factory: ContextBoundProcedureExecutorFactory,
    model_adapter: ModelAdapter | None = None,
    memory_context_provider: MemoryContextProvider | None = None,
    expected_final_world_state_ref: str,
    same_name_expected_ids: tuple[str, ...] = (),
) -> ComparisonRunResult:
    return _run_a009_variant(
        variant=ComparisonVariant.ASCA_PRIMARY,
        policy=LoopPolicy.MISMATCH_DRIVEN_RECOVERY,
        request=request,
        familiarity_index=familiarity_index,
        retrieval_context=retrieval_context,
        expansion_profile=expansion_profile,
        procedure_library=procedure_library,
        procedure_executor_factory=procedure_executor_factory,
        model_adapter=model_adapter,
        memory_context_provider=memory_context_provider,
        expected_final_world_state_ref=expected_final_world_state_ref,
        same_name_expected_ids=same_name_expected_ids,
    )


def run_asca_always_max_scope(
    *,
    request: CognitiveLoopRequest,
    familiarity_index: ExactFamiliarityIndex,
    retrieval_context: IntegratedRetrievalContext,
    expansion_profile: ExpansionProfile,
    procedure_library: ProcedureLibrary,
    procedure_executor_factory: ContextBoundProcedureExecutorFactory,
    model_adapter: ModelAdapter | None = None,
    memory_context_provider: MemoryContextProvider | None = None,
    expected_final_world_state_ref: str,
    same_name_expected_ids: tuple[str, ...] = (),
) -> ComparisonRunResult:
    return _run_a009_variant(
        variant=ComparisonVariant.ASCA_ALWAYS_MAX_SCOPE,
        policy=LoopPolicy.ALWAYS_MAX_SCOPE,
        request=request,
        familiarity_index=familiarity_index,
        retrieval_context=retrieval_context,
        expansion_profile=expansion_profile,
        procedure_library=procedure_library,
        procedure_executor_factory=procedure_executor_factory,
        model_adapter=model_adapter,
        memory_context_provider=memory_context_provider,
        expected_final_world_state_ref=expected_final_world_state_ref,
        same_name_expected_ids=same_name_expected_ids,
    )


def run_familiarity_disabled_ablation(
    *,
    request: CognitiveLoopRequest,
    familiarity_index: ExactFamiliarityIndex,
    retrieval_context: IntegratedRetrievalContext,
    expansion_profile: ExpansionProfile,
    procedure_library: ProcedureLibrary,
    procedure_executor_factory: ContextBoundProcedureExecutorFactory,
    model_adapter: ModelAdapter | None = None,
    memory_context_provider: MemoryContextProvider | None = None,
    expected_final_world_state_ref: str,
    same_name_expected_ids: tuple[str, ...] = (),
) -> ComparisonRunResult:
    del familiarity_index
    return _run_a009_variant(
        variant=ComparisonVariant.ASCA_FAMILIARITY_DISABLED,
        policy=LoopPolicy.MISMATCH_DRIVEN_RECOVERY,
        request=request,
        familiarity_index=ExactFamiliarityIndex(()),
        retrieval_context=retrieval_context,
        expansion_profile=expansion_profile,
        procedure_library=procedure_library,
        procedure_executor_factory=procedure_executor_factory,
        model_adapter=model_adapter,
        memory_context_provider=memory_context_provider,
        expected_final_world_state_ref=expected_final_world_state_ref,
        same_name_expected_ids=same_name_expected_ids,
    )


def run_no_structural_expansion_ablation(
    *,
    request: CognitiveLoopRequest,
    familiarity_index: ExactFamiliarityIndex,
    retrieval_context: IntegratedRetrievalContext,
    expansion_profile: ExpansionProfile,
    procedure_library: ProcedureLibrary,
    procedure_executor_factory: ContextBoundProcedureExecutorFactory,
    model_adapter: ModelAdapter | None = None,
    memory_context_provider: MemoryContextProvider | None = None,
    expected_final_world_state_ref: str,
    same_name_expected_ids: tuple[str, ...] = (),
) -> ComparisonRunResult:
    del model_adapter, memory_context_provider
    if not isinstance(request, CognitiveLoopRequest):
        raise ValueError("request must be a CognitiveLoopRequest")
    if not isinstance(retrieval_context, IntegratedRetrievalContext):
        raise ValueError(
            "retrieval_context must be an IntegratedRetrievalContext"
        )
    if not isinstance(familiarity_index, ExactFamiliarityIndex):
        raise ValueError("familiarity_index must be an ExactFamiliarityIndex")
    if not isinstance(expansion_profile, ExpansionProfile):
        raise ValueError("expansion_profile must be an ExpansionProfile")
    if len(expansion_profile.scopes) > 3:
        raise ValueError("A010 structural ablation supports at most three scopes")
    if not isinstance(procedure_library, ProcedureLibrary):
        raise ValueError("procedure_library must be a ProcedureLibrary")
    if not isinstance(
        procedure_executor_factory,
        ContextBoundProcedureExecutorFactory,
    ):
        raise ValueError(
            "procedure_executor_factory must be a ContextBoundProcedureExecutorFactory"
        )
    procedure_library.get(request.root_procedure_id)
    require_nonempty(
        "expected_final_world_state_ref", expected_final_world_state_ref
    )
    familiarity_index.assess(request.familiarity_cue)

    initial = run_initial_integrated_expansion(
        retrieval_context,
        profile=expansion_profile,
        policy=ExpansionPolicy.NO_EXPANSION,
    )
    evaluations = list(initial.evaluations)
    current = evaluations[-1]
    executions = []
    execution_ids: list[str] = []

    while len(executions) < 3:
        attempt_index = len(executions)
        execution_id = (
            f"a010:{request.loop_id.removeprefix('a009:').split(':', 1)[0]}"
            f":no-structural:procedure-attempt:{attempt_index}"
        )
        selected_ids = tuple(
            entry.ref_id
            for entry in current.working_set_result.working_set.entries
        )
        executor = procedure_executor_factory.create(
            available_memory_ids=selected_ids,
            execution_id=execution_id,
        )
        execution = run_procedure(
            procedure_library,
            root_procedure_id=request.root_procedure_id,
            mode=ProcedureExecutionMode.CHUNKED,
            executor=executor,
            execution_id=execution_id,
        )
        executions.append(execution)
        execution_ids.append(execution_id)
        if execution.state is ProcedureExecutionState.COMPLETED:
            break
        current_index = current.scope.round_index
        if current_index >= len(expansion_profile.scopes) - 1:
            break
        next_scope = expansion_profile.scopes[current_index + 1]
        current = evaluate_integrated_scope(retrieval_context, next_scope)
        evaluations.append(current)

    metrics = _evaluation_metrics(tuple(evaluations))
    final_execution = executions[-1]
    selected_ids = tuple(
        entry.ref_id
        for entry in evaluations[-1].working_set_result.working_set.entries
    )
    success = final_execution.state is ProcedureExecutionState.COMPLETED
    trace_signature = (
        ("INITIAL_POLICY", ("policy:NO_EXPANSION",)),
        *tuple(
            ("SCOPE_EVALUATED", (f"scope:{item.scope.round_index}",))
            for item in evaluations
        ),
        *tuple(
            (
                "PROCEDURE_ATTEMPT",
                (
                    f"execution:{execution_id}",
                    f"state:{execution.state.value}",
                ),
            )
            for execution_id, execution in zip(execution_ids, executions)
        ),
    )
    return ComparisonRunResult(
        variant=ComparisonVariant.ASCA_NO_STRUCTURAL_EXPANSION,
        case_id=(
            request.loop_id.removeprefix("a009:").split(":", 1)[0]
            if request.loop_id.startswith("a009:")
            else request.loop_id
        ),
        procedure_success=success,
        final_state_correct=(
            success
            and final_execution.final_world_state_ref
            == expected_final_world_state_ref
        ),
        final_world_state_ref=final_execution.final_world_state_ref,
        evaluated_scope_indices=tuple(
            item.scope.round_index for item in evaluations
        ),
        final_selected_memory_ids=selected_ids,
        procedure_attempt_count=len(executions),
        execution_ids=tuple(execution_ids),
        procedure_states=tuple(item.state.value for item in executions),
        mismatch_count=sum(
            item.state is ProcedureExecutionState.INTERRUPTED
            for item in executions
        ),
        forced_recovery_scope_count=max(0, len(evaluations) - 1),
        same_name_identity_preserved=_same_name_preserved(
            same_name_expected_ids,
            selected_ids,
        ),
        trace_signature=trace_signature,
        **metrics,
    )
