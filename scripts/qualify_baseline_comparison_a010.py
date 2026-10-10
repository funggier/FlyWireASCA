import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from flywire_asca.baseline_comparison import (
    ComparisonVariant,
    a010_fixture_fingerprint,
    build_a010_deterministic_fixture,
    classify_a010_hypothesis,
    qualify_a010_report,
    run_a010_benchmark,
)

QUALIFICATION_SCOPE = "deterministic_dense_nonselective_baseline_a010"
FIXTURE_VERSION = "a010-deterministic-v1"
EXPECTED_FIXTURE_FINGERPRINT = "a1792f471409db74e436f63765d6c0330a6544575edfd45585b9eef30767dd68"
DENSE_TOP_K_POLICY = "max(1,index.document_count)"
PRIMARY_PROCEDURE_MODE = "CHUNKED"
PRIMARY_ASCA_POLICY = "MISMATCH_DRIVEN_RECOVERY"
VARIANTS = [item.value for item in ComparisonVariant]

_AGGREGATE_FIELDS = (
    "case_count",
    "valid_case_count",
    "invalid_case_count",
    "primary_case_count",
    "asca_success_count",
    "dense_success_count",
    "shared_success_count",
    "dense_only_success_count",
    "asca_only_success_count",
    "asca_final_state_correct_count",
    "dense_final_state_correct_count",
    "asca_query_count",
    "dense_query_count",
    "asca_scored_vector_count",
    "dense_scored_vector_count",
    "asca_cumulative_selected_count",
    "dense_cumulative_selected_count",
    "asca_peak_selected_count",
    "dense_peak_selected_count",
    "asca_procedure_attempt_count",
    "dense_procedure_attempt_count",
    "identity_failure_count",
    "duplicate_execution_id_failure_count",
    "post_completion_extra_attempt_failure_count",
    "designated_parity_reduction_count",
    "asca_deterministic_repeat_match",
    "dense_deterministic_repeat_match",
)


def _run_payload(run):
    return {
        "variant": run.variant.value,
        "case_id": run.case_id,
        "procedure_success": run.procedure_success,
        "final_state_correct": run.final_state_correct,
        "final_world_state_ref": run.final_world_state_ref,
        "evaluated_scope_indices": list(run.evaluated_scope_indices),
        "query_count": run.query_count,
        "stored_count_sum": run.stored_count_sum,
        "metadata_eligible_count_sum": run.metadata_eligible_count_sum,
        "scored_vector_count_sum": run.scored_vector_count_sum,
        "above_threshold_count_sum": run.above_threshold_count_sum,
        "returned_count_sum": run.returned_count_sum,
        "cumulative_unique_candidate_count": run.cumulative_unique_candidate_count,
        "cumulative_activated_candidate_count": run.cumulative_activated_candidate_count,
        "cumulative_selected_count": run.cumulative_selected_count,
        "peak_selected_count": run.peak_selected_count,
        "final_selected_memory_ids": list(run.final_selected_memory_ids),
        "procedure_attempt_count": run.procedure_attempt_count,
        "execution_ids": list(run.execution_ids),
        "procedure_states": list(run.procedure_states),
        "mismatch_count": run.mismatch_count,
        "forced_recovery_scope_count": run.forced_recovery_scope_count,
        "same_name_identity_preserved": run.same_name_identity_preserved,
        "trace_signature": [
            [kind, list(refs)] for kind, refs in run.trace_signature
        ],
    }


def _case_payload(case):
    return {
        "case_id": case.case_id,
        "shared_input_fingerprint": case.shared_input_fingerprint,
        "validation_error_observed": case.validation_error_observed,
        "validation_error": case.validation_error,
        "expected_primary_case": case.expected_primary_case,
        "runs": [_run_payload(run) for run in case.runs],
    }


def _expected_payload():
    cases = build_a010_deterministic_fixture()
    report = run_a010_benchmark(cases)
    errors = qualify_a010_report(report)
    return {
        "qualification_scope": QUALIFICATION_SCOPE,
        "fixture_version": FIXTURE_VERSION,
        "fixture_fingerprint": a010_fixture_fingerprint(cases),
        "case_ids": [case.case_id for case in cases],
        "variants": VARIANTS,
        "dense_top_k_policy": DENSE_TOP_K_POLICY,
        "primary_procedure_mode": PRIMARY_PROCEDURE_MODE,
        "primary_asca_policy": PRIMARY_ASCA_POLICY,
        "aggregate_metrics": {
            name: getattr(report, name) for name in _AGGREGATE_FIELDS
        },
        "cases": [_case_payload(case) for case in report.case_results],
        "primary_hypothesis_outcome": classify_a010_hypothesis(report),
        "experiment_valid": not errors,
        "errors": errors,
        "claims_boundary": (
            "controlled logical retrieval/active-state/procedure evidence only; "
            "no FLOP, energy, RAM-byte, hardware-bandwidth, general-latency, "
            "dense-LLM-superiority, or real-tool autonomy claim"
        ),
    }


def run_qualification():
    return _expected_payload()


def validate_qualification_payload(payload):
    errors = []
    expected = _expected_payload()

    for name in (
        "qualification_scope",
        "fixture_version",
        "fixture_fingerprint",
        "case_ids",
        "variants",
        "dense_top_k_policy",
        "primary_procedure_mode",
        "primary_asca_policy",
    ):
        if payload.get(name) != expected[name]:
            errors.append(f"{name} mismatch")

    aggregate = payload.get("aggregate_metrics")
    if not isinstance(aggregate, dict):
        errors.append("aggregate_metrics must be an object")
    else:
        for name, value in expected["aggregate_metrics"].items():
            if aggregate.get(name) != value:
                errors.append(f"{name} does not match raw frozen case evidence")

    outcome = payload.get("primary_hypothesis_outcome")
    if outcome not in {"SUPPORTED", "MIXED", "NOT_SUPPORTED"}:
        errors.append("primary_hypothesis_outcome has invalid vocabulary")
    elif outcome != expected["primary_hypothesis_outcome"]:
        errors.append(
            "primary_hypothesis_outcome drift from frozen evidence"
        )

    cases = payload.get("cases")
    if not isinstance(cases, list):
        errors.append("cases must be a list")
        return errors

    if [item.get("case_id") for item in cases if isinstance(item, dict)] != expected["case_ids"]:
        errors.append("case_ids/cases order mismatch")

    expected_by_id = {
        item["case_id"]: item for item in expected["cases"]
    }
    for case in cases:
        if not isinstance(case, dict):
            errors.append("case entries must be objects")
            continue
        case_id = case.get("case_id")
        expected_case = expected_by_id.get(case_id)
        if expected_case is None:
            errors.append(f"unknown case_id: {case_id}")
            continue
        if (
            case.get("shared_input_fingerprint")
            != expected_case["shared_input_fingerprint"]
        ):
            errors.append(
                f"shared_input_fingerprint mismatch for {case_id}"
            )
        runs = case.get("runs")
        if not isinstance(runs, list):
            errors.append(f"runs must be a list for {case_id}")
            continue
        for run in runs:
            if not isinstance(run, dict):
                errors.append("run entries must be objects")
                continue
            execution_ids = run.get("execution_ids")
            if (
                not isinstance(execution_ids, list)
                or any(not isinstance(item, str) or not item for item in execution_ids)
            ):
                errors.append("execution_ids must be nonblank strings")
            elif len(execution_ids) != len(set(execution_ids)):
                errors.append("execution_ids must be unique")
            if run.get("procedure_attempt_count") != (
                len(execution_ids) if isinstance(execution_ids, list) else -1
            ):
                errors.append(
                    "procedure_attempt_count must equal len(execution_ids)"
                )
            for name in (
                "cumulative_unique_candidate_count",
                "cumulative_activated_candidate_count",
                "cumulative_selected_count",
                "peak_selected_count",
            ):
                value = run.get(name)
                if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                    errors.append(f"{name} must be a nonnegative integer")
            unique = run.get("cumulative_unique_candidate_count", 0)
            activated = run.get("cumulative_activated_candidate_count", 0)
            selected = run.get("cumulative_selected_count", 0)
            peak = run.get("peak_selected_count", 0)
            if isinstance(unique, int) and isinstance(activated, int) and activated > unique:
                errors.append("activated candidate evidence exceeds unique candidates")
            if isinstance(activated, int) and isinstance(selected, int) and selected > activated:
                errors.append("selected candidate evidence exceeds activated candidates")
            if isinstance(selected, int) and isinstance(peak, int) and peak > selected:
                errors.append("peak selected evidence exceeds cumulative selected")

    if cases != expected["cases"]:
        errors.append("cases raw evidence differs from frozen qualification")

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
