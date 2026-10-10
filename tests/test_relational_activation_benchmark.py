from __future__ import annotations

from dataclasses import replace

from flywire_asca.relational_activation.benchmark import (
    EXPECTED_A013_CASE_IDS,
    EXPECTED_A013_FIXTURE_FINGERPRINT,
    EXPECTED_A013_SHARED_INPUT_FINGERPRINTS,
    a013_fixture_fingerprint,
    benchmark_report_payload,
    build_a013_deterministic_fixture,
    classify_a013_architecture,
    run_a013_benchmark,
    shared_input_fingerprint,
)
from flywire_asca.relational_activation import (
    RelationalActivationDecision,
    RelationalActivationPolicy,
)


def test_a013_fixture_identity_and_literal_fingerprints_are_frozen():
    cases = build_a013_deterministic_fixture()
    assert tuple(case.case_id for case in cases) == EXPECTED_A013_CASE_IDS
    assert a013_fixture_fingerprint(cases) == EXPECTED_A013_FIXTURE_FINGERPRINT
    assert tuple(
        (case.case_id, shared_input_fingerprint(case))
        for case in cases
    ) == EXPECTED_A013_SHARED_INPUT_FINGERPRINTS


def test_a013_fixture_contains_declared_mixed_workload():
    cases = build_a013_deterministic_fixture()
    valid = [case for case in cases if case.case_id != "invalid-contract-control"]
    positives = [case for case in valid if case.primary_relation_positive]
    direct = [case for case in valid if not case.structural_need.active]
    structural_negative = [
        case
        for case in valid
        if case.structural_need.active and not case.primary_relation_positive
    ]
    assert len(cases) == 17
    assert len(valid) == 16
    assert len(positives) == 6
    assert len(direct) == 6
    assert len(structural_negative) == 4


def test_a013_portable_report_matches_frozen_primary_metrics():
    report = run_a013_benchmark()
    assert report.fixture_fingerprint == EXPECTED_A013_FIXTURE_FINGERPRINT
    assert (report.case_count, report.valid_case_count, report.invalid_case_count) == (
        17,
        16,
        1,
    )
    assert report.primary_relation_case_count == 6
    assert report.direct_control_count == 6
    assert report.vector_success_count == 10
    assert report.always_success_count == 16
    assert report.signal_success_count == 16
    assert report.vector_primary_relation_success_count == 0
    assert report.always_primary_relation_success_count == 6
    assert report.signal_primary_relation_success_count == 6
    assert report.vector_direct_success_count == 6
    assert report.signal_direct_success_count == 6
    assert report.always_relation_only_recovery_count == 6
    assert report.signal_relation_only_recovery_count == 6
    assert report.always_regression_count == 0
    assert report.signal_regression_count == 0
    assert report.always_relation_invocation_count == 16
    assert report.signal_relation_invocation_count == 10
    assert report.always_relation_scanned_edge_count == 16
    assert report.signal_relation_scanned_edge_count == 11
    assert report.always_relation_visited_node_count == 29
    assert report.signal_relation_visited_node_count == 18
    assert report.signal_false_activation_count == 0
    assert report.signal_missed_activation_count == 0
    assert report.identity_failure_count == 0
    assert report.provenance_failure_count == 0
    assert report.budget_violation_count == 0
    assert report.duplicate_visit_failure_count == 0
    assert report.deterministic_repeat_match is True
    assert (
        classify_a013_architecture(report)
        is RelationalActivationDecision.SIGNAL_GATED_RELATION_JUSTIFIED
    )


def test_a013_relation_positives_recover_without_runtime_target_oracle():
    report = run_a013_benchmark()
    positives = [
        result
        for result in report.case_results
        if result.primary_relation_positive
    ]
    assert len(positives) == 6
    for result in positives:
        by_policy = {run.policy: run for run in result.runs}
        vector = by_policy[RelationalActivationPolicy.VECTOR_ONLY]
        always = by_policy[RelationalActivationPolicy.ALWAYS_RELATION]
        signal = by_policy[RelationalActivationPolicy.SIGNAL_GATED_RELATION]
        assert vector.task_success is False
        assert always.task_success is True
        assert signal.task_success is True
        assert always.relation_invoked is True
        assert signal.relation_invoked is True
        assert signal.provenance_complete is True
        assert signal.identity_preserved is True


def test_a013_nonstructural_controls_skip_signal_relation_without_regression():
    report = run_a013_benchmark()
    direct = [
        result
        for result in report.case_results
        if not result.validation_error_observed and not result.structural_need_active
    ]
    assert len(direct) == 6
    for result in direct:
        by_policy = {run.policy: run for run in result.runs}
        vector = by_policy[RelationalActivationPolicy.VECTOR_ONLY]
        always = by_policy[RelationalActivationPolicy.ALWAYS_RELATION]
        signal = by_policy[RelationalActivationPolicy.SIGNAL_GATED_RELATION]
        assert vector.task_success is True
        assert signal.task_success is True
        assert signal.relation_invoked is False
        assert always.relation_invoked is True


def test_a013_invalid_contract_fails_closed_outside_success_denominator():
    report = run_a013_benchmark()
    invalid = [
        result for result in report.case_results if result.validation_error_observed
    ]
    assert len(invalid) == 1
    assert invalid[0].case_id == "invalid-contract-control"
    assert "unknown target_id absent-target" in (invalid[0].validation_error or "")
    assert invalid[0].runs == ()


def test_a013_fixture_hash_changes_when_input_changes():
    cases = build_a013_deterministic_fixture()
    tampered = list(cases)
    tampered[0] = replace(tampered[0], query_text="tampered query")
    assert a013_fixture_fingerprint(tampered) != EXPECTED_A013_FIXTURE_FINGERPRINT


def test_a013_report_payload_records_decision_and_raw_case_evidence():
    report = run_a013_benchmark()
    payload = benchmark_report_payload(report)
    assert payload["decision"] == "SIGNAL_GATED_RELATION_JUSTIFIED"
    assert payload["fixture_fingerprint"] == EXPECTED_A013_FIXTURE_FINGERPRINT
    assert len(payload["cases"]) == 17
    assert payload["cases"][0]["runs"][0]["policy"] == "VECTOR_ONLY"
