from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from collections.abc import Iterable

from flywire_asca.contracts import (
    AssociationEdge,
    MemoryKind,
    MemoryRecord,
    RelationType,
)
from flywire_asca.embedding import (
    EmbeddingDescriptor,
    EmbeddingResponse,
    normalize_embedding_values,
)
from flywire_asca.vector_memory import (
    ExactVectorMemoryIndex,
    VectorMemoryDocument,
    VectorMemoryQuery,
)

from .index import BoundedRelationIndex
from .models import (
    ArchitectureDecision,
    ComparisonVariant,
    TraversalRequest,
    TraversalTermination,
)


EXPECTED_A012_CASE_IDS = (
    "ownership-workplace-one-hop",
    "causal-one-hop",
    "temporal-one-hop",
    "part-of-two-hop",
    "used-for-one-hop",
    "same-name-disambiguated-ownership",
    "vector-direct-control",
    "cycle-control",
    "low-confidence-edge-control",
    "relation-allowlist-control",
    "missing-target-control",
    "invalid-contract-control",
)


EXPECTED_A012_FIXTURE_FINGERPRINT = "dcabd86117f22e35c18fe605c8411da143962f112645a78c9124ec5987179aea"

EXPECTED_A012_SHARED_INPUT_FINGERPRINTS = (
    ("ownership-workplace-one-hop", "0ac54245cfe712dccbb5800b8619b39b9becafe1828df11f0946102a93121e31"),
    ("causal-one-hop", "15c1629453700e32cd8963e98ecff81b3bb6d57a9650e2de2bf9fb5da2614c4f"),
    ("temporal-one-hop", "b68e9dfe5747e7dca19245631039454d9f2eb6e9810fc080c1bd4986cf47470f"),
    ("part-of-two-hop", "867192b220e46e5b06ed0ef475a20d63cf520792e5ebab827589d02e71ac8fd4"),
    ("used-for-one-hop", "e5323020884690c263fd1afefe6e6ed86cb60805e207992e1a2f84900802b585"),
    ("same-name-disambiguated-ownership", "a0fa9785b470bedf98cf24165d5e8e7e96b8aeacad8e68b4eeaebb358650f771"),
    ("vector-direct-control", "1c3b46a2cbfd2990836a131725115beea57219e609d27564ffda614cbaa240a6"),
    ("cycle-control", "20708028c323b7a445b2aa1905eef62967d0f84246b40f97d6769272721da969"),
    ("low-confidence-edge-control", "019525da2c53d220cd9feacec2e06ab004d65e6d2d7e54c24ec39266a6757668"),
    ("relation-allowlist-control", "8486178e745a405d634feab30ac200b9d7bd3701505ae70c0d680384fcc49afa"),
    ("missing-target-control", "ea23f43965fb38582cbdc9ac6260514dcd383476a499681b0fcbf06681f8091e"),
    ("invalid-contract-control", "00c8b114cdcf056d3d47998a98afb70d9c73eb3b67ac779836219e8d351dfc9f"),
)


@dataclass(frozen=True, slots=True)
class RelationalMemorySpec:
    memory_id: str
    retrieval_text: str
    vector: tuple[float, ...]
    entity_ids: tuple[str, ...] = ()
    evidence_ids: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class RelationalBenchmarkCase:
    case_id: str
    memories: tuple[RelationalMemorySpec, ...]
    edges: tuple[AssociationEdge, ...]
    query_text: str
    query_vector: tuple[float, ...]
    target_memory_ids: tuple[str, ...]
    allowed_relations: tuple[RelationType, ...]
    expected_found: bool
    relation_dependent: bool
    required_entity_ids: tuple[str, ...] = ()
    forbidden_identity_ids: tuple[str, ...] = ()
    max_hops: int = 3
    max_visited_nodes: int = 8
    max_scanned_edges: int = 32
    minimum_proposition_confidence: float = 0.5
    minimum_similarity: float = 0.9
    top_k: int = 1


@dataclass(frozen=True, slots=True)
class RelationalVariantResult:
    variant: ComparisonVariant
    task_success: bool
    expected_found: bool
    found_target_ids: tuple[str, ...]
    initially_retrieved_ids: tuple[str, ...]
    final_selected_ids: tuple[str, ...]
    vector_query_count: int
    vector_scored_count: int
    relation_scanned_edge_count: int
    relation_hop_count: int
    relation_termination: TraversalTermination | None
    relation_path_edge_ids: tuple[tuple[str, ...], ...]
    relation_path_memory_ids: tuple[tuple[str, ...], ...]
    relation_path_evidence_ids: tuple[tuple[str, ...], ...]
    identity_preserved: bool
    provenance_complete: bool
    false_target_count: int


@dataclass(frozen=True, slots=True)
class RelationalBenchmarkCaseResult:
    case_id: str
    shared_input_fingerprint: str
    relation_dependent: bool
    validation_error_observed: bool
    validation_error: str | None
    runs: tuple[RelationalVariantResult, ...]


@dataclass(frozen=True, slots=True)
class RelationalBenchmarkReport:
    fixture_fingerprint: str
    case_results: tuple[RelationalBenchmarkCaseResult, ...]
    case_count: int
    valid_case_count: int
    invalid_case_count: int
    primary_relation_case_count: int
    vector_success_count: int
    relation_success_count: int
    shared_success_count: int
    relation_only_recovery_count: int
    vector_only_success_count: int
    regression_count: int
    identity_failure_count: int
    provenance_failure_count: int
    budget_violation_count: int
    duplicate_visit_failure_count: int
    vector_query_count: int
    vector_scored_count: int
    relation_scanned_edge_count: int
    deterministic_repeat_match: bool


_A = (1.0, 0.0, 0.0)
_B = (0.0, 1.0, 0.0)
_C = (0.0, 0.0, 1.0)


class _FixtureEmbeddingAdapter:
    def __init__(self, vectors: dict[str, tuple[float, ...]]) -> None:
        self._vectors = dict(vectors)
        dimensions = {len(value) for value in self._vectors.values()}
        if len(dimensions) != 1:
            raise ValueError("fixture vectors must have one dimension")
        self._dimension = next(iter(dimensions))

    def inspect(self) -> EmbeddingDescriptor:
        return EmbeddingDescriptor(
            backend_name="deterministic-fixture",
            backend_version="1",
            model_name="a012-deterministic-embedder",
            model_digest="a012-deterministic-embedder-v1",
            architecture="fixture",
            parameter_count=0,
            parameter_size=None,
            quantization=None,
            context_length=1024,
            embedding_dimension=self._dimension,
            capabilities=("embedding",),
        )

    def embed(self, request) -> EmbeddingResponse:
        vectors = tuple(
            normalize_embedding_values(
                self._vectors[text],
                expected_dimension=self._dimension,
            )
            for text in request.texts
        )
        return EmbeddingResponse(
            request_id=request.request_id,
            model_name="a012-deterministic-embedder",
            model_digest="a012-deterministic-embedder-v1",
            vectors=vectors,
            input_count=len(vectors),
            prompt_tokens=0,
            total_duration_ns=0,
            load_duration_ns=0,
        )


def _memory(
    memory_id: str,
    text: str,
    vector: tuple[float, ...],
    *,
    entity_ids: tuple[str, ...] = (),
    evidence_ids: tuple[str, ...] = (),
) -> RelationalMemorySpec:
    return RelationalMemorySpec(
        memory_id,
        text,
        vector,
        entity_ids,
        evidence_ids,
    )


def _edge(
    edge_id: str,
    source_id: str,
    target_id: str,
    relation: RelationType,
    *,
    weight: float = 0.8,
    confidence: float = 0.9,
    evidence_id: str | None = None,
) -> AssociationEdge:
    return AssociationEdge(
        edge_id,
        source_id,
        target_id,
        relation,
        weight,
        confidence,
        (evidence_id or f"evidence:{edge_id}",),
    )


def build_a012_deterministic_fixture() -> tuple[RelationalBenchmarkCase, ...]:
    return (
        RelationalBenchmarkCase(
            "ownership-workplace-one-hop",
            (
                _memory("person-ada", "Ada profile", _A),
                _memory("company-orbit", "Orbit Labs organization", _B),
                _memory("distractor-ownership", "unrelated ownership distractor", _C),
            ),
            (
                _edge(
                    "edge-ada-work",
                    "person-ada",
                    "company-orbit",
                    RelationType.WORKS_AT,
                ),
            ),
            "where does Ada work",
            _A,
            ("company-orbit",),
            (RelationType.WORKS_AT,),
            True,
            True,
        ),
        RelationalBenchmarkCase(
            "causal-one-hop",
            (
                _memory("event-outage", "observed service outage", _A),
                _memory("cause-power", "power supply interruption", _B),
                _memory("distractor-cause", "unrelated weather note", _C),
            ),
            (
                _edge(
                    "edge-outage-cause",
                    "event-outage",
                    "cause-power",
                    RelationType.CAUSED_BY,
                ),
            ),
            "what caused the observed outage",
            _A,
            ("cause-power",),
            (RelationType.CAUSED_BY,),
            True,
            True,
        ),
        RelationalBenchmarkCase(
            "temporal-one-hop",
            (
                _memory("event-alpha", "event alpha", _A),
                _memory("event-beta", "event beta", _B),
                _memory("distractor-time", "unrelated event", _C),
            ),
            (
                _edge(
                    "edge-alpha-before-beta",
                    "event-alpha",
                    "event-beta",
                    RelationType.OCCURRED_BEFORE,
                ),
            ),
            "what follows event alpha",
            _A,
            ("event-beta",),
            (RelationType.OCCURRED_BEFORE,),
            True,
            True,
        ),
        RelationalBenchmarkCase(
            "part-of-two-hop",
            (
                _memory("component-sensor", "sensor component", _A),
                _memory("subsystem-control", "control subsystem", _B),
                _memory("system-rover", "rover system", _C),
            ),
            (
                _edge(
                    "edge-sensor-subsystem",
                    "component-sensor",
                    "subsystem-control",
                    RelationType.PART_OF,
                ),
                _edge(
                    "edge-subsystem-rover",
                    "subsystem-control",
                    "system-rover",
                    RelationType.PART_OF,
                ),
            ),
            "which whole system contains this sensor",
            _A,
            ("system-rover",),
            (RelationType.PART_OF,),
            True,
            True,
        ),
        RelationalBenchmarkCase(
            "used-for-one-hop",
            (
                _memory("tool-caliper", "digital caliper", _A),
                _memory("purpose-measure", "precision dimension measurement", _B),
                _memory("distractor-tool", "unrelated tool note", _C),
            ),
            (
                _edge(
                    "edge-caliper-use",
                    "tool-caliper",
                    "purpose-measure",
                    RelationType.USED_FOR,
                ),
            ),
            "what is the caliper used for",
            _A,
            ("purpose-measure",),
            (RelationType.USED_FOR,),
            True,
            True,
        ),
        RelationalBenchmarkCase(
            "same-name-disambiguated-ownership",
            (
                _memory(
                    "person-alex-a",
                    "Alex profile",
                    _A,
                    entity_ids=("person-a",),
                ),
                _memory(
                    "person-alex-b",
                    "Alex profile",
                    _A,
                    entity_ids=("person-b",),
                ),
                _memory("company-a", "Company A", _B),
                _memory("company-b", "Company B", _B),
            ),
            (
                _edge(
                    "edge-alex-a-work",
                    "person-alex-a",
                    "company-a",
                    RelationType.WORKS_AT,
                ),
                _edge(
                    "edge-alex-b-work",
                    "person-alex-b",
                    "company-b",
                    RelationType.WORKS_AT,
                ),
                _edge(
                    "edge-same-name",
                    "person-alex-a",
                    "person-alex-b",
                    RelationType.SAME_NAME,
                ),
            ),
            "where does this Alex work",
            _A,
            ("company-b",),
            (RelationType.WORKS_AT,),
            True,
            True,
            required_entity_ids=("person-b",),
            forbidden_identity_ids=("person-alex-a", "company-a"),
        ),
        RelationalBenchmarkCase(
            "vector-direct-control",
            (
                _memory("direct-target", "directly retrievable fact", _A),
                _memory("direct-distractor", "unrelated direct fact", _B),
            ),
            (),
            "direct fact query",
            _A,
            ("direct-target",),
            (RelationType.SIMILAR_TO,),
            True,
            False,
        ),
        RelationalBenchmarkCase(
            "cycle-control",
            (
                _memory("cycle-seed", "cycle seed", _A),
                _memory("cycle-mid", "cycle middle", _B),
                _memory("cycle-target", "cycle unreachable target", _C),
            ),
            (
                _edge(
                    "edge-cycle-forward",
                    "cycle-seed",
                    "cycle-mid",
                    RelationType.PART_OF,
                ),
                _edge(
                    "edge-cycle-back",
                    "cycle-mid",
                    "cycle-seed",
                    RelationType.PART_OF,
                ),
            ),
            "cycle safety query",
            _A,
            ("cycle-target",),
            (RelationType.PART_OF,),
            False,
            False,
        ),
        RelationalBenchmarkCase(
            "low-confidence-edge-control",
            (
                _memory("low-seed", "low confidence seed", _A),
                _memory("low-target", "low confidence target", _B),
            ),
            (
                _edge(
                    "edge-low-confidence",
                    "low-seed",
                    "low-target",
                    RelationType.CAUSED_BY,
                    confidence=0.49,
                ),
            ),
            "low confidence relation query",
            _A,
            ("low-target",),
            (RelationType.CAUSED_BY,),
            False,
            False,
        ),
        RelationalBenchmarkCase(
            "relation-allowlist-control",
            (
                _memory("allow-seed", "allowlist seed", _A),
                _memory("allow-target", "allowlist target", _B),
            ),
            (
                _edge(
                    "edge-wrong-relation",
                    "allow-seed",
                    "allow-target",
                    RelationType.PART_OF,
                ),
            ),
            "relation allowlist query",
            _A,
            ("allow-target",),
            (RelationType.USED_FOR,),
            False,
            False,
        ),
        RelationalBenchmarkCase(
            "missing-target-control",
            (
                _memory("missing-seed", "missing path seed", _A),
                _memory("missing-target", "declared but unreachable target", _B),
            ),
            (),
            "unreachable target query",
            _A,
            ("missing-target",),
            (RelationType.WORKS_AT,),
            False,
            False,
        ),
        RelationalBenchmarkCase(
            "invalid-contract-control",
            (
                _memory("invalid-seed", "invalid seed", _A),
            ),
            (),
            "invalid target query",
            _A,
            ("absent-target",),
            (RelationType.WORKS_AT,),
            True,
            False,
        ),
    )


def _edge_payload(edge: AssociationEdge) -> dict[str, object]:
    return {
        "edge_id": edge.edge_id,
        "source_id": edge.source_id,
        "target_id": edge.target_id,
        "relation": edge.relation.value,
        "activation_weight": edge.activation_weight,
        "proposition_confidence": edge.proposition_confidence,
        "evidence_ids": edge.evidence_ids,
    }


def _shared_payload(case: RelationalBenchmarkCase) -> dict[str, object]:
    return {
        "case_id": case.case_id,
        "memories": [
            {
                "memory_id": memory.memory_id,
                "retrieval_text": memory.retrieval_text,
                "vector": memory.vector,
                "entity_ids": memory.entity_ids,
                "evidence_ids": memory.evidence_ids,
            }
            for memory in case.memories
        ],
        "edges": [_edge_payload(edge) for edge in case.edges],
        "query_text": case.query_text,
        "query_vector": case.query_vector,
        "target_memory_ids": case.target_memory_ids,
        "allowed_relations": tuple(item.value for item in case.allowed_relations),
        "expected_found": case.expected_found,
        "required_entity_ids": case.required_entity_ids,
        "forbidden_identity_ids": case.forbidden_identity_ids,
        "max_hops": case.max_hops,
        "max_visited_nodes": case.max_visited_nodes,
        "max_scanned_edges": case.max_scanned_edges,
        "minimum_proposition_confidence": case.minimum_proposition_confidence,
        "minimum_similarity": case.minimum_similarity,
        "top_k": case.top_k,
    }


def shared_input_fingerprint(case: RelationalBenchmarkCase) -> str:
    payload = json.dumps(
        _shared_payload(case),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def a012_fixture_fingerprint(
    cases: Iterable[RelationalBenchmarkCase],
) -> str:
    materialized = tuple(cases)
    payload = [
        _shared_payload(case)
        | {"relation_dependent": case.relation_dependent}
        for case in materialized
    ]
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _documents(
    case: RelationalBenchmarkCase,
) -> tuple[VectorMemoryDocument, ...]:
    return tuple(
        VectorMemoryDocument(
            MemoryRecord(
                memory.memory_id,
                MemoryKind.SEMANTIC,
                f"content:{memory.memory_id}",
                1.0,
                memory.evidence_ids,
            ),
            memory.retrieval_text,
            memory.entity_ids,
        )
        for memory in case.memories
    )


def _adapter(case: RelationalBenchmarkCase) -> _FixtureEmbeddingAdapter:
    vectors = {
        memory.retrieval_text: memory.vector
        for memory in case.memories
    }
    vectors[case.query_text] = case.query_vector
    return _FixtureEmbeddingAdapter(vectors)


def _task_success(
    found_target_ids: tuple[str, ...],
    target_memory_ids: tuple[str, ...],
    expected_found: bool,
) -> bool:
    found = set(found_target_ids)
    targets = set(target_memory_ids)
    return targets.issubset(found) if expected_found else found.isdisjoint(targets)


def _run_case(
    case: RelationalBenchmarkCase,
    *,
    adapter=None,
    minimum_similarity: float | None = None,
    embedding_profile: str = "a012-deterministic-v1",
) -> RelationalBenchmarkCaseResult:
    fingerprint = shared_input_fingerprint(case)
    try:
        documents = _documents(case)
        memory_records = tuple(document.memory for document in documents)
        known_ids = {memory.memory_id for memory in memory_records}
        unknown_targets = set(case.target_memory_ids) - known_ids
        if unknown_targets:
            raise ValueError(
                "unknown benchmark target memory_id(s): "
                + ", ".join(sorted(unknown_targets))
            )
        index = ExactVectorMemoryIndex(
            documents,
            adapter if adapter is not None else _adapter(case),
            embedding_profile=embedding_profile,
        )
        vector = index.search(
            VectorMemoryQuery(
                query_id=f"a012:{case.case_id}",
                query_text=case.query_text,
                top_k=case.top_k,
                minimum_similarity=(
                    case.minimum_similarity
                    if minimum_similarity is None
                    else minimum_similarity
                ),
                required_entity_ids=case.required_entity_ids,
            )
        )
        initial_ids = tuple(hit.memory_id for hit in vector.hits)
        relation_index = BoundedRelationIndex(memory_records, case.edges)

        initial_target_ids = tuple(
            sorted(set(initial_ids).intersection(case.target_memory_ids))
        )
        vector_success = _task_success(
            initial_target_ids,
            case.target_memory_ids,
            case.expected_found,
        )
        vector_run = RelationalVariantResult(
            variant=ComparisonVariant.VECTOR_METADATA,
            task_success=vector_success,
            expected_found=case.expected_found,
            found_target_ids=initial_target_ids,
            initially_retrieved_ids=initial_ids,
            final_selected_ids=initial_ids,
            vector_query_count=1,
            vector_scored_count=vector.scored_vector_count,
            relation_scanned_edge_count=0,
            relation_hop_count=0,
            relation_termination=None,
            relation_path_edge_ids=(),
            relation_path_memory_ids=(),
            relation_path_evidence_ids=(),
            identity_preserved=not set(initial_ids).intersection(
                case.forbidden_identity_ids
            ),
            provenance_complete=True,
            false_target_count=(
                len(initial_target_ids) if not case.expected_found else 0
            ),
        )

        traversal = None
        if set(case.target_memory_ids).issubset(initial_ids):
            relation_found_ids = initial_target_ids
            final_selected_ids = initial_ids
            path_edges: tuple[tuple[str, ...], ...] = ()
            path_memories: tuple[tuple[str, ...], ...] = ()
            path_evidence: tuple[tuple[str, ...], ...] = ()
            provenance_complete = True
        elif not initial_ids:
            # A physical embedding backend can legitimately retrieve no seed at
            # the frozen threshold. That is a valid retrieval miss, not an
            # invalid relation contract and not permission to invent a seed.
            relation_found_ids = ()
            final_selected_ids = ()
            path_edges = ()
            path_memories = ()
            path_evidence = ()
            provenance_complete = True
        else:
            traversal = relation_index.traverse(
                TraversalRequest(
                    seed_memory_ids=initial_ids,
                    target_memory_ids=case.target_memory_ids,
                    allowed_relations=case.allowed_relations,
                    max_hops=case.max_hops,
                    max_visited_nodes=case.max_visited_nodes,
                    max_scanned_edges=case.max_scanned_edges,
                    minimum_proposition_confidence=(
                        case.minimum_proposition_confidence
                    ),
                )
            )
            relation_found_ids = tuple(
                sorted(
                    set(initial_target_ids).union(
                        traversal.discovered_target_ids
                    )
                )
            )
            final_selected_ids = tuple(traversal.visited_memory_ids)
            path_edges = tuple(path.edge_ids for path in traversal.paths)
            path_memories = tuple(path.memory_ids for path in traversal.paths)
            path_evidence = tuple(path.evidence_ids for path in traversal.paths)
            provenance_complete = all(
                path.edge_ids and path.evidence_ids
                for path in traversal.paths
            )

        relation_success = _task_success(
            relation_found_ids,
            case.target_memory_ids,
            case.expected_found,
        )
        relation_run = RelationalVariantResult(
            variant=ComparisonVariant.BOUNDED_RELATION,
            task_success=relation_success,
            expected_found=case.expected_found,
            found_target_ids=relation_found_ids,
            initially_retrieved_ids=initial_ids,
            final_selected_ids=final_selected_ids,
            vector_query_count=1,
            vector_scored_count=vector.scored_vector_count,
            relation_scanned_edge_count=(
                traversal.scanned_edge_count if traversal is not None else 0
            ),
            relation_hop_count=(
                traversal.max_hop_reached if traversal is not None else 0
            ),
            relation_termination=(
                traversal.termination if traversal is not None else None
            ),
            relation_path_edge_ids=path_edges,
            relation_path_memory_ids=path_memories,
            relation_path_evidence_ids=path_evidence,
            identity_preserved=not set(final_selected_ids).intersection(
                case.forbidden_identity_ids
            ),
            provenance_complete=provenance_complete,
            false_target_count=(
                len(relation_found_ids) if not case.expected_found else 0
            ),
        )
        return RelationalBenchmarkCaseResult(
            case_id=case.case_id,
            shared_input_fingerprint=fingerprint,
            relation_dependent=case.relation_dependent,
            validation_error_observed=False,
            validation_error=None,
            runs=(vector_run, relation_run),
        )
    except ValueError as exc:
        return RelationalBenchmarkCaseResult(
            case_id=case.case_id,
            shared_input_fingerprint=fingerprint,
            relation_dependent=case.relation_dependent,
            validation_error_observed=True,
            validation_error=str(exc),
            runs=(),
        )


def _variant(
    result: RelationalBenchmarkCaseResult,
    variant: ComparisonVariant,
) -> RelationalVariantResult:
    return next(item for item in result.runs if item.variant is variant)


def _aggregate(
    cases: tuple[RelationalBenchmarkCase, ...],
    results: tuple[RelationalBenchmarkCaseResult, ...],
    *,
    deterministic: bool,
) -> RelationalBenchmarkReport:
    valid = tuple(item for item in results if not item.validation_error_observed)
    invalid = tuple(item for item in results if item.validation_error_observed)

    vector_success = 0
    relation_success = 0
    shared_success = 0
    relation_only = 0
    vector_only = 0
    regressions = 0
    identity_failures = 0
    provenance_failures = 0
    budget_failures = 0
    duplicate_visit_failures = 0
    vector_queries = 0
    vector_scored = 0
    relation_scans = 0

    by_case = {case.case_id: case for case in cases}
    for result in valid:
        vector = _variant(result, ComparisonVariant.VECTOR_METADATA)
        relation = _variant(result, ComparisonVariant.BOUNDED_RELATION)
        case = by_case[result.case_id]
        vector_success += int(vector.task_success)
        relation_success += int(relation.task_success)
        shared_success += int(vector.task_success and relation.task_success)
        relation_only += int(
            result.relation_dependent
            and not vector.task_success
            and relation.task_success
        )
        vector_only += int(vector.task_success and not relation.task_success)
        regressions += int(vector.task_success and not relation.task_success)
        identity_failures += int(not relation.identity_preserved)
        provenance_failures += int(not relation.provenance_complete)
        vector_queries += relation.vector_query_count
        vector_scored += relation.vector_scored_count
        relation_scans += relation.relation_scanned_edge_count

        if (
            relation.relation_scanned_edge_count > case.max_scanned_edges
            or relation.relation_hop_count > case.max_hops
            or len(relation.final_selected_ids) > case.max_visited_nodes
        ):
            budget_failures += 1
        if len(relation.final_selected_ids) != len(
            set(relation.final_selected_ids)
        ):
            duplicate_visit_failures += 1

    return RelationalBenchmarkReport(
        fixture_fingerprint=a012_fixture_fingerprint(cases),
        case_results=results,
        case_count=len(results),
        valid_case_count=len(valid),
        invalid_case_count=len(invalid),
        primary_relation_case_count=sum(
            1
            for case, result in zip(cases, results)
            if case.relation_dependent
            and not result.validation_error_observed
        ),
        vector_success_count=vector_success,
        relation_success_count=relation_success,
        shared_success_count=shared_success,
        relation_only_recovery_count=relation_only,
        vector_only_success_count=vector_only,
        regression_count=regressions,
        identity_failure_count=identity_failures,
        provenance_failure_count=provenance_failures,
        budget_violation_count=budget_failures,
        duplicate_visit_failure_count=duplicate_visit_failures,
        vector_query_count=vector_queries,
        vector_scored_count=vector_scored,
        relation_scanned_edge_count=relation_scans,
        deterministic_repeat_match=deterministic,
    )


def _run_a012_benchmark(
    cases: Iterable[RelationalBenchmarkCase],
    *,
    adapter=None,
    minimum_similarity: float | None = None,
    embedding_profile: str = "a012-deterministic-v1",
) -> RelationalBenchmarkReport:
    materialized = tuple(cases)
    ids = tuple(case.case_id for case in materialized)
    if len(ids) != len(set(ids)):
        raise ValueError("case_id values must be unique")
    first = tuple(
        _run_case(
            case,
            adapter=adapter,
            minimum_similarity=minimum_similarity,
            embedding_profile=embedding_profile,
        )
        for case in materialized
    )
    second = tuple(
        _run_case(
            case,
            adapter=adapter,
            minimum_similarity=minimum_similarity,
            embedding_profile=embedding_profile,
        )
        for case in materialized
    )
    return _aggregate(
        materialized,
        first,
        deterministic=first == second,
    )


def run_a012_benchmark(
    cases: Iterable[RelationalBenchmarkCase],
) -> RelationalBenchmarkReport:
    return _run_a012_benchmark(cases)


def run_a012_benchmark_with_adapter(
    cases: Iterable[RelationalBenchmarkCase],
    adapter,
    *,
    minimum_similarity: float,
    embedding_profile: str,
) -> RelationalBenchmarkReport:
    return _run_a012_benchmark(
        cases,
        adapter=adapter,
        minimum_similarity=minimum_similarity,
        embedding_profile=embedding_profile,
    )


def classify_a012_architecture(
    report: RelationalBenchmarkReport,
) -> ArchitectureDecision:
    if (
        report.relation_only_recovery_count == 0
        and report.vector_success_count == report.relation_success_count
        and report.regression_count == 0
    ):
        return ArchitectureDecision.VECTOR_METADATA_REMAINS_SUFFICIENT

    justified = (
        report.relation_only_recovery_count >= 3
        and report.relation_success_count > report.vector_success_count
        and report.regression_count == 0
        and report.identity_failure_count == 0
        and report.provenance_failure_count == 0
        and report.budget_violation_count == 0
        and report.duplicate_visit_failure_count == 0
        and report.deterministic_repeat_match is True
    )
    return (
        ArchitectureDecision.EXPLICIT_RELATION_TRAVERSAL_JUSTIFIED
        if justified
        else ArchitectureDecision.MIXED
    )


def qualify_a012_report(report: RelationalBenchmarkReport) -> list[str]:
    errors: list[str] = []
    expected_cases = build_a012_deterministic_fixture()
    if report.fixture_fingerprint != EXPECTED_A012_FIXTURE_FINGERPRINT:
        errors.append("fixture fingerprint does not match frozen A012 fixture")
    if a012_fixture_fingerprint(expected_cases) != EXPECTED_A012_FIXTURE_FINGERPRINT:
        errors.append("live A012 fixture bytes drift from literal frozen anchor")
    if tuple(item.case_id for item in report.case_results) != EXPECTED_A012_CASE_IDS:
        errors.append("case IDs/order do not match frozen A012 fixture")

    if report.case_count != len(report.case_results):
        errors.append("case_count must equal len(case_results)")
    if report.case_count != report.valid_case_count + report.invalid_case_count:
        errors.append("case_count must equal valid_case_count + invalid_case_count")

    valid = tuple(
        item for item in report.case_results
        if not item.validation_error_observed
    )
    invalid = tuple(
        item for item in report.case_results
        if item.validation_error_observed
    )
    if len(valid) != report.valid_case_count:
        errors.append("valid_case_count does not match case_results")
    if len(invalid) != report.invalid_case_count:
        errors.append("invalid_case_count does not match case_results")
    if report.invalid_case_count != 1:
        errors.append("invalid_case_count must equal 1")

    expected_fp = dict(EXPECTED_A012_SHARED_INPUT_FINGERPRINTS)
    live_fp = {
        case.case_id: shared_input_fingerprint(case)
        for case in expected_cases
    }
    if live_fp != expected_fp:
        errors.append("live A012 shared inputs drift from literal frozen anchors")
    for result in report.case_results:
        if result.shared_input_fingerprint != expected_fp.get(result.case_id):
            errors.append(
                f"{result.case_id} shared input fingerprint mismatch"
            )
        if result.validation_error_observed:
            if result.runs:
                errors.append(
                    f"{result.case_id} invalid case must not have runs"
                )
            continue
        variants = tuple(item.variant for item in result.runs)
        if variants != (
            ComparisonVariant.VECTOR_METADATA,
            ComparisonVariant.BOUNDED_RELATION,
        ):
            errors.append(f"{result.case_id} variant membership/order mismatch")

    calculated = _aggregate(
        expected_cases,
        report.case_results,
        deterministic=report.deterministic_repeat_match,
    )
    aggregate_fields = (
        "case_count",
        "valid_case_count",
        "invalid_case_count",
        "primary_relation_case_count",
        "vector_success_count",
        "relation_success_count",
        "shared_success_count",
        "relation_only_recovery_count",
        "vector_only_success_count",
        "regression_count",
        "identity_failure_count",
        "provenance_failure_count",
        "budget_violation_count",
        "duplicate_visit_failure_count",
        "vector_query_count",
        "vector_scored_count",
        "relation_scanned_edge_count",
    )
    for name in aggregate_fields:
        if getattr(report, name) != getattr(calculated, name):
            errors.append(f"{name} does not match case_results")

    if report.primary_relation_case_count != 6:
        errors.append("primary_relation_case_count must equal 6")
    if report.identity_failure_count != 0:
        errors.append("identity_failure_count must equal 0")
    if report.provenance_failure_count != 0:
        errors.append("provenance_failure_count must equal 0")
    if report.budget_violation_count != 0:
        errors.append("budget_violation_count must equal 0")
    if report.duplicate_visit_failure_count != 0:
        errors.append("duplicate_visit_failure_count must equal 0")
    if not isinstance(report.deterministic_repeat_match, bool):
        errors.append("deterministic_repeat_match must be bool")
    elif report.deterministic_repeat_match is not True:
        errors.append("deterministic_repeat_match must be true")

    return errors


def benchmark_report_payload(
    report: RelationalBenchmarkReport,
    *,
    include_portable_qualification_errors: bool = True,
) -> dict[str, object]:
    return {
        "qualification_scope": "deterministic_relational_reasoning_a012",
        "fixture_version": "a012-deterministic-v1",
        "fixture_fingerprint": report.fixture_fingerprint,
        "case_ids": [item.case_id for item in report.case_results],
        "primary_architecture_decision": classify_a012_architecture(report).value,
        "aggregate_metrics": {
            "case_count": report.case_count,
            "valid_case_count": report.valid_case_count,
            "invalid_case_count": report.invalid_case_count,
            "primary_relation_case_count": report.primary_relation_case_count,
            "vector_success_count": report.vector_success_count,
            "relation_success_count": report.relation_success_count,
            "shared_success_count": report.shared_success_count,
            "relation_only_recovery_count": report.relation_only_recovery_count,
            "vector_only_success_count": report.vector_only_success_count,
            "regression_count": report.regression_count,
            "identity_failure_count": report.identity_failure_count,
            "provenance_failure_count": report.provenance_failure_count,
            "budget_violation_count": report.budget_violation_count,
            "duplicate_visit_failure_count": report.duplicate_visit_failure_count,
            "vector_query_count": report.vector_query_count,
            "vector_scored_count": report.vector_scored_count,
            "relation_scanned_edge_count": report.relation_scanned_edge_count,
            "deterministic_repeat_match": report.deterministic_repeat_match,
        },
        "cases": [
            {
                "case_id": case.case_id,
                "shared_input_fingerprint": case.shared_input_fingerprint,
                "relation_dependent": case.relation_dependent,
                "validation_error_observed": case.validation_error_observed,
                "validation_error": case.validation_error,
                "runs": [
                    {
                        "variant": run.variant.value,
                        "task_success": run.task_success,
                        "expected_found": run.expected_found,
                        "found_target_ids": run.found_target_ids,
                        "initially_retrieved_ids": run.initially_retrieved_ids,
                        "final_selected_ids": run.final_selected_ids,
                        "vector_query_count": run.vector_query_count,
                        "vector_scored_count": run.vector_scored_count,
                        "relation_scanned_edge_count": run.relation_scanned_edge_count,
                        "relation_hop_count": run.relation_hop_count,
                        "relation_termination": (
                            run.relation_termination.value
                            if run.relation_termination is not None
                            else None
                        ),
                        "relation_path_edge_ids": run.relation_path_edge_ids,
                        "relation_path_memory_ids": run.relation_path_memory_ids,
                        "relation_path_evidence_ids": run.relation_path_evidence_ids,
                        "identity_preserved": run.identity_preserved,
                        "provenance_complete": run.provenance_complete,
                        "false_target_count": run.false_target_count,
                    }
                    for run in case.runs
                ],
            }
            for case in report.case_results
        ],
        "claims_boundary": {
            "hardware_flops": False,
            "energy": False,
            "general_latency": False,
            "general_graph_superiority": False,
        },
        "errors": (
            qualify_a012_report(report)
            if include_portable_qualification_errors
            else []
        ),
    }
