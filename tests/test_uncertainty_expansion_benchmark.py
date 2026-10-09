from __future__ import annotations

from dataclasses import fields

from flywire_asca.uncertainty_expansion import (
    ExpansionTerminationReason,
    UncertaintyExpansionBenchmarkReport,
    build_a007_portable_fixture,
    qualify_a007_report,
    run_a007_benchmark,
)


def test_portable_fixture_covers_required_controller_and_policy_cases():
    cases = build_a007_portable_fixture()
    ids = {case.case_id for case in cases}
    assert {
        "easy-stop",
        "recover-round-1",
        "recover-round-2",
        "memory-budget-truncation",
        "working-set-truncation",
        "memory-boundary-tie",
        "working-set-boundary-tie",
        "persistent-insufficient",
        "same-name-ambiguity",
        "initially-sufficient-no-regression",
        "unsupported-state-validation",
        "inconsistent-state-validation",
        "deterministic-repeat",
    } <= ids


def test_portable_benchmark_passes_engineering_gates():
    report = run_a007_benchmark(build_a007_portable_fixture())

    assert report.case_count == 13
    assert report.total_required_memory_ids > 0
    assert report.no_expansion_required_memory_coverage < 1.0
    assert report.signal_driven_required_memory_coverage == 1.0
    assert report.always_expand_required_memory_coverage == 1.0
    assert report.signal_driven_recovery_count >= 2
    assert report.signal_driven_regression_count == 0
    assert report.easy_unnecessary_expansion_count == 0
    assert report.persistent_insufficient_expected_count == 1
    assert report.persistent_insufficient_exhausted_count == 1
    assert report.ambiguity_failure_count == 0
    assert report.structural_validation_failure_count == 0
    assert report.max_signal_driven_rounds <= 3
    assert report.total_signal_driven_rounds < report.total_always_expand_rounds
    assert report.deterministic_repeat_match is True
    assert qualify_a007_report(report) == []


def test_recovery_cases_are_measured_against_no_expansion():
    report = run_a007_benchmark(build_a007_portable_fixture())

    round1 = next(
        item for item in report.case_results
        if item.case_id == "recover-round-1"
    )
    assert round1.required_memory_ids == ("target-r1",)
    assert round1.no_expansion_selected_ids == ()
    assert round1.signal_driven_selected_ids == ("target-r1",)
    assert round1.always_expand_selected_ids == ("target-r1",)
    assert round1.signal_driven_recovered is True
    assert round1.signal_driven_round_count == 2

    round2 = next(
        item for item in report.case_results
        if item.case_id == "recover-round-2"
    )
    assert round2.no_expansion_selected_ids == ()
    assert round2.signal_driven_selected_ids == ("target-r2",)
    assert round2.signal_driven_recovered is True
    assert round2.signal_driven_round_count == 3


def test_easy_case_stops_without_unnecessary_expansion():
    report = run_a007_benchmark(build_a007_portable_fixture())
    easy = next(item for item in report.case_results if item.case_id == "easy-stop")

    assert easy.initially_sufficient is True
    assert easy.signal_driven_round_count == 1
    assert easy.signal_driven_unnecessary_expansion is False
    assert (
        easy.signal_driven_termination_reason
        is ExpansionTerminationReason.CONTROLLER_STOP
    )
    assert easy.always_expand_round_count == 3


def test_persistent_insufficient_is_bounded_and_exhausted():
    report = run_a007_benchmark(build_a007_portable_fixture())
    case = next(
        item for item in report.case_results
        if item.case_id == "persistent-insufficient"
    )
    assert case.persistent_insufficient is True
    assert case.signal_driven_round_count == 3
    assert (
        case.signal_driven_termination_reason
        is ExpansionTerminationReason.CONTROLLER_EXHAUSTED
    )


def test_validation_cases_are_expected_fail_closed_evidence():
    report = run_a007_benchmark(build_a007_portable_fixture())

    unsupported = next(
        item for item in report.case_results
        if item.case_id == "unsupported-state-validation"
    )
    inconsistent = next(
        item for item in report.case_results
        if item.case_id == "inconsistent-state-validation"
    )
    assert unsupported.expected_validation_error == "retrieval_state"
    assert unsupported.validation_error_observed is True
    assert inconsistent.expected_validation_error == "RECALLED"
    assert inconsistent.validation_error_observed is True
    assert report.structural_validation_failure_count == 0


def test_empty_required_engineering_cases_do_not_inflate_coverage():
    report = run_a007_benchmark(build_a007_portable_fixture())
    denominator = sum(
        len(item.required_memory_ids)
        for item in report.case_results
        if item.expected_validation_error is None
    )
    assert report.total_required_memory_ids == denominator
    assert denominator > 0

    engineering_only = [
        item for item in report.case_results
        if not item.required_memory_ids
        and item.expected_validation_error is None
    ]
    assert engineering_only


def test_policy_round_counts_obey_control_semantics():
    report = run_a007_benchmark(build_a007_portable_fixture())
    valid_case_count = sum(
        item.expected_validation_error is None
        for item in report.case_results
    )
    assert report.total_no_expansion_rounds == valid_case_count
    assert report.total_always_expand_rounds == valid_case_count * 3
    assert report.total_signal_driven_rounds <= valid_case_count * 3
    assert report.no_expansion_policy_termination_count == valid_case_count
    assert report.always_expand_policy_termination_count == valid_case_count
    assert (
        report.signal_driven_controller_stop_count
        + report.signal_driven_controller_exhausted_count
        == valid_case_count
    )


def test_portable_report_is_deterministic_across_full_repeated_runs():
    first = run_a007_benchmark(build_a007_portable_fixture())
    second = run_a007_benchmark(build_a007_portable_fixture())
    assert first == second
    assert first.deterministic_repeat_match is True


def test_portable_report_does_not_claim_physical_outcome_or_scalar_surprise():
    names = {field.name.lower() for field in fields(UncertaintyExpansionBenchmarkReport)}
    joined = " ".join(sorted(names))
    assert "hypothesis_outcome" not in names
    assert "supported" not in names
    assert "mixed" not in names
    assert "not_supported" not in names
    assert "surprise_score" not in names
    assert "uncertainty_score" not in names
    assert "flop" not in joined
    assert "energy" not in joined
    assert "power" not in joined
