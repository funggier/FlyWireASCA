from __future__ import annotations

from dataclasses import replace

from flywire_asca.baseline_comparison import ComparisonVariant
from flywire_asca.baseline_comparison.benchmark import (
    a010_fixture_fingerprint,
    build_a010_deterministic_fixture,
    classify_a010_hypothesis,
    qualify_a010_report,
    run_a010_benchmark,
    shared_input_fingerprint,
)


EXPECTED_CASE_IDS = (
    "easy-local-many-distractors",
    "unfamiliar-semantic-many-distractors",
    "structural-expansion-required",
    "procedure-recovery-one-scope",
    "procedure-recovery-two-scopes",
    "persistent-missing-memory",
    "selective-routing-miss-sentinel",
    "same-name-identity",
    "tie-heavy-distractors",
    "structural-expansion-ablation",
    "familiarity-disabled-equivalence",
    "invalid-contract",
)


def _run(case_result, variant: ComparisonVariant):
    return next(item for item in case_result.runs if item.variant is variant)


def test_fixture_case_ids_sizes_and_fingerprints_are_stable():
    cases = build_a010_deterministic_fixture()
    assert tuple(case.case_id for case in cases) == EXPECTED_CASE_IDS
    assert {16, 64, 256}.issubset({case.corpus_size for case in cases})
    fingerprint = a010_fixture_fingerprint(cases)
    assert len(fingerprint) == 64
    int(fingerprint, 16)
    assert a010_fixture_fingerprint(build_a010_deterministic_fixture()) == fingerprint
    assert len({shared_input_fingerprint(case) for case in cases}) == len(cases)


def test_shared_input_fingerprint_changes_on_shared_input_not_metadata():
    case = build_a010_deterministic_fixture()[0]
    baseline = shared_input_fingerprint(case)
    assert shared_input_fingerprint(
        replace(case, designated_parity_reduction=not case.designated_parity_reduction)
    ) == baseline
    assert shared_input_fingerprint(
        replace(case, minimum_similarity=case.minimum_similarity - 0.1)
    ) != baseline
    changed_memory = replace(
        case.memories[0],
        retrieval_text=case.memories[0].retrieval_text + "-changed",
    )
    assert shared_input_fingerprint(
        replace(case, memories=(changed_memory, *case.memories[1:]))
    ) != baseline


def test_benchmark_runs_primary_dense_and_declared_diagnostics():
    cases = build_a010_deterministic_fixture()
    report = run_a010_benchmark(cases)
    assert report.case_count == 12
    assert report.invalid_case_count == 1
    assert report.valid_case_count == 11
    assert report.primary_case_count == 9

    for case, result in zip(cases, report.case_results):
        if case.invalid_root:
            assert result.validation_error_observed is True
            assert result.runs == ()
            continue
        variants = {run.variant for run in result.runs}
        assert ComparisonVariant.ASCA_PRIMARY in variants
        assert ComparisonVariant.DENSE_EXHAUSTIVE in variants
        if case.run_structural_ablation:
            assert ComparisonVariant.ASCA_NO_STRUCTURAL_EXPANSION in variants
        if case.run_familiarity_ablation:
            assert ComparisonVariant.ASCA_FAMILIARITY_DISABLED in variants


def test_routing_miss_sentinel_preserves_honest_dense_only_success():
    report = run_a010_benchmark(build_a010_deterministic_fixture())
    result = next(
        item for item in report.case_results
        if item.case_id == "selective-routing-miss-sentinel"
    )
    asca = _run(result, ComparisonVariant.ASCA_PRIMARY)
    dense = _run(result, ComparisonVariant.DENSE_EXHAUSTIVE)

    assert asca.procedure_success is False
    assert dense.procedure_success is True
    assert report.dense_only_success_count >= 1


def test_same_name_case_preserves_both_identities():
    report = run_a010_benchmark(build_a010_deterministic_fixture())
    result = next(
        item for item in report.case_results if item.case_id == "same-name-identity"
    )
    asca = _run(result, ComparisonVariant.ASCA_PRIMARY)
    dense = _run(result, ComparisonVariant.DENSE_EXHAUSTIVE)
    assert asca.same_name_identity_preserved is True
    assert dense.same_name_identity_preserved is True
    assert {"mem-000-alex-a", "mem-001-alex-b"}.issubset(
        asca.final_selected_memory_ids
    )
    assert {"mem-000-alex-a", "mem-001-alex-b"}.issubset(
        dense.final_selected_memory_ids
    )


def test_benchmark_records_logical_work_and_active_state_separately():
    report = run_a010_benchmark(build_a010_deterministic_fixture())
    assert report.asca_query_count > 0
    assert report.dense_query_count > 0
    assert report.asca_scored_vector_count > 0
    assert report.dense_scored_vector_count > 0
    assert report.asca_cumulative_selected_count < report.dense_cumulative_selected_count
    assert report.designated_parity_reduction_count >= 1
    assert report.asca_deterministic_repeat_match is True
    assert report.dense_deterministic_repeat_match is True
    assert report.identity_failure_count == 0
    assert report.duplicate_execution_id_failure_count == 0
    assert report.post_completion_extra_attempt_failure_count == 0


def test_actual_fixture_remains_evidence_driven_and_is_not_supported_when_retrieval_work_does_not_drop():
    report = run_a010_benchmark(build_a010_deterministic_fixture())
    assert report.dense_only_success_count >= 1
    assert classify_a010_hypothesis(report) == "NOT_SUPPORTED"


def test_supported_requires_equal_success_and_three_dimension_reduction():
    report = run_a010_benchmark(build_a010_deterministic_fixture())
    supported = replace(
        report,
        asca_success_count=report.dense_success_count,
        shared_success_count=report.dense_success_count,
        dense_only_success_count=0,
        asca_only_success_count=0,
        asca_final_state_correct_count=report.dense_success_count,
        asca_query_count=report.dense_query_count - 1,
        asca_scored_vector_count=report.dense_scored_vector_count - 1,
        asca_cumulative_selected_count=report.dense_cumulative_selected_count - 1,
        designated_parity_reduction_count=max(1, report.designated_parity_reduction_count),
    )
    assert classify_a010_hypothesis(supported) == "SUPPORTED"


def test_mixed_when_reductions_exist_but_dense_has_additional_success():
    report = run_a010_benchmark(build_a010_deterministic_fixture())
    mixed = replace(
        report,
        asca_query_count=report.dense_query_count - 1,
        asca_scored_vector_count=report.dense_scored_vector_count - 1,
        asca_cumulative_selected_count=report.dense_cumulative_selected_count - 1,
        designated_parity_reduction_count=max(1, report.designated_parity_reduction_count),
    )
    assert mixed.dense_only_success_count >= 1
    assert classify_a010_hypothesis(mixed) == "MIXED"


def test_not_supported_when_declared_reductions_disappear():
    report = run_a010_benchmark(build_a010_deterministic_fixture())
    no_reduction = replace(
        report,
        asca_query_count=report.dense_query_count,
        asca_scored_vector_count=report.dense_scored_vector_count,
        asca_cumulative_selected_count=report.dense_cumulative_selected_count,
        designated_parity_reduction_count=0,
    )
    assert classify_a010_hypothesis(no_reduction) == "NOT_SUPPORTED"


def test_qualification_rejects_fingerprint_and_aggregate_drift():
    report = run_a010_benchmark(build_a010_deterministic_fixture())
    assert qualify_a010_report(report) == []

    first = report.case_results[0]
    drifted = replace(first, shared_input_fingerprint="0" * 64)
    errors = qualify_a010_report(
        replace(report, case_results=(drifted, *report.case_results[1:]))
    )
    assert any("fingerprint" in item.lower() for item in errors)

    errors = qualify_a010_report(
        replace(report, asca_query_count=report.asca_query_count + 1)
    )
    assert any("asca_query_count" in item for item in errors)

def test_shared_input_fingerprint_covers_execution_contract(monkeypatch):
    import flywire_asca.baseline_comparison.benchmark as benchmark

    case = benchmark.build_a010_deterministic_fixture()[0]
    baseline = benchmark.shared_input_fingerprint(case)

    original = benchmark._action_definitions
    def changed_actions():
        actions = original()
        first = actions[0]
        return (replace(first, writes=(("done", "different"),)), *actions[1:])

    monkeypatch.setattr(benchmark, "_action_definitions", changed_actions)
    assert benchmark.shared_input_fingerprint(case) != baseline


def test_benchmark_final_state_correctness_is_independent_of_procedure_success():
    import flywire_asca.baseline_comparison.benchmark as benchmark

    case = benchmark.build_a010_deterministic_fixture()[0]
    changed = replace(
        case,
        expected_final_state_items=(("done", "unexpected"),),
    )
    report = benchmark.run_a010_benchmark((changed,))
    result = report.case_results[0]
    by_variant = {run.variant: run for run in result.runs}

    assert by_variant[ComparisonVariant.ASCA_PRIMARY].procedure_success is True
    assert by_variant[ComparisonVariant.DENSE_EXHAUSTIVE].procedure_success is True
    assert by_variant[ComparisonVariant.ASCA_PRIMARY].final_state_correct is False
    assert by_variant[ComparisonVariant.DENSE_EXHAUSTIVE].final_state_correct is False


def test_report_qualification_rejects_primary_membership_and_variant_set_drift():
    report = run_a010_benchmark(build_a010_deterministic_fixture())

    first = report.case_results[0]
    changed_membership = replace(first, expected_primary_case=False)
    errors = qualify_a010_report(
        replace(report, case_results=(changed_membership, *report.case_results[1:]))
    )
    assert any("expected_primary_case" in item for item in errors)

    structural_index = next(
        index
        for index, item in enumerate(report.case_results)
        if item.case_id == "structural-expansion-ablation"
    )
    structural = report.case_results[structural_index]
    changed_variants = replace(
        structural,
        runs=tuple(
            run
            for run in structural.runs
            if run.variant is not ComparisonVariant.ASCA_NO_STRUCTURAL_EXPANSION
        ),
    )
    changed_results = list(report.case_results)
    changed_results[structural_index] = changed_variants
    errors = qualify_a010_report(
        replace(report, case_results=tuple(changed_results))
    )
    assert any("variant" in item.lower() for item in errors)
