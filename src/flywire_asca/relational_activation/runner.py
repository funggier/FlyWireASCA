from __future__ import annotations

from flywire_asca.vector_memory import ExactVectorMemoryIndex

from .index import TargetFreeRelationIndex
from .models import (
    ExpansionRequest,
    HybridRecallRequest,
    HybridRecallResult,
    RelationalActivationPolicy,
)


def run_hybrid_recall(
    request: HybridRecallRequest,
    *,
    vector_index: ExactVectorMemoryIndex,
    relation_index: TargetFreeRelationIndex,
) -> HybridRecallResult:
    if not isinstance(request, HybridRecallRequest):
        raise ValueError("request must be a HybridRecallRequest")
    if not isinstance(vector_index, ExactVectorMemoryIndex):
        raise ValueError("vector_index must be an ExactVectorMemoryIndex")
    if not isinstance(relation_index, TargetFreeRelationIndex):
        raise ValueError("relation_index must be a TargetFreeRelationIndex")

    vector_result = vector_index.search(request.vector_query)
    initial_ids = tuple(hit.memory_id for hit in vector_result.hits)

    should_invoke = (
        request.policy is RelationalActivationPolicy.ALWAYS_RELATION
        or (
            request.policy is RelationalActivationPolicy.SIGNAL_GATED_RELATION
            and request.structural_need.active
        )
    )

    expansion = None
    final_ids = initial_ids
    if should_invoke and initial_ids:
        allowed_relations = (
            request.structural_need.required_relations
            if request.structural_need.required_relations
            else request.default_relation_scope
        )
        expansion = relation_index.expand(
            ExpansionRequest(
                seed_memory_ids=initial_ids,
                allowed_relations=allowed_relations,
                max_hops=request.max_hops,
                max_visited_nodes=request.max_visited_nodes,
                max_scanned_edges=request.max_scanned_edges,
                minimum_proposition_confidence=(
                    request.minimum_proposition_confidence
                ),
            )
        )
        final_ids = expansion.visited_memory_ids

    return HybridRecallResult(
        request_id=request.request_id,
        policy=request.policy,
        structural_activation_requested=request.structural_need.active,
        relation_invoked=expansion is not None,
        vector_result=vector_result,
        initial_memory_ids=initial_ids,
        final_memory_ids=final_ids,
        expansion_result=expansion,
    )
