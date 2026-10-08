from __future__ import annotations

import math

import pytest

from flywire_asca.contracts import (
    ActivationBudget,
    ActivationState,
    RetrievalState,
    UncertaintySignal,
    WorkingSet,
    WorkingSetEntry,
    WorkingSetKind,
)


def test_activation_budget_is_explicit_and_bounded():
    budget = ActivationBudget(
        max_memory_nodes=32,
        max_relation_hops=2,
        max_working_set_items=8,
        max_model_input_tokens=2048,
        max_expansions=3,
    )
    assert budget.max_memory_nodes == 32
    assert budget.max_relation_hops == 2

    with pytest.raises(ValueError, match="max_memory_nodes"):
        ActivationBudget(0, 2, 8, 2048, 3)
    with pytest.raises(ValueError, match="max_relation_hops"):
        ActivationBudget(32, -1, 8, 2048, 3)
    with pytest.raises(ValueError, match="max_working_set_items"):
        ActivationBudget(32, 2, 0, 2048, 3)


def test_activation_state_requires_finite_activation_and_nonnegative_hop():
    state = ActivationState(
        node_id="mem-1",
        activation=-0.25,
        hop=1,
        source_cue_ids=("cue-1",),
    )
    assert state.activation == -0.25

    with pytest.raises(ValueError, match="activation"):
        ActivationState("mem-1", math.inf, 0)
    with pytest.raises(ValueError, match="hop"):
        ActivationState("mem-1", 0.5, -1)


def test_working_set_rejects_duplicate_refs_and_budget_overflow():
    budget = ActivationBudget(10, 2, 2, 512, 1)
    first = WorkingSetEntry("mem-1", WorkingSetKind.MEMORY, 0.9, "cue match")
    second = WorkingSetEntry("proc-1", WorkingSetKind.PROCEDURE, 0.7, "familiar routine")

    working = WorkingSet((first, second), RetrievalState.PARTIAL_RECALL, budget)
    assert tuple(entry.ref_id for entry in working.entries) == ("mem-1", "proc-1")

    duplicate = WorkingSetEntry("mem-1", WorkingSetKind.HYPOTHESIS, 0.1, "alternative")
    with pytest.raises(ValueError, match="duplicate"):
        WorkingSet((first, duplicate), RetrievalState.CONFLICTING_RECALL, budget)

    tiny_budget = ActivationBudget(10, 2, 1, 512, 1)
    with pytest.raises(ValueError, match="budget"):
        WorkingSet((first, second), RetrievalState.PARTIAL_RECALL, tiny_budget)


def test_uncertainty_signal_keeps_uncertainty_surprise_and_risk_separate():
    signal = UncertaintySignal(
        uncertainty=0.4,
        surprise=0.8,
        risk=0.2,
        reasons=("unexpected_barrier",),
    )
    assert (signal.uncertainty, signal.surprise, signal.risk) == (0.4, 0.8, 0.2)

    with pytest.raises(ValueError, match="surprise"):
        UncertaintySignal(0.4, 1.1, 0.2)
    with pytest.raises(ValueError, match="reasons"):
        UncertaintySignal(0.4, 0.8, 0.2, reasons=("x", "x"))
