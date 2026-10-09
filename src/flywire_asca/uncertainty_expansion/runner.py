from __future__ import annotations

from collections.abc import Callable

from flywire_asca.selective_activation import SelectiveWorkingSetResult

from .controller import assess_expansion
from .models import (
    ExpansionDecisionKind,
    ExpansionPolicy,
    ExpansionProfile,
    ExpansionRoundResult,
    ExpansionScope,
    ExpansionRunResult,
    ExpansionTerminationReason,
)


def _evaluate_round(
    profile: ExpansionProfile,
    index: int,
    evaluate_scope: Callable[[ExpansionScope], SelectiveWorkingSetResult],
) -> ExpansionRoundResult:
    scope = profile.scopes[index]
    result = evaluate_scope(scope)
    if not isinstance(result, SelectiveWorkingSetResult):
        raise ValueError(
            "evaluate_scope must return a SelectiveWorkingSetResult"
        )
    next_scope = (
        profile.scopes[index + 1]
        if index + 1 < len(profile.scopes)
        else None
    )
    assessment = assess_expansion(
        result,
        current_scope=scope,
        next_scope=next_scope,
    )
    return ExpansionRoundResult(
        scope=scope,
        working_set_result=result,
        assessment=assessment,
    )


def run_expansion_policy(
    profile: ExpansionProfile,
    *,
    policy: ExpansionPolicy,
    evaluate_scope: Callable[[ExpansionScope], SelectiveWorkingSetResult],
) -> ExpansionRunResult:
    if not isinstance(profile, ExpansionProfile):
        raise ValueError("profile must be an ExpansionProfile")
    if not isinstance(policy, ExpansionPolicy):
        raise ValueError("policy must be an ExpansionPolicy")
    if not callable(evaluate_scope):
        raise ValueError("evaluate_scope must be callable")

    rounds: list[ExpansionRoundResult] = []

    if policy is ExpansionPolicy.NO_EXPANSION:
        rounds.append(_evaluate_round(profile, 0, evaluate_scope))
        final = rounds[-1]
        return ExpansionRunResult(
            policy=policy,
            rounds=tuple(rounds),
            final_result=final.working_set_result,
            final_assessment=final.assessment,
            termination_reason=ExpansionTerminationReason.POLICY_NO_EXPANSION,
        )

    if policy is ExpansionPolicy.ALWAYS_EXPAND:
        for index in range(len(profile.scopes)):
            rounds.append(_evaluate_round(profile, index, evaluate_scope))
        final = rounds[-1]
        return ExpansionRunResult(
            policy=policy,
            rounds=tuple(rounds),
            final_result=final.working_set_result,
            final_assessment=final.assessment,
            termination_reason=ExpansionTerminationReason.POLICY_MAX_SCOPE,
        )

    if policy is ExpansionPolicy.SIGNAL_DRIVEN:
        for index in range(len(profile.scopes)):
            round_result = _evaluate_round(profile, index, evaluate_scope)
            rounds.append(round_result)
            kind = round_result.assessment.kind
            if kind is ExpansionDecisionKind.STOP:
                return ExpansionRunResult(
                    policy=policy,
                    rounds=tuple(rounds),
                    final_result=round_result.working_set_result,
                    final_assessment=round_result.assessment,
                    termination_reason=(
                        ExpansionTerminationReason.CONTROLLER_STOP
                    ),
                )
            if kind is ExpansionDecisionKind.EXHAUSTED:
                return ExpansionRunResult(
                    policy=policy,
                    rounds=tuple(rounds),
                    final_result=round_result.working_set_result,
                    final_assessment=round_result.assessment,
                    termination_reason=(
                        ExpansionTerminationReason.CONTROLLER_EXHAUSTED
                    ),
                )
            if kind is not ExpansionDecisionKind.EXPAND:
                raise ValueError("unsupported expansion assessment")
        raise ValueError("SIGNAL_DRIVEN exceeded profile without termination")

    raise ValueError("unsupported ExpansionPolicy")