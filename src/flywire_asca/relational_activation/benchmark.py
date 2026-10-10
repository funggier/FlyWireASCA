from __future__ import annotations

from dataclasses import dataclass, replace
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
from flywire_asca.relational_reasoning import (
    RelationalBenchmarkCase,
    RelationalMemorySpec,
    build_a012_deterministic_fixture,
)
from flywire_asca.vector_memory import (
    ExactVectorMemoryIndex,
    VectorMemoryDocument,
    VectorMemoryQuery,
)

from .index import TargetFreeRelationIndex
from .models import (
    HybridRecallRequest,
    RelationalActivationDecision,
    RelationalActivationPolicy,
    StructuralNeed,
)
from .runner import run_hybrid_recall


EXPECTED_A013_CASE_IDS = (
    "ownership-workplace-one-hop",
    "causal-one-hop",
    "temporal-one-hop",
    "part-of-two-hop",
    "used-for-one-hop",
    "same-name-disambiguated-ownership",
    "cycle-control",
    "low-confidence-edge-control",
    "relation-allowlist-control",
    "missing-target-control",
    "vector-direct-control",
    "vector-direct-context-control",
    "vector-direct-procedure-control",
    "vector-direct-causal-control",
    "vector-direct-episodic-control",
    "vector-direct-spatial-control",
    "invalid-contract-control",
)

EXPECTED_A013_FIXTURE_FINGERPRINT = "fcd805a5229bfad43f8eed6999be37ae61168dda1a8560f04370b3df0262baa5"
EXPECTED_A013_SHARED_INPUT_FINGERPRINTS: tuple[tuple[str, str], ...] = (
    ("ownership-workplace-one-hop", "66563dd2fed458f8f2831c4d110c37c4860abbb8f526e085a73e3a933985e8d1"),
    ("causal-one-hop", "2ddacd79d5b9c60026f338c97a07e04583f959fdf3d9b411b63eeccc30283f39"),
    ("temporal-one-hop", "7204c54f016a98062fe9697a7094c3607427e501e20a0e77e533c9c84239b51c"),
    ("part-of-two-hop", "6ef7609871df30072a2a45abb9a3bdf209df13dbfa3afca3dd65aa6aacab40f7"),
    ("used-for-one-hop", "83b8567e4ff81d387804d9b7d2451dcea9bcedfaa47253ef0a34a3c2d2af5da3"),
    ("same-name-disambiguated-ownership", "e29dff0f2992ed0a422da5e674e83cb0d1e3485ce636c5784f24ebcf92bfd444"),
    ("cycle-control", "2b58c1ca5f12ef62c729f59311e1474db2e24817eb7118a0953745f4ad3a3bd3"),
    ("low-confidence-edge-control", "9b753a7ecd3177546b46be5b72d298ca90fac714f31a1d296f6a65573999cb20"),
    ("relation-allowlist-control", "9ad1a869167d4983b1cde00cc0d1c3f95e9be4497475c92da39191b47d7fcb43"),
    ("missing-target-control", "d5e8644190bc003500b87a47321f031f162da1d411ff0a427baa0bbac5492fce"),
    ("vector-direct-control", "b17f36251141c3ed27e9f4ab387733ee609cd950f1d4f8541558079de92c8546"),
    ("vector-direct-context-control", "42bea70420daa8dc77565b3685f46879396025de671e261ccca8ff122c755b0f"),
    ("vector-direct-procedure-control", "d585552b4ed95ea5b9b287e7ecbbbefd1268bbaabd053aab0ae5b120a62817d5"),
    ("vector-direct-causal-control", "3e6c91c7f592380d0c5b53181f3d00fcf222ba2c785973aeb886a44f3283810b"),
    ("vector-direct-episodic-control", "2a345a27489c17333d55b5258ca2b74362abf7cda839fee158ebbb92bb1542ed"),
    ("vector-direct-spatial-control", "ca714e42eaeddfe4d77310cc24be31c580bf6de96cd3b3e1b50558ff1358e5df"),
    ("invalid-contract-control", "b49c6392b74b6744e306f59faa870ff7f6d7897b9f9faf20748d31039a1b56f8"),
)


@dataclass(frozen=True, slots=True)
class ActivationBenchmarkCase:
    case_id: str
    memories: tuple[RelationalMemorySpec, ...]
    edges: tuple[AssociationEdge, ...]
    query_text: str
    query_vector: tuple[float, ...]
    expected_target_ids: tuple[str, ...]
    structural_need: StructuralNeed
    default_relation_scope: tuple[RelationType, ...]
    expected_found: bool
    primary_relation_positive: bool
    required_entity_ids: tuple[str, ...] = ()
    forbidden_identity_ids: tuple[str, ...] = ()
    max_hops: int = 3
    max_visited_nodes: int = 8
    max_scanned_edges: int = 32
    minimum_proposition_confidence: float = 0.5
    minimum_similarity: float = 0.9
    top_k: int = 1


@dataclass(frozen=True, slots=True)
class ActivationPolicyCaseResult:
    policy: RelationalActivationPolicy
    task_success: bool
    expected_found: bool
    found_expected_ids: tuple[str, ...]
    initially_retrieved_ids: tuple[str, ...]
    final_selected_ids: tuple[str, ...]
    vector_query_count: int
    vector_scored_count: int
    relation_invoked: bool
    relation_scanned_edge_count: int
    relation_visited_node_count: int
    relation_path_edge_ids: tuple[tuple[str, ...], ...]
    relation_path_memory_ids: tuple[tuple[str, ...], ...]
    relation_path_evidence_ids: tuple[tuple[str, ...], ...]
    identity_preserved: bool
    provenance_complete: bool
    budget_respected: bool
    duplicate_visit_free: bool


@dataclass(frozen=True, slots=True)
class ActivationBenchmarkCaseResult:
    case_id: str
    shared_input_fingerprint: str
    structural_need_active: bool
    primary_relation_positive: bool
    validation_error_observed: bool
    validation_error: str | None
    runs: tuple[ActivationPolicyCaseResult, ...]


@dataclass(frozen=True, slots=True)
class ActivationBenchmarkReport:
    fixture_fingerprint: str
    case_results: tuple[ActivationBenchmarkCaseResult, ...]
    case_count: int
    valid_case_count: int
    invalid_case_count: int
    primary_relation_case_count: int
    direct_control_count: int
    vector_success_count: int
    always_success_count: int
    signal_success_count: int
    vector_primary_relation_success_count: int
    always_primary_relation_success_count: int
    signal_primary_relation_success_count: int
    vector_direct_success_count: int
    signal_direct_success_count: int
    always_relation_only_recovery_count: int
    signal_relation_only_recovery_count: int
    always_regression_count: int
    signal_regression_count: int
    always_relation_invocation_count: int
    signal_relation_invocation_count: int
    always_relation_scanned_edge_count: int
    signal_relation_scanned_edge_count: int
    always_relation_visited_node_count: int
    signal_relation_visited_node_count: int
    signal_false_activation_count: int
    signal_missed_activation_count: int
    identity_failure_count: int
    provenance_failure_count: int
    budget_violation_count: int
    duplicate_visit_failure_count: int
    deterministic_repeat_match: bool


_A = (1.0, 0.0, 0.0)
_B = (0.0, 1.0, 0.0)


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
            model_name="a013-deterministic-embedder",
            model_digest="a013-deterministic-embedder-v1",
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
            model_name="a013-deterministic-embedder",
            model_digest="a013-deterministic-embedder-v1",
            vectors=vectors,
            input_count=len(vectors),
            prompt_tokens=0,
            total_duration_ns=0,
            load_duration_ns=0,
        )


def _from_a012(case: RelationalBenchmarkCase, *, structural: bool) -> ActivationBenchmarkCase:
    return ActivationBenchmarkCase(
        case_id=case.case_id,
        memories=case.memories,
        edges=case.edges,
        query_text=case.query_text,
        query_vector=case.query_vector,
        expected_target_ids=case.target_memory_ids,
        structural_need=(
            StructuralNeed(case.allowed_relations, requires_path_provenance=True)
            if structural
            else StructuralNeed()
        ),
        default_relation_scope=case.allowed_relations,
        expected_found=case.expected_found,
        primary_relation_positive=bool(case.relation_dependent and case.expected_found),
        required_entity_ids=case.required_entity_ids,
        forbidden_identity_ids=case.forbidden_identity_ids,
        max_hops=case.max_hops,
        max_visited_nodes=case.max_visited_nodes,
        max_scanned_edges=case.max_scanned_edges,
        minimum_proposition_confidence=case.minimum_proposition_confidence,
        minimum_similarity=case.minimum_similarity,
        top_k=case.top_k,
    )


def _direct_case(case_id: str, label: str) -> ActivationBenchmarkCase:
    target_id = f"{case_id}:target"
    distractor_id = f"{case_id}:distractor"
    return ActivationBenchmarkCase(
        case_id=case_id,
        memories=(
            RelationalMemorySpec(target_id, f"{label} target", _A),
            RelationalMemorySpec(distractor_id, f"{label} distractor", _B),
        ),
        edges=(
            AssociationEdge(
                f"{case_id}:irrelevant-edge",
                target_id,
                distractor_id,
                RelationType.SIMILAR_TO,
                0.8,
                0.9,
                (f"evidence:{case_id}:irrelevant",),
            ),
        ),
        query_text=f"{label} direct query",
        query_vector=_A,
        expected_target_ids=(target_id,),
        structural_need=StructuralNeed(),
        default_relation_scope=(RelationType.SIMILAR_TO,),
        expected_found=True,
        primary_relation_positive=False,
    )


def _invalid_case() -> ActivationBenchmarkCase:
    memory = RelationalMemorySpec("invalid-seed", "invalid seed", _A)
    return ActivationBenchmarkCase(
        case_id="invalid-contract-control",
        memories=(memory,),
        edges=(
            AssociationEdge(
                "invalid-edge",
                "invalid-seed",
                "absent-target",
                RelationType.WORKS_AT,
                0.8,
                0.9,
                ("evidence:invalid-edge",),
            ),
        ),
        query_text="invalid relation contract",
        query_vector=_A,
        expected_target_ids=("absent-target",),
        structural_need=StructuralNeed(
            (RelationType.WORKS_AT,),
            requires_path_provenance=True,
        ),
        default_relation_scope=(RelationType.WORKS_AT,),
        expected_found=True,
        primary_relation_positive=False,
    )


def build_a013_deterministic_fixture() -> tuple[ActivationBenchmarkCase, ...]:
    a012 = {case.case_id: case for case in build_a012_deterministic_fixture()}
    structural_ids = (
        "ownership-workplace-one-hop",
        "causal-one-hop",
        "temporal-one-hop",
        "part-of-two-hop",
        "used-for-one-hop",
        "same-name-disambiguated-ownership",
        "cycle-control",
        "low-confidence-edge-control",
        "relation-allowlist-control",
        "missing-target-control",
    )
    cases = [
        _from_a012(a012[case_id], structural=True)
        for case_id in structural_ids
    ]
    cases.append(_from_a012(a012["vector-direct-control"], structural=False))
    cases.extend(
        (
            _direct_case("vector-direct-context-control", "context"),
            _direct_case("vector-direct-procedure-control", "procedure"),
            _direct_case("vector-direct-causal-control", "causal"),
            _direct_case("vector-direct-episodic-control", "episodic"),
            _direct_case("vector-direct-spatial-control", "spatial"),
        )
    )
    cases.append(_invalid_case())
    return tuple(cases)


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


def _case_payload(case: ActivationBenchmarkCase) -> dict[str, object]:
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
        "expected_target_ids": case.expected_target_ids,
        "structural_need": {
            "required_relations": tuple(
                relation.value
                for relation in case.structural_need.required_relations
            ),
            "requires_path_provenance": (
                case.structural_need.requires_path_provenance
            ),
        },
        "default_relation_scope": tuple(
            relation.value for relation in case.default_relation_scope
        ),
        "expected_found": case.expected_found,
        "primary_relation_positive": case.primary_relation_positive,
        "required_entity_ids": case.required_entity_ids,
        "forbidden_identity_ids": case.forbidden_identity_ids,
        "max_hops": case.max_hops,
        "max_visited_nodes": case.max_visited_nodes,
        "max_scanned_edges": case.max_scanned_edges,
        "minimum_proposition_confidence": case.minimum_proposition_confidence,
        "minimum_similarity": case.minimum_similarity,
        "top_k": case.top_k,
    }


def shared_input_fingerprint(case: ActivationBenchmarkCase) -> str:
    payload = json.dumps(
        _case_payload(case),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def a013_fixture_fingerprint(
    cases: Iterable[ActivationBenchmarkCase],
) -> str:
    payload = [_case_payload(case) for case in tuple(cases)]
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _documents(case: ActivationBenchmarkCase) -> tuple[VectorMemoryDocument, ...]:
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


def _adapter(case: ActivationBenchmarkCase) -> _FixtureEmbeddingAdapter:
    vectors = {memory.retrieval_text: memory.vector for memory in case.memories}
    vectors[case.query_text] = case.query_vector
    return _FixtureEmbeddingAdapter(vectors)


def _task_success(
    found_target_ids: tuple[str, ...],
    expected_target_ids: tuple[str, ...],
    expected_found: bool,
) -> bool:
    found = set(found_target_ids)
    targets = set(expected_target_ids)
    return targets.issubset(found) if expected_found else found.isdisjoint(targets)


def _run_case(case: ActivationBenchmarkCase) -> ActivationBenchmarkCaseResult:
    fingerprint = shared_input_fingerprint(case)
    try:
        documents = _documents(case)
        memory_records = tuple(document.memory for document in documents)
        vector_index = ExactVectorMemoryIndex(
            documents,
            _adapter(case),
            embedding_profile="a013-deterministic-v1",
        )
        relation_index = TargetFreeRelationIndex(memory_records, case.edges)

        runs: list[ActivationPolicyCaseResult] = []
        for policy in RelationalActivationPolicy:
            query = VectorMemoryQuery(
                query_id=f"a013:{case.case_id}:{policy.value}",
                query_text=case.query_text,
                top_k=case.top_k,
                minimum_similarity=case.minimum_similarity,
                required_entity_ids=case.required_entity_ids,
            )
            result = run_hybrid_recall(
                HybridRecallRequest(
                    request_id=f"a013:{case.case_id}:{policy.value}",
                    policy=policy,
                    vector_query=query,
                    structural_need=case.structural_need,
                    default_relation_scope=case.default_relation_scope,
                    max_hops=case.max_hops,
                    max_visited_nodes=case.max_visited_nodes,
                    max_scanned_edges=case.max_scanned_edges,
                    minimum_proposition_confidence=(
                        case.minimum_proposition_confidence
                    ),
                ),
                vector_index=vector_index,
                relation_index=relation_index,
            )
            found_ids = tuple(
                sorted(
                    set(result.final_memory_ids).intersection(
                        case.expected_target_ids
                    )
                )
            )
            expansion = result.expansion_result
            path_by_reached = {
                path.reached_memory_id: path
                for path in (() if expansion is None else expansion.paths)
            }
            provenance_complete = True
            for target_id in found_ids:
                if target_id in result.initial_memory_ids:
                    continue
                path = path_by_reached.get(target_id)
                if (
                    path is None
                    or not path.edge_ids
                    or not path.evidence_ids
                ):
                    provenance_complete = False
            budget_respected = (
                expansion is None
                or (
                    expansion.scanned_edge_count <= case.max_scanned_edges
                    and len(expansion.visited_memory_ids) <= case.max_visited_nodes
                    and expansion.max_hop_reached <= case.max_hops
                )
            )
            duplicate_visit_free = (
                expansion is None
                or len(set(expansion.visited_memory_ids))
                == len(expansion.visited_memory_ids)
            )
            runs.append(
                ActivationPolicyCaseResult(
                    policy=policy,
                    task_success=_task_success(
                        found_ids,
                        case.expected_target_ids,
                        case.expected_found,
                    ),
                    expected_found=case.expected_found,
                    found_expected_ids=found_ids,
                    initially_retrieved_ids=result.initial_memory_ids,
                    final_selected_ids=result.final_memory_ids,
                    vector_query_count=1,
                    vector_scored_count=result.vector_result.scored_vector_count,
                    relation_invoked=result.relation_invoked,
                    relation_scanned_edge_count=(
                        0 if expansion is None else expansion.scanned_edge_count
                    ),
                    relation_visited_node_count=(
                        0 if expansion is None else len(expansion.visited_memory_ids)
                    ),
                    relation_path_edge_ids=(
                        ()
                        if expansion is None
                        else tuple(path.edge_ids for path in expansion.paths)
                    ),
                    relation_path_memory_ids=(
                        ()
                        if expansion is None
                        else tuple(path.memory_ids for path in expansion.paths)
                    ),
                    relation_path_evidence_ids=(
                        ()
                        if expansion is None
                        else tuple(path.evidence_ids for path in expansion.paths)
                    ),
                    identity_preserved=not set(result.final_memory_ids).intersection(
                        case.forbidden_identity_ids
                    ),
                    provenance_complete=provenance_complete,
                    budget_respected=budget_respected,
                    duplicate_visit_free=duplicate_visit_free,
                )
            )

        return ActivationBenchmarkCaseResult(
            case_id=case.case_id,
            shared_input_fingerprint=fingerprint,
            structural_need_active=case.structural_need.active,
            primary_relation_positive=case.primary_relation_positive,
            validation_error_observed=False,
            validation_error=None,
            runs=tuple(runs),
        )
    except ValueError as exc:
        return ActivationBenchmarkCaseResult(
            case_id=case.case_id,
            shared_input_fingerprint=fingerprint,
            structural_need_active=case.structural_need.active,
            primary_relation_positive=case.primary_relation_positive,
            validation_error_observed=True,
            validation_error=str(exc),
            runs=(),
        )


def _policy_run(
    result: ActivationBenchmarkCaseResult,
    policy: RelationalActivationPolicy,
) -> ActivationPolicyCaseResult:
    return next(run for run in result.runs if run.policy is policy)


def _aggregate(
    cases: tuple[ActivationBenchmarkCase, ...],
    case_results: tuple[ActivationBenchmarkCaseResult, ...],
) -> ActivationBenchmarkReport:
    valid = tuple(result for result in case_results if not result.validation_error_observed)
    invalid = tuple(result for result in case_results if result.validation_error_observed)
    case_by_id = {case.case_id: case for case in cases}

    vector_runs = tuple(
        _policy_run(result, RelationalActivationPolicy.VECTOR_ONLY)
        for result in valid
    )
    always_runs = tuple(
        _policy_run(result, RelationalActivationPolicy.ALWAYS_RELATION)
        for result in valid
    )
    signal_runs = tuple(
        _policy_run(result, RelationalActivationPolicy.SIGNAL_GATED_RELATION)
        for result in valid
    )

    primary_results = tuple(
        result for result in valid if result.primary_relation_positive
    )
    direct_results = tuple(
        result for result in valid if not result.structural_need_active
    )

    def success_count(
        results: tuple[ActivationBenchmarkCaseResult, ...],
        policy: RelationalActivationPolicy,
    ) -> int:
        return sum(_policy_run(result, policy).task_success for result in results)

    relation_only = lambda policy: sum(
        (
            not _policy_run(result, RelationalActivationPolicy.VECTOR_ONLY).task_success
            and _policy_run(result, policy).task_success
        )
        for result in primary_results
    )
    regressions = lambda policy: sum(
        (
            _policy_run(result, RelationalActivationPolicy.VECTOR_ONLY).task_success
            and not _policy_run(result, policy).task_success
        )
        for result in valid
    )

    identity_failures = sum(
        not run.identity_preserved
        for result in valid
        for run in result.runs
    )
    provenance_failures = sum(
        not run.provenance_complete
        for result in valid
        for run in result.runs
    )
    budget_violations = sum(
        not run.budget_respected
        for result in valid
        for run in result.runs
    )
    duplicate_failures = sum(
        not run.duplicate_visit_free
        for result in valid
        for run in result.runs
    )

    signal_false = sum(
        _policy_run(
            result,
            RelationalActivationPolicy.SIGNAL_GATED_RELATION,
        ).relation_invoked
        and not result.structural_need_active
        for result in valid
    )
    signal_missed = sum(
        result.structural_need_active
        and bool(
            _policy_run(
                result,
                RelationalActivationPolicy.SIGNAL_GATED_RELATION,
            ).initially_retrieved_ids
        )
        and not _policy_run(
            result,
            RelationalActivationPolicy.SIGNAL_GATED_RELATION,
        ).relation_invoked
        for result in valid
    )

    return ActivationBenchmarkReport(
        fixture_fingerprint=a013_fixture_fingerprint(cases),
        case_results=case_results,
        case_count=len(case_results),
        valid_case_count=len(valid),
        invalid_case_count=len(invalid),
        primary_relation_case_count=len(primary_results),
        direct_control_count=len(direct_results),
        vector_success_count=sum(run.task_success for run in vector_runs),
        always_success_count=sum(run.task_success for run in always_runs),
        signal_success_count=sum(run.task_success for run in signal_runs),
        vector_primary_relation_success_count=success_count(
            primary_results,
            RelationalActivationPolicy.VECTOR_ONLY,
        ),
        always_primary_relation_success_count=success_count(
            primary_results,
            RelationalActivationPolicy.ALWAYS_RELATION,
        ),
        signal_primary_relation_success_count=success_count(
            primary_results,
            RelationalActivationPolicy.SIGNAL_GATED_RELATION,
        ),
        vector_direct_success_count=success_count(
            direct_results,
            RelationalActivationPolicy.VECTOR_ONLY,
        ),
        signal_direct_success_count=success_count(
            direct_results,
            RelationalActivationPolicy.SIGNAL_GATED_RELATION,
        ),
        always_relation_only_recovery_count=relation_only(
            RelationalActivationPolicy.ALWAYS_RELATION
        ),
        signal_relation_only_recovery_count=relation_only(
            RelationalActivationPolicy.SIGNAL_GATED_RELATION
        ),
        always_regression_count=regressions(
            RelationalActivationPolicy.ALWAYS_RELATION
        ),
        signal_regression_count=regressions(
            RelationalActivationPolicy.SIGNAL_GATED_RELATION
        ),
        always_relation_invocation_count=sum(
            run.relation_invoked for run in always_runs
        ),
        signal_relation_invocation_count=sum(
            run.relation_invoked for run in signal_runs
        ),
        always_relation_scanned_edge_count=sum(
            run.relation_scanned_edge_count for run in always_runs
        ),
        signal_relation_scanned_edge_count=sum(
            run.relation_scanned_edge_count for run in signal_runs
        ),
        always_relation_visited_node_count=sum(
            run.relation_visited_node_count for run in always_runs
        ),
        signal_relation_visited_node_count=sum(
            run.relation_visited_node_count for run in signal_runs
        ),
        signal_false_activation_count=signal_false,
        signal_missed_activation_count=signal_missed,
        identity_failure_count=identity_failures,
        provenance_failure_count=provenance_failures,
        budget_violation_count=budget_violations,
        duplicate_visit_failure_count=duplicate_failures,
        deterministic_repeat_match=False,
    )


def run_a013_benchmark(
    cases: Iterable[ActivationBenchmarkCase] | None = None,
) -> ActivationBenchmarkReport:
    materialized = (
        build_a013_deterministic_fixture()
        if cases is None
        else tuple(cases)
    )
    first_results = tuple(_run_case(case) for case in materialized)
    second_results = tuple(_run_case(case) for case in materialized)
    first = _aggregate(materialized, first_results)
    return replace(
        first,
        deterministic_repeat_match=(first_results == second_results),
    )


def classify_a013_architecture(
    report: ActivationBenchmarkReport,
) -> RelationalActivationDecision:
    safety_ok = (
        report.identity_failure_count == 0
        and report.provenance_failure_count == 0
        and report.budget_violation_count == 0
        and report.duplicate_visit_failure_count == 0
    )
    if (
        report.signal_primary_relation_success_count
        == report.always_primary_relation_success_count
        and report.signal_direct_success_count >= report.vector_direct_success_count
        and report.signal_relation_only_recovery_count > 0
        and report.signal_relation_invocation_count
        < report.always_relation_invocation_count
        and report.signal_relation_scanned_edge_count
        < report.always_relation_scanned_edge_count
        and report.signal_false_activation_count == 0
        and report.signal_missed_activation_count == 0
        and report.signal_regression_count == 0
        and safety_ok
        and report.deterministic_repeat_match
    ):
        return RelationalActivationDecision.SIGNAL_GATED_RELATION_JUSTIFIED
    if (
        report.always_success_count > report.signal_success_count
        and report.always_regression_count == 0
        and safety_ok
    ):
        return RelationalActivationDecision.ALWAYS_RELATION_PREFERRED
    if (
        (
            report.always_relation_only_recovery_count == 0
            and report.signal_relation_only_recovery_count == 0
        )
        or not safety_ok
    ):
        return RelationalActivationDecision.RELATION_INTEGRATION_NOT_JUSTIFIED
    return RelationalActivationDecision.MIXED


def benchmark_report_payload(report: ActivationBenchmarkReport) -> dict[str, object]:
    return {
        "fixture_fingerprint": report.fixture_fingerprint,
        "case_count": report.case_count,
        "valid_case_count": report.valid_case_count,
        "invalid_case_count": report.invalid_case_count,
        "primary_relation_case_count": report.primary_relation_case_count,
        "direct_control_count": report.direct_control_count,
        "vector_success_count": report.vector_success_count,
        "always_success_count": report.always_success_count,
        "signal_success_count": report.signal_success_count,
        "vector_primary_relation_success_count": (
            report.vector_primary_relation_success_count
        ),
        "always_primary_relation_success_count": (
            report.always_primary_relation_success_count
        ),
        "signal_primary_relation_success_count": (
            report.signal_primary_relation_success_count
        ),
        "vector_direct_success_count": report.vector_direct_success_count,
        "signal_direct_success_count": report.signal_direct_success_count,
        "always_relation_only_recovery_count": (
            report.always_relation_only_recovery_count
        ),
        "signal_relation_only_recovery_count": (
            report.signal_relation_only_recovery_count
        ),
        "always_regression_count": report.always_regression_count,
        "signal_regression_count": report.signal_regression_count,
        "always_relation_invocation_count": report.always_relation_invocation_count,
        "signal_relation_invocation_count": report.signal_relation_invocation_count,
        "always_relation_scanned_edge_count": (
            report.always_relation_scanned_edge_count
        ),
        "signal_relation_scanned_edge_count": (
            report.signal_relation_scanned_edge_count
        ),
        "always_relation_visited_node_count": (
            report.always_relation_visited_node_count
        ),
        "signal_relation_visited_node_count": (
            report.signal_relation_visited_node_count
        ),
        "signal_false_activation_count": report.signal_false_activation_count,
        "signal_missed_activation_count": report.signal_missed_activation_count,
        "identity_failure_count": report.identity_failure_count,
        "provenance_failure_count": report.provenance_failure_count,
        "budget_violation_count": report.budget_violation_count,
        "duplicate_visit_failure_count": report.duplicate_visit_failure_count,
        "deterministic_repeat_match": report.deterministic_repeat_match,
        "decision": classify_a013_architecture(report).value,
        "cases": [
            {
                "case_id": case.case_id,
                "shared_input_fingerprint": case.shared_input_fingerprint,
                "structural_need_active": case.structural_need_active,
                "primary_relation_positive": case.primary_relation_positive,
                "validation_error_observed": case.validation_error_observed,
                "validation_error": case.validation_error,
                "runs": [
                    {
                        "policy": run.policy.value,
                        "task_success": run.task_success,
                        "expected_found": run.expected_found,
                        "found_expected_ids": run.found_expected_ids,
                        "initially_retrieved_ids": run.initially_retrieved_ids,
                        "final_selected_ids": run.final_selected_ids,
                        "vector_query_count": run.vector_query_count,
                        "vector_scored_count": run.vector_scored_count,
                        "relation_invoked": run.relation_invoked,
                        "relation_scanned_edge_count": (
                            run.relation_scanned_edge_count
                        ),
                        "relation_visited_node_count": (
                            run.relation_visited_node_count
                        ),
                        "relation_path_edge_ids": run.relation_path_edge_ids,
                        "relation_path_memory_ids": run.relation_path_memory_ids,
                        "relation_path_evidence_ids": (
                            run.relation_path_evidence_ids
                        ),
                        "identity_preserved": run.identity_preserved,
                        "provenance_complete": run.provenance_complete,
                        "budget_respected": run.budget_respected,
                        "duplicate_visit_free": run.duplicate_visit_free,
                    }
                    for run in case.runs
                ],
            }
            for case in report.case_results
        ],
    }
