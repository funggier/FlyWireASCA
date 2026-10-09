from __future__ import annotations

from flywire_asca.contracts import RetrievalState
from flywire_asca.selective_activation import SelectiveWorkingSetResult

from .models import (
    ExpansionDecision,
    ExpansionDecisionKind,
    ExpansionScope,
    ExpansionTrigger,
)


_SUPPORTED_STATES = {
    RetrievalState.RECALLED,
    RetrievalState.PARTIAL_RECALL,
    RetrievalState.INSUFFICIENT_EVIDENCE,
}


def _validate_structural_state(result: SelectiveWorkingSetResult) -> None:
    if not isinstance(result, SelectiveWorkingSetResult):
        raise ValueError("result must be a SelectiveWorkingSetResult")

    state = result.working_set.retrieval_state
    if state not in _SUPPORTED_STATES:
        raise ValueError(
            "retrieval_state is not supported by A007 structural expansion"
        )

    memory_drop = result.dropped_by_memory_budget_count
    working_drop = result.dropped_by_working_set_budget_count

    if result.memory_budget_boundary_tie and memory_drop <= 0:
        raise ValueError(
            "memory_budget_boundary_tie requires a memory budget drop"
        )
    if result.working_set_boundary_tie and working_drop <= 0:
        raise ValueError(
            "working_set_boundary_tie requires a working-set budget drop"
        )

    if state is RetrievalState.RECALLED:
        if memory_drop > 0 or working_drop > 0:
            raise ValueError(
                "RECALLED is inconsistent with positive budget drops"
            )
        if result.positive_candidate_count <= 0 or result.selected_count <= 0:
            raise ValueError(
                "RECALLED requires positive selected evidence"
            )
        if (
            result.memory_budget_boundary_tie
            or result.working_set_boundary_tie
        ):
            raise ValueError(
                "RECALLED is inconsistent with boundary ties"
            )
        return

    if state is RetrievalState.PARTIAL_RECALL:
        if memory_drop <= 0 and working_drop <= 0:
            raise ValueError(
                "PARTIAL_RECALL requires at least one positive budget drop"
            )
        if result.positive_candidate_count <= 0:
            raise ValueError(
                "PARTIAL_RECALL requires positive candidate evidence"
            )
        return

    if state is RetrievalState.INSUFFICIENT_EVIDENCE:
        if (
            result.positive_candidate_count != 0
            or result.activated_candidate_count != 0
            or result.selected_count != 0
            or memory_drop != 0
            or working_drop != 0
        ):
            raise ValueError(
                "INSUFFICIENT_EVIDENCE requires zero positive/active/selected "
                "evidence and zero budget drops"
            )
        if result.working_set.entries:
            raise ValueError(
                "INSUFFICIENT_EVIDENCE requires an empty working set"
            )
        if (
            result.memory_budget_boundary_tie
            or result.working_set_boundary_tie
        ):
            raise ValueError(
                "INSUFFICIENT_EVIDENCE is inconsistent with boundary ties"
            )


def derive_expansion_triggers(
    result: SelectiveWorkingSetResult,
) -> tuple[ExpansionTrigger, ...]:
    _validate_structural_state(result)

    triggers: list[ExpansionTrigger] = []
    state = result.working_set.retrieval_state
    if state is RetrievalState.INSUFFICIENT_EVIDENCE:
        triggers.append(ExpansionTrigger.INSUFFICIENT_EVIDENCE)
    if result.dropped_by_memory_budget_count > 0:
        triggers.append(ExpansionTrigger.MEMORY_BUDGET_TRUNCATED)
    if result.dropped_by_working_set_budget_count > 0:
        triggers.append(ExpansionTrigger.WORKING_SET_BUDGET_TRUNCATED)
    if result.memory_budget_boundary_tie:
        triggers.append(ExpansionTrigger.MEMORY_BOUNDARY_TIE)
    if result.working_set_boundary_tie:
        triggers.append(ExpansionTrigger.WORKING_SET_BOUNDARY_TIE)
    return tuple(triggers)


def assess_expansion(
    result: SelectiveWorkingSetResult,
    *,
    current_scope: ExpansionScope,
    next_scope: ExpansionScope | None,
) -> ExpansionDecision:
    if not isinstance(current_scope, ExpansionScope):
        raise ValueError("current_scope must be an ExpansionScope")
    if next_scope is not None and not isinstance(next_scope, ExpansionScope):
        raise ValueError("next_scope must be an ExpansionScope or None")

    triggers = derive_expansion_triggers(result)
    if not triggers:
        return ExpansionDecision(
            round_index=current_scope.round_index,
            kind=ExpansionDecisionKind.STOP,
            triggers=(),
            current_scope=current_scope,
            next_scope=None,
        )
    if next_scope is None:
        return ExpansionDecision(
            round_index=current_scope.round_index,
            kind=ExpansionDecisionKind.EXHAUSTED,
            triggers=triggers,
            current_scope=current_scope,
            next_scope=None,
        )
    return ExpansionDecision(
        round_index=current_scope.round_index,
        kind=ExpansionDecisionKind.EXPAND,
        triggers=triggers,
        current_scope=current_scope,
        next_scope=next_scope,
    )
