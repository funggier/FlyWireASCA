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

from flywire_asca.contracts import MemoryKind, MemoryRecord
from flywire_asca.embedding import (
    EmbeddingAdapterError,
    EmbeddingDescriptor,
    OllamaEmbeddingAdapter,
)
from flywire_asca.selective_activation import (
    SelectiveRetrievalEvidence,
    select_single_best,
)
from flywire_asca.uncertainty_expansion import (
    ExpansionPolicy,
    ExpansionTerminationReason,
    build_a007_primary_profile,
    run_expansion_policy,
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
PRIMARY_SELECTOR = "SINGLE_BEST"
PROFILE_NAME = "a007-structural-expansion-v1"
EMBEDDING_PROFILE = "qwen3-embedding-0.6b-vector-memory-v1"
FIXTURE_VERSION = "a007-physical-v1"
EXPECTED_FIXTURE_FINGERPRINT = "59f95ef115534fe24e59570cb281c0564ab75aadf364f4c26feba0d4078213c9"
BASE_URL = "http://127.0.0.1:11434"
TIMEOUT_SECONDS = 120.0


@dataclass(frozen=True, slots=True)
class PhysicalExpansionCue:
    source_cue_id: str
    query_id: str
    query_text: str


@dataclass(frozen=True, slots=True)
class PhysicalExpansionCueTier:
    tier_index: int
    cues: tuple[PhysicalExpansionCue, ...]


@dataclass(frozen=True, slots=True)
class PhysicalExpansionCase:
    case_id: str
    documents: tuple[VectorMemoryDocument, ...]
    cue_tiers: tuple[PhysicalExpansionCueTier, ...]
    required_memory_ids: tuple[str, ...] = ()
    initially_sufficient: bool = False
    ambiguity_expected: bool = False
    persistent_insufficient: bool = False


_METRIC_KEYS = (
    "embedding_request_count",
    "embedding_input_count",
    "prompt_tokens_total",
    "prompt_tokens_observed_response_count",
    "total_duration_ns_total",
    "total_duration_observed_response_count",
    "load_duration_ns_total",
    "load_duration_observed_response_count",
)


class _RecordingEmbeddingAdapter:
    def __init__(self, delegate) -> None:
        self._delegate = delegate
        self._values = {key: 0 for key in _METRIC_KEYS}

    def inspect(self):
        return self._delegate.inspect()

    def embed(self, request):
        response = self._delegate.embed(request)
        self._values["embedding_request_count"] += 1
        self._values["embedding_input_count"] += response.input_count
        if response.prompt_tokens is not None:
            self._values["prompt_tokens_total"] += response.prompt_tokens
            self._values["prompt_tokens_observed_response_count"] += 1
        if response.total_duration_ns is not None:
            self._values["total_duration_ns_total"] += response.total_duration_ns
            self._values["total_duration_observed_response_count"] += 1
        if response.load_duration_ns is not None:
            self._values["load_duration_ns_total"] += response.load_duration_ns
            self._values["load_duration_observed_response_count"] += 1
        return response

    def snapshot(self):
        return dict(self._values)


def _metrics_delta(before, after):
    delta = {}
    for key in _METRIC_KEYS:
        value = after[key] - before[key]
        if value < 0:
            raise ValueError(f"{key} counter decreased")
        delta[key] = value
    return delta


def _sum_metrics(metrics):
    total = {key: 0 for key in _METRIC_KEYS}
    for item in metrics:
        for key in _METRIC_KEYS:
            total[key] += int(item[key])
    return total


def _doc(memory_id, text, *, entity_ids=()):
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


def _tiers(prefix, texts):
    return tuple(
        PhysicalExpansionCueTier(
            index,
            (
                PhysicalExpansionCue(
                    f"{prefix}-cue-{index}",
                    f"{prefix}-q-{index}",
                    text,
                ),
            ),
        )
        for index, text in enumerate(texts)
    )


def build_physical_fixture():
    return (
        PhysicalExpansionCase(
            "physical-en-easy",
            (
                _doc(
                    "en-easy-target",
                    "The cobalt travel notebook is stored in the second drawer beside the map cabinet.",
                ),
                _doc("en-easy-noise-a", "The greenhouse watering schedule is posted by the east door."),
                _doc("en-easy-noise-b", "The kitchen inventory lists rice, ginger, and sesame oil."),
            ),
            _tiers(
                "en-easy",
                (
                    "Where is the cobalt travel notebook stored?",
                    "Which memory mentions the cobalt notebook and map cabinet?",
                    "Find the note about the travel notebook in the second drawer.",
                ),
            ),
            ("en-easy-target",),
            initially_sufficient=True,
        ),
        PhysicalExpansionCase(
            "physical-th-easy",
            (
                _doc(
                    "th-easy-target",
                    "สมุดบันทึกสีม่วงถูกเก็บไว้ในลิ้นชักบนสุดข้างตู้แผนที่",
                ),
                _doc("th-easy-noise-a", "ตารางรดน้ำต้นไม้อยู่ที่ประตูเรือนกระจก"),
                _doc("th-easy-noise-b", "รายการอาหารในครัวมีข้าว ขิง และงา"),
            ),
            _tiers(
                "th-easy",
                (
                    "สมุดบันทึกสีม่วงถูกเก็บไว้ที่ไหน",
                    "ความทรงจำไหนพูดถึงสมุดสีม่วงกับตู้แผนที่",
                    "ค้นหาเรื่องสมุดบันทึกในลิ้นชักบนสุด",
                ),
            ),
            ("th-easy-target",),
            initially_sufficient=True,
        ),
        PhysicalExpansionCase(
            "physical-en-recovery",
            (
                _doc(
                    "en-recovery-target",
                    "A ceramic teapot painted with a blue crane was purchased at the old Kyoto market.",
                ),
                _doc("en-recovery-noise-a", "The bicycle repair kit is under the wooden workbench."),
                _doc("en-recovery-noise-b", "Pumpkin soup uses onion, ginger, and vegetable stock."),
            ),
            _tiers(
                "en-recovery",
                (
                    "What is the password for the lunar research server?",
                    "Which memory mentions a ceramic teapot painted with a blue crane?",
                    "Where was the blue-crane ceramic teapot purchased?",
                ),
            ),
            ("en-recovery-target",),
        ),
        PhysicalExpansionCase(
            "physical-th-recovery",
            (
                _doc(
                    "th-recovery-target",
                    "จักรยานสีเขียวที่ใช้เที่ยวอยุธยาถูกจอดไว้ข้างกำแพงอิฐใกล้ประตูเหนือ",
                ),
                _doc("th-recovery-noise-a", "สูตรแกงฟักทองใช้กะทิและใบโหระพา"),
                _doc("th-recovery-noise-b", "ตารางประชุมทีมถูกติดไว้ข้างห้องครัว"),
            ),
            _tiers(
                "th-recovery",
                (
                    "สเปกตรัมของควาซาร์มีเส้นฮีเลียมกี่เส้น",
                    "ความทรงจำไหนพูดถึงจักรยานสีเขียวที่ใช้เที่ยวอยุธยา",
                    "จักรยานสีเขียวถูกจอดไว้บริเวณไหน",
                ),
            ),
            ("th-recovery-target",),
        ),
        PhysicalExpansionCase(
            "physical-cross-lingual-recovery",
            (
                _doc(
                    "cross-recovery-target",
                    "A red umbrella was left beside platform three at Chiang Mai railway station.",
                ),
                _doc("cross-recovery-noise-a", "The server rack temperature log is archived monthly."),
                _doc("cross-recovery-noise-b", "The garden tools are stored beside the greenhouse."),
            ),
            _tiers(
                "cross-recovery",
                (
                    "How are neutrino detectors cooled underground?",
                    "ความทรงจำไหนพูดถึงร่มสีแดงที่สถานีรถไฟเชียงใหม่",
                    "Where was the red umbrella left at Chiang Mai station?",
                ),
            ),
            ("cross-recovery-target",),
        ),
        PhysicalExpansionCase(
            "physical-budget-truncation",
            tuple(
                _doc(
                    f"budget-{index:02d}",
                    f"Project launch status note {index}: security backup deployment readiness review.",
                )
                for index in range(12)
            ),
            _tiers(
                "budget",
                (
                    "project launch security backup deployment readiness status",
                    "launch readiness status security backup deployment review",
                    "project status for security backup and deployment readiness",
                ),
            ),
        ),
        PhysicalExpansionCase(
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
            _tiers(
                "somchai",
                (
                    "Where does Somchai work?",
                    "Which memories describe Somchai's workplace?",
                    "Find employment memories for Somchai.",
                ),
            ),
            ("somchai-a", "somchai-b"),
            initially_sufficient=True,
            ambiguity_expected=True,
        ),
        PhysicalExpansionCase(
            "physical-persistent-insufficient",
            (
                _doc("persist-garden", "The garden watering schedule is posted by the greenhouse."),
                _doc("persist-recipe", "The soup recipe uses pumpkin, onion, and ginger."),
                _doc("persist-bicycle", "The bicycle repair kit is under the workbench."),
            ),
            _tiers(
                "persist",
                (
                    "What is the password for the lunar research server?",
                    "Which helium emission line calibrates quasar spectroscopy?",
                    "What protocol cools a cryogenic neutrino detector?",
                ),
            ),
            persistent_insufficient=True,
        ),
    )


def validate_physical_fixture(cases):
    errors = []
    cases = tuple(cases)
    if not cases:
        return ["physical fixture must not be empty"]
    case_ids = [case.case_id for case in cases]
    if len(case_ids) != len(set(case_ids)):
        errors.append("case_id values must be unique")
    for case in cases:
        if not case.documents:
            errors.append(f"{case.case_id}: documents must not be empty")
        if len(case.cue_tiers) != 3:
            errors.append(f"{case.case_id}: exactly three cue tiers are required")
        if tuple(tier.tier_index for tier in case.cue_tiers) != (0, 1, 2):
            errors.append(f"{case.case_id}: cue tier indices must be 0,1,2")
        source_ids = [
            cue.source_cue_id
            for tier in case.cue_tiers
            for cue in tier.cues
        ]
        query_ids = [
            cue.query_id
            for tier in case.cue_tiers
            for cue in tier.cues
        ]
        if any(not tier.cues for tier in case.cue_tiers):
            errors.append(f"{case.case_id}: each cue tier must be nonempty")
        if len(source_ids) != len(set(source_ids)):
            errors.append(f"{case.case_id}: source_cue_id values must be unique")
        if len(query_ids) != len(set(query_ids)):
            errors.append(f"{case.case_id}: query_id values must be unique")
        memory_ids = {doc.memory.memory_id for doc in case.documents}
        if not set(case.required_memory_ids).issubset(memory_ids):
            errors.append(f"{case.case_id}: required_memory_ids must exist in documents")
    return errors


def _fixture_fingerprint(cases):
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
                "cue_tiers": [
                    {
                        "tier_index": tier.tier_index,
                        "cues": [
                            {
                                "source_cue_id": cue.source_cue_id,
                                "query_id": cue.query_id,
                                "query_text": cue.query_text,
                            }
                            for cue in tier.cues
                        ],
                    }
                    for tier in case.cue_tiers
                ],
                "required_memory_ids": list(case.required_memory_ids),
                "initially_sufficient": case.initially_sufficient,
                "ambiguity_expected": case.ambiguity_expected,
                "persistent_insufficient": case.persistent_insufficient,
            }
        )
    encoded = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _profile_payload(profile):
    return [
        {
            "round_index": scope.round_index,
            "enabled_cue_tier_count": scope.enabled_cue_tier_count,
            "top_k": scope.top_k,
            "max_memory_nodes": scope.budget.max_memory_nodes,
            "max_working_set_items": scope.budget.max_working_set_items,
        }
        for scope in profile.scopes
    ]


def _policy_payload(run, metrics, counters, deterministic):
    return {
        "selected_ids": [
            entry.ref_id for entry in run.final_result.working_set.entries
        ],
        "round_count": len(run.rounds),
        "termination_reason": run.termination_reason.value,
        "final_assessment": run.final_assessment.kind.value,
        "embedding_metrics": metrics,
        "retrieval_request_count": counters["retrieval_request_count"],
        "upstream_vectors_scored": counters["upstream_vectors_scored"],
        "a006_input_hits": counters["a006_input_hits"],
        "positive_candidates": counters["positive_candidates"],
        "active_candidates": counters["active_candidates"],
        "selected_items": counters["selected_items"],
        "deterministic_replay_match": deterministic,
        "rounds": [
            {
                "round_index": item.scope.round_index,
                "assessment": item.assessment.kind.value,
                "triggers": [trigger.value for trigger in item.assessment.triggers],
                "selected_ids": [
                    entry.ref_id
                    for entry in item.working_set_result.working_set.entries
                ],
                "retrieval_state": item.working_set_result.working_set.retrieval_state.value,
            }
            for item in run.rounds
        ],
    }


def _run_policy(index, recorder, case, profile, policy, threshold):
    before = recorder.snapshot()
    counters = {
        "retrieval_request_count": 0,
        "upstream_vectors_scored": 0,
        "a006_input_hits": 0,
        "positive_candidates": 0,
        "active_candidates": 0,
        "selected_items": 0,
    }
    scope_results = {}

    def evaluate(scope):
        cues = tuple(
            cue
            for tier in case.cue_tiers[: scope.enabled_cue_tier_count]
            for cue in tier.cues
        )
        evidence = []
        for cue in cues:
            result = index.search(
                VectorMemoryQuery(
                    cue.query_id,
                    cue.query_text,
                    top_k=scope.top_k,
                    minimum_similarity=threshold,
                )
            )
            evidence.append(
                SelectiveRetrievalEvidence(cue.source_cue_id, result)
            )
            counters["retrieval_request_count"] += 1
            counters["upstream_vectors_scored"] += result.scored_vector_count
        selected = select_single_best(tuple(evidence), budget=scope.budget)
        counters["a006_input_hits"] += selected.input_hit_count
        counters["positive_candidates"] += selected.positive_candidate_count
        counters["active_candidates"] += selected.activated_candidate_count
        counters["selected_items"] += selected.selected_count
        scope_results[scope.round_index] = selected
        return selected

    run = run_expansion_policy(
        profile,
        policy=policy,
        evaluate_scope=evaluate,
    )
    after = recorder.snapshot()
    metrics = _metrics_delta(before, after)

    replay = run_expansion_policy(
        profile,
        policy=policy,
        evaluate_scope=lambda scope: scope_results[scope.round_index],
    )
    deterministic = run == replay
    return _policy_payload(run, metrics, counters, deterministic)


def run_physical_case(
    adapter,
    case,
    *,
    profile,
    threshold,
    embedding_profile,
):
    errors = validate_physical_fixture((case,))
    if errors:
        raise ValueError("; ".join(errors))

    recorder = _RecordingEmbeddingAdapter(adapter)
    setup_before = recorder.snapshot()
    index = ExactVectorMemoryIndex(
        case.documents,
        recorder,
        embedding_profile=embedding_profile,
    )
    setup_after = recorder.snapshot()
    setup_metrics = _metrics_delta(setup_before, setup_after)

    policies = {}
    for policy in (
        ExpansionPolicy.NO_EXPANSION,
        ExpansionPolicy.SIGNAL_DRIVEN,
        ExpansionPolicy.ALWAYS_EXPAND,
    ):
        policies[policy.value] = _run_policy(
            index,
            recorder,
            case,
            profile,
            policy,
            threshold,
        )

    required = set(case.required_memory_ids)
    no_ids = set(policies["NO_EXPANSION"]["selected_ids"])
    signal_ids = set(policies["SIGNAL_DRIVEN"]["selected_ids"])
    always_ids = set(policies["ALWAYS_EXPAND"]["selected_ids"])
    no_covers = required.issubset(no_ids)
    signal_covers = required.issubset(signal_ids)
    recovered = bool(required) and (not no_covers) and signal_covers
    regressed = bool(required) and no_covers and not signal_covers
    ambiguity_preserved = (
        not case.ambiguity_expected or signal_ids == required
    )
    persistent_exhausted = (
        not case.persistent_insufficient
        or policies["SIGNAL_DRIVEN"]["termination_reason"]
        == ExpansionTerminationReason.CONTROLLER_EXHAUSTED.value
    )
    unnecessary = (
        case.initially_sufficient
        and policies["SIGNAL_DRIVEN"]["round_count"] > 1
    )
    deterministic = all(
        bool(payload["deterministic_replay_match"])
        for payload in policies.values()
    )

    return {
        "case_id": case.case_id,
        "required_memory_ids": list(case.required_memory_ids),
        "initially_sufficient": case.initially_sufficient,
        "ambiguity_expected": case.ambiguity_expected,
        "persistent_insufficient": case.persistent_insufficient,
        "setup_embedding_metrics": setup_metrics,
        "policies": policies,
        "no_expansion_required_count": len(required & no_ids),
        "signal_driven_required_count": len(required & signal_ids),
        "always_expand_required_count": len(required & always_ids),
        "signal_driven_recovered": recovered,
        "signal_driven_regressed": regressed,
        "signal_driven_unnecessary_expansion": unnecessary,
        "ambiguity_preserved": ambiguity_preserved,
        "persistent_exhausted": persistent_exhausted,
        "deterministic_repeat_match": deterministic,
    }


def classify_hypothesis_outcome(
    *,
    recovery_count,
    regression_count,
    signal_coverage,
    always_coverage,
    easy_unnecessary_expansion_count,
    persistent_exhaustion_complete,
    signal_rounds,
    always_rounds,
):
    if recovery_count <= 0:
        return "NOT_SUPPORTED"
    if (
        regression_count == 0
        and signal_coverage == always_coverage
        and easy_unnecessary_expansion_count == 0
        and persistent_exhaustion_complete
        and signal_rounds < always_rounds
    ):
        return "SUPPORTED"
    return "MIXED"


def run_physical_experiment(adapter):
    cases = build_physical_fixture()
    fixture_errors = validate_physical_fixture(cases)
    if fixture_errors:
        raise ValueError("; ".join(fixture_errors))
    profile = build_a007_primary_profile()

    results = tuple(
        run_physical_case(
            adapter,
            case,
            profile=profile,
            threshold=A005_THRESHOLD,
            embedding_profile=EMBEDDING_PROFILE,
        )
        for case in cases
    )

    total_required = sum(len(case.required_memory_ids) for case in cases)
    required_counts = {}
    for policy_name, field in (
        ("NO_EXPANSION", "no_expansion_required_count"),
        ("SIGNAL_DRIVEN", "signal_driven_required_count"),
        ("ALWAYS_EXPAND", "always_expand_required_count"),
    ):
        count = sum(int(result[field]) for result in results)
        required_counts[policy_name] = (
            count / total_required if total_required else 1.0
        )

    total_rounds = {
        policy.value: sum(
            int(result["policies"][policy.value]["round_count"])
            for result in results
        )
        for policy in ExpansionPolicy
    }
    setup_metrics = _sum_metrics(
        result["setup_embedding_metrics"] for result in results
    )
    policy_metrics = {
        policy.value: _sum_metrics(
            result["policies"][policy.value]["embedding_metrics"]
            for result in results
        )
        for policy in ExpansionPolicy
    }

    recovery_count = sum(
        int(result["signal_driven_recovered"]) for result in results
    )
    regression_count = sum(
        int(result["signal_driven_regressed"]) for result in results
    )
    easy_unnecessary = sum(
        int(result["signal_driven_unnecessary_expansion"])
        for result in results
    )
    persistent_expected = sum(
        int(case.persistent_insufficient) for case in cases
    )
    persistent_exhausted = sum(
        int(
            case.persistent_insufficient
            and result["persistent_exhausted"]
        )
        for case, result in zip(cases, results)
    )
    ambiguity_failures = sum(
        int(not result["ambiguity_preserved"]) for result in results
    )
    deterministic = all(
        bool(result["deterministic_repeat_match"])
        for result in results
    )

    outcome = classify_hypothesis_outcome(
        recovery_count=recovery_count,
        regression_count=regression_count,
        signal_coverage=required_counts["SIGNAL_DRIVEN"],
        always_coverage=required_counts["ALWAYS_EXPAND"],
        easy_unnecessary_expansion_count=easy_unnecessary,
        persistent_exhaustion_complete=(
            persistent_exhausted == persistent_expected
        ),
        signal_rounds=total_rounds["SIGNAL_DRIVEN"],
        always_rounds=total_rounds["ALWAYS_EXPAND"],
    )

    return {
        "fixture_version": FIXTURE_VERSION,
        "fixture_fingerprint": _fixture_fingerprint(cases),
        "case_ids": [case.case_id for case in cases],
        "selector": PRIMARY_SELECTOR,
        "threshold": A005_THRESHOLD,
        "profile": _profile_payload(profile),
        "required_memory_coverage": required_counts,
        "signal_driven_recovery_count": recovery_count,
        "signal_driven_regression_count": regression_count,
        "easy_unnecessary_expansion_count": easy_unnecessary,
        "persistent_insufficient_expected_count": persistent_expected,
        "persistent_insufficient_exhausted_count": persistent_exhausted,
        "ambiguity_failure_count": ambiguity_failures,
        "deterministic_repeat_match": deterministic,
        "total_rounds": total_rounds,
        "setup_embedding_metrics": setup_metrics,
        "policy_embedding_metrics": policy_metrics,
        "cases": list(results),
        "hypothesis_outcome": outcome,
        "experiment_valid": True,
    }


def _validate_metrics(name, metrics):
    errors = []
    if not isinstance(metrics, dict):
        return [f"{name} must be a metric object"]
    for key in _METRIC_KEYS:
        value = metrics.get(key)
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            errors.append(f"{name}.{key} must be a nonnegative integer")
    if errors:
        return errors

    requests = metrics["embedding_request_count"]
    inputs = metrics["embedding_input_count"]
    if requests == 0 and inputs != 0:
        errors.append(
            f"{name}.embedding_input_count must be 0 when "
            "embedding_request_count is 0"
        )
    if requests > 0 and inputs < requests:
        errors.append(
            f"{name}.embedding_input_count must be >= embedding_request_count"
        )

    observed_pairs = (
        (
            "prompt_tokens_observed_response_count",
            "prompt_tokens_total",
        ),
        (
            "total_duration_observed_response_count",
            "total_duration_ns_total",
        ),
        (
            "load_duration_observed_response_count",
            "load_duration_ns_total",
        ),
    )
    for observed_key, total_key in observed_pairs:
        observed = metrics[observed_key]
        if observed > requests:
            errors.append(
                f"{name}.{observed_key} must be <= embedding_request_count"
            )
        if observed == 0 and metrics[total_key] != 0:
            errors.append(
                f"{name}.{total_key} must be 0 when {observed_key} is 0"
            )
    return errors


def validate_physical_experiment(payload):
    errors = []
    cases = build_physical_fixture()
    profile = build_a007_primary_profile()
    if payload.get("fixture_version") != FIXTURE_VERSION:
        errors.append("fixture_version must match the frozen A007 fixture")
    if payload.get("fixture_fingerprint") != EXPECTED_FIXTURE_FINGERPRINT:
        errors.append("fixture_fingerprint must match the frozen A007 fixture")
    if tuple(payload.get("case_ids", ())) != tuple(
        case.case_id for case in cases
    ):
        errors.append("case_ids must match the frozen A007 fixture")
    if payload.get("selector") != PRIMARY_SELECTOR:
        errors.append("selector must remain SINGLE_BEST")
    if payload.get("threshold") != A005_THRESHOLD:
        errors.append("threshold must remain the frozen A005 value")
    if payload.get("profile") != _profile_payload(profile):
        errors.append("profile must match the frozen A007 expansion ladder")
    if payload.get("ambiguity_failure_count") != 0:
        errors.append("ambiguity failure count must be 0")
    expected_persistent = sum(
        int(case.persistent_insufficient) for case in cases
    )
    if payload.get("persistent_insufficient_expected_count") != expected_persistent:
        errors.append("persistent expected count must match fixture")
    if payload.get("persistent_insufficient_exhausted_count") != expected_persistent:
        errors.append("persistent-insufficient cases must exhaust")
    if payload.get("deterministic_repeat_match") is not True:
        errors.append("deterministic logical replay must match")

    errors.extend(
        _validate_metrics(
            "setup_embedding_metrics",
            payload.get("setup_embedding_metrics"),
        )
    )
    policy_metrics = payload.get("policy_embedding_metrics")
    if not isinstance(policy_metrics, dict):
        errors.append("policy_embedding_metrics must be present")
    else:
        for policy in ExpansionPolicy:
            errors.extend(
                _validate_metrics(
                    f"policy_embedding_metrics.{policy.value}",
                    policy_metrics.get(policy.value),
                )
            )

    declared_outcome = payload.get("hypothesis_outcome")
    if declared_outcome not in {
        "SUPPORTED",
        "MIXED",
        "NOT_SUPPORTED",
    }:
        errors.append("hypothesis_outcome must be SUPPORTED, MIXED, or NOT_SUPPORTED")

    coverage = payload.get("required_memory_coverage")
    coverage_valid = isinstance(coverage, dict)
    if not coverage_valid:
        errors.append("required_memory_coverage must be a policy coverage object")
    else:
        for policy in ExpansionPolicy:
            value = coverage.get(policy.value)
            if (
                not isinstance(value, (int, float))
                or isinstance(value, bool)
                or not 0.0 <= float(value) <= 1.0
            ):
                coverage_valid = False
                errors.append(
                    f"required_memory_coverage.{policy.value} must be within [0, 1]"
                )

    count_fields = (
        "signal_driven_recovery_count",
        "signal_driven_regression_count",
        "easy_unnecessary_expansion_count",
        "persistent_insufficient_expected_count",
        "persistent_insufficient_exhausted_count",
    )
    counts_valid = True
    for field in count_fields:
        value = payload.get(field)
        if (
            not isinstance(value, int)
            or isinstance(value, bool)
            or value < 0
        ):
            counts_valid = False
            errors.append(f"{field} must be a nonnegative integer")

    total_rounds = payload.get("total_rounds")
    rounds_valid = isinstance(total_rounds, dict)
    if not rounds_valid:
        errors.append("total_rounds must be a policy round-count object")
    else:
        for policy in ExpansionPolicy:
            value = total_rounds.get(policy.value)
            if (
                not isinstance(value, int)
                or isinstance(value, bool)
                or value < 0
            ):
                rounds_valid = False
                errors.append(
                    f"total_rounds.{policy.value} must be a nonnegative integer"
                )

    if counts_valid:
        persistent_expected = payload["persistent_insufficient_expected_count"]
        persistent_exhausted = payload["persistent_insufficient_exhausted_count"]
        if persistent_exhausted > persistent_expected:
            counts_valid = False
            errors.append(
                "persistent_insufficient_exhausted_count must not exceed "
                "persistent_insufficient_expected_count"
            )

    if (
        declared_outcome in {"SUPPORTED", "MIXED", "NOT_SUPPORTED"}
        and coverage_valid
        and counts_valid
        and rounds_valid
    ):
        expected_outcome = classify_hypothesis_outcome(
            recovery_count=payload["signal_driven_recovery_count"],
            regression_count=payload["signal_driven_regression_count"],
            signal_coverage=float(coverage["SIGNAL_DRIVEN"]),
            always_coverage=float(coverage["ALWAYS_EXPAND"]),
            easy_unnecessary_expansion_count=(
                payload["easy_unnecessary_expansion_count"]
            ),
            persistent_exhaustion_complete=(
                payload["persistent_insufficient_exhausted_count"]
                == payload["persistent_insufficient_expected_count"]
            ),
            signal_rounds=total_rounds["SIGNAL_DRIVEN"],
            always_rounds=total_rounds["ALWAYS_EXPAND"],
        )
        if declared_outcome != expected_outcome:
            errors.append(
                "hypothesis_outcome is inconsistent with frozen aggregate "
                f"evidence; expected {expected_outcome}"
            )
    return errors


def validate_descriptor(descriptor):
    errors = []
    if descriptor.backend_name != "ollama":
        errors.append("backend name must be ollama")
    if descriptor.model_name != MODEL_NAME:
        errors.append(f"model name must be {MODEL_NAME}")
    if descriptor.model_digest != EXPECTED_DIGEST:
        errors.append("model digest must match the pinned A007/A005 digest")
    if descriptor.embedding_dimension != EXPECTED_DIMENSION:
        errors.append(f"embedding dimension must be {EXPECTED_DIMENSION}")
    if "embedding" not in descriptor.capabilities:
        errors.append("capabilities must include embedding")
    return errors


def _descriptor_payload(descriptor):
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


def _base_payload(*, descriptor, experiment_valid, errors):
    return {
        "qualification_scope": "local_physical_uncertainty_expansion_a007",
        "experiment_valid": experiment_valid,
        "errors": errors,
        "profile_name": PROFILE_NAME,
        "embedding_profile": EMBEDDING_PROFILE,
        "frozen_profile": {
            "model": MODEL_NAME,
            "digest": EXPECTED_DIGEST,
            "embedding_dimension": EXPECTED_DIMENSION,
            "threshold": A005_THRESHOLD,
            "selector": PRIMARY_SELECTOR,
            "scopes": _profile_payload(build_a007_primary_profile()),
        },
        "model": (
            _descriptor_payload(descriptor)
            if descriptor is not None
            else {"name": MODEL_NAME}
        ),
    }


def _emit(payload, output_path):
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


def main(argv=None):
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
            errors=["A007 physical model identity arguments must match frozen profile"],
        )
        _emit(payload, args.output)
        return 1

    descriptor = None
    try:
        adapter = OllamaEmbeddingAdapter(
            args.model,
            base_url=args.base_url,
            expected_digest=args.expected_digest,
            expected_dimension=args.expected_dimension,
            timeout_seconds=args.timeout_seconds,
        )
        descriptor = adapter.inspect()
        descriptor_errors = validate_descriptor(descriptor)
        if descriptor_errors:
            payload = _base_payload(
                descriptor=descriptor,
                experiment_valid=False,
                errors=descriptor_errors,
            )
            _emit(payload, args.output)
            return 1

        experiment = run_physical_experiment(adapter)
        experiment_errors = validate_physical_experiment(experiment)
        if experiment_errors:
            payload = _base_payload(
                descriptor=descriptor,
                experiment_valid=False,
                errors=experiment_errors,
            )
            payload.update(experiment)
            payload["experiment_valid"] = False
            payload["errors"] = experiment_errors
            _emit(payload, args.output)
            return 1

        payload = _base_payload(
            descriptor=descriptor,
            experiment_valid=True,
            errors=[],
        )
        payload.update(experiment)
        _emit(payload, args.output)
        return 0
    except (EmbeddingAdapterError, ValueError, KeyError) as exc:
        payload = _base_payload(
            descriptor=descriptor,
            experiment_valid=False,
            errors=[str(exc)],
        )
        _emit(payload, args.output)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())