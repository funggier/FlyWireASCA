from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from flywire_asca.contracts import (
    ActivationBudget,
    Cue,
    CueKind,
    Observation,
    ObservationKind,
    RetrievalState,
    WorkingSet,
)
from flywire_asca.familiarity import FamiliarityCost, FamiliarityResult
from flywire_asca.model import ModelResponse
from flywire_asca.procedural_memory import (
    ExpectedOutcome,
    ProcedureExecutionMetrics,
    ProcedureExecutionMode,
    ProcedureExecutionResult,
    ProcedureExecutionState,
    ProcedureInterruption,
)
from flywire_asca.selective_activation import SelectiveWorkingSetResult
from flywire_asca.uncertainty_expansion import (
    ExpansionDecision,
    ExpansionDecisionKind,
    ExpansionPolicy,
    ExpansionRoundResult,
    ExpansionRunResult,
    ExpansionScope,
    ExpansionTerminationReason,
)

from flywire_asca.integrated_loop import (
    CognitiveLoopPhase,
    CognitiveLoopRequest,
    CognitiveLoopResult,
    CognitiveProcedureAttempt,
    CognitiveTerminationReason,
    CognitiveTraceEvent,
    CognitiveTraceEventKind,
    IntegratedExpansionResult,
    IntegratedScopeEvaluation,
    LoopPolicy,
    ModelUsePolicy,
    RecoveryCause,
)
from flywire_asca.vector_memory import VectorMemoryResult


def _scope(index: int = 0) -> ExpansionScope:
    profiles = (
        (1, 12, 8, 4),
        (2, 24, 12, 8),
        (3, 32, 16, 12),
    )
    tiers, top_k, memory, working = profiles[index]
    return ExpansionScope(
        index,
        tiers,
        top_k,
        ActivationBudget(memory, 0, working, 0, 0),
    )


def _vector(query_id: str = "q") -> VectorMemoryResult:
    return VectorMemoryResult(
        query_id=query_id,
        hits=(),
        stored_count=0,
        metadata_eligible_count=0,
        scored_vector_count=0,
        above_threshold_count=0,
        returned_count=0,
        embedding_model_name="portable-embedder",
        embedding_model_digest="portable-digest",
        embedding_profile="a009-portable",
    )


def _working(scope: ExpansionScope | None = None) -> SelectiveWorkingSetResult:
    scope = scope or _scope(0)
    working_set = WorkingSet((), RetrievalState.INSUFFICIENT_EVIDENCE, scope.budget)
    return SelectiveWorkingSetResult(
        working_set=working_set,
        activation_states=(),
        supports=(),
        input_result_count=1,
        input_hit_count=0,
        unique_candidate_count=0,
        positive_candidate_count=0,
        activated_candidate_count=0,
        selected_count=0,
        dropped_by_memory_budget_count=0,
        dropped_by_working_set_budget_count=0,
        memory_budget_boundary_tie=False,
        working_set_boundary_tie=False,
        embedding_model_name="portable-embedder",
        embedding_model_digest="portable-digest",
        embedding_profile="a009-portable",
    )


def _evaluation(index: int = 0) -> IntegratedScopeEvaluation:
    scope = _scope(index)
    return IntegratedScopeEvaluation(scope, (_vector(f"q-{index}"),), _working(scope))


def _initial_expansion() -> IntegratedExpansionResult:
    evaluation = _evaluation(0)
    decision = ExpansionDecision(
        0,
        ExpansionDecisionKind.STOP,
        (),
        evaluation.scope,
        None,
    )
    round_result = ExpansionRoundResult(
        evaluation.scope,
        evaluation.working_set_result,
        decision,
    )
    run = ExpansionRunResult(
        ExpansionPolicy.NO_EXPANSION,
        (round_result,),
        evaluation.working_set_result,
        decision,
        ExpansionTerminationReason.POLICY_NO_EXPANSION,
    )
    return IntegratedExpansionResult(run, (evaluation,))


def _familiarity() -> FamiliarityResult:
    return FamiliarityResult(
        cue_id="cue",
        retrieval_state=RetrievalState.UNFAMILIAR,
        familiarity_score=0.0,
        candidate_region_ids=(),
        matched_trace_ids=(),
        cost=FamiliarityCost(1, 0, 0),
    )


def _execution(
    execution_id: str,
    state: ProcedureExecutionState = ProcedureExecutionState.COMPLETED,
) -> ProcedureExecutionResult:
    interruption = None
    if state is ProcedureExecutionState.INTERRUPTED:
        expected = ExpectedOutcome("expected", ObservationKind.RESULT, "ok")
        observed = Observation("observed", ObservationKind.RESULT, "missing")
        interruption = ProcedureInterruption(
            root_procedure_id="root",
            failing_procedure_id="root",
            failing_step_id="step",
            call_path=("root",),
            expected_outcome=expected,
            observed=observed,
            explanation_memory_ids=(),
            completed_primitive_step_paths=(),
        )
    return ProcedureExecutionResult(
        execution_id=execution_id,
        root_procedure_id="root",
        mode=ProcedureExecutionMode.CHUNKED,
        state=state,
        step_results=(),
        interruption=interruption,
        final_world_state_ref=f"world:{execution_id}",
        metrics=ProcedureExecutionMetrics(0, 0, 0, 0, 0, 0, 1),
    )


def _attempt(
    index: int,
    *,
    scope_index: int | None = None,
    state: ProcedureExecutionState = ProcedureExecutionState.COMPLETED,
    execution_id: str | None = None,
) -> CognitiveProcedureAttempt:
    scope_index = index if scope_index is None else scope_index
    execution_id = execution_id or f"loop:procedure-attempt:{index}"
    return CognitiveProcedureAttempt(
        attempt_index=index,
        execution_id=execution_id,
        scope=_scope(scope_index),
        working_set_memory_ids=(),
        execution=_execution(execution_id, state),
        recovery_cause=(
            None if index == 0 else RecoveryCause.PROCEDURE_OUTCOME_MISMATCH
        ),
        initial_world_state_ref="world:initial",
    )


def _trace() -> tuple[CognitiveTraceEvent, ...]:
    return (
        CognitiveTraceEvent(0, CognitiveTraceEventKind.FAMILIARITY_ASSESSED, ("cue",)),
        CognitiveTraceEvent(
            1,
            CognitiveTraceEventKind.TERMINAL_STATE_REACHED,
            ("PROCEDURE_COMPLETED",),
        ),
    )


def test_enum_vocabularies_are_exact():
    assert tuple(item.value for item in CognitiveLoopPhase) == (
        "FAMILIARITY",
        "INITIAL_EXPANSION",
        "PROCEDURE_EXECUTION",
        "RECOVERY_EXPANSION",
        "MODEL_FALLBACK",
        "TERMINAL",
    )
    assert tuple(item.value for item in RecoveryCause) == (
        "PROCEDURE_OUTCOME_MISMATCH",
    )
    assert tuple(item.value for item in LoopPolicy) == (
        "NO_PROCEDURE_RECOVERY",
        "MISMATCH_DRIVEN_RECOVERY",
        "ALWAYS_MAX_SCOPE",
    )
    assert tuple(item.value for item in ModelUsePolicy) == (
        "DISABLED",
        "TERMINAL_ONLY",
    )
    assert tuple(item.value for item in CognitiveTerminationReason) == (
        "PROCEDURE_COMPLETED",
        "RECOVERED_AFTER_MISMATCH",
        "PROCEDURE_MISMATCH_EXHAUSTED",
    )
    assert tuple(item.value for item in CognitiveTraceEventKind) == (
        "FAMILIARITY_ASSESSED",
        "INITIAL_EXPANSION_SCOPE_EVALUATED",
        "INITIAL_EXPANSION_TERMINATED",
        "ROOT_PROCEDURE_SELECTED",
        "PROCEDURE_ATTEMPT_STARTED",
        "PROCEDURE_COMPLETED",
        "PROCEDURE_MISMATCH_OBSERVED",
        "RECOVERY_SCOPE_FORCED",
        "MODEL_FALLBACK_INVOKED",
        "TERMINAL_STATE_REACHED",
    )


def test_request_is_frozen_and_uses_real_cue_contract():
    request = CognitiveLoopRequest(
        "loop",
        "make tea",
        Cue("cue", CueKind.TEXT, "make tea", 1.0),
        "root",
        LoopPolicy.MISMATCH_DRIVEN_RECOVERY,
        ModelUsePolicy.DISABLED,
    )
    assert request.familiarity_cue.cue_id == "cue"
    with pytest.raises(FrozenInstanceError):
        request.goal_text = "other"  # type: ignore[misc]
    with pytest.raises(ValueError, match="loop_id"):
        CognitiveLoopRequest(
            "",
            "goal",
            request.familiarity_cue,
            "root",
            request.policy,
            request.model_use_policy,
        )
    with pytest.raises(ValueError, match="goal_text"):
        CognitiveLoopRequest(
            "loop",
            "",
            request.familiarity_cue,
            "root",
            request.policy,
            request.model_use_policy,
        )
    with pytest.raises(ValueError, match="familiarity_cue"):
        CognitiveLoopRequest(
            "loop",
            "goal",
            object(),  # type: ignore[arg-type]
            "root",
            request.policy,
            request.model_use_policy,
        )


def test_scope_and_expansion_records_use_existing_evidence_types():
    evaluation = _evaluation()
    assert isinstance(evaluation.scope, ExpansionScope)
    assert isinstance(evaluation.retrieval_results[0], VectorMemoryResult)
    assert isinstance(evaluation.working_set_result, SelectiveWorkingSetResult)

    expansion = _initial_expansion()
    assert isinstance(expansion.run, ExpansionRunResult)
    assert expansion.evaluations[0].scope == expansion.run.rounds[0].scope

    with pytest.raises(ValueError, match="evaluation"):
        IntegratedExpansionResult(expansion.run, ())


def test_procedure_attempt_requires_chunked_execution_and_canonical_identity():
    attempt = _attempt(0)
    assert attempt.execution.mode is ProcedureExecutionMode.CHUNKED
    with pytest.raises(ValueError, match="execution_id"):
        CognitiveProcedureAttempt(
            0,
            "different",
            attempt.scope,
            (),
            attempt.execution,
            None,
            "world:initial",
        )
    with pytest.raises(ValueError, match="recovery_cause"):
        CognitiveProcedureAttempt(
            1,
            "loop:procedure-attempt:1",
            _scope(1),
            (),
            _execution(
                "loop:procedure-attempt:1",
                ProcedureExecutionState.INTERRUPTED,
            ),
            None,
            "world:initial",
        )
    with pytest.raises(ValueError, match="working_set_memory_ids"):
        CognitiveProcedureAttempt(
            0,
            "loop:procedure-attempt:0",
            _scope(0),
            ("m1", "m1"),
            _execution("loop:procedure-attempt:0"),
            None,
            "world:initial",
        )


def test_trace_requires_contiguous_nonnegative_sequence_and_unique_refs():
    event = CognitiveTraceEvent(
        0,
        CognitiveTraceEventKind.FAMILIARITY_ASSESSED,
        ("cue",),
    )
    assert event.sequence == 0
    with pytest.raises(ValueError, match="sequence"):
        CognitiveTraceEvent(-1, event.kind, ())
    with pytest.raises(ValueError, match="refs"):
        CognitiveTraceEvent(0, event.kind, ("x", "x"))


def test_loop_result_rejects_duplicate_ids_noncontiguous_attempts_and_post_completion():
    initial = _initial_expansion()
    completed = _attempt(0)
    result = CognitiveLoopResult(
        loop_id="loop",
        policy=LoopPolicy.MISMATCH_DRIVEN_RECOVERY,
        familiarity=_familiarity(),
        initial_expansion=initial,
        scope_evaluations=initial.evaluations,
        procedure_attempts=(completed,),
        termination_reason=CognitiveTerminationReason.PROCEDURE_COMPLETED,
        final_working_set=initial.evaluations[-1].working_set_result.working_set,
        final_world_state_ref=completed.execution.final_world_state_ref,
        model_response=None,
        trace=_trace(),
    )
    assert result.procedure_attempts == (completed,)

    interrupted = _attempt(0, state=ProcedureExecutionState.INTERRUPTED)
    noncontiguous = _attempt(
        2,
        scope_index=1,
        state=ProcedureExecutionState.COMPLETED,
    )
    with pytest.raises(ValueError, match="contiguous"):
        CognitiveLoopResult(
            "loop",
            LoopPolicy.MISMATCH_DRIVEN_RECOVERY,
            _familiarity(),
            initial,
            initial.evaluations,
            (interrupted, noncontiguous),
            CognitiveTerminationReason.RECOVERED_AFTER_MISMATCH,
            initial.evaluations[-1].working_set_result.working_set,
            noncontiguous.execution.final_world_state_ref,
            None,
            _trace(),
        )

    duplicate = _attempt(
        1,
        scope_index=1,
        state=ProcedureExecutionState.COMPLETED,
        execution_id=interrupted.execution_id,
    )
    with pytest.raises(ValueError, match="execution_id"):
        CognitiveLoopResult(
            "loop",
            LoopPolicy.MISMATCH_DRIVEN_RECOVERY,
            _familiarity(),
            initial,
            initial.evaluations,
            (interrupted, duplicate),
            CognitiveTerminationReason.RECOVERED_AFTER_MISMATCH,
            initial.evaluations[-1].working_set_result.working_set,
            duplicate.execution.final_world_state_ref,
            None,
            _trace(),
        )

    later = _attempt(1, scope_index=1)
    with pytest.raises(ValueError, match="after.*COMPLETED"):
        CognitiveLoopResult(
            "loop",
            LoopPolicy.MISMATCH_DRIVEN_RECOVERY,
            _familiarity(),
            initial,
            initial.evaluations,
            (completed, later),
            CognitiveTerminationReason.RECOVERED_AFTER_MISMATCH,
            initial.evaluations[-1].working_set_result.working_set,
            later.execution.final_world_state_ref,
            None,
            _trace(),
        )


def test_loop_result_rejects_scope_regression_and_noncontiguous_trace():
    initial = _initial_expansion()
    first = _attempt(0, scope_index=1, state=ProcedureExecutionState.INTERRUPTED)
    second = _attempt(1, scope_index=0)
    bad_trace = (
        CognitiveTraceEvent(0, CognitiveTraceEventKind.FAMILIARITY_ASSESSED, ()),
        CognitiveTraceEvent(2, CognitiveTraceEventKind.TERMINAL_STATE_REACHED, ()),
    )
    with pytest.raises(ValueError, match="scope"):
        CognitiveLoopResult(
            "loop",
            LoopPolicy.MISMATCH_DRIVEN_RECOVERY,
            _familiarity(),
            initial,
            initial.evaluations,
            (first, second),
            CognitiveTerminationReason.RECOVERED_AFTER_MISMATCH,
            initial.evaluations[-1].working_set_result.working_set,
            second.execution.final_world_state_ref,
            None,
            _trace(),
        )
    with pytest.raises(ValueError, match="trace.*contiguous"):
        CognitiveLoopResult(
            "loop",
            LoopPolicy.MISMATCH_DRIVEN_RECOVERY,
            _familiarity(),
            initial,
            initial.evaluations,
            (_attempt(0),),
            CognitiveTerminationReason.PROCEDURE_COMPLETED,
            initial.evaluations[-1].working_set_result.working_set,
            "world:loop:procedure-attempt:0",
            None,
            bad_trace,
        )


def test_loop_result_model_response_must_be_real_contract():
    initial = _initial_expansion()
    attempt = _attempt(0)
    response = ModelResponse(
        "loop:terminal-model",
        "fake-model",
        "digest",
        "diagnostic",
        "stop",
        1,
        1,
        1,
        0,
        0,
        0,
    )
    result = CognitiveLoopResult(
        "loop",
        LoopPolicy.NO_PROCEDURE_RECOVERY,
        _familiarity(),
        initial,
        initial.evaluations,
        (attempt,),
        CognitiveTerminationReason.PROCEDURE_COMPLETED,
        initial.evaluations[-1].working_set_result.working_set,
        attempt.execution.final_world_state_ref,
        response,
        _trace(),
    )
    assert result.model_response is response
