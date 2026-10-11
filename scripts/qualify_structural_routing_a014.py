from __future__ import annotations

import argparse
from dataclasses import replace
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from flywire_asca.structural_routing.benchmark import (
    benchmark_report_payload,
    build_portable_scripted_adapters,
    run_a014_benchmark,
)
from flywire_asca.structural_routing.benchmark_fixture import (
    EXPECTED_A014_CASE_IDS,
    EXPECTED_A014_EVALUATOR_FINGERPRINTS,
    EXPECTED_A014_FIXTURE_FINGERPRINT,
    EXPECTED_A014_RUNTIME_INPUT_FINGERPRINTS,
    a014_fixture_fingerprint,
    build_a014_frozen_fixture,
    evaluator_metadata_fingerprint,
    runtime_input_fingerprint,
)
from flywire_asca.structural_routing.model_router import router_prompt_fingerprint
from flywire_asca.structural_routing.models import StructuralRoutingDecision


QUALIFICATION_SCOPE = "portable_structural_routing_a014"
FIXTURE_VERSION = "a014-bilingual-v1"
EVIDENCE_ROLE = "engineering_control_flow"
EXPECTED_FIXTURE_FINGERPRINT = EXPECTED_A014_FIXTURE_FINGERPRINT
EXPECTED_CASE_IDS = EXPECTED_A014_CASE_IDS
EXPECTED_RUNTIME_INPUT_FINGERPRINTS = EXPECTED_A014_RUNTIME_INPUT_FINGERPRINTS
EXPECTED_EVALUATOR_FINGERPRINTS = EXPECTED_A014_EVALUATOR_FINGERPRINTS
EXPECTED_PROMPT_FINGERPRINT = "b48568801f32579e36f2e633b740a3d6cc0a276ffa6dcaa05d035f790b5f6a8d"
EXPECTED_PORTABLE_EVIDENCE_SHA256 = "b0bc73a6dfe673f79e06d6ab03ddccaaeab7840110b51dec5d5259a59887b8dd"
VALID_DECISIONS = [item.value for item in StructuralRoutingDecision]
CLAIMS_BOUNDARY = (
    "A014 portable qualification validates deterministic routing contracts, "
    "frozen bilingual fixture integrity, rule/model/hybrid control flow, strict "
    "model-output parsing, downstream A013 composition, and evidence derivation. "
    "Its scripted adapter is engineering control-flow evidence only and does not "
    "qualify real-model structural-need inference or establish an A014 physical "
    "architecture decision."
)


def _canonical_sha(payload: object) -> str:
    raw = json.dumps(
        payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _portable_benchmark_payload() -> dict[str, object]:
    first = run_a014_benchmark(adapters_by_policy=build_portable_scripted_adapters())
    second = run_a014_benchmark(adapters_by_policy=build_portable_scripted_adapters())
    deterministic = (
        first.case_results == second.case_results
        and first.policy_metrics == second.policy_metrics
    )
    report = replace(first, deterministic_repeat_match=deterministic)
    return benchmark_report_payload(report)


def _build_payload() -> dict[str, object]:
    payload = _portable_benchmark_payload()
    payload.update(
        {
            "qualification_scope": QUALIFICATION_SCOPE,
            "fixture_version": FIXTURE_VERSION,
            "evidence_role": EVIDENCE_ROLE,
            "model_capability_qualified": False,
            "physical_evidence": False,
            "physical_architecture_decision": None,
            "decision_vocabulary": list(VALID_DECISIONS),
            "portable_evidence_sha256": _canonical_sha(
                {
                    key: value
                    for key, value in payload.items()
                }
            ),
            "claims_boundary": CLAIMS_BOUNDARY,
            "experiment_valid": True,
            "errors": [],
        }
    )
    return payload


def run_qualification() -> dict[str, object]:
    return _build_payload()


def validate_qualification_payload(payload: dict[str, object]) -> list[str]:
    errors: list[str] = []
    cases = build_a014_frozen_fixture()
    if a014_fixture_fingerprint(cases) != EXPECTED_FIXTURE_FINGERPRINT:
        errors.append("runtime frozen fixture fingerprint drift")
    if tuple(case.routing_case_id for case in cases) != EXPECTED_CASE_IDS:
        errors.append("runtime frozen case order/identity drift")
    runtime_fingerprints = tuple(
        (case.routing_case_id, runtime_input_fingerprint(case)) for case in cases
    )
    if runtime_fingerprints != EXPECTED_RUNTIME_INPUT_FINGERPRINTS:
        errors.append("runtime-input fingerprint drift")
    evaluator_fingerprints = tuple(
        (case.routing_case_id, evaluator_metadata_fingerprint(case)) for case in cases
    )
    if evaluator_fingerprints != EXPECTED_EVALUATOR_FINGERPRINTS:
        errors.append("evaluator-metadata fingerprint drift")
    if router_prompt_fingerprint() != EXPECTED_PROMPT_FINGERPRINT:
        errors.append("router prompt fingerprint drift")

    expected = _build_payload()
    if expected["portable_evidence_sha256"] != EXPECTED_PORTABLE_EVIDENCE_SHA256:
        errors.append("runtime portable evidence digest drift")

    protected_fields = (
        "qualification_scope",
        "fixture_version",
        "evidence_role",
        "model_capability_qualified",
        "physical_evidence",
        "physical_architecture_decision",
        "decision_vocabulary",
        "fixture_fingerprint",
        "case_ids",
        "runtime_input_fingerprints",
        "evaluator_metadata_fingerprints",
        "prompt_fingerprint",
        "case_count",
        "policy_metrics",
        "leakage_failure_count",
        "identity_failure_count",
        "provenance_failure_count",
        "budget_violation_count",
        "duplicate_visit_failure_count",
        "deterministic_repeat_match",
        "physical_evidence_bound",
        "cases",
        "portable_evidence_sha256",
        "claims_boundary",
    )
    for name in protected_fields:
        if payload.get(name) != expected.get(name):
            errors.append(f"{name} mismatch")

    if payload.get("evidence_role") != "engineering_control_flow":
        errors.append("portable evidence role must remain engineering_control_flow")
    if payload.get("model_capability_qualified") is not False:
        errors.append("portable evidence cannot qualify model capability")
    if payload.get("physical_evidence") is not False:
        errors.append("portable evidence cannot be labeled physical")
    if payload.get("physical_architecture_decision") is not None:
        errors.append("portable evidence cannot claim a physical architecture decision")
    if payload.get("decision_vocabulary") != VALID_DECISIONS:
        errors.append("decision vocabulary drift")
    if payload.get("deterministic_repeat_match") is not True:
        errors.append("portable deterministic repeat must match")
    for name in (
        "leakage_failure_count",
        "identity_failure_count",
        "provenance_failure_count",
        "budget_violation_count",
        "duplicate_visit_failure_count",
    ):
        if payload.get(name) != 0:
            errors.append(f"{name} must be zero")
    if payload.get("experiment_valid") is not True:
        errors.append("experiment_valid must be true")
    if payload.get("errors") != []:
        errors.append("errors must be empty")
    return errors


def _emit(payload: dict[str, object], output_path: Path | None) -> None:
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


def main(argv=None) -> int:
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
