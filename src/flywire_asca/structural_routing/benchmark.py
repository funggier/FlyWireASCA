from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, fields
import hashlib
import json

from flywire_asca.model import ModelAdapter, ModelResponse
from flywire_asca.relational_activation import StructuralNeed

from .benchmark_fixture import (
    EXPECTED_A014_CASE_IDS,
    EXPECTED_A014_EVALUATOR_FINGERPRINTS,
    EXPECTED_A014_FIXTURE_FINGERPRINT,
    EXPECTED_A014_RUNTIME_INPUT_FINGERPRINTS,
    a014_fixture_fingerprint,
    build_a014_frozen_fixture,
    evaluator_metadata_fingerprint,
    runtime_input_fingerprint,
)
from .evaluation import RoutingPolicyCaseResult, evaluate_routing_case
from .model_router import router_prompt_fingerprint
from .models import (
    RoutingInferenceStatus,
    RoutingPolicy,
    StructuralRoutingDecision,
    StructuralRoutingRequest,
    StructuralRoutingResult,
)


@dataclass(frozen=True, slots=True)
class RoutingPolicyMetrics:
    policy: RoutingPolicy
    valid_case_count: int
    structural_true_positive_count: int
    structural_true_negative_count: int
    false_activation_count: int
    missed_activation_count: int
    exact_relation_set_match_count: int
    relation_set_over_selection_count: int
    relation_set_under_selection_count: int
    invalid_model_output_count: int
    model_error_count: int
    abstention_count: int
    downstream_success_count: int
    relation_positive_success_count: int
    direct_control_success_count: int
    structural_control_success_count: int
    oracle_regression_count: int
    model_invocation_count: int
    relation_invocation_count: int
    relation_scanned_edge_count: int
    relation_visited_node_count: int
    prompt_tokens_total: int | None
    generated_tokens_total: int | None
    identity_failure_count: int
    provenance_failure_count: int
    budget_violation_count: int
    duplicate_visit_failure_count: int


@dataclass(frozen=True, slots=True)
class StructuralRoutingBenchmarkReport:
    fixture_fingerprint: str
    case_ids: tuple[str, ...]
    runtime_input_fingerprints: tuple[tuple[str, str], ...]
    evaluator_metadata_fingerprints: tuple[tuple[str, str], ...]
    prompt_fingerprint: str
    case_results: tuple[RoutingPolicyCaseResult, ...]
    policy_metrics: tuple[RoutingPolicyMetrics, ...]
    case_count: int
    leakage_failure_count: int
    identity_failure_count: int
    provenance_failure_count: int
    budget_violation_count: int
    duplicate_visit_failure_count: int
    deterministic_repeat_match: bool = False
    physical_evidence_bound: bool = False


class _PortableScriptedAdapter:
    def __init__(self) -> None:
        mapping: dict[str, str] = {}
        for case in build_a014_frozen_fixture():
            need = case.expected_structural_need
            payload = json.dumps(
                {
                    "requires_relation": need.active,
                    "required_relations": [relation.value for relation in need.required_relations],
                    "requires_path_provenance": need.requires_path_provenance,
                },
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            )
            prior = mapping.get(case.query_text)
            if prior is not None and prior != payload:
                raise ValueError("portable scripted query mapping is ambiguous")
            mapping[case.query_text] = payload
        self._mapping = mapping
        mapping_bytes = json.dumps(
            mapping, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
        self._digest = hashlib.sha256(mapping_bytes).hexdigest()

    def generate(self, request):
        query_text = request.messages[-1].content
        content = self._mapping[query_text]
        return ModelResponse(
            request_id=request.request_id,
            model_name="a014-portable-scripted-router",
            model_digest=self._digest,
            content=content,
            finish_reason="stop",
            prompt_tokens=0,
            generated_tokens=0,
            total_duration_ns=0,
            load_duration_ns=0,
            prompt_eval_duration_ns=0,
            eval_duration_ns=0,
        )


def build_portable_scripted_adapters() -> dict[RoutingPolicy, ModelAdapter | None]:
    return {
        RoutingPolicy.RULE_ONLY: None,
        RoutingPolicy.MODEL_ONLY: _PortableScriptedAdapter(),
        RoutingPolicy.HYBRID_RULE_THEN_MODEL: _PortableScriptedAdapter(),
    }


def _usage_total(results: tuple[RoutingPolicyCaseResult, ...], field_name: str) -> int | None:
    invoked = [result.routing_result for result in results if result.routing_result.model_invoked]
    if not invoked:
        return 0
    values = [getattr(result, field_name) for result in invoked]
    if any(value is None for value in values):
        return None
    return sum(values)


def _policy_metrics(
    policy: RoutingPolicy,
    results: tuple[RoutingPolicyCaseResult, ...],
) -> RoutingPolicyMetrics:
    expected_active = [result.expected_structural_need.active for result in results]
    inferred_active = [result.routing_result.structural_need.active for result in results]
    exact_relation = [
        result.routing_result.structural_need.required_relations
        == result.expected_structural_need.required_relations
        for result in results
    ]
    over = []
    under = []
    for result in results:
        actual = set(result.routing_result.structural_need.required_relations)
        expected = set(result.expected_structural_need.required_relations)
        over.append(bool(actual - expected))
        under.append(bool(expected - actual))

    direct = tuple(result for result in results if not result.expected_structural_need.active)
    relation_positive = tuple(result for result in results if result.primary_relation_positive)
    structural_controls = tuple(
        result
        for result in results
        if result.expected_structural_need.active and not result.primary_relation_positive
    )
    return RoutingPolicyMetrics(
        policy=policy,
        valid_case_count=len(results),
        structural_true_positive_count=sum(
            expected and actual for expected, actual in zip(expected_active, inferred_active)
        ),
        structural_true_negative_count=sum(
            (not expected) and (not actual)
            for expected, actual in zip(expected_active, inferred_active)
        ),
        false_activation_count=sum(
            (not expected) and actual
            for expected, actual in zip(expected_active, inferred_active)
        ),
        missed_activation_count=sum(
            expected and (not actual)
            for expected, actual in zip(expected_active, inferred_active)
        ),
        exact_relation_set_match_count=sum(exact_relation),
        relation_set_over_selection_count=sum(over),
        relation_set_under_selection_count=sum(under),
        invalid_model_output_count=sum(
            result.routing_result.status is RoutingInferenceStatus.INVALID_MODEL_OUTPUT
            for result in results
        ),
        model_error_count=sum(
            result.routing_result.status is RoutingInferenceStatus.MODEL_ERROR
            for result in results
        ),
        abstention_count=sum(
            result.routing_result.status is RoutingInferenceStatus.ABSTAINED
            for result in results
        ),
        downstream_success_count=sum(result.task_success for result in results),
        relation_positive_success_count=sum(result.task_success for result in relation_positive),
        direct_control_success_count=sum(result.task_success for result in direct),
        structural_control_success_count=sum(result.task_success for result in structural_controls),
        oracle_regression_count=sum(not result.task_success for result in results),
        model_invocation_count=sum(result.routing_result.model_invoked for result in results),
        relation_invocation_count=sum(result.relation_invoked for result in results),
        relation_scanned_edge_count=sum(result.relation_scanned_edge_count for result in results),
        relation_visited_node_count=sum(result.relation_visited_node_count for result in results),
        prompt_tokens_total=_usage_total(results, "prompt_tokens"),
        generated_tokens_total=_usage_total(results, "generated_tokens"),
        identity_failure_count=sum(not result.identity_preserved for result in results),
        provenance_failure_count=sum(not result.provenance_complete for result in results),
        budget_violation_count=sum(not result.budget_respected for result in results),
        duplicate_visit_failure_count=sum(not result.duplicate_visit_free for result in results),
    )


def _runtime_leakage_failure_count() -> int:
    forbidden = ("target", "expected", "answer", "benchmark", "label")
    failures = 0
    for cls in (StructuralRoutingRequest, StructuralRoutingResult):
        for field in fields(cls):
            name = field.name.casefold()
            failures += any(token in name for token in forbidden)
    prompt = router_prompt_fingerprint()
    failures += int(len(prompt) != 64)
    return failures


def run_a014_benchmark(
    *,
    adapters_by_policy: Mapping[RoutingPolicy, ModelAdapter | None],
) -> StructuralRoutingBenchmarkReport:
    cases = build_a014_frozen_fixture()
    results: list[RoutingPolicyCaseResult] = []
    for case in cases:
        for policy in RoutingPolicy:
            results.append(
                evaluate_routing_case(
                    case,
                    policy=policy,
                    model_adapter=adapters_by_policy.get(policy),
                )
            )
    case_results = tuple(results)
    policy_metrics = tuple(
        _policy_metrics(
            policy,
            tuple(result for result in case_results if result.policy is policy),
        )
        for policy in RoutingPolicy
    )
    return StructuralRoutingBenchmarkReport(
        fixture_fingerprint=a014_fixture_fingerprint(cases),
        case_ids=tuple(case.routing_case_id for case in cases),
        runtime_input_fingerprints=tuple(
            (case.routing_case_id, runtime_input_fingerprint(case)) for case in cases
        ),
        evaluator_metadata_fingerprints=tuple(
            (case.routing_case_id, evaluator_metadata_fingerprint(case)) for case in cases
        ),
        prompt_fingerprint=router_prompt_fingerprint(),
        case_results=case_results,
        policy_metrics=policy_metrics,
        case_count=len(cases),
        leakage_failure_count=_runtime_leakage_failure_count(),
        identity_failure_count=sum(item.identity_failure_count for item in policy_metrics),
        provenance_failure_count=sum(item.provenance_failure_count for item in policy_metrics),
        budget_violation_count=sum(item.budget_violation_count for item in policy_metrics),
        duplicate_visit_failure_count=sum(item.duplicate_visit_failure_count for item in policy_metrics),
    )


def _metrics_by_policy(report: StructuralRoutingBenchmarkReport) -> dict[RoutingPolicy, RoutingPolicyMetrics]:
    return {item.policy: item for item in report.policy_metrics}


def _policy_integrity_clean(item: RoutingPolicyMetrics) -> bool:
    return (
        item.identity_failure_count == 0
        and item.provenance_failure_count == 0
        and item.budget_violation_count == 0
        and item.duplicate_visit_failure_count == 0
    )


def classify_a014_architecture(
    report: StructuralRoutingBenchmarkReport,
) -> StructuralRoutingDecision:
    if not report.physical_evidence_bound:
        return StructuralRoutingDecision.MIXED
    metrics = _metrics_by_policy(report)
    rule = metrics[RoutingPolicy.RULE_ONLY]
    model = metrics[RoutingPolicy.MODEL_ONLY]
    hybrid = metrics[RoutingPolicy.HYBRID_RULE_THEN_MODEL]
    if report.leakage_failure_count:
        return StructuralRoutingDecision.STRUCTURAL_ROUTING_NOT_SUPPORTED

    best_downstream = max(item.downstream_success_count for item in metrics.values())
    best_relation = max(item.relation_positive_success_count for item in metrics.values())
    best_direct = max(item.direct_control_success_count for item in metrics.values())
    best_exact = max(item.exact_relation_set_match_count for item in metrics.values())
    min_missed = min(item.missed_activation_count for item in metrics.values())
    min_false = min(item.false_activation_count for item in metrics.values())

    if (
        rule.downstream_success_count == best_downstream
        and rule.relation_positive_success_count == best_relation
        and rule.relation_positive_success_count > 0
        and rule.direct_control_success_count == best_direct
        and rule.exact_relation_set_match_count == best_exact
        and rule.missed_activation_count == min_missed
        and rule.false_activation_count == min_false
        and rule.model_invocation_count == 0
        and _policy_integrity_clean(rule)
    ):
        return StructuralRoutingDecision.RULE_ROUTING_SUFFICIENT

    if (
        hybrid.downstream_success_count == best_downstream
        and hybrid.relation_positive_success_count == best_relation
        and hybrid.relation_positive_success_count > 0
        and hybrid.direct_control_success_count >= best_direct
        and hybrid.missed_activation_count <= model.missed_activation_count
        and hybrid.false_activation_count <= model.false_activation_count
        and hybrid.exact_relation_set_match_count >= model.exact_relation_set_match_count
        and hybrid.model_invocation_count < model.model_invocation_count
        and _policy_integrity_clean(hybrid)
    ):
        return StructuralRoutingDecision.HYBRID_STRUCTURAL_ROUTING_JUSTIFIED

    if (
        model.downstream_success_count > hybrid.downstream_success_count
        and model.downstream_success_count > rule.downstream_success_count
        and model.relation_positive_success_count > 0
        and _policy_integrity_clean(model)
    ):
        return StructuralRoutingDecision.MODEL_ROUTING_PREFERRED

    if (
        best_relation == 0
        or all(not _policy_integrity_clean(item) for item in metrics.values())
    ):
        return StructuralRoutingDecision.STRUCTURAL_ROUTING_NOT_SUPPORTED
    return StructuralRoutingDecision.MIXED


def _need_payload(need: StructuralNeed) -> dict[str, object]:
    return {
        "required_relations": [relation.value for relation in need.required_relations],
        "requires_path_provenance": need.requires_path_provenance,
    }


def _metrics_payload(item: RoutingPolicyMetrics) -> dict[str, object]:
    payload = {field.name: getattr(item, field.name) for field in fields(item)}
    payload["policy"] = item.policy.value
    return payload


def benchmark_report_payload(report: StructuralRoutingBenchmarkReport) -> dict[str, object]:
    return {
        "fixture_fingerprint": report.fixture_fingerprint,
        "case_ids": list(report.case_ids),
        "runtime_input_fingerprints": [list(item) for item in report.runtime_input_fingerprints],
        "evaluator_metadata_fingerprints": [list(item) for item in report.evaluator_metadata_fingerprints],
        "prompt_fingerprint": report.prompt_fingerprint,
        "case_count": report.case_count,
        "policy_metrics": [_metrics_payload(item) for item in report.policy_metrics],
        "leakage_failure_count": report.leakage_failure_count,
        "identity_failure_count": report.identity_failure_count,
        "provenance_failure_count": report.provenance_failure_count,
        "budget_violation_count": report.budget_violation_count,
        "duplicate_visit_failure_count": report.duplicate_visit_failure_count,
        "deterministic_repeat_match": report.deterministic_repeat_match,
        "physical_evidence_bound": report.physical_evidence_bound,
        "cases": [
            {
                "routing_case_id": item.routing_case_id,
                "base_a013_case_id": item.base_a013_case_id,
                "language": item.language,
                "policy": item.policy.value,
                "routing_status": item.routing_result.status.value,
                "routing_source": item.routing_result.source.value,
                "inferred_structural_need": _need_payload(item.routing_result.structural_need),
                "expected_structural_need": _need_payload(item.expected_structural_need),
                "rule_evidence_ids": list(item.routing_result.rule_evidence_ids),
                "model_invoked": item.routing_result.model_invoked,
                "model_name": item.routing_result.model_name,
                "model_digest": item.routing_result.model_digest,
                "raw_model_output": item.routing_result.raw_model_output,
                "prompt_tokens": item.routing_result.prompt_tokens,
                "generated_tokens": item.routing_result.generated_tokens,
                "total_duration_ns": item.routing_result.total_duration_ns,
                "primary_relation_positive": item.primary_relation_positive,
                "task_success": item.task_success,
                "expected_found": item.expected_found,
                "found_expected_ids": list(item.found_expected_ids),
                "initially_retrieved_ids": list(item.initially_retrieved_ids),
                "final_selected_ids": list(item.final_selected_ids),
                "vector_scored_count": item.vector_scored_count,
                "relation_invoked": item.relation_invoked,
                "relation_scanned_edge_count": item.relation_scanned_edge_count,
                "relation_visited_node_count": item.relation_visited_node_count,
                "relation_path_edge_ids": [list(path) for path in item.relation_path_edge_ids],
                "relation_path_memory_ids": [list(path) for path in item.relation_path_memory_ids],
                "relation_path_evidence_ids": [list(path) for path in item.relation_path_evidence_ids],
                "identity_preserved": item.identity_preserved,
                "provenance_complete": item.provenance_complete,
                "budget_respected": item.budget_respected,
                "duplicate_visit_free": item.duplicate_visit_free,
            }
            for item in report.case_results
        ],
    }
