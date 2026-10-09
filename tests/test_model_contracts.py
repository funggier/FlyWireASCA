from __future__ import annotations

from dataclasses import FrozenInstanceError
import math
from typing import get_type_hints

import pytest

from flywire_asca.model import (
    ModelAdapter,
    ModelDescriptor,
    ModelMessage,
    ModelRequest,
    ModelResponse,
    ModelRole,
)


def test_model_role_vocabulary_is_backend_neutral():
    assert tuple(role.value for role in ModelRole) == ("system", "user", "assistant")


def test_model_message_is_frozen_and_rejects_blank_content():
    message = ModelMessage(ModelRole.USER, "hello")
    assert message.content == "hello"
    with pytest.raises(FrozenInstanceError):
        message.content = "changed"  # type: ignore[misc]
    with pytest.raises(ValueError, match="content"):
        ModelMessage(ModelRole.USER, "   ")


def test_model_request_validates_messages_limits_temperature_seed_and_thinking():
    request = ModelRequest(
        request_id="req-1",
        messages=(ModelMessage(ModelRole.USER, "hello"),),
    )
    assert request.max_output_tokens == 256
    assert request.context_limit == 8192
    assert request.temperature == 0.0
    assert request.seed == 0
    assert request.thinking is False

    with pytest.raises(ValueError, match="request_id"):
        ModelRequest("", (ModelMessage(ModelRole.USER, "hello"),))
    with pytest.raises(ValueError, match="messages"):
        ModelRequest("req", ())
    with pytest.raises(ValueError, match="max_output_tokens"):
        ModelRequest("req", (ModelMessage(ModelRole.USER, "x"),), max_output_tokens=0)
    with pytest.raises(ValueError, match="context_limit"):
        ModelRequest("req", (ModelMessage(ModelRole.USER, "x"),), context_limit=0)
    with pytest.raises(ValueError, match="temperature"):
        ModelRequest("req", (ModelMessage(ModelRole.USER, "x"),), temperature=-0.1)
    with pytest.raises(ValueError, match="temperature"):
        ModelRequest("req", (ModelMessage(ModelRole.USER, "x"),), temperature=math.inf)
    with pytest.raises(ValueError, match="seed"):
        ModelRequest("req", (ModelMessage(ModelRole.USER, "x"),), seed=True)  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="thinking"):
        ModelRequest("req", (ModelMessage(ModelRole.USER, "x"),), thinking=1)  # type: ignore[arg-type]


def test_model_descriptor_is_frozen_canonical_and_validates_optional_counts():
    descriptor = ModelDescriptor(
        backend_name="local-backend",
        backend_version="1.2.3",
        model_name="example-model",
        model_digest="abc123",
        architecture="example",
        parameter_count=123,
        parameter_size="123M",
        quantization="Q4",
        context_length=8192,
        embedding_length=512,
        capabilities=("completion", "thinking"),
    )
    assert descriptor.capabilities == ("completion", "thinking")
    with pytest.raises(FrozenInstanceError):
        descriptor.model_name = "changed"  # type: ignore[misc]
    with pytest.raises(ValueError, match="capabilities"):
        ModelDescriptor(
            "b", "1", "m", None, None, None, None, None, None, None,
            ("thinking", "completion"),
        )
    with pytest.raises(ValueError, match="parameter_count"):
        ModelDescriptor(
            "b", "1", "m", None, None, -1, None, None, None, None, (),
        )
    with pytest.raises(ValueError, match="context_length"):
        ModelDescriptor(
            "b", "1", "m", None, None, None, None, None, -1, None, (),
        )


def test_model_response_allows_empty_content_but_validates_metadata_counts():
    response = ModelResponse(
        request_id="req-1",
        model_name="example-model",
        model_digest=None,
        content="",
        finish_reason=None,
        prompt_tokens=10,
        generated_tokens=2,
        total_duration_ns=100,
        load_duration_ns=10,
        prompt_eval_duration_ns=20,
        eval_duration_ns=70,
    )
    assert response.content == ""

    fields = (
        "prompt_tokens",
        "generated_tokens",
        "total_duration_ns",
        "load_duration_ns",
        "prompt_eval_duration_ns",
        "eval_duration_ns",
    )
    for field in fields:
        kwargs = {
            "request_id": "req",
            "model_name": "m",
            "model_digest": None,
            "content": "",
            "finish_reason": None,
            "prompt_tokens": None,
            "generated_tokens": None,
            "total_duration_ns": None,
            "load_duration_ns": None,
            "prompt_eval_duration_ns": None,
            "eval_duration_ns": None,
        }
        kwargs[field] = -1
        with pytest.raises(ValueError, match=field):
            ModelResponse(**kwargs)


def test_generic_contracts_and_protocol_do_not_name_ollama_or_qwen():
    names = {
        ModelRole.__name__,
        ModelMessage.__name__,
        ModelRequest.__name__,
        ModelDescriptor.__name__,
        ModelResponse.__name__,
        ModelAdapter.__name__,
    }
    lowered = " ".join(sorted(names)).lower()
    assert "ollama" not in lowered
    assert "qwen" not in lowered

    hints = get_type_hints(ModelAdapter.generate)
    assert hints["request"] is ModelRequest
    assert hints["return"] is ModelResponse

def test_public_contracts_reject_malformed_runtime_types_at_boundary():
    with pytest.raises(ValueError, match="role"):
        ModelMessage("user", "hello")  # type: ignore[arg-type]

    with pytest.raises(ValueError, match="messages"):
        ModelRequest(
            "req",
            ("not-a-message",),  # type: ignore[arg-type]
        )

    with pytest.raises(ValueError, match="temperature"):
        ModelRequest(
            "req",
            (ModelMessage(ModelRole.USER, "x"),),
            temperature=True,  # type: ignore[arg-type]
        )

    with pytest.raises(ValueError, match="content"):
        ModelResponse(
            request_id="req",
            model_name="m",
            model_digest=None,
            content=None,  # type: ignore[arg-type]
            finish_reason=None,
            prompt_tokens=None,
            generated_tokens=None,
            total_duration_ns=None,
            load_duration_ns=None,
            prompt_eval_duration_ns=None,
            eval_duration_ns=None,
        )
