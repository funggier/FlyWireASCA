from __future__ import annotations

import json

import pytest

from flywire_asca.contracts import RelationType
from flywire_asca.model import (
    ModelDescriptor,
    ModelResponse,
    ModelRole,
    ModelTimeoutError,
)
from flywire_asca.structural_routing import (
    RoutingInferenceSource,
    RoutingInferenceStatus,
    RoutingPolicy,
    StructuralRoutingRequest,
)
from flywire_asca.structural_routing.model_router import (
    A014_ROUTER_SYSTEM_PROMPT,
    build_router_model_request,
    parse_router_model_response,
    route_by_model,
    router_prompt_fingerprint,
)


def _response(content: str, *, request_id: str = "a014-router:req") -> ModelResponse:
    return ModelResponse(
        request_id=request_id,
        model_name="qwen3.5:4b",
        model_digest="digest",
        content=content,
        finish_reason="stop",
        prompt_tokens=12,
        generated_tokens=7,
        total_duration_ns=123,
        load_duration_ns=1,
        prompt_eval_duration_ns=2,
        eval_duration_ns=3,
    )


class _Adapter:
    def __init__(self, response=None, error=None):
        self.response = response
        self.error = error
        self.requests = []

    def inspect(self):
        return ModelDescriptor(
            backend_name="fixture",
            backend_version="1",
            model_name="qwen3.5:4b",
            model_digest="digest",
            architecture="fixture",
            parameter_count=0,
            parameter_size=None,
            quantization=None,
            context_length=8192,
            embedding_length=None,
            capabilities=("completion",),
        )

    def generate(self, request):
        self.requests.append(request)
        if self.error is not None:
            raise self.error
        return self.response


def _valid_relational_json():
    return json.dumps(
        {
            "requires_relation": True,
            "required_relations": ["works_at"],
            "requires_path_provenance": True,
        },
        separators=(",", ":"),
    )


def _valid_nonrelational_json():
    return json.dumps(
        {
            "requires_relation": False,
            "required_relations": [],
            "requires_path_provenance": False,
        },
        separators=(",", ":"),
    )


def test_model_request_is_fixed_deterministic_and_contains_only_query_runtime_input():
    request = StructuralRoutingRequest("req", "Where does Ada work?", "en")
    model_request = build_router_model_request(request)
    assert model_request.request_id == "a014-router:req"
    assert model_request.max_output_tokens == 192
    assert model_request.context_limit == 8192
    assert model_request.temperature == 0.0
    assert model_request.seed == 0
    assert model_request.thinking is False
    assert tuple(message.role for message in model_request.messages) == (
        ModelRole.SYSTEM, ModelRole.USER
    )
    assert model_request.messages[0].content == A014_ROUTER_SYSTEM_PROMPT
    assert model_request.messages[1].content == request.query_text
    prompt_lower = model_request.messages[0].content.casefold()
    for forbidden in ("target", "expected", "benchmark", "case id"):
        assert forbidden not in prompt_lower
    for relation in ("works_at", "caused_by", "occurred_before", "part_of", "used_for"):
        assert relation in prompt_lower
    for relation in ("same_name", "same_person", "similar_to", "co_occurs_with", "occurred_at"):
        assert relation not in prompt_lower


def test_prompt_fingerprint_is_stable_sha256():
    value = router_prompt_fingerprint()
    assert len(value) == 64
    assert int(value, 16) >= 0
    assert router_prompt_fingerprint() == value


def test_thai_query_is_passed_unchanged_to_user_message():
    query = "ต้นตอของเหตุขัดข้องที่สังเกตพบคืออะไร?"
    model_request = build_router_model_request(StructuralRoutingRequest("req", query, "th"))
    assert model_request.messages[1].content == query


def test_valid_relational_json_parses_to_model_structural_need_and_preserves_evidence():
    request = StructuralRoutingRequest("req", "Where does Ada work?")
    response = _response(_valid_relational_json())
    result = parse_router_model_response(request, response, policy=RoutingPolicy.MODEL_ONLY)
    assert result.status is RoutingInferenceStatus.DECIDED_RELATIONAL
    assert result.source is RoutingInferenceSource.MODEL
    assert result.structural_need.required_relations == (RelationType.WORKS_AT,)
    assert result.structural_need.requires_path_provenance is True
    assert result.model_invoked is True
    assert result.model_name == "qwen3.5:4b"
    assert result.model_digest == "digest"
    assert result.raw_model_output == response.content
    assert (result.prompt_tokens, result.generated_tokens, result.total_duration_ns) == (12, 7, 123)


def test_valid_nonrelational_json_parses_to_empty_need():
    request = StructuralRoutingRequest("req", "What fact is stated directly?")
    result = parse_router_model_response(
        request, _response(_valid_nonrelational_json()), policy=RoutingPolicy.MODEL_ONLY
    )
    assert result.status is RoutingInferenceStatus.DECIDED_NON_RELATIONAL
    assert result.source is RoutingInferenceSource.MODEL
    assert result.structural_need.active is False


@pytest.mark.parametrize(
    "content",
    [
        '{"requires_relation":true,"required_relations":["same_person"],"requires_path_provenance":true}',
        '{"requires_relation":true,"required_relations":["works_at"],"requires_path_provenance":true,"confidence":0.9}',
        'prefix {"requires_relation":false,"required_relations":[],"requires_path_provenance":false}',
        '{"requires_relation":false,"required_relations":[],"requires_path_provenance":false} suffix',
        '```json\n{"requires_relation":false,"required_relations":[],"requires_path_provenance":false}\n```',
        '{"requires_relation":true,"requires_relation":false,"required_relations":[],"requires_path_provenance":false}',
        '{"requires_relation":true,"required_relations":[],"requires_path_provenance":true}',
        '{"requires_relation":false,"required_relations":["works_at"],"requires_path_provenance":false}',
        '{"requires_relation":false,"required_relations":[],"requires_path_provenance":true}',
        '{"requires_relation":true,"required_relations":["unknown"],"requires_path_provenance":true}',
        '[]',
        'not-json',
    ],
)
def test_invalid_or_nonexact_model_output_fails_closed_without_salvage(content):
    request = StructuralRoutingRequest("req", "query")
    result = parse_router_model_response(
        request, _response(content), policy=RoutingPolicy.MODEL_ONLY
    )
    assert result.status is RoutingInferenceStatus.INVALID_MODEL_OUTPUT
    assert result.source is RoutingInferenceSource.FAIL_CLOSED
    assert result.structural_need.active is False
    assert result.model_invoked is True
    assert result.raw_model_output == content


def test_wrong_response_request_id_is_model_error_not_nonrelational():
    request = StructuralRoutingRequest("req", "query")
    result = parse_router_model_response(
        request,
        _response(_valid_nonrelational_json(), request_id="a014-router:other"),
        policy=RoutingPolicy.MODEL_ONLY,
    )
    assert result.status is RoutingInferenceStatus.MODEL_ERROR
    assert result.source is RoutingInferenceSource.FAIL_CLOSED
    assert result.structural_need.active is False
    assert result.status is not RoutingInferenceStatus.DECIDED_NON_RELATIONAL


def test_route_by_model_calls_adapter_once_and_returns_parsed_result():
    adapter = _Adapter(_response(_valid_relational_json()))
    request = StructuralRoutingRequest("req", "Where does Ada work?")
    result = route_by_model(request, adapter, policy=RoutingPolicy.MODEL_ONLY)
    assert len(adapter.requests) == 1
    assert adapter.requests[0] == build_router_model_request(request)
    assert result.status is RoutingInferenceStatus.DECIDED_RELATIONAL


def test_model_adapter_error_becomes_fail_closed_model_error():
    adapter = _Adapter(error=ModelTimeoutError("timeout"))
    result = route_by_model(
        StructuralRoutingRequest("req", "query"),
        adapter,
        policy=RoutingPolicy.MODEL_ONLY,
    )
    assert len(adapter.requests) == 1
    assert result.status is RoutingInferenceStatus.MODEL_ERROR
    assert result.source is RoutingInferenceSource.FAIL_CLOSED
    assert result.structural_need.active is False
    assert result.model_invoked is True
    assert result.model_name is None
    assert result.raw_model_output is None


def test_model_router_rejects_rule_only_policy():
    adapter = _Adapter(_response(_valid_nonrelational_json()))
    with pytest.raises(ValueError, match="model-capable"):
        route_by_model(
            StructuralRoutingRequest("req", "query"),
            adapter,
            policy=RoutingPolicy.RULE_ONLY,
        )
