import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from flywire_asca.relational_reasoning.benchmark import (
    EXPECTED_A012_CASE_IDS,
    EXPECTED_A012_FIXTURE_FINGERPRINT,
    EXPECTED_A012_SHARED_INPUT_FINGERPRINTS,
    a012_fixture_fingerprint,
    benchmark_report_payload,
    build_a012_deterministic_fixture,
    classify_a012_architecture,
    qualify_a012_report,
    run_a012_benchmark,
    shared_input_fingerprint,
)


QUALIFICATION_SCOPE = "deterministic_relational_reasoning_a012"
FIXTURE_VERSION = "a012-deterministic-v1"
EXPECTED_FIXTURE_FINGERPRINT = EXPECTED_A012_FIXTURE_FINGERPRINT
EXPECTED_CASE_IDS = EXPECTED_A012_CASE_IDS
EXPECTED_SHARED_INPUT_FINGERPRINTS = EXPECTED_A012_SHARED_INPUT_FINGERPRINTS
EXPECTED_ARCHITECTURE_DECISION = "EXPLICIT_RELATION_TRAVERSAL_JUSTIFIED"
VARIANTS = ["VECTOR_METADATA", "BOUNDED_RELATION"]
VALID_DECISIONS = {
    "EXPLICIT_RELATION_TRAVERSAL_JUSTIFIED",
    "VECTOR_METADATA_REMAINS_SUFFICIENT",
    "MIXED",
}


def _expected_payload():
    cases = build_a012_deterministic_fixture()
    report = run_a012_benchmark(cases)
    payload = benchmark_report_payload(report)
    payload["variants"] = list(VARIANTS)
    payload["bounds"] = {
        "max_hops": 3,
        "max_visited_nodes": 8,
        "max_scanned_edges": 32,
        "minimum_proposition_confidence": 0.5,
    }
    payload["experiment_valid"] = not qualify_a012_report(report)
    payload["errors"] = qualify_a012_report(report)
    return payload


def run_qualification():
    return _expected_payload()


def validate_qualification_payload(payload):
    errors = []
    expected = _expected_payload()

    runtime_cases = build_a012_deterministic_fixture()
    if a012_fixture_fingerprint(runtime_cases) != EXPECTED_FIXTURE_FINGERPRINT:
        errors.append("runtime frozen fixture fingerprint drift")
    if tuple(case.case_id for case in runtime_cases) != EXPECTED_CASE_IDS:
        errors.append("runtime frozen case order/identity drift")
    runtime_shared = tuple(
        (case.case_id, shared_input_fingerprint(case))
        for case in runtime_cases
    )
    if runtime_shared != EXPECTED_SHARED_INPUT_FINGERPRINTS:
        errors.append("runtime frozen shared-input fingerprint drift")

    runtime_report = run_a012_benchmark(runtime_cases)
    runtime_decision = classify_a012_architecture(runtime_report).value
    if runtime_decision != EXPECTED_ARCHITECTURE_DECISION:
        errors.append("runtime frozen architecture decision drift")
    runtime_errors = qualify_a012_report(runtime_report)
    if runtime_errors:
        errors.extend(f"runtime report invalid: {item}" for item in runtime_errors)

    for name in (
        "qualification_scope",
        "fixture_version",
        "fixture_fingerprint",
        "case_ids",
        "variants",
        "bounds",
        "claims_boundary",
    ):
        if payload.get(name) != expected.get(name):
            errors.append(f"{name} mismatch")

    aggregate = payload.get("aggregate_metrics")
    if not isinstance(aggregate, dict):
        errors.append("aggregate_metrics must be an object")
    elif aggregate != expected["aggregate_metrics"]:
        for name, value in expected["aggregate_metrics"].items():
            if aggregate.get(name) != value:
                errors.append(
                    f"{name} does not match raw frozen case evidence"
                )

    decision = payload.get("primary_architecture_decision")
    if decision not in VALID_DECISIONS:
        errors.append("primary_architecture_decision has invalid vocabulary")
    elif decision != EXPECTED_ARCHITECTURE_DECISION:
        errors.append("primary_architecture_decision drift from frozen decision")

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
    payload_errors = payload.get("errors")
    if payload_errors != []:
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
