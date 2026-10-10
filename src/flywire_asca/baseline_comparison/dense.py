from __future__ import annotations

from dataclasses import dataclass

from flywire_asca.contracts.validation import require_nonempty
from flywire_asca.integrated_loop import (
    ContextBoundProcedureExecutorFactory,
    IntegratedRetrievalContext,
)
from flywire_asca.procedural_memory import (
    ProcedureExecutionMode,
    ProcedureExecutionState,
    ProcedureLibrary,
    run_procedure,
)
from flywire_asca.selective_activation import (
    SelectiveRetrievalEvidence,
    SelectiveWorkingSetResult,
    select_exhaustive,
)
from flywire_asca.vector_memory import VectorMemoryQuery, VectorMemoryResult

from .models import ComparisonRunResult, ComparisonVariant


@dataclass(frozen=True, slots=True)
class DenseRetrievalEvaluation:
    retrieval_results: tuple[VectorMemoryResult, ...]
    working_set_result: SelectiveWorkingSetResult


def evaluate_dense_exhaustive(
    context: IntegratedRetrievalContext,
) -> DenseRetrievalEvaluation:
    if not isinstance(context, IntegratedRetrievalContext):
        raise ValueError("context must be an IntegratedRetrievalContext")

    enabled_cues = tuple(
        cue
        for tier in context.cue_tiers
        for cue in tier.cues
    )
    top_k = max(1, context.index.document_count)
    results = tuple(
        context.index.search(
            VectorMemoryQuery(
                query_id=cue.query_id,
                query_text=cue.query_text,
                top_k=top_k,
                minimum_similarity=context.minimum_similarity,
            )
        )
        for cue in enabled_cues
    )
    evidence = tuple(
        SelectiveRetrievalEvidence(cue.source_cue_id, result)
        for cue, result in zip(enabled_cues, results)
    )
    return DenseRetrievalEvaluation(
        retrieval_results=results,
        working_set_result=select_exhaustive(evidence),
    )


def run_dense_exhaustive(
    *,
    case_id: str,
    root_procedure_id: str,
    retrieval_context: IntegratedRetrievalContext,
    procedure_library: ProcedureLibrary,
    procedure_executor_factory: ContextBoundProcedureExecutorFactory,
    same_name_expected_ids: tuple[str, ...] = (),
) -> ComparisonRunResult:
    require_nonempty("case_id", case_id)
    require_nonempty("root_procedure_id", root_procedure_id)
    if not isinstance(retrieval_context, IntegratedRetrievalContext):
        raise ValueError(
            "retrieval_context must be an IntegratedRetrievalContext"
        )
    if not isinstance(procedure_library, ProcedureLibrary):
        raise ValueError("procedure_library must be a ProcedureLibrary")
    if not isinstance(
        procedure_executor_factory,
        ContextBoundProcedureExecutorFactory,
    ):
        raise ValueError(
            "procedure_executor_factory must be a ContextBoundProcedureExecutorFactory"
        )
    procedure_library.get(root_procedure_id)

    evaluation = evaluate_dense_exhaustive(retrieval_context)
    selected_ids = tuple(
        entry.ref_id
        for entry in evaluation.working_set_result.working_set.entries
    )
    execution_id = f"a010:{case_id}:dense:procedure-attempt:0"
    executor = procedure_executor_factory.create(
        available_memory_ids=selected_ids,
        execution_id=execution_id,
    )
    execution = run_procedure(
        procedure_library,
        root_procedure_id=root_procedure_id,
        mode=ProcedureExecutionMode.CHUNKED,
        executor=executor,
        execution_id=execution_id,
    )
    success = execution.state is ProcedureExecutionState.COMPLETED
    mismatch_count = int(
        execution.state is ProcedureExecutionState.INTERRUPTED
    )
    same_name_preserved = (
        True
        if not same_name_expected_ids
        else set(same_name_expected_ids).issubset(selected_ids)
    )
    results = evaluation.retrieval_results
    ws = evaluation.working_set_result
    scope_index = len(retrieval_context.cue_tiers) - 1
    trace_signature = (
        (
            "DENSE_RETRIEVAL",
            (
                f"scope:{scope_index}",
                f"queries:{len(results)}",
                f"selected:{ws.selected_count}",
            ),
        ),
        (
            "PROCEDURE_ATTEMPT",
            (
                f"execution:{execution_id}",
                f"state:{execution.state.value}",
            ),
        ),
    )
    return ComparisonRunResult(
        variant=ComparisonVariant.DENSE_EXHAUSTIVE,
        case_id=case_id,
        procedure_success=success,
        final_state_correct=success,
        final_world_state_ref=execution.final_world_state_ref,
        evaluated_scope_indices=(scope_index,),
        query_count=len(results),
        stored_count_sum=sum(item.stored_count for item in results),
        metadata_eligible_count_sum=sum(
            item.metadata_eligible_count for item in results
        ),
        scored_vector_count_sum=sum(
            item.scored_vector_count for item in results
        ),
        above_threshold_count_sum=sum(
            item.above_threshold_count for item in results
        ),
        returned_count_sum=sum(item.returned_count for item in results),
        cumulative_unique_candidate_count=ws.unique_candidate_count,
        cumulative_activated_candidate_count=ws.activated_candidate_count,
        cumulative_selected_count=ws.selected_count,
        peak_selected_count=ws.selected_count,
        final_selected_memory_ids=selected_ids,
        procedure_attempt_count=1,
        execution_ids=(execution_id,),
        procedure_states=(execution.state.value,),
        mismatch_count=mismatch_count,
        forced_recovery_scope_count=0,
        same_name_identity_preserved=same_name_preserved,
        trace_signature=trace_signature,
    )
