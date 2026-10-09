from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import json
import math

from flywire_asca.contracts import MemoryKind, MemoryRecord, dumps_contract
from flywire_asca.contracts.validation import require_nonempty
from flywire_asca.embedding import EmbeddingAdapter

from .index import ExactVectorMemoryIndex
from .models import VectorMemoryDocument, VectorMemoryQuery


class GraphDecision(str, Enum):
    VECTOR_SUFFICIENT = "VECTOR_SUFFICIENT"
    VECTOR_NEEDS_INDEX_OR_METADATA = "VECTOR_NEEDS_INDEX_OR_METADATA"
    GRAPH_JUSTIFIED = "GRAPH_JUSTIFIED"


@dataclass(frozen=True, slots=True)
class VectorMemoryBenchmarkCase:
    case_id: str
    query: VectorMemoryQuery
    relevant_memory_ids: tuple[str, ...]
    require_recall_at_1: bool = True
    ambiguity_expected: bool = False
    metadata_filter_expected: bool = False
    relation_semantic_required: bool = False
    expected_ranked_ids: tuple[str, ...] = ()
    max_scored_vectors: int | None = None

    def __post_init__(self) -> None:
        require_nonempty("case_id", self.case_id)
        if not isinstance(self.query, VectorMemoryQuery):
            raise ValueError("query must be a VectorMemoryQuery")
        canonical = tuple(sorted(set(self.relevant_memory_ids)))
        if canonical != self.relevant_memory_ids:
            raise ValueError("relevant_memory_ids must be sorted and unique")
        if self.expected_ranked_ids:
            if len(set(self.expected_ranked_ids)) != len(self.expected_ranked_ids):
                raise ValueError("expected_ranked_ids must be unique")
            if set(self.expected_ranked_ids) != set(self.relevant_memory_ids):
                raise ValueError(
                    "expected_ranked_ids must contain exactly relevant_memory_ids"
                )
        if self.ambiguity_expected and len(self.relevant_memory_ids) < 2:
            raise ValueError(
                "ambiguity_expected requires at least two relevant memories"
            )
        if self.max_scored_vectors is not None and (
            not isinstance(self.max_scored_vectors, int)
            or isinstance(self.max_scored_vectors, bool)
            or self.max_scored_vectors < 0
        ):
            raise ValueError("max_scored_vectors must be nonnegative or None")


@dataclass(frozen=True, slots=True)
class VectorMemoryBenchmarkCaseResult:
    case_id: str
    returned_memory_ids: tuple[str, ...]
    relevant_memory_ids: tuple[str, ...]
    recall_at_1: float | None
    recall_at_k: float | None
    reciprocal_rank: float | None
    no_hit_correct: bool | None
    metadata_filter_correct: bool | None
    false_retrieval_count: int
    ambiguity_preserved: bool
    relation_semantic_failure: bool
    scalability_warning: bool
    stored_count: int
    metadata_eligible_count: int
    scored_vector_count: int
    above_threshold_count: int
    returned_count: int


@dataclass(frozen=True, slots=True)
class VectorMemoryBenchmarkReport:
    scope: str
    frozen_threshold: float
    threshold_origin: str
    case_results: tuple[VectorMemoryBenchmarkCaseResult, ...]
    case_count: int
    recall_at_1: float
    recall_at_k: float
    mean_reciprocal_rank: float
    no_hit_correctness: float
    metadata_filter_correctness: float
    false_retrieval_count: int
    ambiguity_failure_count: int
    relation_semantic_failure_count: int
    scalability_warning_count: int
    stored_memory_count: int
    vector_scored_total: int
    embedding_request_count: int
    embedding_input_count: int
    embedding_model_name: str
    embedding_model_digest: str | None
    embedding_profile: str

    def __post_init__(self) -> None:
        require_nonempty("scope", self.scope)
        require_nonempty("threshold_origin", self.threshold_origin)
        require_nonempty("embedding_model_name", self.embedding_model_name)
        require_nonempty("embedding_profile", self.embedding_profile)
        if self.embedding_model_digest is not None:
            require_nonempty("embedding_model_digest", self.embedding_model_digest)
        if not math.isfinite(self.frozen_threshold) or not -1 <= self.frozen_threshold <= 1:
            raise ValueError("frozen_threshold must be finite and within [-1, 1]")
        if self.case_count != len(self.case_results):
            raise ValueError("case_count must equal len(case_results)")
        for name in (
            "recall_at_1",
            "recall_at_k",
            "mean_reciprocal_rank",
            "no_hit_correctness",
            "metadata_filter_correctness",
        ):
            value = getattr(self, name)
            if not math.isfinite(value) or not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} must be finite and within [0, 1]")
        for name in (
            "false_retrieval_count",
            "ambiguity_failure_count",
            "relation_semantic_failure_count",
            "scalability_warning_count",
            "stored_memory_count",
            "vector_scored_total",
            "embedding_request_count",
            "embedding_input_count",
        ):
            value = getattr(self, name)
            if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                raise ValueError(f"{name} must be a nonnegative integer")


@dataclass(frozen=True, slots=True)
class PortableVectorMemoryFixture:
    documents: tuple[VectorMemoryDocument, ...]
    cases: tuple[VectorMemoryBenchmarkCase, ...]
    embedding_vectors: tuple[tuple[str, tuple[float, ...]], ...]
    embedding_profile: str
    frozen_threshold: float | None = None
    threshold_origin: str = "portable_calibration"


def _memory(
    memory_id: str,
    text: str,
    *,
    confidence: float = 0.8,
    kind: MemoryKind = MemoryKind.SEMANTIC,
    evidence_ids: tuple[str, ...] = (),
    entity_ids: tuple[str, ...] = (),
    context_tags: tuple[str, ...] = (),
    source_tags: tuple[str, ...] = (),
) -> VectorMemoryDocument:
    return VectorMemoryDocument(
        MemoryRecord(
            memory_id,
            kind,
            f"content:{memory_id}",
            confidence,
            evidence_ids,
        ),
        text,
        entity_ids,
        context_tags,
        source_tags,
    )


def _basis(index: int, dimension: int = 8) -> tuple[float, ...]:
    return tuple(1.0 if offset == index else 0.0 for offset in range(dimension))


def _negative_all(dimension: int = 8) -> tuple[float, ...]:
    value = -1.0 / math.sqrt(dimension)
    return tuple(value for _ in range(dimension))


def _positive_all(dimension: int = 8) -> tuple[float, ...]:
    value = 1.0 / math.sqrt(dimension)
    return tuple(value for _ in range(dimension))


def build_a005_portable_calibration_fixture() -> PortableVectorMemoryFixture:
    documents = (
        _memory("cal-car", "calibration car memory"),
        _memory("cal-cat", "calibration cat memory"),
        _memory("cal-distractor", "calibration unrelated memory"),
    )
    cases = (
        VectorMemoryBenchmarkCase(
            "cal-query-car",
            VectorMemoryQuery(
                "cal-query-car",
                "calibration car query",
                top_k=3,
                minimum_similarity=-1.0,
            ),
            ("cal-car",),
        ),
        VectorMemoryBenchmarkCase(
            "cal-query-cat",
            VectorMemoryQuery(
                "cal-query-cat",
                "calibration cat query",
                top_k=3,
                minimum_similarity=-1.0,
            ),
            ("cal-cat",),
        ),
    )
    vectors = (
        ("calibration car memory", _basis(0)),
        ("calibration cat memory", _basis(1)),
        ("calibration unrelated memory", _basis(2)),
        ("calibration car query", _basis(0)),
        ("calibration cat query", _basis(1)),
    )
    return PortableVectorMemoryFixture(
        documents,
        cases,
        vectors,
        "a005-portable-calibration-v1",
    )


def calibrate_a005_threshold(
    documents: tuple[VectorMemoryDocument, ...],
    adapter: EmbeddingAdapter,
    cases: tuple[VectorMemoryBenchmarkCase, ...],
    *,
    embedding_profile: str,
) -> float:
    if not documents or not cases:
        raise ValueError("calibration requires documents and cases")
    index = ExactVectorMemoryIndex(
        documents,
        adapter,
        embedding_profile=embedding_profile,
    )
    relevant_scores: list[float] = []
    irrelevant_scores: list[float] = []
    for case in cases:
        wide_query = VectorMemoryQuery(
            query_id=case.query.query_id,
            query_text=case.query.query_text,
            top_k=len(documents),
            minimum_similarity=-1.0,
            allowed_memory_kinds=case.query.allowed_memory_kinds,
            required_entity_ids=case.query.required_entity_ids,
            required_context_tags=case.query.required_context_tags,
            required_source_tags=case.query.required_source_tags,
        )
        result = index.search(wide_query)
        relevant = set(case.relevant_memory_ids)
        for hit in result.hits:
            if hit.memory_id in relevant:
                relevant_scores.append(hit.similarity)
            else:
                irrelevant_scores.append(hit.similarity)
    if not relevant_scores or not irrelevant_scores:
        raise ValueError(
            "calibration requires both relevant and irrelevant score samples"
        )
    min_relevant = min(relevant_scores)
    max_irrelevant = max(irrelevant_scores)
    if min_relevant > max_irrelevant:
        return (min_relevant + max_irrelevant) / 2.0

    scores = sorted(set(relevant_scores + irrelevant_scores))
    candidates = {-1.0, 1.0}
    candidates.update(scores)
    candidates.update(
        (left + right) / 2.0
        for left, right in zip(scores, scores[1:])
    )
    best: tuple[int, float] | None = None
    for threshold in sorted(candidates):
        errors = sum(score < threshold for score in relevant_scores)
        errors += sum(score >= threshold for score in irrelevant_scores)
        candidate = (errors, -threshold)
        if best is None or candidate < best:
            best = candidate
    assert best is not None
    threshold = -best[1]
    return max(-1.0, min(1.0, threshold))


def build_a005_portable_qualification_fixture(
    *,
    frozen_threshold: float,
) -> PortableVectorMemoryFixture:
    if not math.isfinite(frozen_threshold) or not -1 <= frozen_threshold <= 1:
        raise ValueError("frozen_threshold must be finite and within [-1, 1]")

    core = [
        _memory("mem-car-trip", "I drove a Toyota Corolla to Chiang Mai."),
        _memory("mem-thai-cat", "แมวสีขาวชอบนอนบนโซฟา"),
        _memory("mem-english-office", "Alice works at the riverside office."),
        _memory("mem-thai-coffee", "ร้านกาแฟอยู่ข้างสถานีรถไฟ"),
        _memory("mem-exact-blue", "BLUE code"),
        _memory(
            "somchai-a",
            "Somchai works at company A.",
            entity_ids=("person-a",),
        ),
        _memory(
            "somchai-b",
            "Somchai works at company B.",
            entity_ids=("person-b",),
        ),
        _memory(
            "context-office",
            "Project status was discussed.",
            context_tags=("office",),
        ),
        _memory(
            "context-home",
            "Project status was discussed.",
            context_tags=("home",),
        ),
        _memory(
            "mem-low-confidence",
            "The prototype uses a ceramic housing.",
            confidence=0.2,
            evidence_ids=("e-low",),
        ),
        _memory(
            "mem-high-confidence",
            "The weather note says the sky is clear.",
            confidence=0.99,
            evidence_ids=("e-high",),
        ),
    ]
    for index in range(256):
        core.append(
            _memory(
                f"distractor-{index:03d}",
                f"unrelated distractor memory {index:03d}",
            )
        )

    vectors: list[tuple[str, tuple[float, ...]]] = [
        ("I drove a Toyota Corolla to Chiang Mai.", _basis(0)),
        ("แมวสีขาวชอบนอนบนโซฟา", _basis(1)),
        ("Alice works at the riverside office.", _basis(2)),
        ("ร้านกาแฟอยู่ข้างสถานีรถไฟ", _basis(3)),
        ("BLUE code", _basis(4)),
        ("Somchai works at company A.", _basis(5)),
        ("Somchai works at company B.", _basis(5)),
        ("Project status was discussed.", _basis(6)),
        ("The prototype uses a ceramic housing.", _basis(7)),
        ("The weather note says the sky is clear.", _negative_all()),
    ]
    for index in range(256):
        vectors.append(
            (f"unrelated distractor memory {index:03d}", _negative_all())
        )

    query_vectors = (
        ("Which car did I take to northern Thailand?", _basis(0)),
        ("สัตว์เลี้ยงสีขาวชอบนอนที่ไหน", _basis(1)),
        ("อลิซทำงานที่สำนักงานไหน", _basis(2)),
        ("Where is the coffee shop near the station?", _basis(3)),
        ("BLUE code", _basis(4)),
        ("Somchai works where?", _basis(5)),
        ("Which Somchai works at company B?", _basis(5)),
        ("What project status was discussed at the office?", _basis(6)),
        ("What material does the prototype housing use?", _basis(7)),
        ("Find the remembered car trip among distractors.", _basis(0)),
        ("This query should have no sufficiently similar memory.", _positive_all()),
        ("Tie-order Somchai query", _basis(5)),
    )
    vectors.extend(query_vectors)

    def query(
        case_id: str,
        text: str,
        relevant: tuple[str, ...],
        *,
        top_k: int = 1,
        recall1: bool = True,
        ambiguity: bool = False,
        metadata: bool = False,
        entity_ids: tuple[str, ...] = (),
        context_tags: tuple[str, ...] = (),
        ranked: tuple[str, ...] = (),
    ) -> VectorMemoryBenchmarkCase:
        return VectorMemoryBenchmarkCase(
            case_id,
            VectorMemoryQuery(
                case_id,
                text,
                top_k=top_k,
                minimum_similarity=frozen_threshold,
                required_entity_ids=entity_ids,
                required_context_tags=context_tags,
            ),
            relevant,
            require_recall_at_1=recall1,
            ambiguity_expected=ambiguity,
            metadata_filter_expected=metadata,
            expected_ranked_ids=ranked,
        )

    cases = (
        query(
            "english-paraphrase",
            "Which car did I take to northern Thailand?",
            ("mem-car-trip",),
        ),
        query(
            "thai-paraphrase",
            "สัตว์เลี้ยงสีขาวชอบนอนที่ไหน",
            ("mem-thai-cat",),
        ),
        query(
            "thai-to-english",
            "อลิซทำงานที่สำนักงานไหน",
            ("mem-english-office",),
        ),
        query(
            "english-to-thai",
            "Where is the coffee shop near the station?",
            ("mem-thai-coffee",),
        ),
        query("exact-wording", "BLUE code", ("mem-exact-blue",)),
        query(
            "same-name-ambiguity",
            "Somchai works where?",
            ("somchai-a", "somchai-b"),
            top_k=2,
            recall1=False,
            ambiguity=True,
            ranked=("somchai-a", "somchai-b"),
        ),
        query(
            "entity-filter",
            "Which Somchai works at company B?",
            ("somchai-b",),
            metadata=True,
            entity_ids=("person-b",),
        ),
        query(
            "context-filter",
            "What project status was discussed at the office?",
            ("context-office",),
            metadata=True,
            context_tags=("office",),
        ),
        query(
            "confidence-independence",
            "What material does the prototype housing use?",
            ("mem-low-confidence",),
        ),
        query(
            "distractor-corpus",
            "Find the remembered car trip among distractors.",
            ("mem-car-trip",),
        ),
        query(
            "threshold-no-hit",
            "This query should have no sufficiently similar memory.",
            (),
            recall1=False,
        ),
        query(
            "tie-order",
            "Tie-order Somchai query",
            ("somchai-a", "somchai-b"),
            top_k=2,
            recall1=False,
            ranked=("somchai-a", "somchai-b"),
        ),
    )
    return PortableVectorMemoryFixture(
        tuple(core),
        cases,
        tuple(vectors),
        "a005-portable-qualification-v1",
        frozen_threshold,
        "portable_fake_geometry_only",
    )


def run_vector_memory_benchmark(
    documents: tuple[VectorMemoryDocument, ...],
    adapter: EmbeddingAdapter,
    cases: tuple[VectorMemoryBenchmarkCase, ...],
    *,
    embedding_profile: str,
    frozen_threshold: float,
    threshold_origin: str,
) -> VectorMemoryBenchmarkReport:
    require_nonempty("threshold_origin", threshold_origin)
    index = ExactVectorMemoryIndex(
        documents,
        adapter,
        embedding_profile=embedding_profile,
    )
    results: list[VectorMemoryBenchmarkCaseResult] = []
    recall1_values: list[float] = []
    recallk_values: list[float] = []
    rr_values: list[float] = []
    no_hit_values: list[float] = []
    metadata_values: list[float] = []

    for case in cases:
        if case.query.minimum_similarity != frozen_threshold:
            raise ValueError(
                "benchmark query threshold must equal frozen_threshold"
            )
        result = index.search(case.query)
        returned = tuple(hit.memory_id for hit in result.hits)
        relevant = set(case.relevant_memory_ids)

        recall1: float | None = None
        recallk: float | None = None
        rr: float | None = None
        if relevant:
            if case.require_recall_at_1:
                recall1 = 1.0 if returned and returned[0] in relevant else 0.0
                recall1_values.append(recall1)
            found = len(relevant.intersection(returned))
            recallk = found / len(relevant)
            recallk_values.append(recallk)
            first_rank = next(
                (index + 1 for index, item in enumerate(returned) if item in relevant),
                None,
            )
            rr = 0.0 if first_rank is None else 1.0 / first_rank
            rr_values.append(rr)

        no_hit_correct: bool | None = None
        if not relevant:
            no_hit_correct = not returned
            no_hit_values.append(1.0 if no_hit_correct else 0.0)

        false_count = sum(item not in relevant for item in returned)
        metadata_correct: bool | None = None
        if case.metadata_filter_expected:
            metadata_correct = set(returned) == relevant and false_count == 0
            metadata_values.append(1.0 if metadata_correct else 0.0)

        ambiguity_preserved = True
        if case.ambiguity_expected:
            ambiguity_preserved = set(returned) == relevant
        if case.expected_ranked_ids:
            ambiguity_preserved = (
                ambiguity_preserved
                and returned[: len(case.expected_ranked_ids)]
                == case.expected_ranked_ids
            )

        relation_failure = bool(
            case.relation_semantic_required
            and (recallk is None or recallk != 1.0)
        )
        scalability_warning = bool(
            case.max_scored_vectors is not None
            and result.scored_vector_count > case.max_scored_vectors
        )
        results.append(
            VectorMemoryBenchmarkCaseResult(
                case_id=case.case_id,
                returned_memory_ids=returned,
                relevant_memory_ids=case.relevant_memory_ids,
                recall_at_1=recall1,
                recall_at_k=recallk,
                reciprocal_rank=rr,
                no_hit_correct=no_hit_correct,
                metadata_filter_correct=metadata_correct,
                false_retrieval_count=false_count,
                ambiguity_preserved=ambiguity_preserved,
                relation_semantic_failure=relation_failure,
                scalability_warning=scalability_warning,
                stored_count=result.stored_count,
                metadata_eligible_count=result.metadata_eligible_count,
                scored_vector_count=result.scored_vector_count,
                above_threshold_count=result.above_threshold_count,
                returned_count=result.returned_count,
            )
        )

    def average(values: list[float]) -> float:
        return sum(values) / len(values) if values else 1.0

    descriptor = adapter.inspect()
    return VectorMemoryBenchmarkReport(
        scope="controlled_fixture_only",
        frozen_threshold=frozen_threshold,
        threshold_origin=threshold_origin,
        case_results=tuple(results),
        case_count=len(results),
        recall_at_1=average(recall1_values),
        recall_at_k=average(recallk_values),
        mean_reciprocal_rank=average(rr_values),
        no_hit_correctness=average(no_hit_values),
        metadata_filter_correctness=average(metadata_values),
        false_retrieval_count=sum(r.false_retrieval_count for r in results),
        ambiguity_failure_count=sum(not r.ambiguity_preserved for r in results),
        relation_semantic_failure_count=sum(
            r.relation_semantic_failure for r in results
        ),
        scalability_warning_count=sum(r.scalability_warning for r in results),
        stored_memory_count=len(documents),
        vector_scored_total=sum(r.scored_vector_count for r in results),
        embedding_request_count=(1 if documents else 0) + len(cases),
        embedding_input_count=len(documents) + len(cases),
        embedding_model_name=descriptor.model_name,
        embedding_model_digest=descriptor.model_digest,
        embedding_profile=embedding_profile,
    )


def qualify_a005_report(report: VectorMemoryBenchmarkReport) -> list[str]:
    errors: list[str] = []
    if report.scope != "controlled_fixture_only":
        errors.append('scope must be "controlled_fixture_only"')
    if report.recall_at_1 != 1.0:
        errors.append("recall_at_1 must be 1.0")
    if report.recall_at_k != 1.0:
        errors.append("recall_at_k must be 1.0")
    if report.mean_reciprocal_rank != 1.0:
        errors.append("mean_reciprocal_rank must be 1.0")
    if report.no_hit_correctness != 1.0:
        errors.append("no_hit_correctness must be 1.0")
    if report.metadata_filter_correctness != 1.0:
        errors.append("metadata_filter_correctness must be 1.0")
    if report.false_retrieval_count != 0:
        errors.append("false_retrieval_count must be 0")
    if report.ambiguity_failure_count != 0:
        errors.append("ambiguity_failure_count must be 0")
    return errors


def decide_graph_need(report: VectorMemoryBenchmarkReport) -> GraphDecision:
    if report.relation_semantic_failure_count > 0:
        return GraphDecision.GRAPH_JUSTIFIED
    if (
        qualify_a005_report(report)
        or report.scalability_warning_count > 0
    ):
        return GraphDecision.VECTOR_NEEDS_INDEX_OR_METADATA
    return GraphDecision.VECTOR_SUFFICIENT


def benchmark_report_payload(
    report: VectorMemoryBenchmarkReport,
) -> dict[str, object]:
    return json.loads(dumps_contract(report))
