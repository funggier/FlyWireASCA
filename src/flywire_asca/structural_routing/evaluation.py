from __future__ import annotations

from dataclasses import dataclass, replace

from flywire_asca.model import ModelAdapter
from flywire_asca.relational_activation import (
    HybridRecallRequest,
    RelationalActivationPolicy,
    StructuralNeed,
    TargetFreeRelationIndex,
    run_hybrid_recall,
)
from flywire_asca.relational_activation import benchmark as a013_benchmark

from .benchmark_fixture import StructuralRoutingBenchmarkCase
from .models import RoutingPolicy, StructuralRoutingRequest, StructuralRoutingResult
from .runner import run_structural_routing


@dataclass(frozen=True, slots=True)
class RoutingPolicyCaseResult:
    routing_case_id: str
    base_a013_case_id: str
    language: str
    policy: RoutingPolicy
    routing_result: StructuralRoutingResult
    expected_structural_need: StructuralNeed
    primary_relation_positive: bool
    task_success: bool
    expected_found: bool
    found_expected_ids: tuple[str, ...]
    initially_retrieved_ids: tuple[str, ...]
    final_selected_ids: tuple[str, ...]
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

    def __post_init__(self) -> None:
        if not isinstance(self.policy, RoutingPolicy):
            raise ValueError("policy must be a RoutingPolicy")
        if not isinstance(self.routing_result, StructuralRoutingResult):
            raise ValueError("routing_result must be a StructuralRoutingResult")
        if self.routing_result.policy is not self.policy:
            raise ValueError("routing_result.policy must match policy")
        if not isinstance(self.expected_structural_need, StructuralNeed):
            raise ValueError("expected_structural_need must be a StructuralNeed")


def _task_success(
    found_ids: tuple[str, ...],
    expected_ids: tuple[str, ...],
    expected_found: bool,
) -> bool:
    found = set(found_ids)
    expected = set(expected_ids)
    return expected.issubset(found) if expected_found else found.isdisjoint(expected)


def evaluate_routing_case(
    case: StructuralRoutingBenchmarkCase,
    *,
    policy: RoutingPolicy,
    model_adapter: ModelAdapter | None,
) -> RoutingPolicyCaseResult:
    if not isinstance(case, StructuralRoutingBenchmarkCase):
        raise ValueError("case must be a StructuralRoutingBenchmarkCase")
    if not isinstance(policy, RoutingPolicy):
        raise ValueError("policy must be a RoutingPolicy")

    routing_request = StructuralRoutingRequest(
        case.request_id,
        case.query_text,
        case.language,
    )
    routing_result = run_structural_routing(
        routing_request,
        policy=policy,
        model_adapter=model_adapter,
    )

    runtime_case = replace(
        case.base_case,
        query_text=case.query_text,
        structural_need=routing_result.structural_need,
    )
    documents = a013_benchmark._documents(runtime_case)
    memory_records = tuple(document.memory for document in documents)
    vector_index = a013_benchmark.ExactVectorMemoryIndex(
        documents,
        a013_benchmark._adapter(runtime_case),
        embedding_profile="a013-deterministic-v1",
    )
    relation_index = TargetFreeRelationIndex(memory_records, runtime_case.edges)
    vector_query = a013_benchmark.VectorMemoryQuery(
        query_id=f"a014:{case.routing_case_id}:{policy.value}",
        query_text=case.query_text,
        top_k=runtime_case.top_k,
        minimum_similarity=runtime_case.minimum_similarity,
        required_entity_ids=runtime_case.required_entity_ids,
    )
    recall_result = run_hybrid_recall(
        HybridRecallRequest(
            request_id=f"a014:{case.routing_case_id}:{policy.value}",
            policy=RelationalActivationPolicy.SIGNAL_GATED_RELATION,
            vector_query=vector_query,
            structural_need=routing_result.structural_need,
            default_relation_scope=runtime_case.default_relation_scope,
            max_hops=runtime_case.max_hops,
            max_visited_nodes=runtime_case.max_visited_nodes,
            max_scanned_edges=runtime_case.max_scanned_edges,
            minimum_proposition_confidence=runtime_case.minimum_proposition_confidence,
        ),
        vector_index=vector_index,
        relation_index=relation_index,
    )

    found_ids = tuple(
        sorted(set(recall_result.final_memory_ids).intersection(case.expected_target_ids))
    )
    expansion = recall_result.expansion_result
    path_by_reached = {
        path.reached_memory_id: path
        for path in (() if expansion is None else expansion.paths)
    }
    provenance_complete = True
    for target_id in found_ids:
        if target_id in recall_result.initial_memory_ids:
            continue
        path = path_by_reached.get(target_id)
        if path is None or not path.edge_ids or not path.evidence_ids:
            provenance_complete = False

    budget_respected = expansion is None or (
        expansion.scanned_edge_count <= runtime_case.max_scanned_edges
        and len(expansion.visited_memory_ids) <= runtime_case.max_visited_nodes
        and expansion.max_hop_reached <= runtime_case.max_hops
    )
    duplicate_visit_free = expansion is None or (
        len(set(expansion.visited_memory_ids)) == len(expansion.visited_memory_ids)
    )
    identity_preserved = not set(recall_result.final_memory_ids).intersection(
        runtime_case.forbidden_identity_ids
    )

    return RoutingPolicyCaseResult(
        routing_case_id=case.routing_case_id,
        base_a013_case_id=case.base_a013_case_id,
        language=case.language,
        policy=policy,
        routing_result=routing_result,
        expected_structural_need=case.expected_structural_need,
        primary_relation_positive=case.primary_relation_positive,
        task_success=_task_success(
            found_ids,
            case.expected_target_ids,
            case.expected_found,
        ),
        expected_found=case.expected_found,
        found_expected_ids=found_ids,
        initially_retrieved_ids=recall_result.initial_memory_ids,
        final_selected_ids=recall_result.final_memory_ids,
        vector_scored_count=recall_result.vector_result.scored_vector_count,
        relation_invoked=recall_result.relation_invoked,
        relation_scanned_edge_count=(
            0 if expansion is None else expansion.scanned_edge_count
        ),
        relation_visited_node_count=(
            0 if expansion is None else len(expansion.visited_memory_ids)
        ),
        relation_path_edge_ids=(
            () if expansion is None else tuple(path.edge_ids for path in expansion.paths)
        ),
        relation_path_memory_ids=(
            () if expansion is None else tuple(path.memory_ids for path in expansion.paths)
        ),
        relation_path_evidence_ids=(
            () if expansion is None else tuple(path.evidence_ids for path in expansion.paths)
        ),
        identity_preserved=identity_preserved,
        provenance_complete=provenance_complete,
        budget_respected=budget_respected,
        duplicate_visit_free=duplicate_visit_free,
    )
