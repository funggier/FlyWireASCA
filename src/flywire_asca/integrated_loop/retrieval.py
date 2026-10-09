from __future__ import annotations

from dataclasses import dataclass
import math

from flywire_asca.contracts.validation import require_nonempty
from flywire_asca.selective_activation import (
    SelectiveRetrievalEvidence,
    select_single_best,
)
from flywire_asca.uncertainty_expansion import (
    ExpansionPolicy,
    ExpansionProfile,
    ExpansionScope,
    run_expansion_policy,
)
from flywire_asca.vector_memory import (
    ExactVectorMemoryIndex,
    VectorMemoryQuery,
)

from .models import IntegratedExpansionResult, IntegratedScopeEvaluation


def _require_nonnegative_int(name: str, value: int) -> None:
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise ValueError(f"{name} must be a nonnegative integer")


@dataclass(frozen=True, slots=True)
class IntegratedRetrievalCue:
    source_cue_id: str
    query_id: str
    query_text: str

    def __post_init__(self) -> None:
        require_nonempty("source_cue_id", self.source_cue_id)
        require_nonempty("query_id", self.query_id)
        require_nonempty("query_text", self.query_text)


@dataclass(frozen=True, slots=True)
class IntegratedRetrievalCueTier:
    tier_index: int
    cues: tuple[IntegratedRetrievalCue, ...]

    def __post_init__(self) -> None:
        _require_nonnegative_int("tier_index", self.tier_index)
        if not self.cues:
            raise ValueError("cues must not be empty")
        if any(not isinstance(cue, IntegratedRetrievalCue) for cue in self.cues):
            raise ValueError(
                "cues must contain only IntegratedRetrievalCue values"
            )
        source_ids = tuple(cue.source_cue_id for cue in self.cues)
        query_ids = tuple(cue.query_id for cue in self.cues)
        if len(source_ids) != len(set(source_ids)):
            raise ValueError("cues contain duplicate source_cue_id values")
        if len(query_ids) != len(set(query_ids)):
            raise ValueError("cues contain duplicate query_id values")


@dataclass(frozen=True, slots=True)
class IntegratedRetrievalContext:
    index: ExactVectorMemoryIndex
    cue_tiers: tuple[IntegratedRetrievalCueTier, ...]
    minimum_similarity: float

    def __post_init__(self) -> None:
        if not isinstance(self.index, ExactVectorMemoryIndex):
            raise ValueError("index must be an ExactVectorMemoryIndex")
        if not self.cue_tiers:
            raise ValueError("cue_tiers must not be empty")
        if any(
            not isinstance(tier, IntegratedRetrievalCueTier)
            for tier in self.cue_tiers
        ):
            raise ValueError(
                "cue_tiers must contain only IntegratedRetrievalCueTier values"
            )
        indices = tuple(tier.tier_index for tier in self.cue_tiers)
        if indices != tuple(range(len(self.cue_tiers))):
            raise ValueError("cue_tier indices must be contiguous from 0")

        source_ids = tuple(
            cue.source_cue_id
            for tier in self.cue_tiers
            for cue in tier.cues
        )
        query_ids = tuple(
            cue.query_id
            for tier in self.cue_tiers
            for cue in tier.cues
        )
        if len(source_ids) != len(set(source_ids)):
            raise ValueError("source_cue_id values must be unique across tiers")
        if len(query_ids) != len(set(query_ids)):
            raise ValueError("query_id values must be unique across tiers")

        if (
            not isinstance(self.minimum_similarity, (int, float))
            or isinstance(self.minimum_similarity, bool)
        ):
            raise ValueError(
                "minimum_similarity must be finite and within [-1, 1]"
            )
        value = float(self.minimum_similarity)
        if not math.isfinite(value) or not -1.0 <= value <= 1.0:
            raise ValueError(
                "minimum_similarity must be finite and within [-1, 1]"
            )
        object.__setattr__(self, "minimum_similarity", value)


def evaluate_integrated_scope(
    context: IntegratedRetrievalContext,
    scope: ExpansionScope,
) -> IntegratedScopeEvaluation:
    if not isinstance(context, IntegratedRetrievalContext):
        raise ValueError("context must be an IntegratedRetrievalContext")
    if not isinstance(scope, ExpansionScope):
        raise ValueError("scope must be an ExpansionScope")
    if scope.enabled_cue_tier_count > len(context.cue_tiers):
        raise ValueError(
            "enabled_cue_tier_count exceeds available cue tiers"
        )

    enabled_cues = tuple(
        cue
        for tier in context.cue_tiers[: scope.enabled_cue_tier_count]
        for cue in tier.cues
    )
    results = tuple(
        context.index.search(
            VectorMemoryQuery(
                query_id=cue.query_id,
                query_text=cue.query_text,
                top_k=scope.top_k,
                minimum_similarity=context.minimum_similarity,
            )
        )
        for cue in enabled_cues
    )
    evidence = tuple(
        SelectiveRetrievalEvidence(cue.source_cue_id, result)
        for cue, result in zip(enabled_cues, results)
    )
    working_set_result = select_single_best(
        evidence,
        budget=scope.budget,
    )
    return IntegratedScopeEvaluation(
        scope=scope,
        retrieval_results=results,
        working_set_result=working_set_result,
    )


def run_initial_integrated_expansion(
    context: IntegratedRetrievalContext,
    *,
    profile: ExpansionProfile,
    policy: ExpansionPolicy,
) -> IntegratedExpansionResult:
    if not isinstance(context, IntegratedRetrievalContext):
        raise ValueError("context must be an IntegratedRetrievalContext")
    if not isinstance(profile, ExpansionProfile):
        raise ValueError("profile must be an ExpansionProfile")
    if not isinstance(policy, ExpansionPolicy):
        raise ValueError("policy must be an ExpansionPolicy")

    evaluations: list[IntegratedScopeEvaluation] = []

    def evaluate(scope: ExpansionScope):
        result = evaluate_integrated_scope(context, scope)
        evaluations.append(result)
        return result.working_set_result

    run = run_expansion_policy(
        profile,
        policy=policy,
        evaluate_scope=evaluate,
    )
    return IntegratedExpansionResult(run=run, evaluations=tuple(evaluations))
