from __future__ import annotations

from collections import Counter

import pytest

from flywire_asca.contracts import (
    ActivationBudget,
    ActivationState,
    MemoryKind,
    RetrievalState,
    WorkingSet,
    WorkingSetEntry,
    WorkingSetKind,
)
from flywire_asca.selective_activation import (
    MemoryActivationSupport,
    SelectiveWorkingSetResult,
)
from flywire_asca.uncertainty_expansion import (
    ExpansionDecisionKind,
    ExpansionPolicy,
    ExpansionRunResult,
    ExpansionRoundResult,
    ExpansionTerminationReason,
    build_a007_primary_profile,
    run_expansion_policy,
)


def _support(memory_id: str):
    return MemoryActivationSupport(
        memory_id=memory_id,
        source_cue_ids=("cue",),
        similarities=(0.8,),
        support_count=1,
        max_similarity=0.8,
        activation=0.8,
        memory_kind=MemoryKind.SEMANTIC,
        proposition_confidence=0.5,
        evidence_ids=(),
        entity_ids=(),
        context_tags=(),
        source_tags=(),
    )


def _result(state: RetrievalState, *, round_index: int):
    if state is RetrievalState.RECALLED:
        support = _support(f"m{round_index}")
        budget = ActivationBudget(1, 0, 1, 0, 0)
        return SelectiveWorkingSetResult(
            working_set=WorkingSet(
                (
                    WorkingSetEntry(
                        support.memory_id,
                        WorkingSetKind.MEMORY,
                        support.activation,
                        "single_cue_support",
                    ),
                ),
                RetrievalState.RECALLED,
                budget,
            ),
            activation_states=(
                ActivationState(
                    support.memory_id,
                    support.activation,
                    0,
                    ("cue",),
                ),
            ),
            supports=(support,),
            input_result_count=1,
            input_hit_count=1,
            unique_candidate_count=1,
            positive_candidate_count=1,
            activated_candidate_count=1,
            selected_count=1,
            dropped_by_memory_budget_count=0,
            dropped_by_working_set_budget_count=0,
            memory_budget_boundary_tie=False,
            working_set_boundary_tie=False,
            embedding_model_name="embedder",
            embedding_model_digest="digest",
            embedding_profile="profile",
        )

    if state is RetrievalState.INSUFFICIENT_EVIDENCE:
        budget = ActivationBudget(1, 0, 1, 0, 0)
        return SelectiveWorkingSetResult(
            working_set=WorkingSet((), state, budget),
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
            embedding_model_name="embedder",
            embedding_model_digest="digest",
            embedding_profile="profile",
        )

    raise AssertionError(state)


def _evaluator(states, calls):
    def evaluate(scope):
        calls.append(scope.round_index)
        return _result(states[scope.round_index], round_index=scope.round_index)
    return evaluate


def test_signal_driven_stops_at_round_zero_without_speculative_calls():
    calls = []
    run = run_expansion_policy(
        build_a007_primary_profile(),
        policy=ExpansionPolicy.SIGNAL_DRIVEN,
        evaluate_scope=_evaluator({0: RetrievalState.RECALLED}, calls),
    )
    assert calls == [0]
    assert len(run.rounds) == 1
    assert run.final_assessment.kind is ExpansionDecisionKind.STOP
    assert run.termination_reason is ExpansionTerminationReason.CONTROLLER_STOP


def test_signal_driven_expands_once_then_stops():
    calls = []
    run = run_expansion_policy(
        build_a007_primary_profile(),
        policy=ExpansionPolicy.SIGNAL_DRIVEN,
        evaluate_scope=_evaluator(
            {
                0: RetrievalState.INSUFFICIENT_EVIDENCE,
                1: RetrievalState.RECALLED,
            },
            calls,
        ),
    )
    assert calls == [0, 1]
    assert [item.scope.round_index for item in run.rounds] == [0, 1]
    assert run.rounds[0].assessment.kind is ExpansionDecisionKind.EXPAND
    assert run.rounds[1].assessment.kind is ExpansionDecisionKind.STOP
    assert run.termination_reason is ExpansionTerminationReason.CONTROLLER_STOP


def test_signal_driven_exhausts_at_round_two_and_never_calls_round_three():
    calls = []
    run = run_expansion_policy(
        build_a007_primary_profile(),
        policy=ExpansionPolicy.SIGNAL_DRIVEN,
        evaluate_scope=_evaluator(
            {
                0: RetrievalState.INSUFFICIENT_EVIDENCE,
                1: RetrievalState.INSUFFICIENT_EVIDENCE,
                2: RetrievalState.INSUFFICIENT_EVIDENCE,
            },
            calls,
        ),
    )
    assert calls == [0, 1, 2]
    assert max(calls) == 2
    assert run.final_assessment.kind is ExpansionDecisionKind.EXHAUSTED
    assert run.termination_reason is ExpansionTerminationReason.CONTROLLER_EXHAUSTED


def test_no_expansion_stops_by_policy_even_when_assessment_wants_expand():
    calls = []
    run = run_expansion_policy(
        build_a007_primary_profile(),
        policy=ExpansionPolicy.NO_EXPANSION,
        evaluate_scope=_evaluator(
            {0: RetrievalState.INSUFFICIENT_EVIDENCE},
            calls,
        ),
    )
    assert calls == [0]
    assert run.final_assessment.kind is ExpansionDecisionKind.EXPAND
    assert run.termination_reason is ExpansionTerminationReason.POLICY_NO_EXPANSION


def test_always_expand_evaluates_all_scopes_even_when_assessments_stop():
    calls = []
    run = run_expansion_policy(
        build_a007_primary_profile(),
        policy=ExpansionPolicy.ALWAYS_EXPAND,
        evaluate_scope=_evaluator(
            {
                0: RetrievalState.RECALLED,
                1: RetrievalState.RECALLED,
                2: RetrievalState.RECALLED,
            },
            calls,
        ),
    )
    assert calls == [0, 1, 2]
    assert all(
        item.assessment.kind is ExpansionDecisionKind.STOP
        for item in run.rounds
    )
    assert run.final_assessment.kind is ExpansionDecisionKind.STOP
    assert run.termination_reason is ExpansionTerminationReason.POLICY_MAX_SCOPE


def test_each_policy_evaluates_each_selected_scope_exactly_once():
    for policy, expected in (
        (ExpansionPolicy.NO_EXPANSION, [0]),
        (ExpansionPolicy.SIGNAL_DRIVEN, [0, 1, 2]),
        (ExpansionPolicy.ALWAYS_EXPAND, [0, 1, 2]),
    ):
        calls = []
        run_expansion_policy(
            build_a007_primary_profile(),
            policy=policy,
            evaluate_scope=_evaluator(
                {
                    0: RetrievalState.INSUFFICIENT_EVIDENCE,
                    1: RetrievalState.INSUFFICIENT_EVIDENCE,
                    2: RetrievalState.INSUFFICIENT_EVIDENCE,
                },
                calls,
            ),
        )
        assert calls == expected
        assert Counter(calls) == Counter({index: 1 for index in expected})


def test_repeated_deterministic_execution_is_logically_equal():
    profile = build_a007_primary_profile()

    first_calls = []
    first = run_expansion_policy(
        profile,
        policy=ExpansionPolicy.SIGNAL_DRIVEN,
        evaluate_scope=_evaluator(
            {
                0: RetrievalState.INSUFFICIENT_EVIDENCE,
                1: RetrievalState.RECALLED,
            },
            first_calls,
        ),
    )
    second_calls = []
    second = run_expansion_policy(
        profile,
        policy=ExpansionPolicy.SIGNAL_DRIVEN,
        evaluate_scope=_evaluator(
            {
                0: RetrievalState.INSUFFICIENT_EVIDENCE,
                1: RetrievalState.RECALLED,
            },
            second_calls,
        ),
    )
    assert first == second
    assert first_calls == second_calls == [0, 1]


def test_run_record_contract_rejects_mismatched_final_values_and_termination():
    profile = build_a007_primary_profile()
    calls = []
    good = run_expansion_policy(
        profile,
        policy=ExpansionPolicy.SIGNAL_DRIVEN,
        evaluate_scope=_evaluator({0: RetrievalState.RECALLED}, calls),
    )
    round0 = good.rounds[0]

    with pytest.raises(ValueError, match="final_result"):
        ExpansionRunResult(
            policy=good.policy,
            rounds=good.rounds,
            final_result=_result(RetrievalState.RECALLED, round_index=9),
            final_assessment=good.final_assessment,
            termination_reason=good.termination_reason,
        )

    with pytest.raises(ValueError, match="termination_reason"):
        ExpansionRunResult(
            policy=ExpansionPolicy.SIGNAL_DRIVEN,
            rounds=good.rounds,
            final_result=good.final_result,
            final_assessment=good.final_assessment,
            termination_reason=ExpansionTerminationReason.POLICY_NO_EXPANSION,
        )

    with pytest.raises(ValueError, match="assessment"):
        ExpansionRoundResult(
            scope=profile.scopes[1],
            working_set_result=round0.working_set_result,
            assessment=round0.assessment,
        )


def test_runner_rejects_non_callable_evaluator_and_wrong_return_type():
    profile = build_a007_primary_profile()
    with pytest.raises(ValueError, match="evaluate_scope"):
        run_expansion_policy(
            profile,
            policy=ExpansionPolicy.SIGNAL_DRIVEN,
            evaluate_scope=None,  # type: ignore[arg-type]
        )

    with pytest.raises(ValueError, match="SelectiveWorkingSetResult"):
        run_expansion_policy(
            profile,
            policy=ExpansionPolicy.SIGNAL_DRIVEN,
            evaluate_scope=lambda scope: object(),  # type: ignore[return-value]
        )
