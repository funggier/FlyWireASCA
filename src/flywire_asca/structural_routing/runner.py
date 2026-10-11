from __future__ import annotations

from dataclasses import replace

from flywire_asca.model import ModelAdapter
from flywire_asca.relational_activation import StructuralNeed

from .model_router import route_by_model
from .models import (
    RoutingInferenceSource,
    RoutingInferenceStatus,
    RoutingPolicy,
    StructuralRoutingRequest,
    StructuralRoutingResult,
)
from .rules import route_by_rules


def _missing_model_result(
    request: StructuralRoutingRequest,
    policy: RoutingPolicy,
) -> StructuralRoutingResult:
    return StructuralRoutingResult(
        request_id=request.request_id,
        policy=policy,
        status=RoutingInferenceStatus.MODEL_ERROR,
        source=RoutingInferenceSource.FAIL_CLOSED,
        structural_need=StructuralNeed(),
        model_invoked=False,
    )


def run_structural_routing(
    request: StructuralRoutingRequest,
    *,
    policy: RoutingPolicy,
    model_adapter: ModelAdapter | None = None,
) -> StructuralRoutingResult:
    if not isinstance(request, StructuralRoutingRequest):
        raise ValueError("request must be a StructuralRoutingRequest")
    if not isinstance(policy, RoutingPolicy):
        raise ValueError("policy must be a RoutingPolicy")

    if policy is RoutingPolicy.RULE_ONLY:
        return route_by_rules(request)

    if policy is RoutingPolicy.MODEL_ONLY:
        if model_adapter is None:
            return _missing_model_result(request, policy)
        return route_by_model(request, model_adapter, policy=policy)

    rule_result = route_by_rules(request)
    if rule_result.status is not RoutingInferenceStatus.ABSTAINED:
        return replace(rule_result, policy=policy)
    if model_adapter is None:
        return _missing_model_result(request, policy)
    return route_by_model(request, model_adapter, policy=policy)
