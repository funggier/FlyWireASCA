from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from flywire_asca.contracts import ActivationBudget
from flywire_asca.uncertainty_expansion import (
    ExpansionDecision,
    ExpansionDecisionKind,
    ExpansionPolicy,
    ExpansionProfile,
    ExpansionScope,
    ExpansionTerminationReason,
    ExpansionTrigger,
    build_a007_primary_profile,
)


def _budget(memory=8, working=4, *, hops=0, expansions=0, model_tokens=0):
    return ActivationBudget(
        max_memory_nodes=memory,
        max_relation_hops=hops,
        max_working_set_items=working,
        max_model_input_tokens=model_tokens,
        max_expansions=expansions,
    )


def _scope(round_index=0, tiers=1, top_k=12, memory=8, working=4):
    return ExpansionScope(
        round_index=round_index,
        enabled_cue_tier_count=tiers,
        top_k=top_k,
        budget=_budget(memory, working),
    )


def test_enum_vocabularies_and_order_are_exact():
    assert tuple(item.value for item in ExpansionTrigger) == (
        "INSUFFICIENT_EVIDENCE",
        "MEMORY_BUDGET_TRUNCATED",
        "WORKING_SET_BUDGET_TRUNCATED",
        "MEMORY_BOUNDARY_TIE",
        "WORKING_SET_BOUNDARY_TIE",
    )
    assert tuple(item.value for item in ExpansionDecisionKind) == (
        "STOP",
        "EXPAND",
        "EXHAUSTED",
    )
    assert tuple(item.value for item in ExpansionPolicy) == (
        "NO_EXPANSION",
        "SIGNAL_DRIVEN",
        "ALWAYS_EXPAND",
    )
    assert tuple(item.value for item in ExpansionTerminationReason) == (
        "CONTROLLER_STOP",
        "CONTROLLER_EXHAUSTED",
        "POLICY_NO_EXPANSION",
        "POLICY_MAX_SCOPE",
    )


def test_expansion_scope_is_frozen_and_validates_budget_boundary():
    scope = _scope()
    assert scope.round_index == 0
    with pytest.raises(FrozenInstanceError):
        scope.top_k = 99  # type: ignore[misc]

    with pytest.raises(ValueError, match="round_index"):
        ExpansionScope(-1, 1, 12, _budget())
    with pytest.raises(ValueError, match="enabled_cue_tier_count"):
        ExpansionScope(0, 0, 12, _budget())
    with pytest.raises(ValueError, match="top_k"):
        ExpansionScope(0, 1, 0, _budget())
    with pytest.raises(ValueError, match="max_working_set_items"):
        ExpansionScope(0, 1, 12, _budget(memory=4, working=5))
    with pytest.raises(ValueError, match="max_relation_hops"):
        ExpansionScope(0, 1, 12, _budget(hops=1))
    with pytest.raises(ValueError, match="max_expansions"):
        ExpansionScope(0, 1, 12, _budget(expansions=1))
    with pytest.raises(ValueError, match="max_model_input_tokens"):
        ExpansionScope(0, 1, 12, _budget(model_tokens=1))


def test_profile_requires_contiguous_monotonic_non_noop_scopes():
    profile = ExpansionProfile(
        "profile",
        (
            _scope(0, 1, 12, 8, 4),
            _scope(1, 2, 24, 12, 8),
            _scope(2, 3, 32, 16, 12),
        ),
    )
    assert tuple(scope.round_index for scope in profile.scopes) == (0, 1, 2)

    with pytest.raises(ValueError, match="profile_name"):
        ExpansionProfile("", (_scope(),))
    with pytest.raises(ValueError, match="scopes"):
        ExpansionProfile("p", ())
    with pytest.raises(ValueError, match="round_index"):
        ExpansionProfile("p", (_scope(1),))
    with pytest.raises(ValueError, match="contiguous"):
        ExpansionProfile("p", (_scope(0), _scope(2, 2, 24, 12, 8)))
    with pytest.raises(ValueError, match="enabled_cue_tier_count"):
        ExpansionProfile("p", (_scope(0, 2, 12, 8, 4), _scope(1, 1, 24, 12, 8)))
    with pytest.raises(ValueError, match="top_k"):
        ExpansionProfile("p", (_scope(0, 1, 24, 8, 4), _scope(1, 2, 12, 12, 8)))
    with pytest.raises(ValueError, match="max_memory_nodes"):
        ExpansionProfile("p", (_scope(0, 1, 12, 12, 4), _scope(1, 2, 24, 8, 8)))
    with pytest.raises(ValueError, match="max_working_set_items"):
        ExpansionProfile("p", (_scope(0, 1, 12, 8, 6), _scope(1, 2, 24, 12, 4)))
    with pytest.raises(ValueError, match="no-op"):
        ExpansionProfile("p", (_scope(0), _scope(1)))


def test_primary_profile_is_frozen_exactly():
    profile = build_a007_primary_profile()
    assert profile.profile_name == "a007-structural-expansion-v1"
    assert [
        (
            scope.round_index,
            scope.enabled_cue_tier_count,
            scope.top_k,
            scope.budget.max_memory_nodes,
            scope.budget.max_working_set_items,
            scope.budget.max_relation_hops,
            scope.budget.max_expansions,
            scope.budget.max_model_input_tokens,
        )
        for scope in profile.scopes
    ] == [
        (0, 1, 12, 8, 4, 0, 0, 0),
        (1, 2, 24, 12, 8, 0, 0, 0),
        (2, 3, 32, 16, 12, 0, 0, 0),
    ]


def test_decision_canonicalizes_triggers_in_explicit_enum_order():
    current = _scope(0)
    nxt = _scope(1, 2, 24, 12, 8)
    decision = ExpansionDecision(
        round_index=0,
        kind=ExpansionDecisionKind.EXPAND,
        triggers=(
            ExpansionTrigger.WORKING_SET_BOUNDARY_TIE,
            ExpansionTrigger.MEMORY_BUDGET_TRUNCATED,
            ExpansionTrigger.MEMORY_BUDGET_TRUNCATED,
        ),
        current_scope=current,
        next_scope=nxt,
    )
    assert decision.triggers == (
        ExpansionTrigger.MEMORY_BUDGET_TRUNCATED,
        ExpansionTrigger.WORKING_SET_BOUNDARY_TIE,
    )


def test_decision_contracts_are_fail_closed():
    current = _scope(0)
    nxt = _scope(1, 2, 24, 12, 8)
    trigger = (ExpansionTrigger.INSUFFICIENT_EVIDENCE,)

    stop = ExpansionDecision(0, ExpansionDecisionKind.STOP, (), current, None)
    assert stop.next_scope is None

    with pytest.raises(ValueError, match="STOP"):
        ExpansionDecision(0, ExpansionDecisionKind.STOP, trigger, current, None)
    with pytest.raises(ValueError, match="STOP"):
        ExpansionDecision(0, ExpansionDecisionKind.STOP, (), current, nxt)

    with pytest.raises(ValueError, match="EXPAND"):
        ExpansionDecision(0, ExpansionDecisionKind.EXPAND, (), current, nxt)
    with pytest.raises(ValueError, match="EXPAND"):
        ExpansionDecision(0, ExpansionDecisionKind.EXPAND, trigger, current, None)

    exhausted = ExpansionDecision(
        0,
        ExpansionDecisionKind.EXHAUSTED,
        trigger,
        current,
        None,
    )
    assert exhausted.kind is ExpansionDecisionKind.EXHAUSTED

    with pytest.raises(ValueError, match="EXHAUSTED"):
        ExpansionDecision(0, ExpansionDecisionKind.EXHAUSTED, (), current, None)
    with pytest.raises(ValueError, match="EXHAUSTED"):
        ExpansionDecision(0, ExpansionDecisionKind.EXHAUSTED, trigger, current, nxt)

    with pytest.raises(ValueError, match="round_index"):
        ExpansionDecision(1, ExpansionDecisionKind.STOP, (), current, None)

    wrong_next = _scope(2, 2, 24, 12, 8)
    with pytest.raises(ValueError, match="next_scope"):
        ExpansionDecision(0, ExpansionDecisionKind.EXPAND, trigger, current, wrong_next)

    noop_next = _scope(1)
    with pytest.raises(ValueError, match="no-op"):
        ExpansionDecision(0, ExpansionDecisionKind.EXPAND, trigger, current, noop_next)
