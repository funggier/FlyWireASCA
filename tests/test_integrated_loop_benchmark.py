from __future__ import annotations

from dataclasses import replace

from flywire_asca.integrated_loop import (
    LoopPolicy,
    build_a009_deterministic_fixture,
    classify_a009_hypothesis,
    fixture_fingerprint,
    qualify_a009_report,
    run_a009_benchmark,
)


EXPECTED_CASE_IDS = (
    "easy-familiar-success",
    "unfamiliar-semantic-success",
    "structural-expansion-success",
    "procedure-recovery-round-one",
    "procedure-recovery-round-two",
    "persistent-procedure-mismatch",
    "max-scope-mismatch",
    "same-name-ambiguity-preserved",
    "model-terminal-fallback",
    "invalid-contract",
)


def _policy(case_result, policy: LoopPolicy):
    return next(item for item in case_result.policy_results if item.policy is policy)


def test_fixture_families_are_exact_unique_and_fingerprint_is_stable():
    cases = build_a009_deterministic_fixture()
    assert tuple(case.case_id for case in cases) == EXPECTED_CASE_IDS
    assert len({case.case_id for case in cases}) == len(cases)
    fingerprint = fixture_fingerprint(cases)
    assert len(fingerprint) == 64
    int(fingerprint, 16)
    assert fixture_fingerprint(build_a009_deterministic_fixture()) == fingerprint


def test_every_valid_case_runs_all_three_loop_policies():
    report = run_a009_benchmark(build_a009_deterministic_fixture())
    assert report.case_count == 10
    assert report.valid_case_count == 9
    assert report.invalid_case_count == 1
    invalid = next(item for item in report.case_results if item.case_id == "invalid-contract")
    assert invalid.validation_error_observed is True
    assert invalid.policy_results == ()
    for item in report.case_results:
        if item.case_id == "invalid-contract":
            continue
        assert tuple(result.policy for result in item.policy_results) == (
            LoopPolicy.NO_PROCEDURE_RECOVERY,
            LoopPolicy.MISMATCH_DRIVEN_RECOVERY,
            LoopPolicy.ALWAYS_MAX_SCOPE,
        )


def test_recovery_cases_distinguish_no_recovery_primary_and_always_max():
    report = run_a009_benchmark(build_a009_deterministic_fixture())

    round_one = next(
        item for item in report.case_results
        if item.case_id == "procedure-recovery-round-one"
    )
    no_recovery = _policy(round_one, LoopPolicy.NO_PROCEDURE_RECOVERY)
    primary = _policy(round_one, LoopPolicy.MISMATCH_DRIVEN_RECOVERY)
    always = _policy(round_one, LoopPolicy.ALWAYS_MAX_SCOPE)
    assert no_recovery.procedure_success is False
    assert primary.procedure_success is True
    assert primary.evaluated_scope_indices == (0, 1)
    assert primary.procedure_attempt_count == 2
    assert primary.forced_recovery_scope_count == 1
    assert always.procedure_success is True
    assert always.evaluated_scope_indices == (0, 1, 2)
    assert always.procedure_attempt_count == 1

    round_two = next(
        item for item in report.case_results
        if item.case_id == "procedure-recovery-round-two"
    )
    primary_two = _policy(round_two, LoopPolicy.MISMATCH_DRIVEN_RECOVERY)
    assert primary_two.evaluated_scope_indices == (0, 1, 2)
    assert primary_two.procedure_attempt_count == 3
    assert primary_two.forced_recovery_scope_count == 2


def test_report_measures_boundedness_regression_scope_savings_and_ambiguity():
    report = run_a009_benchmark(build_a009_deterministic_fixture())
    assert report.genuine_recovery_count >= 2
    assert report.regression_count == 0
    assert report.primary_recoverable_success_count == report.always_recoverable_success_count
    assert report.primary_total_scope_evaluations < report.always_total_scope_evaluations
    assert report.max_procedure_attempt_count <= 3
    assert report.max_scope_index <= 2
    assert report.duplicate_execution_id_failure_count == 0
    assert report.primary_same_name_ambiguity_failure_count == 0
    assert report.primary_final_state_correct_count == report.primary_success_count
    assert report.chunked_flat_equivalence_count == report.chunked_flat_diagnostic_case_count
    assert report.deterministic_repeat_match is True


def test_same_name_case_preserves_both_memory_identities():
    report = run_a009_benchmark(build_a009_deterministic_fixture())
    case = next(
        item for item in report.case_results
        if item.case_id == "same-name-ambiguity-preserved"
    )
    primary = _policy(case, LoopPolicy.MISMATCH_DRIVEN_RECOVERY)
    assert {"mem-alex-a", "mem-alex-b"}.issubset(primary.final_working_set_ids)
    assert primary.same_name_ambiguity_preserved is True


def test_model_fallback_is_recorded_but_does_not_convert_failure_to_success():
    report = run_a009_benchmark(build_a009_deterministic_fixture())
    case = next(
        item for item in report.case_results
        if item.case_id == "model-terminal-fallback"
    )
    primary = _policy(case, LoopPolicy.MISMATCH_DRIVEN_RECOVERY)
    assert primary.model_fallback_called is True
    assert primary.procedure_success is False
    assert report.model_fallback_call_count >= 1
    assert report.model_control_leakage_failure_count == 0


def test_primary_fixture_classifies_supported_and_qualification_is_clean():
    report = run_a009_benchmark(build_a009_deterministic_fixture())
    assert classify_a009_hypothesis(report) == "SUPPORTED"
    assert qualify_a009_report(report) == []


def test_classification_not_supported_without_genuine_recovery_and_mixed_on_regression():
    report = run_a009_benchmark(build_a009_deterministic_fixture())
    assert classify_a009_hypothesis(
        replace(report, genuine_recovery_count=0)
    ) == "NOT_SUPPORTED"
    assert classify_a009_hypothesis(
        replace(report, regression_count=1)
    ) == "MIXED"


def test_qualification_rejects_impossible_boundedness_and_count_relationships():
    report = run_a009_benchmark(build_a009_deterministic_fixture())
    errors = qualify_a009_report(
        replace(report, max_procedure_attempt_count=4)
    )
    assert any("max_procedure_attempt_count" in error for error in errors)

    errors = qualify_a009_report(
        replace(
            report,
            primary_recoverable_success_count=report.recoverable_case_count + 1,
        )
    )
    assert any("recoverable" in error.lower() for error in errors)
