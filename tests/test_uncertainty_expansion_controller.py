from __future__ import annotations

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
    ExpansionScope,
    ExpansionTrigger,
    assess_expansion,
    derive_expansion_triggers,
)


def _budget(memory=4, working=2):
    return ActivationBudget(memory, 0, working, 0, 0)


def _scope(round_index=0, tiers=1, top_k=12, memory=4, working=2):
    return ExpansionScope(
        round_index,
        tiers,
        top_k,
        _budget(memory, working),
    )


def _support(memory_id: str, similarity: float = 0.8):
    return MemoryActivationSupport(
        memory_id=memory_id,
        source_cue_ids=("cue",),
        similarities=(similarity,),
        support_count=1,
        max_similarity=similarity,
        activation=similarity,
        memory_kind=MemoryKind.SEMANTIC,
        proposition_confidence=0.5,
        evidence_ids=(),
        entity_ids=(),
        context_tags=(),
        source_tags=(),
    )


def _result(
    state: RetrievalState,
    *,
    positive: int,
    activated: int,
    selected: int,
    memory_tie: bool = False,
    working_tie: bool = False,
) -> SelectiveWorkingSetResult:
    assert positive >= activated >= selected >= 0
    supports = tuple(_support(f"m{i}", 0.9 - i * 0.01) for i in range(positive))
    activation_states = tuple(
        ActivationState(
            node_id=f"m{i}",
            activation=supports[i].activation,
            hop=0,
            source_cue_ids=("cue",),
        )
        for i in range(activated)
    )
    entries = tuple(
        WorkingSetEntry(
            ref_id=f"m{i}",
            kind=WorkingSetKind.MEMORY,
            activation=supports[i].activation,
            reason="single_cue_support",
        )
        for i in range(selected)
    )
    budget = _budget(max(activated, 1), max(selected, 1))
    working_set = WorkingSet(entries, state, budget)
    return SelectiveWorkingSetResult(
        working_set=working_set,
        activation_states=activation_states,
        supports=supports,
        input_result_count=1,
        input_hit_count=positive,
        unique_candidate_count=positive,
        positive_candidate_count=positive,
        activated_candidate_count=activated,
        selected_count=selected,
        dropped_by_memory_budget_count=positive - activated,
        dropped_by_working_set_budget_count=activated - selected,
        memory_budget_boundary_tie=memory_tie,
        working_set_boundary_tie=working_tie,
        embedding_model_name="embedder",
        embedding_model_digest="digest",
        embedding_profile="profile",
    )


def test_recalled_without_drops_has_no_triggers_and_stops():
    result = _result(RetrievalState.RECALLED, positive=2, activated=2, selected=2)
    assert derive_expansion_triggers(result) == ()

    decision = assess_expansion(
        result,
        current_scope=_scope(0),
        next_scope=_scope(1, 2, 24, 8, 4),
    )
    assert decision.kind is ExpansionDecisionKind.STOP
    assert decision.triggers == ()
    assert decision.next_scope is None


def test_insufficient_evidence_trigger_expands_or_exhausts():
    result = _result(
        RetrievalState.INSUFFICIENT_EVIDENCE,
        positive=0,
        activated=0,
        selected=0,
    )
    assert derive_expansion_triggers(result) == (
        ExpansionTrigger.INSUFFICIENT_EVIDENCE,
    )

    expanded = assess_expansion(
        result,
        current_scope=_scope(0),
        next_scope=_scope(1, 2, 24, 8, 4),
    )
    assert expanded.kind is ExpansionDecisionKind.EXPAND
    assert expanded.triggers == (ExpansionTrigger.INSUFFICIENT_EVIDENCE,)

    exhausted = assess_expansion(
        result,
        current_scope=_scope(2, 3, 32, 16, 12),
        next_scope=None,
    )
    assert exhausted.kind is ExpansionDecisionKind.EXHAUSTED


def test_partial_recall_derives_budget_triggers_and_ties_in_exact_order():
    result = _result(
        RetrievalState.PARTIAL_RECALL,
        positive=5,
        activated=3,
        selected=2,
        memory_tie=True,
        working_tie=True,
    )
    assert derive_expansion_triggers(result) == (
        ExpansionTrigger.MEMORY_BUDGET_TRUNCATED,
        ExpansionTrigger.WORKING_SET_BUDGET_TRUNCATED,
        ExpansionTrigger.MEMORY_BOUNDARY_TIE,
        ExpansionTrigger.WORKING_SET_BOUNDARY_TIE,
    )


@pytest.mark.parametrize(
    "state,positive,activated,selected,memory_tie,working_tie,match",
    [
        (RetrievalState.RECALLED, 3, 2, 2, False, False, "RECALLED"),
        (RetrievalState.RECALLED, 2, 2, 1, False, False, "RECALLED"),
        (RetrievalState.PARTIAL_RECALL, 2, 2, 2, False, False, "PARTIAL_RECALL"),
        (RetrievalState.INSUFFICIENT_EVIDENCE, 1, 1, 1, False, False, "INSUFFICIENT_EVIDENCE"),
        (RetrievalState.PARTIAL_RECALL, 3, 3, 2, True, False, "memory_budget_boundary_tie"),
        (RetrievalState.PARTIAL_RECALL, 3, 2, 2, False, True, "working_set_boundary_tie"),
    ],
)
def test_structural_contradictions_fail_closed(
    state,
    positive,
    activated,
    selected,
    memory_tie,
    working_tie,
    match,
):
    result = _result(
        state,
        positive=positive,
        activated=activated,
        selected=selected,
        memory_tie=memory_tie,
        working_tie=working_tie,
    )
    with pytest.raises(ValueError, match=match):
        derive_expansion_triggers(result)


@pytest.mark.parametrize(
    "unsupported",
    [
        RetrievalState.UNFAMILIAR,
        RetrievalState.FAMILIAR,
        RetrievalState.KNOWN_BUT_NOT_RECALLED,
        RetrievalState.CONFLICTING_RECALL,
    ],
)
def test_unsupported_a006_retrieval_states_fail_closed(unsupported):
    result = _result(unsupported, positive=0, activated=0, selected=0)
    with pytest.raises(ValueError, match="retrieval_state"):
        derive_expansion_triggers(result)


def test_assessment_rejects_invalid_scope_adjacency():
    result = _result(
        RetrievalState.INSUFFICIENT_EVIDENCE,
        positive=0,
        activated=0,
        selected=0,
    )
    current = _scope(0)
    with pytest.raises(ValueError, match="next_scope"):
        assess_expansion(
            result,
            current_scope=current,
            next_scope=_scope(2, 2, 24, 8, 4),
        )

    with pytest.raises(ValueError, match="no-op"):
        assess_expansion(
            result,
            current_scope=current,
            next_scope=_scope(1, 1, 12, 4, 2),
        )


def test_assessment_does_not_mutate_result_or_scopes():
    result = _result(RetrievalState.RECALLED, positive=1, activated=1, selected=1)
    current = _scope(0)
    nxt = _scope(1, 2, 24, 8, 4)
    snapshot = (result, current, nxt)

    decision = assess_expansion(result, current_scope=current, next_scope=nxt)

    assert snapshot == (result, current, nxt)
    assert decision.current_scope == current
    assert decision.next_scope is None
