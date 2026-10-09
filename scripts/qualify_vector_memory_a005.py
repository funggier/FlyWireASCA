from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from flywire_asca.contracts import MemoryKind, MemoryRecord
from flywire_asca.embedding import (
    EmbeddingAdapterError,
    EmbeddingDescriptor,
    EmbeddingInputKind,
    EmbeddingRequest,
    OllamaEmbeddingAdapter,
)
from flywire_asca.vector_memory import (
    GraphDecision,
    VectorMemoryBenchmarkCase,
    VectorMemoryDocument,
    VectorMemoryQuery,
    benchmark_report_payload,
    calibrate_a005_threshold,
    decide_graph_need,
    qualify_a005_report,
    run_vector_memory_benchmark,
)


MODEL_NAME = "qwen3-embedding:0.6b"
PROFILE_NAME = "qwen3-embedding-0.6b-vector-memory-v1"
BASE_URL = "http://127.0.0.1:11434"
EXPECTED_DIMENSION = 1024
EXPECTED_DIGEST = "ac6da0dfba84a81fdbfbaf330198c33cd77c4cdfc53e8bc50eb581914a15621d"
FROZEN_PHYSICAL_THRESHOLD = 0.5037018224299838
TIMEOUT_SECONDS = 120.0
HEALTH_REPEATS = 8
CALIBRATION_ORIGIN = "physical_development_fixture_v1"
QUALIFICATION_ORIGIN = "physical_frozen_threshold_v1"


def _doc(
    memory_id: str,
    text: str,
    *,
    entity_ids: tuple[str, ...] = (),
) -> VectorMemoryDocument:
    return VectorMemoryDocument(
        MemoryRecord(
            memory_id,
            MemoryKind.SEMANTIC,
            f"content:{memory_id}",
            0.8,
        ),
        text,
        entity_ids=entity_ids,
    )


def build_physical_calibration_fixture() -> tuple[
    tuple[VectorMemoryDocument, ...],
    tuple[VectorMemoryBenchmarkCase, ...],
]:
    documents = (
        _doc("physical-cal-bike-memory", "The bicycle is stored in the garage."),
        _doc("physical-cal-cat-memory", "แมวสีดำชอบนอนบนเก้าอี้ไม้"),
        _doc("physical-cal-meeting-distractor", "The company meeting starts at 9 AM."),
        _doc("physical-cal-restaurant-distractor", "ร้านอาหารปิดเวลา 21:00 น."),
    )
    cases = (
        VectorMemoryBenchmarkCase(
            "physical-cal-bike",
            VectorMemoryQuery(
                "physical-cal-bike",
                "Where is the bike kept?",
                top_k=len(documents),
                minimum_similarity=-1.0,
            ),
            ("physical-cal-bike-memory",),
        ),
        VectorMemoryBenchmarkCase(
            "physical-cal-cat",
            VectorMemoryQuery(
                "physical-cal-cat",
                "แมวสีดำชอบนอนที่ไหน",
                top_k=len(documents),
                minimum_similarity=-1.0,
            ),
            ("physical-cal-cat-memory",),
        ),
    )
    return documents, cases


def build_physical_qualification_fixture(
    frozen_threshold: float,
) -> tuple[
    tuple[VectorMemoryDocument, ...],
    tuple[VectorMemoryBenchmarkCase, ...],
]:
    if not math.isfinite(frozen_threshold) or not -1.0 <= frozen_threshold <= 1.0:
        raise ValueError("physical threshold must be finite and within [-1, 1]")
    documents = (
        _doc(
            "physical-red-scooter",
            "I parked the red scooter beside the library.",
        ),
        _doc(
            "physical-green-parrot",
            "นกแก้วสีเขียวชอบกินเมล็ดทานตะวัน",
        ),
        _doc(
            "physical-backup-drive",
            "The backup drive is stored in the blue cabinet.",
        ),
        _doc(
            "physical-meeting-room",
            "ห้องประชุมอยู่ชั้นสามของอาคาร",
        ),
        _doc(
            "physical-somchai-a",
            "Somchai works at company A.",
            entity_ids=("person-a",),
        ),
        _doc(
            "physical-somchai-b",
            "Somchai works at company B.",
            entity_ids=("person-b",),
        ),
    )
    cases = (
        VectorMemoryBenchmarkCase(
            "physical-en-paraphrase",
            VectorMemoryQuery(
                "physical-en-paraphrase",
                "Where did I park the red scooter?",
                minimum_similarity=frozen_threshold,
            ),
            ("physical-red-scooter",),
        ),
        VectorMemoryBenchmarkCase(
            "physical-th-paraphrase",
            VectorMemoryQuery(
                "physical-th-paraphrase",
                "นกแก้วสีเขียวชอบกินอะไร",
                minimum_similarity=frozen_threshold,
            ),
            ("physical-green-parrot",),
        ),
        VectorMemoryBenchmarkCase(
            "physical-th-to-en",
            VectorMemoryQuery(
                "physical-th-to-en",
                "ไดรฟ์สำรองเก็บไว้ที่ไหน",
                minimum_similarity=frozen_threshold,
            ),
            ("physical-backup-drive",),
        ),
        VectorMemoryBenchmarkCase(
            "physical-en-to-th",
            VectorMemoryQuery(
                "physical-en-to-th",
                "Which floor is the meeting room on?",
                minimum_similarity=frozen_threshold,
            ),
            ("physical-meeting-room",),
        ),
        VectorMemoryBenchmarkCase(
            "physical-same-name",
            VectorMemoryQuery(
                "physical-same-name",
                "Somchai works where?",
                top_k=2,
                minimum_similarity=frozen_threshold,
            ),
            ("physical-somchai-a", "physical-somchai-b"),
            require_recall_at_1=False,
            ambiguity_expected=True,
            expected_ranked_ids=("physical-somchai-a", "physical-somchai-b"),
        ),
        VectorMemoryBenchmarkCase(
            "physical-entity-filter",
            VectorMemoryQuery(
                "physical-entity-filter",
                "Which Somchai works at company B?",
                minimum_similarity=frozen_threshold,
                required_entity_ids=("person-b",),
            ),
            ("physical-somchai-b",),
            metadata_filter_expected=True,
        ),
    )
    return documents, cases


def validate_descriptor(
    descriptor: EmbeddingDescriptor,
    expected_digest: str | None,
) -> list[str]:
    errors: list[str] = []
    if descriptor.backend_name != "ollama":
        errors.append("backend name must be ollama")
    if descriptor.model_name != MODEL_NAME:
        errors.append(f"model name must be {MODEL_NAME}")
    if expected_digest is not None and descriptor.model_digest != expected_digest:
        errors.append("model digest must match the pinned A005 digest")
    if descriptor.embedding_dimension != EXPECTED_DIMENSION:
        errors.append(
            f"embedding dimension must be {EXPECTED_DIMENSION}"
        )
    if "embedding" not in descriptor.capabilities:
        errors.append("capabilities must include embedding")
    return errors


def run_vector_health(adapter, *, repeats: int = HEALTH_REPEATS) -> dict[str, object]:
    if not isinstance(repeats, int) or isinstance(repeats, bool) or repeats <= 0:
        raise ValueError("repeats must be a positive integer")
    norms: list[float] = []
    dimensions: list[int] = []
    zero_count = 0
    nonfinite_count = 0
    for index in range(repeats):
        response = adapter.embed(
            EmbeddingRequest(
                f"a005-health-{index}",
                EmbeddingInputKind.DOCUMENT,
                ("health probe english", "ทดสอบเวกเตอร์สุขภาพ"),
            )
        )
        for vector in response.vectors:
            dimensions.append(vector.dimension)
            norm = math.sqrt(sum(value * value for value in vector.values))
            norms.append(norm)
            if not math.isfinite(norm):
                nonfinite_count += 1
            if norm <= 1e-12:
                zero_count += 1
    if not norms:
        raise ValueError("vector health produced no vectors")
    unique_dimensions = sorted(set(dimensions))
    return {
        "probe_count": len(norms),
        "repeated_request_count": repeats,
        "dimension": unique_dimensions[0] if len(unique_dimensions) == 1 else None,
        "observed_dimensions": unique_dimensions,
        "zero_vector_count": zero_count,
        "nonfinite_vector_count": nonfinite_count,
        "norm_min": min(norms),
        "norm_max": max(norms),
    }


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


def _base_payload(
    *,
    mode: str,
    descriptor: EmbeddingDescriptor | None,
    experiment_valid: bool,
    errors: list[str],
) -> dict[str, object]:
    return {
        "qualification_scope": "local_physical_vector_memory_a005",
        "mode": mode,
        "experiment_valid": experiment_valid,
        "errors": errors,
        "embedding_profile": PROFILE_NAME,
        "model": (
            _descriptor_payload(descriptor)
            if descriptor is not None
            else {"name": MODEL_NAME}
        ),
    }


def _emit(payload: dict[str, object], output_path: Path | None) -> None:
    line = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ) + "\n"
    encoded = line.encode("utf-8")
    stdout_buffer = getattr(sys.stdout, "buffer", None)
    if stdout_buffer is not None:
        stdout_buffer.write(encoded)
        stdout_buffer.flush()
    else:
        sys.stdout.write(line)
    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(encoded)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default=BASE_URL)
    parser.add_argument("--model", default=MODEL_NAME)
    parser.add_argument("--expected-digest", default=EXPECTED_DIGEST)
    parser.add_argument("--expected-dimension", type=int, default=EXPECTED_DIMENSION)
    parser.add_argument("--timeout-seconds", type=float, default=TIMEOUT_SECONDS)
    parser.add_argument("--health-repeats", type=int, default=HEALTH_REPEATS)
    parser.add_argument("--calibrate", action="store_true")
    parser.add_argument(
        "--threshold",
        type=float,
        default=FROZEN_PHYSICAL_THRESHOLD,
    )
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)

    if args.model != MODEL_NAME or args.expected_dimension != EXPECTED_DIMENSION:
        payload = _base_payload(
            mode="calibration" if args.calibrate else "qualification",
            descriptor=None,
            experiment_valid=False,
            errors=["A005 physical model name/dimension must match the qualified profile"],
        )
        _emit(payload, args.output)
        return 1
    if not args.calibrate and args.threshold is None:
        payload = _base_payload(
            mode="qualification",
            descriptor=None,
            experiment_valid=False,
            errors=["frozen physical threshold is required for qualification"],
        )
        _emit(payload, args.output)
        return 1

    descriptor: EmbeddingDescriptor | None = None
    try:
        adapter = OllamaEmbeddingAdapter(
            args.model,
            base_url=args.base_url,
            expected_digest=args.expected_digest,
            expected_dimension=args.expected_dimension,
            timeout_seconds=args.timeout_seconds,
        )
        descriptor = adapter.inspect()
        errors = validate_descriptor(descriptor, args.expected_digest)
        if errors:
            payload = _base_payload(
                mode="calibration" if args.calibrate else "qualification",
                descriptor=descriptor,
                experiment_valid=False,
                errors=errors,
            )
            _emit(payload, args.output)
            return 1

        health = run_vector_health(adapter, repeats=args.health_repeats)
        if (
            health["zero_vector_count"] != 0
            or health["nonfinite_vector_count"] != 0
            or health["dimension"] != EXPECTED_DIMENSION
        ):
            payload = _base_payload(
                mode="calibration" if args.calibrate else "qualification",
                descriptor=descriptor,
                experiment_valid=False,
                errors=["vector health qualification failed"],
            )
            payload["vector_health"] = health
            _emit(payload, args.output)
            return 1

        calibration_documents, calibration_cases = (
            build_physical_calibration_fixture()
        )
        calibration_case_ids = [case.case_id for case in calibration_cases]

        if args.calibrate:
            threshold = calibrate_a005_threshold(
                calibration_documents,
                adapter,
                calibration_cases,
                embedding_profile=PROFILE_NAME,
            )
            payload = _base_payload(
                mode="calibration",
                descriptor=descriptor,
                experiment_valid=True,
                errors=[],
            )
            payload.update(
                {
                    "vector_health": health,
                    "physical_threshold": threshold,
                    "threshold_origin": CALIBRATION_ORIGIN,
                    "calibration_case_ids": calibration_case_ids,
                }
            )
            _emit(payload, args.output)
            return 0

        threshold = float(args.threshold)
        if not math.isfinite(threshold) or not -1.0 <= threshold <= 1.0:
            raise ValueError(
                "frozen physical threshold must be finite and within [-1, 1]"
            )
        qualification_documents, qualification_cases = (
            build_physical_qualification_fixture(threshold)
        )
        qualification_ids = [case.case_id for case in qualification_cases]
        if not set(calibration_case_ids).isdisjoint(qualification_ids):
            raise ValueError(
                "physical calibration and qualification case IDs must be disjoint"
            )

        report = run_vector_memory_benchmark(
            qualification_documents,
            adapter,
            qualification_cases,
            embedding_profile=PROFILE_NAME,
            frozen_threshold=threshold,
            threshold_origin=QUALIFICATION_ORIGIN,
        )
        retrieval_errors = qualify_a005_report(report)
        decision = decide_graph_need(report)
        payload = _base_payload(
            mode="qualification",
            descriptor=descriptor,
            experiment_valid=True,
            errors=retrieval_errors,
        )
        payload.update(
            {
                "retrieval_qualified": not retrieval_errors,
                "physical_threshold": threshold,
                "threshold_origin": QUALIFICATION_ORIGIN,
                "vector_health": health,
                "calibration_case_ids": calibration_case_ids,
                "qualification_case_ids": qualification_ids,
                "qualification_query_texts": [
                    case.query.query_text for case in qualification_cases
                ],
                "benchmark": benchmark_report_payload(report),
                "graph_decision": decision.value,
            }
        )
        _emit(payload, args.output)
        return 0
    except (EmbeddingAdapterError, ValueError) as exc:
        payload = _base_payload(
            mode="calibration" if args.calibrate else "qualification",
            descriptor=descriptor,
            experiment_valid=False,
            errors=[str(exc)],
        )
        _emit(payload, args.output)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
