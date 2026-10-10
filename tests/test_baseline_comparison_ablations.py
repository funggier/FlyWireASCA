from __future__ import annotations

from dataclasses import replace

from flywire_asca.baseline_comparison import ComparisonVariant
from flywire_asca.baseline_comparison.ablations import (
    normalize_a009_result,
    run_asca_always_max_scope,
    run_asca_primary,
    run_familiarity_disabled_ablation,
    run_no_structural_expansion_ablation,
)
from flywire_asca.familiarity import ExactFamiliarityIndex
from flywire_asca.integrated_loop import LoopPolicy
from flywire_asca.integrated_loop import benchmark as a009_benchmark
from flywire_asca.integrated_loop import controller as a009_controller
from flywire_asca.uncertainty_expansion import build_a007_primary_profile


def _case(case_id: str):
    return next(
        item
        for item in a009_benchmark.build_a009_deterministic_fixture()
        if item.case_id == case_id
    )


def _inputs(case_id: str, policy: LoopPolicy = LoopPolicy.MISMATCH_DRIVEN_RECOVERY):
    case = _case(case_id)
    return case, dict(
        request=a009_benchmark._request(case, policy),
        familiarity_index=a009_benchmark._familiarity_index(case),
        retrieval_context=a009_benchmark._retrieval_context(case),
        expansion_profile=build_a007_primary_profile(),
        procedure_library=a009_benchmark._procedure_library(),
        procedure_executor_factory=a009_benchmark._factory(case),
        model_adapter=None,
        memory_context_provider=a009_benchmark._FixtureMemoryContext(case),
        same_name_expected_ids=case.same_name_expected_ids,
    )


def test_asca_primary_delegates_once_to_real_a009_controller(monkeypatch):
    case, kwargs = _inputs("easy-familiar-success")
    original = a009_controller.run_cognitive_loop
    calls = []

    def spy(request, **call_kwargs):
        calls.append((request, call_kwargs))
        return original(request, **call_kwargs)

    monkeypatch.setattr(a009_controller, "run_cognitive_loop", spy)
    result = run_asca_primary(**kwargs)

    assert len(calls) == 1
    assert calls[0][0].policy is LoopPolicy.MISMATCH_DRIVEN_RECOVERY
    assert result.variant is ComparisonVariant.ASCA_PRIMARY
    assert result.procedure_success is True
    assert result.procedure_attempt_count == 1


def test_normalize_a009_result_derives_raw_retrieval_and_attempt_counts():
    case, kwargs = _inputs("procedure-recovery-round-one")
    raw = a009_controller.run_cognitive_loop(
        kwargs["request"],
        familiarity_index=kwargs["familiarity_index"],
        retrieval_context=kwargs["retrieval_context"],
        expansion_profile=kwargs["expansion_profile"],
        procedure_library=kwargs["procedure_library"],
        procedure_executor_factory=kwargs["procedure_executor_factory"],
        model_adapter=None,
        memory_context_provider=kwargs["memory_context_provider"],
    )
    result = normalize_a009_result(
        case.case_id,
        ComparisonVariant.ASCA_PRIMARY,
        raw,
        same_name_expected_ids=case.same_name_expected_ids,
    )

    assert result.query_count == sum(
        len(item.retrieval_results) for item in raw.scope_evaluations
    )
    assert result.scored_vector_count_sum == sum(
        retrieval.scored_vector_count
        for item in raw.scope_evaluations
        for retrieval in item.retrieval_results
    )
    assert result.procedure_attempt_count == len(raw.procedure_attempts) == 2
    assert result.forced_recovery_scope_count == 1
    assert result.mismatch_count == 1
    assert all(kind != "FAMILIARITY_ASSESSED" for kind, _ in result.trace_signature)


def test_asca_always_max_scope_uses_a009_always_max_policy():
    _, kwargs = _inputs("easy-familiar-success")
    result = run_asca_always_max_scope(**kwargs)

    assert result.variant is ComparisonVariant.ASCA_ALWAYS_MAX_SCOPE
    assert result.evaluated_scope_indices == (0, 1, 2)
    assert result.procedure_attempt_count == 1
    assert result.procedure_success is True


def test_no_structural_expansion_starts_scope_zero_then_recovers_one_scope():
    case, kwargs = _inputs("structural-expansion-success")
    threshold_before = kwargs["retrieval_context"].minimum_similarity
    tiers_before = kwargs["retrieval_context"].cue_tiers
    snapshot_before = kwargs["procedure_executor_factory"].initial_world_state_ref

    result = run_no_structural_expansion_ablation(**kwargs)

    assert result.variant is ComparisonVariant.ASCA_NO_STRUCTURAL_EXPANSION
    assert result.evaluated_scope_indices == (0, 1)
    assert result.procedure_attempt_count == 2
    assert result.execution_ids == (
        f"a010:{case.case_id}:no-structural:procedure-attempt:0",
        f"a010:{case.case_id}:no-structural:procedure-attempt:1",
    )
    assert result.forced_recovery_scope_count == 1
    assert result.procedure_success is True
    assert kwargs["retrieval_context"].minimum_similarity == threshold_before
    assert kwargs["retrieval_context"].cue_tiers == tiers_before
    assert kwargs["procedure_executor_factory"].initial_world_state_ref == snapshot_before


def test_no_structural_expansion_is_bounded_at_three_attempts():
    _, kwargs = _inputs("persistent-procedure-mismatch")
    result = run_no_structural_expansion_ablation(**kwargs)

    assert result.procedure_success is False
    assert result.evaluated_scope_indices == (0, 1, 2)
    assert result.procedure_attempt_count == 3
    assert result.forced_recovery_scope_count == 2
    assert len(set(result.execution_ids)) == 3


def test_familiarity_disabled_preserves_control_retrieval_and_procedure_evidence():
    _, kwargs = _inputs("easy-familiar-success")
    primary = run_asca_primary(**kwargs)
    disabled = run_familiarity_disabled_ablation(**kwargs)

    assert disabled.variant is ComparisonVariant.ASCA_FAMILIARITY_DISABLED
    assert replace(disabled, variant=ComparisonVariant.ASCA_PRIMARY) == primary


def test_familiarity_disabled_uses_empty_index_without_mutating_shared_inputs():
    _, kwargs = _inputs("easy-familiar-success")
    context = kwargs["retrieval_context"]
    library = kwargs["procedure_library"]
    factory = kwargs["procedure_executor_factory"]
    before = (
        context.minimum_similarity,
        context.cue_tiers,
        tuple(item.procedure.procedure_id for item in library.procedures),
        factory.initial_world_state_ref,
    )
    run_familiarity_disabled_ablation(**kwargs)
    after = (
        context.minimum_similarity,
        context.cue_tiers,
        tuple(item.procedure.procedure_id for item in library.procedures),
        factory.initial_world_state_ref,
    )

    assert after == before
