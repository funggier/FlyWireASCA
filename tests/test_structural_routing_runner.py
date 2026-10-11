from __future__ import annotations

import json

from flywire_asca.model import ModelResponse
from flywire_asca.structural_routing import (
    RoutingInferenceSource,
    RoutingInferenceStatus,
    RoutingPolicy,
    StructuralRoutingRequest,
    run_structural_routing,
)


class _CountingAdapter:
    def __init__(self, content: str):
        self.content = content
        self.calls = []

    def generate(self, request):
        self.calls.append(request)
        return ModelResponse(
            request_id=request.request_id,
            model_name="fixture-router",
            model_digest="fixture-digest",
            content=self.content,
            finish_reason="stop",
            prompt_tokens=5,
            generated_tokens=3,
            total_duration_ns=10,
            load_duration_ns=0,
            prompt_eval_duration_ns=1,
            eval_duration_ns=2,
        )


def _model_relational(relation="works_at"):
    return json.dumps(
        {
            "requires_relation": True,
            "required_relations": [relation],
            "requires_path_provenance": True,
        },
        separators=(",", ":"),
    )


def _model_nonrelational():
    return json.dumps(
        {
            "requires_relation": False,
            "required_relations": [],
            "requires_path_provenance": False,
        },
        separators=(",", ":"),
    )


def test_rule_only_never_calls_model_even_when_adapter_is_supplied():
    adapter = _CountingAdapter(_model_nonrelational())
    result = run_structural_routing(
        StructuralRoutingRequest("req", "Where does Ada work?"),
        policy=RoutingPolicy.RULE_ONLY,
        model_adapter=adapter,
    )
    assert adapter.calls == []
    assert result.policy is RoutingPolicy.RULE_ONLY
    assert result.source is RoutingInferenceSource.RULE
    assert result.status is RoutingInferenceStatus.DECIDED_RELATIONAL
    assert result.model_invoked is False


def test_rule_only_abstention_remains_fail_closed_without_model_call():
    adapter = _CountingAdapter(_model_relational())
    result = run_structural_routing(
        StructuralRoutingRequest("req", "Identify this Alex's employer."),
        policy=RoutingPolicy.RULE_ONLY,
        model_adapter=adapter,
    )
    assert adapter.calls == []
    assert result.status is RoutingInferenceStatus.ABSTAINED
    assert result.source is RoutingInferenceSource.FAIL_CLOSED
    assert result.structural_need.active is False


def test_model_only_invokes_exactly_once_even_for_strong_rule_positive():
    adapter = _CountingAdapter(_model_nonrelational())
    result = run_structural_routing(
        StructuralRoutingRequest("req", "Where does Ada work?"),
        policy=RoutingPolicy.MODEL_ONLY,
        model_adapter=adapter,
    )
    assert len(adapter.calls) == 1
    assert result.policy is RoutingPolicy.MODEL_ONLY
    assert result.source is RoutingInferenceSource.MODEL
    assert result.status is RoutingInferenceStatus.DECIDED_NON_RELATIONAL


def test_model_only_missing_adapter_fails_closed_as_model_error():
    result = run_structural_routing(
        StructuralRoutingRequest("req", "query"),
        policy=RoutingPolicy.MODEL_ONLY,
    )
    assert result.policy is RoutingPolicy.MODEL_ONLY
    assert result.status is RoutingInferenceStatus.MODEL_ERROR
    assert result.source is RoutingInferenceSource.FAIL_CLOSED
    assert result.structural_need.active is False
    assert result.model_invoked is False


def test_hybrid_strong_rule_positive_skips_model_and_records_hybrid_policy():
    adapter = _CountingAdapter(_model_nonrelational())
    result = run_structural_routing(
        StructuralRoutingRequest("req", "Where does Ada work?"),
        policy=RoutingPolicy.HYBRID_RULE_THEN_MODEL,
        model_adapter=adapter,
    )
    assert adapter.calls == []
    assert result.policy is RoutingPolicy.HYBRID_RULE_THEN_MODEL
    assert result.source is RoutingInferenceSource.RULE
    assert result.status is RoutingInferenceStatus.DECIDED_RELATIONAL
    assert result.model_invoked is False


def test_hybrid_strong_rule_negative_skips_model_and_records_hybrid_policy():
    adapter = _CountingAdapter(_model_relational())
    result = run_structural_routing(
        StructuralRoutingRequest("req", "What cause is stated directly?"),
        policy=RoutingPolicy.HYBRID_RULE_THEN_MODEL,
        model_adapter=adapter,
    )
    assert adapter.calls == []
    assert result.policy is RoutingPolicy.HYBRID_RULE_THEN_MODEL
    assert result.source is RoutingInferenceSource.RULE
    assert result.status is RoutingInferenceStatus.DECIDED_NON_RELATIONAL


def test_hybrid_abstention_invokes_model_exactly_once():
    adapter = _CountingAdapter(_model_relational())
    result = run_structural_routing(
        StructuralRoutingRequest("req", "Identify this Alex's employer."),
        policy=RoutingPolicy.HYBRID_RULE_THEN_MODEL,
        model_adapter=adapter,
    )
    assert len(adapter.calls) == 1
    assert result.policy is RoutingPolicy.HYBRID_RULE_THEN_MODEL
    assert result.source is RoutingInferenceSource.MODEL
    assert result.status is RoutingInferenceStatus.DECIDED_RELATIONAL
    assert result.model_invoked is True


def test_hybrid_abstention_without_adapter_fails_closed_as_model_error():
    result = run_structural_routing(
        StructuralRoutingRequest("req", "Identify this Alex's employer."),
        policy=RoutingPolicy.HYBRID_RULE_THEN_MODEL,
    )
    assert result.policy is RoutingPolicy.HYBRID_RULE_THEN_MODEL
    assert result.status is RoutingInferenceStatus.MODEL_ERROR
    assert result.source is RoutingInferenceSource.FAIL_CLOSED
    assert result.structural_need.active is False
    assert result.model_invoked is False


def test_hybrid_does_not_override_rule_result_with_model():
    adapter = _CountingAdapter(_model_nonrelational())
    result = run_structural_routing(
        StructuralRoutingRequest("req", "What caused this failure?"),
        policy=RoutingPolicy.HYBRID_RULE_THEN_MODEL,
        model_adapter=adapter,
    )
    assert adapter.calls == []
    assert result.status is RoutingInferenceStatus.DECIDED_RELATIONAL
    assert result.source is RoutingInferenceSource.RULE
