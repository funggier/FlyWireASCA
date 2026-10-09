from __future__ import annotations

from collections.abc import Iterable

from flywire_asca.contracts import ActivationBudget

from .models import (
    MemoryActivationSupport,
    SelectiveRetrievalEvidence,
    SelectiveWorkingSetResult,
)
from .selector import (
    _build_result,
    _prepare_evidence,
    validate_a006_budget,
)


def _single_best_support(
    support: MemoryActivationSupport,
) -> MemoryActivationSupport:
    return MemoryActivationSupport(
        memory_id=support.memory_id,
        source_cue_ids=support.source_cue_ids,
        similarities=support.similarities,
        support_count=support.support_count,
        max_similarity=support.max_similarity,
        activation=support.max_similarity,
        memory_kind=support.memory_kind,
        proposition_confidence=support.proposition_confidence,
        evidence_ids=support.evidence_ids,
        entity_ids=support.entity_ids,
        context_tags=support.context_tags,
        source_tags=support.source_tags,
    )


def select_single_best(
    evidence: Iterable[SelectiveRetrievalEvidence],
    *,
    budget: ActivationBudget,
) -> SelectiveWorkingSetResult:
    validate_a006_budget(budget)
    prepared = _prepare_evidence(evidence)
    ranked = tuple(
        sorted(
            (_single_best_support(support) for support in prepared.supports),
            key=lambda support: (
                -support.max_similarity,
                support.memory_id,
            ),
        )
    )
    return _build_result(
        prepared,
        budget=budget,
        ranked_supports=ranked,
        tie_key=lambda support: (support.max_similarity,),
    )


def select_exhaustive(
    evidence: Iterable[SelectiveRetrievalEvidence],
) -> SelectiveWorkingSetResult:
    prepared = _prepare_evidence(evidence)
    positive_count = len(prepared.supports)
    size = max(1, positive_count)
    budget = ActivationBudget(
        max_memory_nodes=size,
        max_relation_hops=0,
        max_working_set_items=size,
        max_model_input_tokens=0,
        max_expansions=0,
    )
    return _build_result(
        prepared,
        budget=budget,
        ranked_supports=prepared.supports,
    )
