from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
import math

from flywire_asca.contracts import (
    ActivationBudget,
    ActivationState,
    RetrievalState,
    WorkingSet,
    WorkingSetEntry,
    WorkingSetKind,
)
from flywire_asca.vector_memory import VectorMemoryHit

from .models import (
    MemoryActivationSupport,
    SelectiveRetrievalEvidence,
    SelectiveWorkingSetResult,
)


@dataclass(frozen=True, slots=True)
class _CandidateMetadata:
    memory_kind: object
    proposition_confidence: float
    evidence_ids: tuple[str, ...]
    entity_ids: tuple[str, ...]
    context_tags: tuple[str, ...]
    source_tags: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class _PreparedEvidence:
    evidence: tuple[SelectiveRetrievalEvidence, ...]
    input_hit_count: int
    unique_candidate_count: int
    embedding_model_name: str
    embedding_model_digest: str | None
    embedding_profile: str
    supports: tuple[MemoryActivationSupport, ...]


def validate_a006_budget(budget: ActivationBudget) -> None:
    if not isinstance(budget, ActivationBudget):
        raise ValueError("budget must be an ActivationBudget")
    if budget.max_working_set_items > budget.max_memory_nodes:
        raise ValueError(
            "max_working_set_items must be <= max_memory_nodes"
        )
    if budget.max_relation_hops != 0:
        raise ValueError("max_relation_hops must be 0 for A006")
    if budget.max_expansions != 0:
        raise ValueError("max_expansions must be 0 for A006")
    if budget.max_model_input_tokens != 0:
        raise ValueError("max_model_input_tokens must be 0 for A006")


def bounded_union_activation(similarities: Iterable[float]) -> float:
    values = tuple(similarities)
    if not values:
        raise ValueError("similarities must not be empty")
    remainder = 1.0
    for value in values:
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            raise ValueError("similarities must contain finite numeric values")
        numeric = float(value)
        if not math.isfinite(numeric):
            raise ValueError("similarities must be finite")
        if not 0.0 < numeric <= 1.0:
            if numeric <= 0.0:
                raise ValueError("similarities must contain positive values")
            raise ValueError("similarities must be within (0, 1]")
        remainder *= 1.0 - numeric
    activation = 1.0 - remainder
    return max(0.0, min(1.0, activation))


def _metadata(hit: VectorMemoryHit) -> _CandidateMetadata:
    return _CandidateMetadata(
        memory_kind=hit.memory_kind,
        proposition_confidence=hit.proposition_confidence,
        evidence_ids=hit.evidence_ids,
        entity_ids=hit.entity_ids,
        context_tags=hit.context_tags,
        source_tags=hit.source_tags,
    )


def _check_metadata(
    memory_id: str,
    expected: _CandidateMetadata,
    observed: _CandidateMetadata,
) -> None:
    fields = (
        "memory_kind",
        "proposition_confidence",
        "evidence_ids",
        "entity_ids",
        "context_tags",
        "source_tags",
    )
    for field in fields:
        if getattr(expected, field) != getattr(observed, field):
            raise ValueError(
                f"conflicting {field} for memory_id {memory_id}"
            )


def _rank_key(support: MemoryActivationSupport) -> tuple[float, float, int, str]:
    return (
        -support.activation,
        -support.max_similarity,
        -support.support_count,
        support.memory_id,
    )


def _boundary_tie(
    ranked: tuple[MemoryActivationSupport, ...],
    keep_count: int,
) -> bool:
    if keep_count <= 0 or keep_count >= len(ranked):
        return False
    left = ranked[keep_count - 1]
    right = ranked[keep_count]
    return (
        left.activation == right.activation
        and left.max_similarity == right.max_similarity
        and left.support_count == right.support_count
    )


def _prepare_evidence(
    evidence: Iterable[SelectiveRetrievalEvidence],
) -> _PreparedEvidence:
    items = tuple(evidence)
    if not items:
        raise ValueError("evidence must not be empty")
    if any(not isinstance(item, SelectiveRetrievalEvidence) for item in items):
        raise ValueError(
            "evidence must contain only SelectiveRetrievalEvidence values"
        )

    cue_ids = tuple(item.source_cue_id for item in items)
    if len(set(cue_ids)) != len(cue_ids):
        raise ValueError("source_cue_id values must be unique")
    query_ids = tuple(item.result.query_id for item in items)
    if len(set(query_ids)) != len(query_ids):
        raise ValueError("result query_id values must be unique")

    first = items[0].result
    model_name = first.embedding_model_name
    model_digest = first.embedding_model_digest
    profile = first.embedding_profile

    metadata_by_id: dict[str, _CandidateMetadata] = {}
    contributions: dict[str, list[tuple[str, float]]] = {}
    input_hit_count = 0

    for item in items:
        result = item.result
        if result.embedding_model_name != model_name:
            raise ValueError("embedding_model_name mismatch across results")
        if result.embedding_model_digest != model_digest:
            raise ValueError("embedding_model_digest mismatch across results")
        if result.embedding_profile != profile:
            raise ValueError("embedding_profile mismatch across results")

        seen_in_result: set[str] = set()
        for hit in result.hits:
            input_hit_count += 1
            if hit.memory_id in seen_in_result:
                raise ValueError(
                    f"duplicate memory_id in one result: {hit.memory_id}"
                )
            seen_in_result.add(hit.memory_id)

            observed = _metadata(hit)
            existing = metadata_by_id.get(hit.memory_id)
            if existing is None:
                metadata_by_id[hit.memory_id] = observed
            else:
                _check_metadata(hit.memory_id, existing, observed)

            if hit.similarity > 0.0:
                contributions.setdefault(hit.memory_id, []).append(
                    (item.source_cue_id, hit.similarity)
                )

    supports: list[MemoryActivationSupport] = []
    for memory_id, pairs in contributions.items():
        ordered = tuple(sorted(pairs, key=lambda pair: pair[0]))
        cue_tuple = tuple(cue_id for cue_id, _ in ordered)
        similarity_tuple = tuple(similarity for _, similarity in ordered)
        metadata = metadata_by_id[memory_id]
        supports.append(
            MemoryActivationSupport(
                memory_id=memory_id,
                source_cue_ids=cue_tuple,
                similarities=similarity_tuple,
                support_count=len(cue_tuple),
                max_similarity=max(similarity_tuple),
                activation=bounded_union_activation(similarity_tuple),
                memory_kind=metadata.memory_kind,
                proposition_confidence=metadata.proposition_confidence,
                evidence_ids=metadata.evidence_ids,
                entity_ids=metadata.entity_ids,
                context_tags=metadata.context_tags,
                source_tags=metadata.source_tags,
            )
        )
    supports.sort(key=_rank_key)

    return _PreparedEvidence(
        evidence=items,
        input_hit_count=input_hit_count,
        unique_candidate_count=len(metadata_by_id),
        embedding_model_name=model_name,
        embedding_model_digest=model_digest,
        embedding_profile=profile,
        supports=tuple(supports),
    )


def _build_result(
    prepared: _PreparedEvidence,
    *,
    budget: ActivationBudget,
    ranked_supports: tuple[MemoryActivationSupport, ...],
) -> SelectiveWorkingSetResult:
    positive_count = len(ranked_supports)
    memory_keep = min(positive_count, budget.max_memory_nodes)
    activated_supports = ranked_supports[:memory_keep]
    working_keep = min(
        len(activated_supports),
        budget.max_working_set_items,
    )
    selected_supports = activated_supports[:working_keep]

    memory_tie = _boundary_tie(
        ranked_supports,
        budget.max_memory_nodes,
    )
    working_tie = _boundary_tie(
        activated_supports,
        budget.max_working_set_items,
    )

    activation_states = tuple(
        ActivationState(
            node_id=support.memory_id,
            activation=support.activation,
            hop=0,
            source_cue_ids=support.source_cue_ids,
        )
        for support in activated_supports
    )
    entries = tuple(
        WorkingSetEntry(
            ref_id=support.memory_id,
            kind=WorkingSetKind.MEMORY,
            activation=support.activation,
            reason=(
                "multi_cue_convergence"
                if support.support_count > 1
                else "single_cue_support"
            ),
        )
        for support in selected_supports
    )

    dropped_memory = positive_count - len(activation_states)
    dropped_working = len(activation_states) - len(entries)
    if positive_count == 0:
        retrieval_state = RetrievalState.INSUFFICIENT_EVIDENCE
    elif dropped_memory > 0 or dropped_working > 0:
        retrieval_state = RetrievalState.PARTIAL_RECALL
    else:
        retrieval_state = RetrievalState.RECALLED

    working_set = WorkingSet(
        entries=entries,
        retrieval_state=retrieval_state,
        budget=budget,
    )
    return SelectiveWorkingSetResult(
        working_set=working_set,
        activation_states=activation_states,
        supports=ranked_supports,
        input_result_count=len(prepared.evidence),
        input_hit_count=prepared.input_hit_count,
        unique_candidate_count=prepared.unique_candidate_count,
        positive_candidate_count=positive_count,
        activated_candidate_count=len(activation_states),
        selected_count=len(entries),
        dropped_by_memory_budget_count=dropped_memory,
        dropped_by_working_set_budget_count=dropped_working,
        memory_budget_boundary_tie=memory_tie,
        working_set_boundary_tie=working_tie,
        embedding_model_name=prepared.embedding_model_name,
        embedding_model_digest=prepared.embedding_model_digest,
        embedding_profile=prepared.embedding_profile,
    )


def select_working_set(
    evidence: Iterable[SelectiveRetrievalEvidence],
    *,
    budget: ActivationBudget,
) -> SelectiveWorkingSetResult:
    validate_a006_budget(budget)
    prepared = _prepare_evidence(evidence)
    return _build_result(
        prepared,
        budget=budget,
        ranked_supports=prepared.supports,
    )
