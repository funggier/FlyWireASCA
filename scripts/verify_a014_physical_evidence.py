from __future__ import annotations

import argparse
from dataclasses import fields
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
SCRIPTS = ROOT / "scripts"
for path in (SRC, SCRIPTS):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from qualify_structural_routing_a014_physical import (
    EXPECTED_DIGEST,
    MODEL_NAME,
    a014_source_manifest,
    a014_source_manifest_fingerprint,
)
from flywire_asca.structural_routing import RoutingPolicy
from flywire_asca.structural_routing.benchmark import (
    RoutingPolicyMetrics,
    StructuralRoutingBenchmarkReport,
    classify_a014_architecture,
)
from flywire_asca.structural_routing.benchmark_fixture import (
    EXPECTED_A014_CASE_IDS,
    EXPECTED_A014_EVALUATOR_FINGERPRINTS,
    EXPECTED_A014_FIXTURE_FINGERPRINT,
    EXPECTED_A014_RUNTIME_INPUT_FINGERPRINTS,
)
from flywire_asca.structural_routing.model_router import router_prompt_fingerprint


def _usage_total(cases: list[dict[str, object]], field: str) -> int | None:
    invoked = [case for case in cases if case.get("model_invoked") is True]
    if not invoked:
        return 0
    values = [case.get(field) for case in invoked]
    if any(value is None for value in values):
        return None
    if any(type(value) is not int or value < 0 for value in values):
        return None
    return sum(values)


def _active(need: object) -> bool:
    if not isinstance(need, dict):
        return False
    relations = need.get("required_relations")
    provenance = need.get("requires_path_provenance")
    return bool(relations) or provenance is True


def _recompute_policy_metrics(
    policy: RoutingPolicy, cases: list[dict[str, object]]
) -> RoutingPolicyMetrics:
    selected = [case for case in cases if case.get("policy") == policy.value]
    expected_active = [_active(case.get("expected_structural_need")) for case in selected]
    inferred_active = [_active(case.get("inferred_structural_need")) for case in selected]

    def relations(case: dict[str, object], key: str) -> set[str]:
        need = case.get(key)
        if not isinstance(need, dict):
            return set()
        values = need.get("required_relations")
        if not isinstance(values, list):
            return set()
        return {value for value in values if isinstance(value, str)}

    exact = [
        relations(case, "inferred_structural_need")
        == relations(case, "expected_structural_need")
        for case in selected
    ]
    over = [
        bool(
            relations(case, "inferred_structural_need")
            - relations(case, "expected_structural_need")
        )
        for case in selected
    ]
    under = [
        bool(
            relations(case, "expected_structural_need")
            - relations(case, "inferred_structural_need")
        )
        for case in selected
    ]
    relation_positive = [
        case for case in selected if case.get("primary_relation_positive") is True
    ]
    direct = [
        case for case, active in zip(selected, expected_active) if not active
    ]
    structural_controls = [
        case
        for case, active in zip(selected, expected_active)
        if active and case.get("primary_relation_positive") is not True
    ]

    return RoutingPolicyMetrics(
        policy=policy,
        valid_case_count=len(selected),
        structural_true_positive_count=sum(
            expected and actual
            for expected, actual in zip(expected_active, inferred_active)
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
        exact_relation_set_match_count=sum(exact),
        relation_set_over_selection_count=sum(over),
        relation_set_under_selection_count=sum(under),
        invalid_model_output_count=sum(
            case.get("routing_status") == "INVALID_MODEL_OUTPUT" for case in selected
        ),
        model_error_count=sum(
            case.get("routing_status") == "MODEL_ERROR" for case in selected
        ),
        abstention_count=sum(
            case.get("routing_status") == "ABSTAINED" for case in selected
        ),
        downstream_success_count=sum(case.get("task_success") is True for case in selected),
        relation_positive_success_count=sum(
            case.get("task_success") is True for case in relation_positive
        ),
        direct_control_success_count=sum(
            case.get("task_success") is True for case in direct
        ),
        structural_control_success_count=sum(
            case.get("task_success") is True for case in structural_controls
        ),
        oracle_regression_count=sum(case.get("task_success") is not True for case in selected),
        model_invocation_count=sum(case.get("model_invoked") is True for case in selected),
        relation_invocation_count=sum(case.get("relation_invoked") is True for case in selected),
        relation_scanned_edge_count=sum(
            int(case.get("relation_scanned_edge_count", 0)) for case in selected
        ),
        relation_visited_node_count=sum(
            int(case.get("relation_visited_node_count", 0)) for case in selected
        ),
        prompt_tokens_total=_usage_total(selected, "prompt_tokens"),
        generated_tokens_total=_usage_total(selected, "generated_tokens"),
        identity_failure_count=sum(case.get("identity_preserved") is not True for case in selected),
        provenance_failure_count=sum(case.get("provenance_complete") is not True for case in selected),
        budget_violation_count=sum(case.get("budget_respected") is not True for case in selected),
        duplicate_visit_failure_count=sum(case.get("duplicate_visit_free") is not True for case in selected),
    )


def _metrics_payload(item: RoutingPolicyMetrics) -> dict[str, object]:
    payload = {field.name: getattr(item, field.name) for field in fields(item)}
    payload["policy"] = item.policy.value
    return payload


def _decision_from_payload(
    benchmark: dict[str, object],
    metrics: tuple[RoutingPolicyMetrics, ...],
):
    report = StructuralRoutingBenchmarkReport(
        fixture_fingerprint=str(benchmark.get("fixture_fingerprint", "")),
        case_ids=tuple(benchmark.get("case_ids", [])),
        runtime_input_fingerprints=tuple(
            tuple(item) for item in benchmark.get("runtime_input_fingerprints", [])
        ),
        evaluator_metadata_fingerprints=tuple(
            tuple(item) for item in benchmark.get("evaluator_metadata_fingerprints", [])
        ),
        prompt_fingerprint=str(benchmark.get("prompt_fingerprint", "")),
        case_results=(),
        policy_metrics=metrics,
        case_count=int(benchmark.get("case_count", 0)),
        leakage_failure_count=int(benchmark.get("leakage_failure_count", 0)),
        identity_failure_count=int(benchmark.get("identity_failure_count", 0)),
        provenance_failure_count=int(benchmark.get("provenance_failure_count", 0)),
        budget_violation_count=int(benchmark.get("budget_violation_count", 0)),
        duplicate_visit_failure_count=int(benchmark.get("duplicate_visit_failure_count", 0)),
        deterministic_repeat_match=bool(benchmark.get("deterministic_repeat_match", False)),
        physical_evidence_bound=benchmark.get("physical_evidence_bound") is True,
    )
    return classify_a014_architecture(report)


def verify_payload(payload: dict[str, object], *, root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    if not isinstance(payload, dict):
        return ["physical evidence must be a JSON object"]
    if payload.get("experiment_valid") is not True:
        errors.append("experiment_valid must be true")
    if payload.get("physical_evidence") is not True:
        errors.append("physical_evidence must be true")
    if payload.get("evidence_role") != "physical_model_capability":
        errors.append("physical evidence role mismatch")

    source = payload.get("source")
    if not isinstance(source, dict):
        errors.append("source metadata missing")
        source = {}
    source_sha = source.get("git_sha")
    if not isinstance(source_sha, str) or not source_sha:
        errors.append("source git SHA missing")
    else:
        try:
            expected_manifest = a014_source_manifest(root=root, ref=source_sha)
            expected_fp = a014_source_manifest_fingerprint(root=root, ref=source_sha)
            current_fp = a014_source_manifest_fingerprint(root=root, ref="HEAD")
        except Exception as exc:
            errors.append(f"source manifest unavailable: {exc}")
        else:
            recorded_manifest = source.get("manifest")
            if recorded_manifest != [list(item) for item in expected_manifest]:
                errors.append("source manifest mismatch")
            if source.get("manifest_fingerprint") != expected_fp:
                errors.append("source manifest fingerprint mismatch")
            if current_fp != expected_fp:
                errors.append("current A014 source differs from bound source")

    if payload.get("fixture_fingerprint") != EXPECTED_A014_FIXTURE_FINGERPRINT:
        errors.append("fixture fingerprint mismatch")
    if payload.get("prompt_fingerprint") != router_prompt_fingerprint():
        errors.append("prompt fingerprint mismatch")

    model = payload.get("model")
    if not isinstance(model, dict):
        errors.append("model metadata missing")
    else:
        if model.get("name") != MODEL_NAME:
            errors.append("model name mismatch")
        if model.get("digest") != EXPECTED_DIGEST:
            errors.append("model digest mismatch")

    benchmark = payload.get("benchmark")
    if not isinstance(benchmark, dict):
        errors.append("benchmark payload missing")
        return errors

    if benchmark.get("fixture_fingerprint") != EXPECTED_A014_FIXTURE_FINGERPRINT:
        errors.append("benchmark fixture fingerprint mismatch")
    if benchmark.get("prompt_fingerprint") != router_prompt_fingerprint():
        errors.append("benchmark prompt fingerprint mismatch")
    if benchmark.get("case_ids") != list(EXPECTED_A014_CASE_IDS):
        errors.append("case IDs mismatch")
    if benchmark.get("runtime_input_fingerprints") != [
        list(item) for item in EXPECTED_A014_RUNTIME_INPUT_FINGERPRINTS
    ]:
        errors.append("runtime input fingerprints mismatch")
    if benchmark.get("evaluator_metadata_fingerprints") != [
        list(item) for item in EXPECTED_A014_EVALUATOR_FINGERPRINTS
    ]:
        errors.append("evaluator fingerprints mismatch")
    if benchmark.get("physical_evidence_bound") is not True:
        errors.append("benchmark must be physically bound")

    cases = benchmark.get("cases")
    if not isinstance(cases, list):
        errors.append("benchmark cases missing")
        return errors
    if len(cases) != len(EXPECTED_A014_CASE_IDS) * len(RoutingPolicy):
        errors.append("unexpected physical case-result count")

    for case in cases:
        if not isinstance(case, dict):
            errors.append("case record must be an object")
            continue
        if case.get("model_invoked") is True:
            raw = case.get("raw_model_output")
            if not isinstance(raw, str) or not raw:
                errors.append("model invocation missing raw model output")

    recomputed = tuple(_recompute_policy_metrics(policy, cases) for policy in RoutingPolicy)
    if benchmark.get("policy_metrics") != [_metrics_payload(item) for item in recomputed]:
        errors.append("policy metrics do not recompute from raw cases")

    decision = _decision_from_payload(benchmark, recomputed)
    if payload.get("physical_architecture_decision") != decision.value:
        errors.append("physical architecture decision mismatch")

    return errors


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("evidence", type=Path)
    args = parser.parse_args(argv)
    if not args.evidence.exists():
        print(f"missing physical evidence: {args.evidence}", file=sys.stderr)
        return 1
    try:
        payload = json.loads(args.evidence.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"invalid physical evidence: {exc}", file=sys.stderr)
        return 1
    errors = verify_payload(payload, root=ROOT)
    if errors:
        print(json.dumps({"experiment_valid": False, "errors": errors}, sort_keys=True))
        return 1
    print(json.dumps({"experiment_valid": True, "errors": []}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
