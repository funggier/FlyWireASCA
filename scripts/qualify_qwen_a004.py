from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from flywire_asca.model import (
    ModelAdapterError,
    ModelBaselineReport,
    ModelDescriptor,
    OllamaModelAdapter,
    build_qwen_a004_baseline_cases,
    qualify_qwen_a004_report,
    run_model_baseline,
)


QUALIFICATION_SCOPE = "local_physical_qwen_a004"
PROFILE_NAME = "qwen3.5-4b-thinking-off-v1"
MODEL_NAME = "qwen3.5:4b"
EXPECTED_DIGEST = "2a654d98e6fba55d452b7043684e9b57a947e393bbffa62485a7aac05ee4eefd"
EXPECTED_ARCHITECTURE = "qwen35"
EXPECTED_PARAMETER_COUNT = 4_659_865_088
EXPECTED_PARAMETER_SIZE = "4.7B"
EXPECTED_QUANTIZATION = "Q4_K_M"
EXPECTED_EMBEDDING_LENGTH = 2560
BASE_URL = "http://127.0.0.1:11434"
TIMEOUT_SECONDS = 120.0
CONTEXT_LIMIT = 8192
MAX_OUTPUT_TOKENS = 256
TEMPERATURE = 0.0
SEED = 0


def validate_descriptor(descriptor: ModelDescriptor) -> list[str]:
    errors: list[str] = []
    if descriptor.backend_name != "ollama":
        errors.append("backend name must be ollama")
    if descriptor.model_name != MODEL_NAME:
        errors.append(f"model name must be {MODEL_NAME}")
    if descriptor.model_digest != EXPECTED_DIGEST:
        errors.append("model digest must match the pinned A004 digest")
    if descriptor.architecture != EXPECTED_ARCHITECTURE:
        errors.append(f"architecture must be {EXPECTED_ARCHITECTURE}")
    if descriptor.parameter_count != EXPECTED_PARAMETER_COUNT:
        errors.append(
            f"parameter_count must be {EXPECTED_PARAMETER_COUNT}"
        )
    if descriptor.parameter_size != EXPECTED_PARAMETER_SIZE:
        errors.append(
            f"parameter_size must be {EXPECTED_PARAMETER_SIZE}"
        )
    if descriptor.quantization != EXPECTED_QUANTIZATION:
        errors.append(
            f"quantization must be {EXPECTED_QUANTIZATION}"
        )
    if (
        descriptor.context_length is None
        or descriptor.context_length < CONTEXT_LIMIT
    ):
        errors.append(
            f"context_length must be at least {CONTEXT_LIMIT}"
        )
    if descriptor.embedding_length != EXPECTED_EMBEDDING_LENGTH:
        errors.append(
            f"embedding_length must be {EXPECTED_EMBEDDING_LENGTH}"
        )
    required = {"completion", "thinking"}
    if not required <= set(descriptor.capabilities):
        errors.append(
            "capabilities must include completion and thinking"
        )
    return errors


def _case_payload(result) -> dict[str, object]:
    return {
        "case_id": result.case_id,
        "passed": result.passed,
        "normalized_output": result.normalized_output,
        "prompt_tokens": result.prompt_tokens,
        "generated_tokens": result.generated_tokens,
        "total_duration_ns": result.total_duration_ns,
        "load_duration_ns": result.load_duration_ns,
        "prompt_eval_duration_ns": result.prompt_eval_duration_ns,
        "eval_duration_ns": result.eval_duration_ns,
    }


def build_qualification_payload(
    descriptor: ModelDescriptor,
    report: ModelBaselineReport,
) -> dict[str, object]:
    errors = validate_descriptor(descriptor) + qualify_qwen_a004_report(report)
    return {
        "qualification_scope": QUALIFICATION_SCOPE,
        "qualified": not errors,
        "errors": errors,
        "runtime": {
            "backend_name": descriptor.backend_name,
            "backend_version": descriptor.backend_version,
        },
        "model": {
            "name": descriptor.model_name,
            "digest": descriptor.model_digest,
            "architecture": descriptor.architecture,
            "parameter_count": descriptor.parameter_count,
            "parameter_size": descriptor.parameter_size,
            "quantization": descriptor.quantization,
            "context_length": descriptor.context_length,
            "embedding_length": descriptor.embedding_length,
            "capabilities": list(descriptor.capabilities),
        },
        "generation_profile": {
            "profile_name": PROFILE_NAME,
            "thinking": False,
            "tools": False,
            "vision": False,
            "context_limit": CONTEXT_LIMIT,
            "max_output_tokens": MAX_OUTPUT_TOKENS,
            "temperature": TEMPERATURE,
            "seed": SEED,
        },
        "baseline": {
            "case_count": report.case_count,
            "passed_case_count": report.passed_case_count,
            "pass_rate": report.pass_rate,
            "prompt_tokens_total": report.prompt_tokens_total,
            "generated_tokens_total": report.generated_tokens_total,
            "total_duration_ns": report.total_duration_ns,
            "load_duration_ns": report.load_duration_ns,
            "prompt_eval_duration_ns": report.prompt_eval_duration_ns,
            "eval_duration_ns": report.eval_duration_ns,
            "case_results": [
                _case_payload(result)
                for result in report.case_results
            ],
        },
    }


def _failure_payload(error: str) -> dict[str, object]:
    return {
        "qualification_scope": QUALIFICATION_SCOPE,
        "qualified": False,
        "errors": [error],
        "generation_profile": {
            "profile_name": PROFILE_NAME,
            "thinking": False,
            "tools": False,
            "vision": False,
            "context_limit": CONTEXT_LIMIT,
            "max_output_tokens": MAX_OUTPUT_TOKENS,
            "temperature": TEMPERATURE,
            "seed": SEED,
        },
    }


def _emit(payload: dict[str, object], output_path: Path | None) -> None:
    line = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ) + "\n"
    sys.stdout.write(line)
    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(line, encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default=BASE_URL)
    parser.add_argument("--model", default=MODEL_NAME)
    parser.add_argument("--expected-digest", default=EXPECTED_DIGEST)
    parser.add_argument("--timeout-seconds", type=float, default=TIMEOUT_SECONDS)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)

    try:
        adapter = OllamaModelAdapter(
            args.model,
            base_url=args.base_url,
            expected_digest=args.expected_digest,
            timeout_seconds=args.timeout_seconds,
        )
        descriptor = adapter.inspect()
        report = run_model_baseline(
            adapter,
            build_qwen_a004_baseline_cases(),
            profile_name=PROFILE_NAME,
        )
        payload = build_qualification_payload(descriptor, report)
    except (ModelAdapterError, ValueError) as exc:
        payload = _failure_payload(str(exc))

    _emit(payload, args.output)
    return 0 if payload["qualified"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
