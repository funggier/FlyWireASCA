from __future__ import annotations

import hashlib
import json

from flywire_asca.contracts import RelationType
from flywire_asca.model import (
    ModelAdapter,
    ModelAdapterError,
    ModelMessage,
    ModelRequest,
    ModelResponse,
    ModelRole,
)
from flywire_asca.relational_activation import StructuralNeed

from .models import (
    RoutingInferenceSource,
    RoutingInferenceStatus,
    RoutingPolicy,
    StructuralRoutingRequest,
    StructuralRoutingResult,
)


_MODEL_POLICIES = (RoutingPolicy.MODEL_ONLY, RoutingPolicy.HYBRID_RULE_THEN_MODEL)
_ALLOWED_RELATIONS = {
    relation.value: relation
    for relation in (
        RelationType.WORKS_AT,
        RelationType.CAUSED_BY,
        RelationType.OCCURRED_BEFORE,
        RelationType.PART_OF,
        RelationType.USED_FOR,
    )
}
_EXPECTED_KEYS = frozenset(
    {"requires_relation", "required_relations", "requires_path_provenance"}
)


A014_ROUTER_SYSTEM_PROMPT = """Classify whether the user query requires explicit relational traversal.
Return exactly one JSON object and no other text.
The object must contain exactly these keys:
- requires_relation: boolean
- required_relations: array of strings
- requires_path_provenance: boolean
Allowed required_relations values and meanings:
- works_at: employment or workplace relation
- caused_by: explicit causal relation
- occurred_before: temporal ordering, including asking what happened before or after
- part_of: component-to-containing-system relation
- used_for: tool/component-to-purpose relation
If relational traversal is not required, set requires_relation to false, required_relations to [], and requires_path_provenance to false.
If relational traversal is required, set requires_relation to true and include one or more allowed relation values.
Do not include extra keys, markdown, commentary, or confidence scores.
""".strip()


def router_prompt_fingerprint() -> str:
    return hashlib.sha256(A014_ROUTER_SYSTEM_PROMPT.encode("utf-8")).hexdigest()


def build_router_model_request(request: StructuralRoutingRequest) -> ModelRequest:
    if not isinstance(request, StructuralRoutingRequest):
        raise ValueError("request must be a StructuralRoutingRequest")
    return ModelRequest(
        request_id=f"a014-router:{request.request_id}",
        messages=(
            ModelMessage(ModelRole.SYSTEM, A014_ROUTER_SYSTEM_PROMPT),
            ModelMessage(ModelRole.USER, request.query_text),
        ),
        max_output_tokens=192,
        context_limit=8192,
        temperature=0.0,
        seed=0,
        thinking=False,
    )


class _DuplicateJsonKey(ValueError):
    pass


def _strict_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise _DuplicateJsonKey(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _invalid_result(
    request: StructuralRoutingRequest,
    response: ModelResponse,
    *,
    policy: RoutingPolicy,
    status: RoutingInferenceStatus = RoutingInferenceStatus.INVALID_MODEL_OUTPUT,
) -> StructuralRoutingResult:
    return StructuralRoutingResult(
        request_id=request.request_id,
        policy=policy,
        status=status,
        source=RoutingInferenceSource.FAIL_CLOSED,
        structural_need=StructuralNeed(),
        model_invoked=True,
        model_name=response.model_name,
        model_digest=response.model_digest,
        raw_model_output=response.content,
        prompt_tokens=response.prompt_tokens,
        generated_tokens=response.generated_tokens,
        total_duration_ns=response.total_duration_ns,
    )


def _parse_payload(content: str) -> StructuralNeed | None:
    try:
        payload = json.loads(content, object_pairs_hook=_strict_object)
    except (json.JSONDecodeError, _DuplicateJsonKey, TypeError, ValueError):
        return None
    if not isinstance(payload, dict) or set(payload) != _EXPECTED_KEYS:
        return None

    requires_relation = payload["requires_relation"]
    required_relations = payload["required_relations"]
    requires_path_provenance = payload["requires_path_provenance"]
    if type(requires_relation) is not bool or type(requires_path_provenance) is not bool:
        return None
    if not isinstance(required_relations, list):
        return None
    if any(not isinstance(value, str) for value in required_relations):
        return None
    if any(value not in _ALLOWED_RELATIONS for value in required_relations):
        return None

    if not requires_relation:
        if required_relations or requires_path_provenance:
            return None
        return StructuralNeed()

    if not required_relations:
        return None
    relations = tuple(_ALLOWED_RELATIONS[value] for value in required_relations)
    return StructuralNeed(
        relations,
        requires_path_provenance=requires_path_provenance,
    )


def parse_router_model_response(
    request: StructuralRoutingRequest,
    response: ModelResponse,
    *,
    policy: RoutingPolicy,
) -> StructuralRoutingResult:
    if not isinstance(request, StructuralRoutingRequest):
        raise ValueError("request must be a StructuralRoutingRequest")
    if not isinstance(response, ModelResponse):
        raise ValueError("response must be a ModelResponse")
    if policy not in _MODEL_POLICIES:
        raise ValueError("policy must be model-capable")

    expected_request_id = f"a014-router:{request.request_id}"
    if response.request_id != expected_request_id:
        return _invalid_result(
            request,
            response,
            policy=policy,
            status=RoutingInferenceStatus.MODEL_ERROR,
        )

    need = _parse_payload(response.content)
    if need is None:
        return _invalid_result(request, response, policy=policy)

    return StructuralRoutingResult(
        request_id=request.request_id,
        policy=policy,
        status=(
            RoutingInferenceStatus.DECIDED_RELATIONAL
            if need.active
            else RoutingInferenceStatus.DECIDED_NON_RELATIONAL
        ),
        source=RoutingInferenceSource.MODEL,
        structural_need=need,
        model_invoked=True,
        model_name=response.model_name,
        model_digest=response.model_digest,
        raw_model_output=response.content,
        prompt_tokens=response.prompt_tokens,
        generated_tokens=response.generated_tokens,
        total_duration_ns=response.total_duration_ns,
    )


def route_by_model(
    request: StructuralRoutingRequest,
    adapter: ModelAdapter,
    *,
    policy: RoutingPolicy,
) -> StructuralRoutingResult:
    if not isinstance(request, StructuralRoutingRequest):
        raise ValueError("request must be a StructuralRoutingRequest")
    if policy not in _MODEL_POLICIES:
        raise ValueError("policy must be model-capable")
    model_request = build_router_model_request(request)
    try:
        response = adapter.generate(model_request)
    except ModelAdapterError:
        return StructuralRoutingResult(
            request_id=request.request_id,
            policy=policy,
            status=RoutingInferenceStatus.MODEL_ERROR,
            source=RoutingInferenceSource.FAIL_CLOSED,
            structural_need=StructuralNeed(),
            model_invoked=True,
        )
    return parse_router_model_response(
        request,
        response,
        policy=policy,
    )
