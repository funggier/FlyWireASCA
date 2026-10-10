import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

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


QUALIFICATION_SCOPE = "deterministic_relational_activation_a013"
FIXTURE_VERSION = "a013-deterministic-v1"
EXPECTED_FIXTURE_FINGERPRINT = EXPECTED_A013_FIXTURE_FINGERPRINT
EXPECTED_CASE_IDS = EXPECTED_A013_CASE_IDS
EXPECTED_SHARED_INPUT_FINGERPRINTS = EXPECTED_A013_SHARED_INPUT_FINGERPRINTS
EXPECTED_ARCHITECTURE_DECISION = "SIGNAL_GATED_RELATION_JUSTIFIED"
POLICIES = ["VECTOR_ONLY", "ALWAYS_RELATION", "SIGNAL_GATED_RELATION"]
VALID_DECISIONS = {
    "SIGNAL_GATED_RELATION_JUSTIFIED",
    "ALWAYS_RELATION_PREFERRED",
    "RELATION_INTEGRATION_NOT_JUSTIFIED",
    "MIXED",
}
BOUNDS = {
    "max_hops": 3,
    "max_visited_nodes": 8,
    "max_scanned_edges": 32,
    "minimum_proposition_confidence": 0.5,
}
CLAIMS_BOUNDARY = (
    "A013 qualifies target-free bounded relational activation on the frozen "
    "mixed portable workload only. It does not qualify natural-language "
    "structural-need inference, a persistent graph database, general latency/"
    "FLOP/energy/RAM superiority, autonomous relation learning, production "
    "safety, AGI, consciousness, or biological equivalence."
)


def _report_errors(report):
    errors = []
    if report.case_count != 17:
        errors.append("case_count must be 17")
    if report.valid_case_count != 16 or report.invalid_case_count != 1:
        errors.append("valid/invalid case counts must be 16/1")
    if report.primary_relation_case_count != 6:
        errors.append("primary relation case count must be 6")
    if report.direct_control_count != 6:
        errors.append("direct control count must be 6")
    if report.signal_false_activation_count != 0:
        errors.append("signal false activation must be zero")
    if report.signal_missed_activation_count != 0:
        errors.append("signal missed activation must be zero")
    if report.identity_failure_count != 0:
        errors.append("identity failures must be zero")
    if report.provenance_failure_count != 0:
        errors.append("provenance failures must be zero")
    if report.budget_violation_count != 0:
        errors.append("budget violations must be zero")
    if report.duplicate_visit_failure_count != 0:
        errors.append("duplicate visit failures must be zero")
    if not report.deterministic_repeat_match:
        errors.append("deterministic repeat must match")
    invalid = [
        case for case in report.case_results if case.validation_error_observed
    ]
    if len(invalid) != 1 or invalid[0].case_id != "invalid-contract-control":
        errors.append("only invalid-contract-control may be invalid")
    for case in report.case_results:
        if case.validation_error_observed:
            continue
        if len(case.runs) != 3:
            errors.append(f"{case.case_id}: expected exactly three policy runs")
            continue
        policies = tuple(run.policy.value for run in case.runs)
        if policies != tuple(POLICIES):
            errors.append(f"{case.case_id}: policy order/vocabulary drift")
        for run in case.runs:
            if run.vector_query_count != 1:
                errors.append(f"{case.case_id}/{run.policy.value}: vector query count drift")
            if not run.identity_preserved:
                errors.append(f"{case.case_id}/{run.policy.value}: identity failure")
            if not run.provenance_complete:
                errors.append(f"{case.case_id}/{run.policy.value}: provenance failure")
            if not run.budget_respected:
                errors.append(f"{case.case_id}/{run.policy.value}: budget violation")
            if not run.duplicate_visit_free:
                errors.append(f"{case.case_id}/{run.policy.value}: duplicate visit")
    return errors


def _expected_payload():
    cases = build_a013_deterministic_fixture()
    report = run_a013_benchmark(cases)
    payload = benchmark_report_payload(report)
    payload.update(
        {
            "qualification_scope": QUALIFICATION_SCOPE,
            "fixture_version": FIXTURE_VERSION,
            "case_ids": list(EXPECTED_CASE_IDS),
            "policies": list(POLICIES),
            "bounds": dict(BOUNDS),
            "primary_architecture_decision": classify_a013_architecture(report).value,
            "claims_boundary": CLAIMS_BOUNDARY,
            "experiment_valid": not _report_errors(report),
            "errors": _report_errors(report),
        }
    )
    return payload


def run_qualification():
    return _expected_payload()


def validate_qualification_payload(payload):
    errors = []
    expected = _expected_payload()

    runtime_cases = build_a013_deterministic_fixture()
    if a013_fixture_fingerprint(runtime_cases) != EXPECTED_FIXTURE_FINGERPRINT:
        errors.append("runtime frozen fixture fingerprint drift")
    if tuple(case.case_id for case in runtime_cases) != EXPECTED_CASE_IDS:
        errors.append("runtime frozen case order/identity drift")
    runtime_shared = tuple(
        (case.case_id, shared_input_fingerprint(case))
        for case in runtime_cases
    )
    if runtime_shared != EXPECTED_SHARED_INPUT_FINGERPRINTS:
        errors.append("runtime frozen shared-input fingerprint drift")

    runtime_report = run_a013_benchmark(runtime_cases)
    runtime_decision = classify_a013_architecture(runtime_report).value
    if runtime_decision != EXPECTED_ARCHITECTURE_DECISION:
        errors.append("runtime frozen architecture decision drift")
    errors.extend(f"runtime report invalid: {item}" for item in _report_errors(runtime_report))

    for name in (
        "qualification_scope",
        "fixture_version",
        "fixture_fingerprint",
        "case_ids",
        "policies",
        "bounds",
        "claims_boundary",
    ):
        if payload.get(name) != expected.get(name):
            errors.append(f"{name} mismatch")

    decision = payload.get("primary_architecture_decision")
    if decision not in VALID_DECISIONS:
        errors.append("primary_architecture_decision has invalid vocabulary")
    elif decision != EXPECTED_ARCHITECTURE_DECISION:
        errors.append("primary_architecture_decision drift from frozen decision")

    scalar_names = (
        "case_count",
        "valid_case_count",
        "invalid_case_count",
        "primary_relation_case_count",
        "direct_control_count",
        "vector_success_count",
        "always_success_count",
        "signal_success_count",
        "vector_primary_relation_success_count",
        "always_primary_relation_success_count",
        "signal_primary_relation_success_count",
        "vector_direct_success_count",
        "signal_direct_success_count",
        "always_relation_only_recovery_count",
        "signal_relation_only_recovery_count",
        "always_regression_count",
        "signal_regression_count",
        "always_relation_invocation_count",
        "signal_relation_invocation_count",
        "always_relation_scanned_edge_count",
        "signal_relation_scanned_edge_count",
        "always_relation_visited_node_count",
        "signal_relation_visited_node_count",
        "signal_false_activation_count",
        "signal_missed_activation_count",
        "identity_failure_count",
        "provenance_failure_count",
        "budget_violation_count",
        "duplicate_visit_failure_count",
        "deterministic_repeat_match",
    )
    for name in scalar_names:
        if payload.get(name) != expected.get(name):
            errors.append(f"{name} does not match raw frozen case evidence")

    cases = payload.get("cases")
    if not isinstance(cases, list):
        errors.append("cases must be a list")
    else:
        observed_ids = [
            item.get("case_id")
            for item in cases
            if isinstance(item, dict)
        ]
        if observed_ids != list(EXPECTED_CASE_IDS):
            errors.append("case_ids/cases order mismatch")
        if cases != expected["cases"]:
            errors.append("cases raw evidence differs from frozen qualification")

    if payload.get("experiment_valid") is not True:
        errors.append("experiment_valid must be true for frozen qualification")
    if payload.get("errors") != []:
        errors.append("errors must be empty for frozen qualification")
    return errors


def _emit(payload, output_path):
    data = (
        json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
    ).encode("utf-8")
    stream = getattr(sys.stdout, "buffer", None)
    if stream is not None:
        stream.write(data)
        stream.flush()
    else:
        sys.stdout.write(data.decode("utf-8"))
    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(data)


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--note")
    args = parser.parse_args(argv)

    payload = run_qualification()
    if args.note is not None:
        payload["note"] = args.note
    errors = validate_qualification_payload(payload)
    if errors:
        payload["experiment_valid"] = False
        payload["errors"] = errors
        _emit(payload, args.output)
        return 1
    payload["experiment_valid"] = True
    payload["errors"] = []
    _emit(payload, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
