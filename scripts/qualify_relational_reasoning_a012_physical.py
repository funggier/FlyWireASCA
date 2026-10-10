from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from flywire_asca.embedding import (
    EmbeddingAdapterError,
    EmbeddingDescriptor,
    OllamaEmbeddingAdapter,
)
from flywire_asca.relational_reasoning import (
    ArchitectureDecision,
    benchmark_report_payload,
    build_a012_deterministic_fixture,
    classify_a012_architecture,
    run_a012_benchmark_with_adapter,
)


QUALIFICATION_SCOPE = "local_physical_relational_reasoning_a012"
MODEL_NAME = "qwen3-embedding:0.6b"
PROFILE_NAME = "qwen3-embedding-0.6b-a012-relational-v1"
BASE_URL = "http://127.0.0.1:11434"
EXPECTED_DIMENSION = 1024
EXPECTED_DIGEST = "ac6da0dfba84a81fdbfbaf330198c33cd77c4cdfc53e8bc50eb581914a15621d"
FROZEN_PHYSICAL_THRESHOLD = 0.5037018224299838
TIMEOUT_SECONDS = 120.0
PORTABLE_PRIMARY_DECISION = "EXPLICIT_RELATION_TRAVERSAL_JUSTIFIED"


def _descriptor_payload(descriptor: EmbeddingDescriptor) -> dict[str, object]:
    return {
        "backend_name": descriptor.backend_name,
        "backend_version": descriptor.backend_version,
        "name": descriptor.model_name,
        "digest": descriptor.model_digest,
        "architecture": descriptor.architecture,
        "parameter_count": descriptor.parameter_count,
        "parameter_size": descriptor.parameter_size,
        "quantization": descriptor.quantization,
        "context_length": descriptor.context_length,
        "embedding_dimension": descriptor.embedding_dimension,
        "capabilities": list(descriptor.capabilities),
    }


def _validate_descriptor(descriptor: EmbeddingDescriptor) -> list[str]:
    errors: list[str] = []
    if descriptor.backend_name != "ollama":
        errors.append("backend name must be ollama")
    if descriptor.model_name != MODEL_NAME:
        errors.append(f"model name must be {MODEL_NAME}")
    if descriptor.model_digest != EXPECTED_DIGEST:
        errors.append("model digest must match the pinned A012/A005 digest")
    if descriptor.embedding_dimension != EXPECTED_DIMENSION:
        errors.append(f"embedding dimension must be {EXPECTED_DIMENSION}")
    if "embedding" not in descriptor.capabilities:
        errors.append("capabilities must include embedding")
    return errors


def _base_payload(
    descriptor: EmbeddingDescriptor | None,
    *,
    experiment_valid: bool,
    errors: list[str],
) -> dict[str, object]:
    return {
        "qualification_scope": QUALIFICATION_SCOPE,
        "evidence_role": (
            "secondary physical embedding replay; portable deterministic "
            "A012 decision remains authoritative"
        ),
        "experiment_valid": experiment_valid,
        "portable_primary_architecture_decision": PORTABLE_PRIMARY_DECISION,
        "physical_threshold": FROZEN_PHYSICAL_THRESHOLD,
        "embedding_profile": PROFILE_NAME,
        "model": (
            _descriptor_payload(descriptor)
            if descriptor is not None
            else {"name": MODEL_NAME}
        ),
        "errors": errors,
    }


def run_physical_qualification(
    *,
    base_url: str = BASE_URL,
    timeout_seconds: float = TIMEOUT_SECONDS,
) -> dict[str, object]:
    descriptor: EmbeddingDescriptor | None = None
    try:
        adapter = OllamaEmbeddingAdapter(
            MODEL_NAME,
            base_url=base_url,
            expected_digest=EXPECTED_DIGEST,
            expected_dimension=EXPECTED_DIMENSION,
            timeout_seconds=timeout_seconds,
            keep_alive="6h",
        )
        descriptor = adapter.inspect()
        identity_errors = _validate_descriptor(descriptor)
        if identity_errors:
            return _base_payload(
                descriptor,
                experiment_valid=False,
                errors=identity_errors,
            )

        cases = build_a012_deterministic_fixture()
        report = run_a012_benchmark_with_adapter(
            cases,
            adapter,
            minimum_similarity=FROZEN_PHYSICAL_THRESHOLD,
            embedding_profile=PROFILE_NAME,
        )

        structural_errors: list[str] = []
        if report.case_count != 12:
            structural_errors.append("physical case_count must equal 12")
        if report.invalid_case_count != 1:
            structural_errors.append("physical invalid_case_count must equal 1")
        if report.deterministic_repeat_match is not True:
            structural_errors.append("physical repeat must be deterministic")
        if report.identity_failure_count != 0:
            structural_errors.append("physical identity_failure_count must equal 0")
        if report.provenance_failure_count != 0:
            structural_errors.append("physical provenance_failure_count must equal 0")
        if report.budget_violation_count != 0:
            structural_errors.append("physical budget_violation_count must equal 0")
        if report.duplicate_visit_failure_count != 0:
            structural_errors.append(
                "physical duplicate_visit_failure_count must equal 0"
            )

        physical_decision = classify_a012_architecture(report).value
        payload = _base_payload(
            descriptor,
            experiment_valid=not structural_errors,
            errors=structural_errors,
        )
        payload.update(
            {
                "physical_observed_architecture_decision": physical_decision,
                "physical_agrees_with_portable_decision": (
                    physical_decision == PORTABLE_PRIMARY_DECISION
                ),
                "benchmark": benchmark_report_payload(
                    report,
                    include_portable_qualification_errors=False,
                ),
                "claims_boundary": (
                    "physical replay is embedding-specific secondary evidence; "
                    "it cannot rewrite the frozen portable A012 decision and "
                    "does not claim persistent-graph or general graph superiority"
                ),
            }
        )
        return payload
    except (EmbeddingAdapterError, ValueError) as exc:
        return _base_payload(
            descriptor,
            experiment_valid=False,
            errors=[str(exc)],
        )


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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default=BASE_URL)
    parser.add_argument("--timeout-seconds", type=float, default=TIMEOUT_SECONDS)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--note")
    args = parser.parse_args(argv)

    payload = run_physical_qualification(
        base_url=args.base_url,
        timeout_seconds=args.timeout_seconds,
    )
    if args.note is not None:
        payload["note"] = args.note
    _emit(payload, args.output)
    return 0 if payload.get("experiment_valid") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
