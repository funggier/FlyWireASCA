from __future__ import annotations

from dataclasses import replace

from flywire_asca.structural_routing import RoutingPolicy, StructuralRoutingDecision
from flywire_asca.structural_routing.benchmark import (
    benchmark_report_payload,
    build_portable_scripted_adapters,
    classify_a014_architecture,
    run_a014_benchmark,
)


def _portable_report():
    return run_a014_benchmark(adapters_by_policy=build_portable_scripted_adapters())


def _metrics(report, policy):
    return next(item for item in report.policy_metrics if item.policy is policy)


def _replace_metrics(report, policy, **changes):
    updated = tuple(
        replace(item, **changes) if item.policy is policy else item
        for item in report.policy_metrics
    )
    return replace(report, policy_metrics=updated)


def test_portable_scripted_benchmark_has_expected_policy_metrics():
    report = _portable_report()
    assert report.case_count == 32
    assert report.fixture_fingerprint == "c100f828265063c369d535f85db8166cbeaaba26943fbb6d276a24dc46018eca"
    assert len(report.case_results) == 96

    rule = _metrics(report, RoutingPolicy.RULE_ONLY)
    model = _metrics(report, RoutingPolicy.MODEL_ONLY)
    hybrid = _metrics(report, RoutingPolicy.HYBRID_RULE_THEN_MODEL)

    assert (rule.structural_true_positive_count, rule.structural_true_negative_count) == (11, 12)
    assert (rule.false_activation_count, rule.missed_activation_count) == (0, 9)
    assert rule.exact_relation_set_match_count == 23
    assert rule.abstention_count == 9
    assert rule.downstream_success_count == 27
    assert rule.relation_positive_success_count == 7
    assert rule.direct_control_success_count == 12
    assert rule.structural_control_success_count == 8
    assert rule.oracle_regression_count == 5
    assert rule.model_invocation_count == 0
    assert rule.relation_invocation_count == 11

    for item in (model, hybrid):
        assert item.structural_true_positive_count == 20
        assert item.structural_true_negative_count == 12
        assert item.false_activation_count == 0
        assert item.missed_activation_count == 0
        assert item.exact_relation_set_match_count == 32
        assert item.downstream_success_count == 32
        assert item.relation_positive_success_count == 12
        assert item.direct_control_success_count == 12
        assert item.structural_control_success_count == 8
        assert item.oracle_regression_count == 0
        assert item.relation_invocation_count == 20

    assert model.model_invocation_count == 32
    assert hybrid.model_invocation_count == 9
    assert hybrid.model_invocation_count < model.model_invocation_count
    assert report.leakage_failure_count == 0
    assert report.identity_failure_count == 0
    assert report.provenance_failure_count == 0
    assert report.budget_violation_count == 0
    assert report.duplicate_visit_failure_count == 0


def test_portable_scripted_runs_are_deterministic_on_raw_case_evidence():
    first = _portable_report()
    second = _portable_report()
    assert first.case_results == second.case_results
    assert first.policy_metrics == second.policy_metrics
    assert benchmark_report_payload(first) == benchmark_report_payload(second)


def test_classifier_hybrid_branch_requires_best_correctness_fewer_model_calls_and_binding():
    report = replace(_portable_report(), physical_evidence_bound=True)
    assert classify_a014_architecture(report) is StructuralRoutingDecision.HYBRID_STRUCTURAL_ROUTING_JUSTIFIED
    assert classify_a014_architecture(replace(report, physical_evidence_bound=False)) is StructuralRoutingDecision.MIXED


def test_classifier_rule_sufficient_branch_takes_precedence_when_rules_match_best():
    report = replace(_portable_report(), physical_evidence_bound=True)
    rule = _metrics(report, RoutingPolicy.RULE_ONLY)
    best = _metrics(report, RoutingPolicy.MODEL_ONLY)
    report = _replace_metrics(
        report,
        RoutingPolicy.RULE_ONLY,
        structural_true_positive_count=best.structural_true_positive_count,
        missed_activation_count=best.missed_activation_count,
        exact_relation_set_match_count=best.exact_relation_set_match_count,
        downstream_success_count=best.downstream_success_count,
        relation_positive_success_count=best.relation_positive_success_count,
        oracle_regression_count=0,
    )
    assert _metrics(report, RoutingPolicy.RULE_ONLY).model_invocation_count == rule.model_invocation_count == 0
    assert classify_a014_architecture(report) is StructuralRoutingDecision.RULE_ROUTING_SUFFICIENT


def test_classifier_model_preferred_branch_requires_strict_downstream_advantage():
    report = replace(_portable_report(), physical_evidence_bound=True)
    report = _replace_metrics(
        report, RoutingPolicy.HYBRID_RULE_THEN_MODEL,
        downstream_success_count=31, relation_positive_success_count=11,
        exact_relation_set_match_count=31, missed_activation_count=1,
    )
    assert classify_a014_architecture(report) is StructuralRoutingDecision.MODEL_ROUTING_PREFERRED


def test_classifier_not_supported_when_no_policy_recovers_relation_positive_work():
    report = replace(_portable_report(), physical_evidence_bound=True)
    for policy in RoutingPolicy:
        report = _replace_metrics(
            report, policy, downstream_success_count=20, relation_positive_success_count=0
        )
    assert classify_a014_architecture(report) is StructuralRoutingDecision.STRUCTURAL_ROUTING_NOT_SUPPORTED


def test_classifier_not_supported_on_global_leakage_failure():
    report = replace(_portable_report(), physical_evidence_bound=True, leakage_failure_count=1)
    assert classify_a014_architecture(report) is StructuralRoutingDecision.STRUCTURAL_ROUTING_NOT_SUPPORTED


def test_classifier_mixed_for_valid_evidence_with_no_predeclared_preference():
    report = replace(_portable_report(), physical_evidence_bound=True)
    report = _replace_metrics(
        report, RoutingPolicy.MODEL_ONLY,
        downstream_success_count=31, relation_positive_success_count=11,
        exact_relation_set_match_count=31,
    )
    model_calls = _metrics(report, RoutingPolicy.MODEL_ONLY).model_invocation_count
    report = _replace_metrics(
        report, RoutingPolicy.HYBRID_RULE_THEN_MODEL,
        downstream_success_count=31, relation_positive_success_count=11,
        exact_relation_set_match_count=31, model_invocation_count=model_calls,
    )
    assert classify_a014_architecture(report) is StructuralRoutingDecision.MIXED
