import argparse
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from flywire_asca.contracts import ActivationBudget, MemoryKind, MemoryRecord
from flywire_asca.embedding import (
    EmbeddingAdapterError,
    EmbeddingDescriptor,
    OllamaEmbeddingAdapter,
)
from flywire_asca.selective_activation import (
    SelectiveRetrievalEvidence,
    select_exhaustive,
    select_single_best,
    select_working_set,
)
from flywire_asca.vector_memory import (
    ExactVectorMemoryIndex,
    VectorMemoryDocument,
    VectorMemoryQuery,
)


MODEL_NAME = "qwen3-embedding:0.6b"
EXPECTED_DIGEST = "ac6da0dfba84a81fdbfbaf330198c33cd77c4cdfc53e8bc50eb581914a15621d"
EXPECTED_DIMENSION = 1024
A005_THRESHOLD = 0.5037018224299838
A005_TOP_K = 12
A006_MAX_MEMORY_NODES = 8
A006_MAX_WORKING_SET_ITEMS = 4
SELECTOR_PROFILE = "a006-selective-convergence-v1"
EMBEDDING_PROFILE = "qwen3-embedding-0.6b-vector-memory-v1"
FIXTURE_VERSION = "a006-physical-v1"
BASE_URL = "http://127.0.0.1:11434"
TIMEOUT_SECONDS = 120.0


@dataclass(frozen=True, slots=True)
class PhysicalCue:
    source_cue_id: str
    query_id: str
    query_text: str


@dataclass(frozen=True, slots=True)
class PhysicalSelectiveCase:
    case_id: str
    documents: tuple[VectorMemoryDocument, ...]
    cues: tuple[PhysicalCue, ...]
    required_memory_ids: tuple[str, ...] = ()
    expected_no_selection: bool = False
    ambiguity_expected: bool = False
    strict_budget_expected: bool = False
    convergence_recovery_challenge: bool = False


def _doc(
    memory_id: str,
    text: str,
    *,
    confidence: float = 0.8,
    entity_ids: tuple[str, ...] = (),
) -> VectorMemoryDocument:
    return VectorMemoryDocument(
        MemoryRecord(
            memory_id,
            MemoryKind.SEMANTIC,
            f"content:{memory_id}",
            confidence,
        ),
        text,
        entity_ids=entity_ids,
    )


def physical_budget() -> ActivationBudget:
    return ActivationBudget(
        max_memory_nodes=A006_MAX_MEMORY_NODES,
        max_relation_hops=0,
        max_working_set_items=A006_MAX_WORKING_SET_ITEMS,
        max_model_input_tokens=0,
        max_expansions=0,
    )


def build_physical_fixture() -> tuple[PhysicalSelectiveCase, ...]:
    return (
        PhysicalSelectiveCase(
            "physical-en-convergence",
            (
                _doc(
                    "en-shared-launch",
                    "The release readiness memory connects security review, backup verification, deployment approval, and the project launch.",
                ),
                _doc("en-security-only", "Security review findings for the project launch."),
                _doc("en-backup-only", "Backup verification checklist for launch day."),
                _doc("en-deploy-only", "Deployment approval record for the release."),
                _doc("en-meeting-only", "Project launch meeting agenda and attendee list."),
            ),
            (
                PhysicalCue("en-cue-security", "en-q-security", "Which memory links the project launch with security review?"),
                PhysicalCue("en-cue-backup", "en-q-backup", "Which memory links the project launch with backup verification?"),
                PhysicalCue("en-cue-deploy", "en-q-deploy", "Which memory links the project launch with deployment approval?"),
            ),
            ("en-shared-launch",),
        ),
        PhysicalSelectiveCase(
            "physical-th-convergence",
            (
                _doc(
                    "th-shared-trip",
                    "ความทรงจำการเดินทางเชียงใหม่รวมเรื่องรถสีแดง โรงแรมริมแม่น้ำ และการแวะตลาดเช้า",
                ),
                _doc("th-car-only", "รถสีแดงที่ใช้เดินทางไปเชียงใหม่"),
                _doc("th-hotel-only", "โรงแรมริมแม่น้ำในเชียงใหม่"),
                _doc("th-market-only", "ตลาดเช้าที่แวะซื้ออาหารระหว่างทริป"),
                _doc("th-weather-only", "พยากรณ์อากาศเชียงใหม่ช่วงสุดสัปดาห์"),
            ),
            (
                PhysicalCue("th-cue-car", "th-q-car", "ความทรงจำไหนเชื่อมทริปเชียงใหม่กับรถสีแดง"),
                PhysicalCue("th-cue-hotel", "th-q-hotel", "ความทรงจำไหนเชื่อมทริปเชียงใหม่กับโรงแรมริมแม่น้ำ"),
                PhysicalCue("th-cue-market", "th-q-market", "ความทรงจำไหนเชื่อมทริปเชียงใหม่กับตลาดเช้า"),
            ),
            ("th-shared-trip",),
        ),
        PhysicalSelectiveCase(
            "physical-cross-lingual-convergence",
            (
                _doc(
                    "cross-shared",
                    "The backup incident memory connects the blue cabinet, the external drive, and the recovery checklist.",
                ),
                _doc("cross-cabinet", "The blue cabinet contains archived equipment."),
                _doc("cross-drive", "The external backup drive is labeled for recovery."),
                _doc("cross-checklist", "The recovery checklist is printed beside the server rack."),
            ),
            (
                PhysicalCue("cross-cue-th", "cross-q-th", "ความทรงจำไหนเชื่อมตู้สีน้ำเงินกับไดรฟ์สำรอง"),
                PhysicalCue("cross-cue-en", "cross-q-en", "Which memory connects the external drive with the recovery checklist?"),
            ),
            ("cross-shared",),
        ),
        PhysicalSelectiveCase(
            "physical-same-name-ambiguity",
            (
                _doc(
                    "somchai-a",
                    "Somchai works at company A on the accounting team.",
                    entity_ids=("person-a",),
                ),
                _doc(
                    "somchai-b",
                    "Somchai works at company B on the operations team.",
                    entity_ids=("person-b",),
                ),
            ),
            (
                PhysicalCue("somchai-cue", "somchai-q", "Where does Somchai work?"),
            ),
            ("somchai-a", "somchai-b"),
            ambiguity_expected=True,
        ),
        PhysicalSelectiveCase(
            "physical-budget-truncation",
            tuple(
                _doc(
                    f"budget-{index:02d}",
                    f"Project status note {index}: launch readiness security backup deployment review.",
                )
                for index in range(12)
            ),
            (
                PhysicalCue("budget-cue", "budget-q", "project launch readiness security backup deployment status"),
            ),
            (),
            strict_budget_expected=True,
        ),
        PhysicalSelectiveCase(
            "physical-no-hit",
            (
                _doc("nohit-garden", "The garden watering schedule is posted by the greenhouse."),
                _doc("nohit-recipe", "The soup recipe uses pumpkin, onion, and ginger."),
                _doc("nohit-bicycle", "The bicycle repair kit is under the workbench."),
            ),
            (
                PhysicalCue("nohit-cue", "nohit-q", "What is the password for the lunar research server?"),
            ),
            (),
            expected_no_selection=True,
        ),
        PhysicalSelectiveCase(
            "physical-convergence-recovery-challenge",
            (
                _doc(
                    "challenge-shared",
                    "The incident response memory connects database latency, queue backlog, API timeout, and the production release.",
                ),
                _doc("challenge-db-a", "Database latency investigation for the production release."),
                _doc("challenge-db-b", "Database latency metrics and slow query analysis."),
                _doc("challenge-queue-a", "Queue backlog investigation during the production release."),
                _doc("challenge-queue-b", "Queue backlog metrics and worker saturation report."),
                _doc("challenge-api-a", "API timeout investigation for the production release."),
                _doc("challenge-api-b", "API timeout metrics and gateway latency report."),
            ),
            (
                PhysicalCue("challenge-db-cue", "challenge-db-q", "Which memory connects the production release with database latency?"),
                PhysicalCue("challenge-queue-cue", "challenge-queue-q", "Which memory connects the production release with queue backlog?"),
                PhysicalCue("challenge-api-cue", "challenge-api-q", "Which memory connects the production release with API timeout?"),
            ),
            ("challenge-shared",),
            convergence_recovery_challenge=True,
        ),
    )


def _fixture_fingerprint(cases: tuple[PhysicalSelectiveCase, ...]) -> str:
    payload = []
    for case in cases:
        payload.append(
            {
                "case_id": case.case_id,
                "documents": [
                    {
                        "memory_id": doc.memory.memory_id,
                        "retrieval_text": doc.retrieval_text,
                        "entity_ids": list(doc.entity_ids),
                    }
                    for doc in case.documents
                ],
                "cues": [
                    {
                        "source_cue_id": cue.source_cue_id,
                        "query_id": cue.query_id,
                        "query_text": cue.query_text,
                    }
                    for cue in case.cues
                ],
                "required_memory_ids": list(case.required_memory_ids),
                "expected_no_selection": case.expected_no_selection,
                "ambiguity_expected": case.ambiguity_expected,
                "strict_budget_expected": case.strict_budget_expected,
                "convergence_recovery_challenge": case.convergence_recovery_challenge,
            }
        )
    encoded = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _mode_payload(result) -> dict[str, object]:
    return {
        "selected_ids": [entry.ref_id for entry in result.working_set.entries],
        "active_ids": [state.node_id for state in result.activation_states],
        "support_ids": [support.memory_id for support in result.supports],
        "input_hit_count": result.input_hit_count,
        "unique_candidate_count": result.unique_candidate_count,
        "positive_candidate_count": result.positive_candidate_count,
        "activated_candidate_count": result.activated_candidate_count,
        "selected_count": result.selected_count,
        "memory_budget_drop_count": result.dropped_by_memory_budget_count,
        "working_set_budget_drop_count": result.dropped_by_working_set_budget_count,
        "memory_budget_boundary_tie": result.memory_budget_boundary_tie,
        "working_set_boundary_tie": result.working_set_boundary_tie,
        "retrieval_state": result.working_set.retrieval_state.value,
    }


def run_physical_case(
    adapter,
    case: PhysicalSelectiveCase,
    *,
    threshold: float,
    top_k: int,
    budget: ActivationBudget,
    embedding_profile: str,
) -> dict[str, object]:
    index = ExactVectorMemoryIndex(
        case.documents,
        adapter,
        embedding_profile=embedding_profile,
    )
    retrieval_results = tuple(
        index.search(
            VectorMemoryQuery(
                cue.query_id,
                cue.query_text,
                top_k=top_k,
                minimum_similarity=threshold,
            )
        )
        for cue in case.cues
    )
    evidence = tuple(
        SelectiveRetrievalEvidence(cue.source_cue_id, result)
        for cue, result in zip(case.cues, retrieval_results)
    )

    selective = select_working_set(evidence, budget=budget)
    single_best = select_single_best(evidence, budget=budget)
    exhaustive = select_exhaustive(evidence)

    selective_repeat = select_working_set(evidence, budget=budget)
    single_repeat = select_single_best(evidence, budget=budget)
    exhaustive_repeat = select_exhaustive(evidence)
    deterministic = (
        selective == selective_repeat
        and single_best == single_repeat
        and exhaustive == exhaustive_repeat
    )

    selective_ids = tuple(entry.ref_id for entry in selective.working_set.entries)
    single_ids = tuple(entry.ref_id for entry in single_best.working_set.entries)
    exhaustive_ids = tuple(entry.ref_id for entry in exhaustive.working_set.entries)
    required = set(case.required_memory_ids)
    selective_set = set(selective_ids)
    single_set = set(single_ids)
    exhaustive_set = set(exhaustive_ids)
    selective_covers = required.issubset(selective_set)
    single_covers = required.issubset(single_set)

    convergence_recovered = (
        case.convergence_recovery_challenge
        and selective_covers
        and not single_covers
    )
    convergence_regressed = bool(required) and single_covers and not selective_covers
    ambiguity_preserved = (
        not case.ambiguity_expected
        or required.issubset(selective_set)
    )
    no_selection_correct = (
        not selective_ids
        if case.expected_no_selection
        else True
    )
    strict_budget_observed = (
        selective.dropped_by_memory_budget_count > 0
        or selective.dropped_by_working_set_budget_count > 0
    )
    positive = selective.positive_candidate_count
    reduction = (
        (positive - selective.selected_count) / positive
        if positive
        else 0.0
    )

    return {
        "case_id": case.case_id,
        "required_memory_ids": list(case.required_memory_ids),
        "selective": _mode_payload(selective),
        "single_best": _mode_payload(single_best),
        "exhaustive": _mode_payload(exhaustive),
        "retrieval_hit_counts": [
            result.returned_count for result in retrieval_results
        ],
        "upstream_vectors_scored": sum(
            result.scored_vector_count for result in retrieval_results
        ),
        "required_selected_count": len(required & selective_set),
        "single_best_required_count": len(required & single_set),
        "exhaustive_required_count": len(required & exhaustive_set),
        "convergence_recovered": convergence_recovered,
        "convergence_regressed": convergence_regressed,
        "ambiguity_preserved": ambiguity_preserved,
        "no_selection_correct": no_selection_correct,
        "strict_budget_expected": case.strict_budget_expected,
        "strict_budget_observed": strict_budget_observed,
        "active_state_reduction_ratio": reduction,
        "deterministic_repeat_match": deterministic,
    }


def classify_hypothesis_outcome(
    *,
    required_memory_coverage: float,
    convergence_recovery_count: int,
    convergence_regression_count: int,
) -> str:
    if (
        required_memory_coverage == 1.0
        and convergence_recovery_count >= 1
        and convergence_regression_count == 0
    ):
        return "SUPPORTED"
    if convergence_recovery_count >= 1:
        return "MIXED"
    return "NOT_SUPPORTED"


def run_physical_experiment(adapter) -> dict[str, object]:
    cases = build_physical_fixture()
    budget = physical_budget()
    results = tuple(
        run_physical_case(
            adapter,
            case,
            threshold=A005_THRESHOLD,
            top_k=A005_TOP_K,
            budget=budget,
            embedding_profile=EMBEDDING_PROFILE,
        )
        for case in cases
    )

    total_required = sum(
        len(case.required_memory_ids)
        for case in cases
        if not case.expected_no_selection
    )
    total_required_selected = sum(
        int(result["required_selected_count"])
        for case, result in zip(cases, results)
        if not case.expected_no_selection
    )
    coverage = (
        total_required_selected / total_required
        if total_required
        else 1.0
    )
    recovery_count = sum(
        int(bool(result["convergence_recovered"]))
        for result in results
    )
    regression_count = sum(
        int(bool(result["convergence_regressed"]))
        for result in results
    )
    total_positive = sum(
        int(result["selective"]["positive_candidate_count"])
        for result in results
    )
    total_selected = sum(
        int(result["selective"]["selected_count"])
        for result in results
    )
    reduction = (
        (total_positive - total_selected) / total_positive
        if total_positive
        else 0.0
    )
    outcome = classify_hypothesis_outcome(
        required_memory_coverage=coverage,
        convergence_recovery_count=recovery_count,
        convergence_regression_count=regression_count,
    )

    return {
        "fixture_version": FIXTURE_VERSION,
        "fixture_fingerprint": _fixture_fingerprint(cases),
        "case_ids": [case.case_id for case in cases],
        "required_memory_coverage": coverage,
        "convergence_recovery_count": recovery_count,
        "convergence_regression_count": regression_count,
        "ambiguity_failure_count": sum(
            int(not bool(result["ambiguity_preserved"]))
            for result in results
        ),
        "no_selection_failure_count": sum(
            int(not bool(result["no_selection_correct"]))
            for result in results
        ),
        "strict_budget_observation_count": sum(
            int(
                case.strict_budget_expected
                and bool(result["strict_budget_observed"])
            )
            for case, result in zip(cases, results)
        ),
        "total_positive_candidates": total_positive,
        "total_selected_items": total_selected,
        "active_state_reduction_ratio": reduction,
        "deterministic_repeat_match": all(
            bool(result["deterministic_repeat_match"])
            for result in results
        ),
        "cases": list(results),
        "hypothesis_outcome": outcome,
        "experiment_valid": True,
    }


def validate_descriptor(descriptor: EmbeddingDescriptor) -> list[str]:
    errors: list[str] = []
    if descriptor.backend_name != "ollama":
        errors.append("backend name must be ollama")
    if descriptor.model_name != MODEL_NAME:
        errors.append(f"model name must be {MODEL_NAME}")
    if descriptor.model_digest != EXPECTED_DIGEST:
        errors.append("model digest must match the pinned A006/A005 digest")
    if descriptor.embedding_dimension != EXPECTED_DIMENSION:
        errors.append(f"embedding dimension must be {EXPECTED_DIMENSION}")
    if "embedding" not in descriptor.capabilities:
        errors.append("capabilities must include embedding")
    return errors


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
    descriptor: EmbeddingDescriptor | None,
    experiment_valid: bool,
    errors: list[str],
) -> dict[str, object]:
    return {
        "qualification_scope": "local_physical_selective_activation_a006",
        "experiment_valid": experiment_valid,
        "errors": errors,
        "selector_profile": SELECTOR_PROFILE,
        "embedding_profile": EMBEDDING_PROFILE,
        "frozen_profile": {
            "model": MODEL_NAME,
            "digest": EXPECTED_DIGEST,
            "embedding_dimension": EXPECTED_DIMENSION,
            "a005_threshold": A005_THRESHOLD,
            "a005_top_k": A005_TOP_K,
            "max_memory_nodes": A006_MAX_MEMORY_NODES,
            "max_working_set_items": A006_MAX_WORKING_SET_ITEMS,
            "max_relation_hops": 0,
            "max_expansions": 0,
            "max_model_input_tokens": 0,
        },
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
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)

    if (
        args.model != MODEL_NAME
        or args.expected_digest != EXPECTED_DIGEST
        or args.expected_dimension != EXPECTED_DIMENSION
    ):
        payload = _base_payload(
            descriptor=None,
            experiment_valid=False,
            errors=["A006 physical model identity/profile arguments must match the frozen profile"],
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
        errors = validate_descriptor(descriptor)
        if errors:
            payload = _base_payload(
                descriptor=descriptor,
                experiment_valid=False,
                errors=errors,
            )
            _emit(payload, args.output)
            return 1

        experiment = run_physical_experiment(adapter)
        if not experiment.get("deterministic_repeat_match", True):
            raise ValueError("physical selector repeated execution is nondeterministic")
        payload = _base_payload(
            descriptor=descriptor,
            experiment_valid=bool(experiment.get("experiment_valid", True)),
            errors=[],
        )
        payload.update(experiment)
        _emit(payload, args.output)
        return 0 if payload["experiment_valid"] else 1
    except (EmbeddingAdapterError, ValueError) as exc:
        payload = _base_payload(
            descriptor=descriptor,
            experiment_valid=False,
            errors=[str(exc)],
        )
        _emit(payload, args.output)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())