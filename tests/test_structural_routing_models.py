from __future__ import annotations

from dataclasses import fields

import pytest

from flywire_asca.contracts import RelationType
from flywire_asca.relational_activation import StructuralNeed
from flywire_asca.structural_routing import (
    RoutingInferenceSource,
    RoutingInferenceStatus,
    RoutingPolicy,
    StructuralRoutingDecision,
    StructuralRoutingRequest,
    StructuralRoutingResult,
)


def _result(**overrides):
    values = {
        "request_id": "req-1",
        "policy": RoutingPolicy.RULE_ONLY,
        "status": RoutingInferenceStatus.DECIDED_NON_RELATIONAL,
        "source": RoutingInferenceSource.RULE,
        "structural_need": StructuralNeed(),
        "model_invoked": False,
        "rule_evidence_ids": ("rule:b", "rule:a", "rule:a"),
        "model_name": None,
        "model_digest": None,
        "raw_model_output": None,
        "prompt_tokens": None,
        "generated_tokens": None,
        "total_duration_ns": None,
    }
    values.update(overrides)
    return StructuralRoutingResult(**values)


@pytest.mark.parametrize("request_id,query_text", [("", "query"), ("   ", "query"), ("id", ""), ("id", "  ")])
def test_request_rejects_blank_required_text(request_id, query_text):
    with pytest.raises(ValueError):
        StructuralRoutingRequest(request_id, query_text)


@pytest.mark.parametrize("hint", [None, "en", "th"])
def test_request_accepts_only_supported_language_hints(hint):
    request = StructuralRoutingRequest("id", "query", hint)
    assert request.language_hint == hint


@pytest.mark.parametrize("hint", ["EN", "thai", "ja", "", " "])
def test_request_rejects_unsupported_language_hints(hint):
    with pytest.raises(ValueError):
        StructuralRoutingRequest("id", "query", hint)


def test_runtime_dataclasses_expose_no_oracle_named_fields():
    forbidden = ("target", "expected", "answer", "benchmark", "label")
    for cls in (StructuralRoutingRequest, StructuralRoutingResult):
        names = tuple(field.name.casefold() for field in fields(cls))
        assert not [name for name in names if any(word in name for word in forbidden)]


def test_enum_vocabularies_are_exact():
    assert tuple(item.value for item in RoutingPolicy) == (
        "RULE_ONLY", "MODEL_ONLY", "HYBRID_RULE_THEN_MODEL"
    )
    assert tuple(item.value for item in RoutingInferenceStatus) == (
        "DECIDED_RELATIONAL",
        "DECIDED_NON_RELATIONAL",
        "ABSTAINED",
        "INVALID_MODEL_OUTPUT",
        "MODEL_ERROR",
    )
    assert RoutingInferenceStatus.MODEL_ERROR is not RoutingInferenceStatus.DECIDED_NON_RELATIONAL
    assert tuple(item.value for item in RoutingInferenceSource) == ("RULE", "MODEL", "FAIL_CLOSED")
    assert tuple(item.value for item in StructuralRoutingDecision) == (
        "HYBRID_STRUCTURAL_ROUTING_JUSTIFIED",
        "RULE_ROUTING_SUFFICIENT",
        "MODEL_ROUTING_PREFERRED",
        "STRUCTURAL_ROUTING_NOT_SUPPORTED",
        "MIXED",
    )


def test_relational_status_requires_active_structural_need():
    with pytest.raises(ValueError, match="DECIDED_RELATIONAL"):
        _result(status=RoutingInferenceStatus.DECIDED_RELATIONAL)
    result = _result(
        status=RoutingInferenceStatus.DECIDED_RELATIONAL,
        structural_need=StructuralNeed((RelationType.WORKS_AT,), True),
    )
    assert result.structural_need.active is True


@pytest.mark.parametrize(
    "status",
    [
        RoutingInferenceStatus.DECIDED_NON_RELATIONAL,
        RoutingInferenceStatus.ABSTAINED,
        RoutingInferenceStatus.INVALID_MODEL_OUTPUT,
        RoutingInferenceStatus.MODEL_ERROR,
    ],
)
def test_nonrelational_abstain_invalid_and_error_require_empty_structural_need(status):
    with pytest.raises(ValueError):
        _result(
            status=status,
            structural_need=StructuralNeed((RelationType.WORKS_AT,), True),
        )


def test_rule_evidence_ids_are_canonicalized():
    result = _result()
    assert result.rule_evidence_ids == ("rule:a", "rule:b")
    with pytest.raises(ValueError):
        _result(rule_evidence_ids=("",))


@pytest.mark.parametrize("name", ["prompt_tokens", "generated_tokens", "total_duration_ns"])
def test_usage_fields_are_nonnegative_or_none(name):
    assert getattr(_result(model_invoked=True, **{name: None}), name) is None
    assert getattr(_result(model_invoked=True, **{name: 0}), name) == 0
    with pytest.raises(ValueError):
        _result(model_invoked=True, **{name: -1})
    with pytest.raises(ValueError):
        _result(model_invoked=True, **{name: True})


@pytest.mark.parametrize(
    "extra",
    [
        {"model_name": "qwen"},
        {"model_digest": "digest"},
        {"raw_model_output": "{}"},
        {"prompt_tokens": 1},
        {"generated_tokens": 1},
        {"total_duration_ns": 1},
    ],
)
def test_model_evidence_fields_require_model_invocation(extra):
    with pytest.raises(ValueError, match="model_invoked"):
        _result(**extra)


def test_model_invocation_may_record_identity_output_and_usage():
    result = _result(
        policy=RoutingPolicy.MODEL_ONLY,
        status=RoutingInferenceStatus.DECIDED_RELATIONAL,
        source=RoutingInferenceSource.MODEL,
        structural_need=StructuralNeed((RelationType.CAUSED_BY,), True),
        model_invoked=True,
        model_name="qwen3.5:4b",
        model_digest="digest",
        raw_model_output='{"requires_relation":true}',
        prompt_tokens=10,
        generated_tokens=5,
        total_duration_ns=100,
    )
    assert result.model_invoked is True
    assert result.model_name == "qwen3.5:4b"


def test_optional_model_text_must_be_nonblank_when_present():
    for name in ("model_name", "model_digest"):
        with pytest.raises(ValueError):
            _result(model_invoked=True, **{name: "  "})
