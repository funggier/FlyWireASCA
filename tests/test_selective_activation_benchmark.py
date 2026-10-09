from __future__ import annotations

from dataclasses import fields

from flywire_asca.selective_activation import (
    SelectiveActivationBenchmarkReport,
    build_a006_portable_fixture,
    qualify_a006_report,
    run_a006_benchmark,
)


def test_portable_fixture_covers_required_behavior_and_256_distractors():
    cases = build_a006_portable_fixture()
    ids = {case.case_id for case in cases}
    required = {
        "single-query",
        "convergence-recovery",
        "convergence-parity",
        "memory-budget",
        "working-set-budget",
        "memory-boundary-tie",
        "working-set-boundary-tie",
        "same-name-ambiguity",
        "confidence-independence",
        "insufficient-evidence",
        "duplicate-cue-validation",
        "profile-mismatch-validation",
        "deterministic-repeat",
        "distractor-heavy",
    }
    assert required <= ids

    distractor = next(case for case in cases if case.case_id == "distractor-heavy")
    unique_ids = {
        hit.memory_id
        for evidence in distractor.evidence
        for hit in evidence.result.hits
    }
    assert len([memory_id for memory_id in unique_ids if memory_id.startswith("distractor-")]) >= 256


def test_portable_benchmark_passes_engineering_gates_and_records_raw_counts():
    report = run_a006_benchmark(build_a006_portable_fixture())

    assert report.case_count == 14
    assert report.required_memory_coverage == 1.0
    assert report.active_memory_required_coverage == 1.0
    assert report.exhaustive_required_memory_coverage == 1.0
    assert report.convergence_recovery_count >= 1
    assert report.convergence_regression_count == 0
    assert report.ambiguity_failure_count == 0
    assert report.confidence_separation_failure_count == 0
    assert report.budget_violation_count == 0
    assert report.count_invariant_failure_count == 0
    assert report.validation_failure_count == 0
    assert report.deterministic_repeat_match is True
    assert report.total_input_hits >= report.total_unique_candidates
    assert report.total_unique_candidates >= report.total_positive_candidates
    assert report.total_positive_candidates >= report.total_activated_candidates
    assert report.total_activated_candidates >= report.total_selected_items
    assert report.total_memory_budget_drops >= 0
    assert report.total_working_set_budget_drops >= 0
    assert report.boundary_tie_count >= 2
    assert 0.0 <= report.selected_set_precision <= 1.0
    assert 0.0 <= report.aggregate_active_state_reduction_ratio <= 1.0
    assert report.aggregate_active_state_reduction_ratio > 0.9

    assert qualify_a006_report(report) == []


def test_convergence_recovery_case_beats_single_best_without_regression():
    report = run_a006_benchmark(build_a006_portable_fixture())
    result = next(
        item for item in report.case_results
        if item.case_id == "convergence-recovery"
    )
    assert result.required_memory_ids == ("target",)
    assert result.selective_selected_ids == ("target",)
    assert result.single_best_selected_ids != ("target",)
    assert "target" in result.exhaustive_selected_ids
    assert result.convergence_recovered is True
    assert result.convergence_regressed is False


def test_ambiguity_confidence_and_no_hit_cases_remain_explicit():
    report = run_a006_benchmark(build_a006_portable_fixture())

    ambiguity = next(
        item for item in report.case_results
        if item.case_id == "same-name-ambiguity"
    )
    assert set(ambiguity.selective_selected_ids) == {"somchai-a", "somchai-b"}
    assert ambiguity.ambiguity_preserved is True

    confidence = next(
        item for item in report.case_results
        if item.case_id == "confidence-independence"
    )
    assert confidence.selective_selected_ids == ("low-confidence",)
    assert confidence.confidence_separated is True

    no_hit = next(
        item for item in report.case_results
        if item.case_id == "insufficient-evidence"
    )
    assert no_hit.selective_selected_ids == ()
    assert no_hit.expected_no_selection is True
    assert no_hit.no_selection_correct is True


def test_expected_validation_failures_are_captured_not_silently_ignored():
    report = run_a006_benchmark(build_a006_portable_fixture())
    duplicate = next(
        item for item in report.case_results
        if item.case_id == "duplicate-cue-validation"
    )
    mismatch = next(
        item for item in report.case_results
        if item.case_id == "profile-mismatch-validation"
    )
    assert duplicate.expected_validation_error == "source_cue_id"
    assert duplicate.validation_error_observed is True
    assert mismatch.expected_validation_error == "embedding_profile"
    assert mismatch.validation_error_observed is True
    assert report.validation_failure_count == 0


def test_active_state_reduction_formula_and_zero_positive_convention():
    report = run_a006_benchmark(build_a006_portable_fixture())

    distractor = next(
        item for item in report.case_results
        if item.case_id == "distractor-heavy"
    )
    assert distractor.active_state_reduction_ratio == (
        distractor.positive_candidate_count - distractor.selected_count
    ) / distractor.positive_candidate_count

    no_hit = next(
        item for item in report.case_results
        if item.case_id == "insufficient-evidence"
    )
    assert no_hit.positive_candidate_count == 0
    assert no_hit.active_state_reduction_ratio == 0.0

    assert report.aggregate_active_state_reduction_ratio == (
        report.total_positive_candidates - report.total_selected_items
    ) / report.total_positive_candidates


def test_report_is_deterministic_across_repeated_full_runs():
    first = run_a006_benchmark(build_a006_portable_fixture())
    second = run_a006_benchmark(build_a006_portable_fixture())
    assert first == second
    assert first.deterministic_repeat_match is True


def test_report_contract_does_not_encode_compute_or_energy_reduction_claims():
    names = {field.name.lower() for field in fields(SelectiveActivationBenchmarkReport)}
    joined = " ".join(sorted(names))
    assert "flop" not in joined
    assert "energy" not in joined
    assert "hardware" not in joined
    assert "compute_reduction" not in joined
    assert "active_state_reduction" in joined
