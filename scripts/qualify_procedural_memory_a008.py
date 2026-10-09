import argparse
import json
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from flywire_asca.procedural_memory import (
    ProcedureExecutionMode,
    build_a008_fixture,
    classify_a008_hypothesis,
    fixture_fingerprint,
    qualify_a008_report,
    run_a008_benchmark,
)

QUALIFICATION_SCOPE = "deterministic_procedural_memory_a008"
FIXTURE_VERSION = "a008-deterministic-v1"
EXPECTED_FIXTURE_FINGERPRINT = "f52fbd4ab018386ff3cbfb62a68cc44a4b40e54ec4fd9a3b2e885dd2c5663fc6"
MAX_CALL_DEPTH = 8


_INT_METRICS = (
    "case_count",
    "valid_case_count",
    "invalid_case_count",
    "success_case_count",
    "flat_success_count",
    "chunked_success_count",
    "blind_success_count",
    "primitive_sequence_equivalence_count",
    "flat_final_state_correct_count",
    "chunked_final_state_correct_count",
    "blind_final_state_correct_count",
    "flat_root_visible_dispatches",
    "chunked_root_visible_dispatches",
    "chunk_reuse_count",
    "checked_failure_case_count",
    "flat_exact_failure_localization_count",
    "chunked_exact_failure_localization_count",
    "blind_boundary_localization_count",
    "explanation_provenance_correct_count",
    "no_post_interruption_failure_count",
    "invalid_validation_failure_count",
)


def _metrics_payload(metrics):
    return {
        "primitive_action_count": metrics.primitive_action_count,
        "procedure_call_count": metrics.procedure_call_count,
        "root_visible_dispatch_count": metrics.root_visible_dispatch_count,
        "total_step_event_count": metrics.total_step_event_count,
        "expected_outcome_check_count": metrics.expected_outcome_check_count,
        "suppressed_internal_check_count": metrics.suppressed_internal_check_count,
        "max_runtime_call_depth": metrics.max_runtime_call_depth,
    }


def _mode_payload(mode_result):
    return {
        "mode": mode_result.mode.value,
        "state": mode_result.state.value,
        "primitive_action_refs": list(mode_result.primitive_action_refs),
        "executed_primitive_step_paths": list(mode_result.executed_primitive_step_paths),
        "final_world_state_ref": mode_result.final_world_state_ref,
        "final_state_correct": mode_result.final_state_correct,
        "metrics": _metrics_payload(mode_result.metrics),
        "interruption_procedure_id": mode_result.interruption_procedure_id,
        "interruption_step_id": mode_result.interruption_step_id,
        "interruption_call_path": list(mode_result.interruption_call_path),
        "interruption_explanation_memory_ids": list(
            mode_result.interruption_explanation_memory_ids
        ),
        "deterministic_repeat_match": mode_result.deterministic_repeat_match,
    }


def _case_payload(case_result):
    return {
        "case_id": case_result.case_id,
        "expected_validation_error": case_result.expected_validation_error,
        "validation_error_observed": case_result.validation_error_observed,
        "mode_results": [_mode_payload(item) for item in case_result.mode_results],
    }


def _aggregate_payload(report):
    return {
        "case_count": report.case_count,
        "valid_case_count": report.valid_case_count,
        "invalid_case_count": report.invalid_case_count,
        "success_case_count": report.success_case_count,
        "flat_success_count": report.flat_success_count,
        "chunked_success_count": report.chunked_success_count,
        "blind_success_count": report.blind_success_count,
        "primitive_sequence_equivalence_count": (
            report.primitive_sequence_equivalence_count
        ),
        "flat_final_state_correct_count": report.flat_final_state_correct_count,
        "chunked_final_state_correct_count": (
            report.chunked_final_state_correct_count
        ),
        "blind_final_state_correct_count": report.blind_final_state_correct_count,
        "flat_root_visible_dispatches": (
            report.aggregate_flat_root_visible_dispatches
        ),
        "chunked_root_visible_dispatches": (
            report.aggregate_chunked_root_visible_dispatches
        ),
        "max_deliberative_compression_ratio": (
            report.max_deliberative_compression_ratio
        ),
        "chunk_reuse_count": report.chunk_reuse_count,
        "checked_failure_case_count": report.checked_failure_case_count,
        "flat_exact_failure_localization_count": (
            report.flat_exact_failure_localization_count
        ),
        "chunked_exact_failure_localization_count": (
            report.chunked_exact_failure_localization_count
        ),
        "blind_boundary_localization_count": (
            report.blind_boundary_localization_count
        ),
        "explanation_provenance_correct_count": (
            report.explanation_provenance_correct_count
        ),
        "no_post_interruption_failure_count": (
            report.no_post_interruption_failure_count
        ),
        "invalid_validation_failure_count": (
            report.invalid_validation_failure_count
        ),
        "deterministic_repeat_match": report.deterministic_repeat_match,
    }


def _classify_aggregate(aggregate, reused_procedure_ids):
    has_reuse = (
        aggregate["chunk_reuse_count"] >= 2
        and bool(reused_procedure_ids)
    )
    has_reduction = (
        aggregate["chunked_root_visible_dispatches"]
        < aggregate["flat_root_visible_dispatches"]
        and aggregate["max_deliberative_compression_ratio"] > 1.0
    )
    if not has_reuse or not has_reduction:
        return "NOT_SUPPORTED"
    supported = (
        aggregate["flat_success_count"] == aggregate["success_case_count"]
        and aggregate["chunked_success_count"] == aggregate["success_case_count"]
        and aggregate["primitive_sequence_equivalence_count"]
        == aggregate["success_case_count"]
        and aggregate["flat_final_state_correct_count"]
        == aggregate["success_case_count"]
        and aggregate["chunked_final_state_correct_count"]
        == aggregate["success_case_count"]
        and aggregate["flat_exact_failure_localization_count"]
        == aggregate["checked_failure_case_count"]
        and aggregate["chunked_exact_failure_localization_count"]
        == aggregate["checked_failure_case_count"]
        and aggregate["blind_boundary_localization_count"]
        == aggregate["checked_failure_case_count"]
        and aggregate["explanation_provenance_correct_count"]
        == aggregate["checked_failure_case_count"] * 3
        and aggregate["no_post_interruption_failure_count"] == 0
        and aggregate["deterministic_repeat_match"] is True
    )
    return "SUPPORTED" if supported else "MIXED"


def run_qualification():
    cases = build_a008_fixture()
    report = run_a008_benchmark(cases)
    errors = qualify_a008_report(report)
    payload = {
        "qualification_scope": QUALIFICATION_SCOPE,
        "fixture_version": FIXTURE_VERSION,
        "fixture_fingerprint": fixture_fingerprint(cases),
        "case_ids": [case.case_id for case in cases],
        "modes": [mode.value for mode in ProcedureExecutionMode],
        "max_call_depth": MAX_CALL_DEPTH,
        "primary_architecture": "CHUNKED",
        "controls": ["FLAT", "BLIND_CHUNKED"],
        "reused_procedure_ids": list(report.reused_procedure_ids),
        "chunk_reuse_counts": [
            [procedure_id, count]
            for procedure_id, count in report.chunk_reuse_counts
        ],
        "aggregate_metrics": _aggregate_payload(report),
        "cases": [_case_payload(item) for item in report.case_results],
        "primary_hypothesis_outcome": classify_a008_hypothesis(report),
        "experiment_valid": not errors,
        "errors": errors,
        "claims_boundary": (
            "root-visible dispatch and control-state metrics only; "
            "no hardware or runtime efficiency claim"
        ),
    }
    return payload


def _nonnegative_int(errors, name, value):
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        errors.append(f"{name} must be a nonnegative integer")


def validate_qualification_payload(payload):
    errors = []
    cases = build_a008_fixture()
    expected_ids = [case.case_id for case in cases]
    if payload.get("qualification_scope") != QUALIFICATION_SCOPE:
        errors.append("qualification_scope mismatch")
    if payload.get("fixture_version") != FIXTURE_VERSION:
        errors.append("fixture_version mismatch")
    if payload.get("fixture_fingerprint") != EXPECTED_FIXTURE_FINGERPRINT:
        errors.append("fixture_fingerprint mismatch")
    if payload.get("case_ids") != expected_ids:
        errors.append("case_ids mismatch")
    if payload.get("modes") != [mode.value for mode in ProcedureExecutionMode]:
        errors.append("modes mismatch")
    if payload.get("max_call_depth") != MAX_CALL_DEPTH:
        errors.append("max_call_depth mismatch")

    aggregate = payload.get("aggregate_metrics")
    if not isinstance(aggregate, dict):
        return errors + ["aggregate_metrics must be an object"]
    for name in _INT_METRICS:
        _nonnegative_int(errors, name, aggregate.get(name))
    ratio = aggregate.get("max_deliberative_compression_ratio")
    if (
        not isinstance(ratio, (int, float))
        or isinstance(ratio, bool)
        or not math.isfinite(float(ratio))
        or float(ratio) < 0.0
    ):
        errors.append(
            "max_deliberative_compression_ratio must be finite and nonnegative"
        )
    if not isinstance(aggregate.get("deterministic_repeat_match"), bool):
        errors.append("deterministic_repeat_match must be bool")

    if aggregate.get("invalid_validation_failure_count") != 0:
        errors.append("invalid_validation_failure_count must be 0")
    if aggregate.get("no_post_interruption_failure_count") != 0:
        errors.append("no_post_interruption_failure_count must be 0")

    if (
        isinstance(aggregate.get("case_count"), int)
        and isinstance(aggregate.get("valid_case_count"), int)
        and isinstance(aggregate.get("invalid_case_count"), int)
        and aggregate["case_count"]
        != aggregate["valid_case_count"] + aggregate["invalid_case_count"]
    ):
        errors.append("case_count must equal valid_case_count + invalid_case_count")

    if (
        isinstance(aggregate.get("success_case_count"), int)
        and isinstance(aggregate.get("valid_case_count"), int)
        and aggregate["success_case_count"] > aggregate["valid_case_count"]
    ):
        errors.append("success_case_count cannot exceed valid_case_count")

    success_bound_metrics = (
        "flat_success_count",
        "chunked_success_count",
        "blind_success_count",
        "primitive_sequence_equivalence_count",
        "flat_final_state_correct_count",
        "chunked_final_state_correct_count",
        "blind_final_state_correct_count",
    )
    success_cases = aggregate.get("success_case_count")
    if isinstance(success_cases, int):
        for name in success_bound_metrics:
            value = aggregate.get(name)
            if isinstance(value, int) and value > success_cases:
                errors.append(f"{name} cannot exceed success_case_count")

    failure_cases = aggregate.get("checked_failure_case_count")
    if isinstance(failure_cases, int):
        for name in (
            "flat_exact_failure_localization_count",
            "chunked_exact_failure_localization_count",
            "blind_boundary_localization_count",
        ):
            value = aggregate.get(name)
            if isinstance(value, int) and value > failure_cases:
                errors.append(f"{name} cannot exceed checked_failure_case_count")
        provenance = aggregate.get("explanation_provenance_correct_count")
        if isinstance(provenance, int) and provenance > failure_cases * 3:
            errors.append(
                "explanation_provenance_correct_count cannot exceed "
                "checked_failure_case_count * 3"
            )

    reused = payload.get("reused_procedure_ids")
    if not isinstance(reused, list) or any(
        not isinstance(item, str) or not item for item in reused
    ):
        errors.append("reused_procedure_ids must be a list of nonblank strings")
        reused = []

    reuse_counts_raw = payload.get("chunk_reuse_counts")
    parsed_reuse_counts = {}
    if not isinstance(reuse_counts_raw, list):
        errors.append("chunk_reuse_counts must be a list")
    else:
        for item in reuse_counts_raw:
            if (
                not isinstance(item, list)
                or len(item) != 2
                or not isinstance(item[0], str)
                or not item[0]
                or not isinstance(item[1], int)
                or isinstance(item[1], bool)
                or item[1] < 0
            ):
                errors.append("chunk_reuse_counts entries must be [nonblank id, nonnegative int]")
                parsed_reuse_counts = {}
                break
            if item[0] in parsed_reuse_counts:
                errors.append("chunk_reuse_counts procedure IDs must be unique")
                parsed_reuse_counts = {}
                break
            parsed_reuse_counts[item[0]] = item[1]

    if parsed_reuse_counts:
        expected_reused = sorted(
            procedure_id
            for procedure_id, count in parsed_reuse_counts.items()
            if count >= 2
        )
        if sorted(reused) != expected_reused:
            errors.append("reused_procedure_ids reuse metadata drift")
        expected_reuse_count = sum(
            count
            for procedure_id, count in parsed_reuse_counts.items()
            if procedure_id in expected_reused
        )
        if aggregate.get("chunk_reuse_count") != expected_reuse_count:
            errors.append("chunk_reuse_count reuse metadata drift")
    elif reused or aggregate.get("chunk_reuse_count") not in (0, None):
        errors.append("reuse metadata is inconsistent with chunk_reuse_counts")

    outcome = payload.get("primary_hypothesis_outcome")
    if outcome not in {"SUPPORTED", "MIXED", "NOT_SUPPORTED"}:
        errors.append("primary_hypothesis_outcome has invalid vocabulary")
    else:
        required_keys_present = all(name in aggregate for name in _INT_METRICS)
        required_keys_present = required_keys_present and (
            "max_deliberative_compression_ratio" in aggregate
            and "deterministic_repeat_match" in aggregate
        )
        if required_keys_present and not errors:
            expected = _classify_aggregate(aggregate, reused)
            if outcome != expected:
                errors.append(
                    f"primary hypothesis outcome drift: expected {expected}"
                )

    return errors


def _emit(payload, output_path):
    line = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ) + "\n"
    encoded = line.encode("utf-8")
    stream = getattr(sys.stdout, "buffer", None)
    if stream is not None:
        stream.write(encoded)
        stream.flush()
    else:
        sys.stdout.write(line)
    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(encoded)


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