from __future__ import annotations

import json

from flywire_asca.contracts import RelationType
from flywire_asca.model import ModelResponse
from flywire_asca.relational_activation import HybridRecallRequest, StructuralNeed
from flywire_asca.structural_routing import (
    RoutingInferenceStatus,
    RoutingPolicy,
    StructuralRoutingRequest,
)
from flywire_asca.structural_routing.benchmark_fixture import build_a014_frozen_fixture
from flywire_asca.structural_routing.evaluation import evaluate_routing_case
import flywire_asca.structural_routing.evaluation as evaluation_module


class _ScriptedAdapter:
    def __init__(self, required_relations):
        self.required_relations = required_relations
        self.calls = []

    def generate(self, request):
        self.calls.append(request)
        relations = [
            item.value if isinstance(item, RelationType) else item
            for item in self.required_relations
        ]
        content = json.dumps(
            {
                "requires_relation": bool(relations),
                "required_relations": relations,
                "requires_path_provenance": bool(relations),
            },
            separators=(",", ":"),
        )
        return ModelResponse(
            request_id=request.request_id,
            model_name="fixture-router",
            model_digest="fixture-digest",
            content=content,
            finish_reason="stop",
            prompt_tokens=4,
            generated_tokens=3,
            total_duration_ns=10,
            load_duration_ns=0,
            prompt_eval_duration_ns=1,
            eval_duration_ns=2,
        )


def _case(base_id: str, language: str = "en"):
    return next(
        case for case in build_a014_frozen_fixture()
        if case.base_a013_case_id == base_id and case.language == language
    )


def test_routing_receives_only_runtime_request_before_evaluator_truth(monkeypatch):
    case = _case("ownership-workplace-one-hop")
    observed = []
    original = evaluation_module.run_structural_routing

    def spy(request, *, policy, model_adapter=None):
        observed.append((request, policy, model_adapter))
        return original(request, policy=policy, model_adapter=model_adapter)

    monkeypatch.setattr(evaluation_module, "run_structural_routing", spy)
    result = evaluate_routing_case(case, policy=RoutingPolicy.RULE_ONLY, model_adapter=None)

    assert len(observed) == 1
    request, policy, adapter = observed[0]
    assert request == StructuralRoutingRequest(case.request_id, case.query_text, case.language)
    assert policy is RoutingPolicy.RULE_ONLY
    assert adapter is None
    assert not hasattr(request, "expected_structural_need")
    assert not hasattr(request, "expected_target_ids")
    assert result.expected_structural_need == case.expected_structural_need


def test_inferred_need_alone_is_inserted_into_a013_signal_gated_request(monkeypatch):
    case = _case("ownership-workplace-one-hop")
    observed = []
    original = evaluation_module.run_hybrid_recall

    def spy(request, **kwargs):
        observed.append(request)
        return original(request, **kwargs)

    monkeypatch.setattr(evaluation_module, "run_hybrid_recall", spy)
    result = evaluate_routing_case(case, policy=RoutingPolicy.RULE_ONLY, model_adapter=None)
    assert len(observed) == 1
    request = observed[0]
    assert isinstance(request, HybridRecallRequest)
    assert request.structural_need == result.routing_result.structural_need
    assert request.structural_need == StructuralNeed((RelationType.WORKS_AT,), True)
    assert not hasattr(request, "expected_target_ids")


def test_direct_control_stays_vector_direct_when_router_says_nonrelational():
    case = _case("vector-direct-causal-control")
    result = evaluate_routing_case(case, policy=RoutingPolicy.RULE_ONLY, model_adapter=None)
    assert result.routing_result.status is RoutingInferenceStatus.DECIDED_NON_RELATIONAL
    assert result.routing_result.structural_need.active is False
    assert result.relation_invoked is False
    assert result.task_success is True
    assert result.found_expected_ids == case.expected_target_ids


def test_relation_positive_recovers_only_when_inferred_relation_is_active():
    positive = _case("ownership-workplace-one-hop")
    recovered = evaluate_routing_case(positive, policy=RoutingPolicy.RULE_ONLY, model_adapter=None)
    assert recovered.routing_result.structural_need.active is True
    assert recovered.relation_invoked is True
    assert recovered.task_success is True
    assert recovered.found_expected_ids == positive.expected_target_ids

    abstaining = _case("same-name-disambiguated-ownership")
    missed = evaluate_routing_case(abstaining, policy=RoutingPolicy.RULE_ONLY, model_adapter=None)
    assert missed.routing_result.status is RoutingInferenceStatus.ABSTAINED
    assert missed.routing_result.structural_need.active is False
    assert missed.relation_invoked is False
    assert missed.task_success is False


def test_fail_closed_cycle_control_preserves_a013_safety_evidence():
    case = _case("cycle-control")
    result = evaluate_routing_case(case, policy=RoutingPolicy.RULE_ONLY, model_adapter=None)
    assert result.relation_invoked is True
    assert result.task_success is True
    assert result.identity_preserved is True
    assert result.provenance_complete is True
    assert result.budget_respected is True
    assert result.duplicate_visit_free is True


def test_wrong_inferred_relation_causes_measured_downstream_failure_without_oracle_repair():
    case = _case("ownership-workplace-one-hop")
    adapter = _ScriptedAdapter((RelationType.USED_FOR,))
    result = evaluate_routing_case(
        case, policy=RoutingPolicy.MODEL_ONLY, model_adapter=adapter
    )
    assert len(adapter.calls) == 1
    assert result.routing_result.structural_need == StructuralNeed((RelationType.USED_FOR,), True)
    assert result.expected_structural_need == StructuralNeed((RelationType.WORKS_AT,), True)
    assert result.relation_invoked is True
    assert result.task_success is False
    assert result.found_expected_ids == ()


def test_model_recovery_on_rule_abstention_flows_through_existing_a013_runtime():
    case = _case("same-name-disambiguated-ownership")
    adapter = _ScriptedAdapter((RelationType.WORKS_AT,))
    result = evaluate_routing_case(
        case, policy=RoutingPolicy.HYBRID_RULE_THEN_MODEL, model_adapter=adapter
    )
    assert len(adapter.calls) == 1
    assert result.routing_result.status is RoutingInferenceStatus.DECIDED_RELATIONAL
    assert result.relation_invoked is True
    assert result.task_success is True
    assert result.identity_preserved is True
    assert result.provenance_complete is True

