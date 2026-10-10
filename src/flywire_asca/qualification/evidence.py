"""Validate child evidence without importing any legacy script/cognitive package."""
from __future__ import annotations
from dataclasses import dataclass
import hashlib
import json
import re
from typing import Callable

from .manifest import json_value, strict_json_object
from .records import (
    EvidenceRole, FrozenCheck, Freshness, GateStatus, JsonObject, JsonValue,
    QualificationError, Reason, ResearchObservation, ResearchOutcome, freeze_json,
)

LegacyValidator = Callable[[dict[str, JsonValue]], tuple[str, ...]]


@dataclass(frozen=True)
class AdapterResult:
    status: GateStatus
    payload: JsonObject | None
    errors: tuple[Reason, ...]
    frozen_checks: tuple[FrozenCheck, ...]
    observation: ResearchObservation | None
    semantic_sha256: str | None

    def __post_init__(self):
        if self.payload is not None:
            object.__setattr__(self, "payload", freeze_json(self.payload))
        for name in ("errors", "frozen_checks"):
            object.__setattr__(self, name, tuple(getattr(self, name)))


def semantic_payload_sha256(payload, milestone, profile):
    rule = profile.values["portable_payloads"].get(milestone)
    if rule is None:
        raise QualificationError("EVIDENCE_INVALID", "Unknown portable milestone")
    keys = set(payload)
    required = set(rule["required_top_level_keys"])
    if not required <= keys or keys - required - set(rule["allowed_optional_keys"]):
        raise QualificationError("EVIDENCE_INVALID", "Unknown or missing portable control fields")
    semantic = {key: json_value(value) for key, value in payload.items()
                if key not in rule["excluded_semantic_keys"]}
    try:
        raw = json.dumps(semantic, ensure_ascii=False, sort_keys=True,
                         separators=(",", ":"), allow_nan=False).encode("utf-8")
    except (ValueError, TypeError) as exc:
        raise QualificationError("EVIDENCE_INVALID", "Invalid semantic JSON") from exc
    return hashlib.sha256(raw).hexdigest()


def _physical_detail_errors(gate_id, payload):
    """Check the acceptance evidence emitted by the unchanged physical CLIs."""
    errors = []
    def reject(message):
        errors.append(message)
    def uint(value):
        return type(value) is int and value >= 0
    def ids(value):
        return (type(value) is list and all(type(item) is str and item for item in value)
                and len(set(value)) == len(value))
    def same(left, right):
        return json.dumps(left, sort_keys=True, allow_nan=False) == json.dumps(right, sort_keys=True, allow_nan=False)

    if gate_id == "H02_A005":
        report = payload.get("benchmark")
        if type(report) is not dict:
            return ("A005 benchmark detail is missing or malformed",)
        if (report.get("scope") != "controlled_fixture_only" or
            any(type(report.get(key)) is not float or report[key] != 1.0 for key in (
                "recall_at_1", "recall_at_k", "mean_reciprocal_rank",
                "no_hit_correctness", "metadata_filter_correctness")) or
            any(type(report.get(key)) is not int or report[key] != 0 for key in (
                "false_retrieval_count", "ambiguity_failure_count"))):
            reject("A005 benchmark contradicts existing retrieval acceptance")
        cases = report.get("case_results")
        if (type(cases) is not list or not cases or
            type(report.get("case_count")) is not int or report["case_count"] != len(cases) or
            any(type(case) is not dict for case in cases)):
            return tuple(errors + ["A005 benchmark case evidence is missing or inconsistent"])
        case_ids = [case.get("case_id") for case in cases]
        calibration_ids = payload.get("calibration_case_ids")
        if (not ids(case_ids) or not same(case_ids,payload.get("qualification_case_ids")) or
            not ids(calibration_ids) or not calibration_ids or
            set(case_ids) & set(calibration_ids)):
            reject("A005 benchmark case identities contradict qualification provenance")
        for case in cases:
            relevant, returned = case.get("relevant_memory_ids"), case.get("returned_memory_ids")
            if (not ids(relevant) or not ids(returned) or
                type(case.get("false_retrieval_count")) is not int or case["false_retrieval_count"] != 0 or
                case.get("ambiguity_preserved") is not True or
                any(case.get(key) is not None and
                    (type(case[key]) is not float or case[key] != 1.0)
                    for key in ("recall_at_1", "recall_at_k", "reciprocal_rank")) or
                any(case.get(key) is not None and case[key] is not True
                    for key in ("no_hit_correct", "metadata_filter_correct")) or
                not uint(case.get("returned_count")) or case["returned_count"] != len(returned)):
                reject("A005 per-case evidence contradicts successful retrieval summary")
                continue
            if ((relevant and (case.get("recall_at_k") != 1.0 or
                               case.get("reciprocal_rank") != 1.0 or not set(relevant) <= set(returned))) or
                (not relevant and (case.get("no_hit_correct") is not True or returned))):
                reject("A005 per-case retrieval evidence contradicts existing acceptance")
        model = payload.get("model", {})
        for field, expected in (
            ("frozen_threshold",payload.get("physical_threshold")),
            ("threshold_origin",payload.get("threshold_origin")),
            ("embedding_model_name",model.get("name")),
            ("embedding_model_digest",model.get("digest")),
        ):
            if not same(report.get(field),expected):
                reject("A005 benchmark identity differs from observed frozen identity: "+field)
    elif gate_id == "H05_A009":
        detail = payload.get("physical_integration")
        if type(detail) is not dict:
            return ("A009 physical integration detail is missing or malformed",)
        if (any(detail.get(key) is not True for key in (
                "success_case_completed", "fallback_case_exhausted",
                "terminal_model_invoked", "terminal_model_response_nonempty")) or
            any(type(detail.get(key)) is not int or detail[key] != expected
                for key,expected in (("success_case_attempt_count",1),
                    ("fallback_case_attempt_count",3),("terminal_model_request_count",1))) or
            not ids(detail.get("success_case_final_working_set_ids")) or
            "mem-physical" not in detail.get("success_case_final_working_set_ids", [])):
            reject("A009 physical integration contradicts existing secondary acceptance")
        metadata = payload.get("physical_metadata", {})
        if (metadata.get("terminal_model_invoked") is not True or
            type(metadata.get("terminal_model_request_count")) is not int or
            metadata["terminal_model_request_count"] != 1):
            reject("A009 terminal invocation metadata contradicts integration detail")
    elif gate_id == "H06_A010":
        comparison = payload.get("physical_comparison")
        if type(comparison) is not dict or any(type(comparison.get(key)) is not dict for key in ("asca","dense")):
            return ("A010 physical comparison detail is missing or malformed",)
        for variant in ("asca","dense"):
            detail = comparison[variant]
            if (detail.get("procedure_success") is not True or
                not ids(detail.get("final_selected_memory_ids")) or
                "mem-000-target" not in detail.get("final_selected_memory_ids", []) or
                type(detail.get("query_count")) is not int or
                (detail["query_count"] != 3 if variant == "dense" else detail["query_count"] < 1)):
                reject("A010 "+variant+" comparison contradicts existing secondary acceptance")
    return tuple(errors)


def normalize_child(gate_id, evidence, output_bytes, profile, validator=None):
    errors, checks = [], []
    payload = observation = semantic = None
    ref = f"raw/{gate_id}/output.json" if evidence.command.output_path is not None and output_bytes is not None else f"raw/{gate_id}/stdout.log"

    def error(code, message):
        errors.append(Reason(code, gate_id, message, (ref,)))

    def check(identity, expected, observed):
        # Exact JSON types matter, e.g. bool is never an integer dimension.
        matches = (observed is not None and
                   json.dumps(json_value(expected), sort_keys=True, allow_nan=False) ==
                   json.dumps(json_value(observed), sort_keys=True, allow_nan=False))
        checks.append(FrozenCheck(identity, expected, observed,
                                 GateStatus.PASS if matches else GateStatus.FAIL, (ref,)))
        if not matches:
            error("IDENTITY_DRIFT", identity + " differs from frozen identity")

    if evidence.command.gate_id != gate_id:
        error("EVIDENCE_INVALID", "Command/evidence gate identity differs")
    if evidence.execution_error is not None or evidence.exit_code != 0:
        error("QUALIFIER_FAILED", evidence.execution_error or f"Child exited {evidence.exit_code}")
    if gate_id in ("P01_TESTS", "P02_ARCHITECTURE", "P03_REPOSITORY"):
        try:
            stdout = evidence.stdout.decode("utf-8")
            if gate_id == "P01_TESTS":
                valid = re.search(r"\b[1-9]\d* passed(?:[^\r\n]*) in \d+(?:\.\d+)?s\b", stdout) is not None
                valid = valid and not re.search(r"\b\d+ (?:failed|errors?)\b", stdout)
            else:
                marker = "architecture_contract_audit" if gate_id == "P02_ARCHITECTURE" else "repository_qualification"
                valid = marker + "=PASS" in stdout.splitlines() and marker + "=FAIL" not in stdout
            if not valid:
                error("EVIDENCE_INVALID", "Child completion/acceptance marker missing or contradictory")
        except UnicodeError:
            error("EVIDENCE_INVALID", "Child log is not UTF-8")
        return AdapterResult(GateStatus.FAIL if errors else GateStatus.PASS, None,
                             tuple(errors), (), None, None)
    json_gates = {"P04_A003", "P05_A008", "P06_A009", "P07_A010",
                  "H01_A004", "H02_A005", "H03_A006", "H04_A007", "H05_A009", "H06_A010"}
    if gate_id not in json_gates:
        error("EVIDENCE_INVALID", "Unknown child gate")
        return AdapterResult(GateStatus.FAIL, None, tuple(errors), (), None, None)
    try:
        payload = strict_json_object(evidence.stdout)
        if evidence.command.output_path is not None:
            if output_bytes is None:
                raise QualificationError("EVIDENCE_INVALID", "Required child JSON output is missing")
            artifact_payload = strict_json_object(output_bytes)
            if json.dumps(artifact_payload, sort_keys=True, separators=(",", ":")) != json.dumps(payload, sort_keys=True, separators=(",", ":")):
                raise QualificationError("EVIDENCE_INVALID", "Stdout and output JSON disagree")
    except QualificationError as exc:
        error("EVIDENCE_INVALID", str(exc))
        return AdapterResult(GateStatus.FAIL, payload, tuple(errors), (), None, None)

    values = profile.values
    successful_exit = evidence.exit_code == 0 and evidence.execution_error is None
    def required_flag(name):
        if payload.get(name) is not True:
            error("QUALIFIER_FAILED" if name in payload or not successful_exit else "EVIDENCE_INVALID", name + " was not true")
    def observed(identity, expected, value):
        # Diagnostic nonzero variants may lack descriptors; never accept them.
        # A supplied wrong identity is a hard failure even when the child also failed.
        if value is not None or successful_exit:
            check(identity, expected, value)

    try:
        if gate_id == "P04_A003":
            if "--qualify" not in evidence.command.argv or "--output" in evidence.command.argv:
                error("EVIDENCE_INVALID", "A003 command must use its existing --qualify stdout contract")
            count = payload.get("case_count")
            if (type(count) is not int or count <= 0 or type(payload.get("case_results")) is not list or
                len(payload["case_results"]) != count or
                payload.get("correct_classification_count") != count or
                payload.get("classification_accuracy") != 1.0 or
                any(type(payload.get(key)) is not int or payload[key] != 0 for key in (
                    "ambiguity_failure_count", "false_familiarity_count",
                    "false_unfamiliar_count", "semantic_mismatch_count")) or
                payload.get("scope") != "controlled_fixture_only"):
                error("EVIDENCE_INVALID", "A003 report contradicts existing qualification acceptance")
            cases = payload.get("case_results", [])
            if any(type(case) is not dict or any(case.get(key) is not True for key in (
                "classification_correct", "regions_correct", "ambiguity_preserved", "semantic_equivalent"))
                or case.get("actual_state") != case.get("expected_state")
                or case.get("actual_region_ids") != case.get("expected_region_ids") for case in cases):
                error("EVIDENCE_INVALID", "A003 per-case evidence contradicts success summary")
        else:
            if type(payload.get("errors")) is not list or payload["errors"]:
                error("QUALIFIER_FAILED", "Child reports validation errors or missing error list")
            if gate_id in ("P05_A008", "P06_A009", "P07_A010"):
                milestone = {"P05_A008":"A008", "P06_A009":"A009", "P07_A010":"A010"}[gate_id]
                required_flag("experiment_valid")
                rule = values["portable_payloads"][milestone]
                for key in ("fixture_version", "qualification_scope"):
                    check(milestone+"."+key, rule[key], payload.get(key))
                check(milestone+".fingerprint", values["fixture_fingerprints"][milestone], payload.get("fixture_fingerprint"))
                check(milestone+".outcome", values["research_outcomes"][milestone], payload.get("primary_hypothesis_outcome"))
                semantic = semantic_payload_sha256(payload, milestone, profile)
                if semantic != rule["semantic_sha256"]:
                    error("REPLAY_DRIFT", "Portable semantic payload differs from frozen digest")
                if validator is None:
                    error("EVIDENCE_INVALID", "Existing portable validator is required")
                observation = ResearchObservation(ResearchOutcome(payload["primary_hypothesis_outcome"]),
                    EvidenceRole.PORTABLE_PRIMARY, Freshness.FRESH_PORTABLE, ref)
            elif gate_id in ("H01_A004", "H02_A005", "H03_A006", "H04_A007"):
                milestone = {"H01_A004":"A004","H02_A005":"A005","H03_A006":"A006","H04_A007":"A007"}[gate_id]
                model = payload.get("model", {})
                identity = values["terminal"] if milestone == "A004" else values["embedding"]
                observed(milestone+".model", identity["model"], model.get("name"))
                observed(milestone+".digest", identity["digest"], model.get("digest"))
                if milestone == "A004":
                    required_flag("qualified")
                    observed("A004.scope", "local_physical_qwen_a004", payload.get("qualification_scope"))
                    generation = payload.get("generation_profile", {})
                    for key in ("thinking", "tools", "vision"):
                        observed("A004."+key, False, generation.get(key))
                    baseline = payload.get("baseline", {})
                    if successful_exit:
                        cases = baseline.get("case_results")
                        if (type(baseline.get("case_count")) is not int or baseline["case_count"] != 6 or
                            type(baseline.get("passed_case_count")) is not int or baseline["passed_case_count"] != 6 or
                            type(baseline.get("pass_rate")) is not float or baseline["pass_rate"] != 1.0 or
                            type(cases) is not list or len(cases) != 6 or
                            any(type(c) is not dict or c.get("passed") is not True or
                                type(c.get("case_id")) is not str or not c["case_id"] for c in cases) or
                            len({c["case_id"] for c in cases if type(c) is dict and type(c.get("case_id")) is str}) != 6):
                            error("EVIDENCE_INVALID", "A004 baseline contradicts existing six-case/all-pass acceptance")
                        observed("A004.generation.profile_name", "qwen3.5-4b-thinking-off-v1", generation.get("profile_name"))
                else:
                    required_flag("experiment_valid")
                    observed(milestone+".dimension", 1024, model.get("embedding_dimension"))
                    if milestone == "A005":
                        required_flag("retrieval_qualified")
                        observed("A005.mode", "qualification", payload.get("mode"))
                        observed("A005.threshold", values["a005_threshold"], payload.get("physical_threshold"))
                        observed("A005.threshold_origin", "physical_frozen_threshold_v1", payload.get("threshold_origin"))
                        health = payload.get("vector_health", {})
                        observed("A005.vector_health.dimension", 1024, health.get("dimension"))
                        for key in ("zero_vector_count", "nonfinite_vector_count"):
                            observed("A005.vector_health."+key, 0, health.get(key))
                    else:
                        frozen = payload.get("frozen_profile", {})
                        experiment = payload
                        observed(milestone+".frozen.model", identity["model"], frozen.get("model"))
                        observed(milestone+".frozen.digest", identity["digest"], frozen.get("digest"))
                        observed(milestone+".frozen.dimension", 1024, frozen.get("embedding_dimension"))
                        threshold_key = "a005_threshold" if milestone == "A006" else "threshold"
                        observed(milestone+".threshold", values["a005_threshold"], frozen.get(threshold_key))
                        observed(milestone+".fingerprint", values["fixture_fingerprints"][milestone], experiment.get("fixture_fingerprint"))
                        observed(milestone+".outcome", values["research_outcomes"][milestone], experiment.get("hypothesis_outcome"))
                        if validator is None:
                            error("EVIDENCE_INVALID", "Existing physical experiment validator is required")
                        if experiment.get("hypothesis_outcome") in ("SUPPORTED", "NOT_SUPPORTED"):
                            observation = ResearchObservation(ResearchOutcome(experiment["hypothesis_outcome"]),
                                EvidenceRole.PHYSICAL_PRIMARY, Freshness.FRESH_PHYSICAL, ref)
            else:
                milestone = "A009" if gate_id == "H05_A009" else "A010"
                required_flag("physical_prerequisites_valid")
                required_flag("physical_integration_valid")
                observed(milestone+".physical.fixture", milestone.lower()+"-physical-v1", payload.get("fixture_version"))
                observed(milestone+".portable_primary", values["research_outcomes"][milestone], payload.get("portable_primary_outcome"))
                metadata = payload.get("physical_metadata", {})
                for key, expected in (("embedding_model", values["embedding"]["model"]),
                    ("embedding_digest", values["embedding"]["digest"]), ("embedding_dimension",1024),
                    ("minimum_similarity",values["a005_threshold"])):
                    observed(milestone+"."+key, expected, metadata.get(key))
                if milestone == "A009":
                    for key, expected in (("terminal_model",values["terminal"]["model"]),
                        ("terminal_model_digest",values["terminal"]["digest"]),
                        ("primary_selector","SINGLE_BEST"), ("primary_procedure_mode","CHUNKED")):
                        observed("A009."+key, expected, metadata.get(key))
                if payload.get("portable_primary_outcome") in ("SUPPORTED", "NOT_SUPPORTED"):
                    observation = ResearchObservation(ResearchOutcome(payload["portable_primary_outcome"]),
                        EvidenceRole.PHYSICAL_SECONDARY, Freshness.FRESH_PHYSICAL, ref)
            if successful_exit and gate_id in ("H02_A005", "H05_A009", "H06_A010"):
                for message in _physical_detail_errors(gate_id,payload):
                    error("EVIDENCE_INVALID", message)
            diagnostic_without_experiment = (gate_id in ("H03_A006", "H04_A007") and
                not successful_exit and "fixture_version" not in payload)
            if validator is not None and not diagnostic_without_experiment:
                for message in validator(payload):
                    error("EVIDENCE_INVALID", "Existing validator: " + message)
    except (QualificationError, ValueError, TypeError, KeyError, AttributeError) as exc:
        error("EVIDENCE_INVALID", f"Malformed child acceptance payload: {exc}")
    return AdapterResult(GateStatus.FAIL if errors else GateStatus.PASS, payload,
        tuple(errors), tuple(checks), observation if not errors else None, semantic)
