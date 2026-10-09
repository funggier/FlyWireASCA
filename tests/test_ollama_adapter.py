from __future__ import annotations

import io
import json
import socket
import urllib.error

import pytest

from flywire_asca.model import (
    ModelIdentityMismatchError,
    ModelMessage,
    ModelNotFoundError,
    ModelProtocolError,
    ModelRequest,
    ModelRole,
    ModelTimeoutError,
    ModelUnavailableError,
    OllamaModelAdapter,
    UrllibJsonTransport,
)


TARGET_DIGEST = "2a654d98e6fba55d452b7043684e9b57a947e393bbffa62485a7aac05ee4eefd"


class FakeTransport:
    def __init__(self, responses):
        self.responses = responses
        self.calls = []

    def request_json(self, method, path, payload, timeout_seconds):
        self.calls.append((method, path, payload, timeout_seconds))
        key = (method, path)
        response = self.responses[key]
        if isinstance(response, Exception):
            raise response
        if callable(response):
            return response(payload)
        return response


def _responses(*, digest: str = TARGET_DIGEST, content: str = "OK", thinking=None):
    return {
        ("GET", "/api/version"): {"version": "0.32.15"},
        ("GET", "/api/tags"): {
            "models": [
                {
                    "name": "qwen3.5:4b",
                    "digest": digest,
                    "details": {
                        "format": "gguf",
                        "family": "qwen35",
                        "parameter_size": "4.7B",
                        "quantization_level": "Q4_K_M",
                    },
                }
            ]
        },
        ("POST", "/api/show"): {
            "model_info": {
                "general.architecture": "qwen35",
                "general.parameter_count": 4659865088,
                "qwen35.context_length": 262144,
                "qwen35.embedding_length": 2560,
            },
            "capabilities": ["thinking", "completion", "tools", "vision"],
            "details": {
                "format": "gguf",
                "family": "qwen35",
                "parameter_size": "4.7B",
                "quantization_level": "Q4_K_M",
            },
        },
        ("POST", "/api/chat"): {
            "model": "qwen3.5:4b",
            "message": {
                "role": "assistant",
                "content": content,
                "thinking": thinking,
            },
            "done": True,
            "done_reason": "stop",
            "prompt_eval_count": 16,
            "eval_count": 2,
            "total_duration": 1000,
            "load_duration": 100,
            "prompt_eval_duration": 300,
            "eval_duration": 600,
        },
    }


def _request(*, thinking: bool = False, seed: int | None = 0):
    return ModelRequest(
        "req-1",
        (
            ModelMessage(ModelRole.SYSTEM, "Answer exactly."),
            ModelMessage(ModelRole.USER, "Reply OK"),
        ),
        max_output_tokens=256,
        context_limit=8192,
        temperature=0.0,
        seed=seed,
        thinking=thinking,
    )


def test_inspect_maps_runtime_tag_show_metadata_and_canonical_capabilities():
    transport = FakeTransport(_responses())
    adapter = OllamaModelAdapter(
        "qwen3.5:4b",
        expected_digest=TARGET_DIGEST,
        transport=transport,
    )
    descriptor = adapter.inspect()
    assert descriptor.backend_name == "ollama"
    assert descriptor.backend_version == "0.32.15"
    assert descriptor.model_name == "qwen3.5:4b"
    assert descriptor.model_digest == TARGET_DIGEST
    assert descriptor.architecture == "qwen35"
    assert descriptor.parameter_count == 4659865088
    assert descriptor.parameter_size == "4.7B"
    assert descriptor.quantization == "Q4_K_M"
    assert descriptor.context_length == 262144
    assert descriptor.embedding_length == 2560
    assert descriptor.capabilities == ("completion", "thinking", "tools", "vision")
    assert [(method, path) for method, path, _, _ in transport.calls] == [
        ("GET", "/api/version"),
        ("GET", "/api/tags"),
        ("POST", "/api/show"),
    ]


def test_inspect_fails_closed_for_missing_tag_and_digest_mismatch():
    missing = _responses()
    missing[("GET", "/api/tags")] = {"models": []}
    with pytest.raises(ModelNotFoundError, match="qwen3.5:4b"):
        OllamaModelAdapter("qwen3.5:4b", transport=FakeTransport(missing)).inspect()

    with pytest.raises(ModelIdentityMismatchError, match="digest"):
        OllamaModelAdapter(
            "qwen3.5:4b",
            expected_digest="expected-digest",
            transport=FakeTransport(_responses(digest="other-digest")),
        ).inspect()


def test_generate_maps_thinking_off_baseline_request_without_tools_or_images():
    transport = FakeTransport(_responses())
    adapter = OllamaModelAdapter(
        "qwen3.5:4b",
        expected_digest=TARGET_DIGEST,
        transport=transport,
        keep_alive="5m",
    )
    response = adapter.generate(_request())
    chat = [call for call in transport.calls if call[1] == "/api/chat"]
    assert len(chat) == 1
    method, path, payload, timeout = chat[0]
    assert method == "POST"
    assert path == "/api/chat"
    assert payload == {
        "model": "qwen3.5:4b",
        "messages": [
            {"role": "system", "content": "Answer exactly."},
            {"role": "user", "content": "Reply OK"},
        ],
        "stream": False,
        "think": False,
        "keep_alive": "5m",
        "options": {
            "num_ctx": 8192,
            "num_predict": 256,
            "temperature": 0.0,
            "seed": 0,
        },
    }
    assert isinstance(payload["think"], bool)
    assert "tools" not in payload
    assert "images" not in payload
    assert response.content == "OK"
    assert response.model_digest == TARGET_DIGEST
    assert response.finish_reason == "stop"
    assert response.prompt_tokens == 16
    assert response.generated_tokens == 2
    assert response.total_duration_ns == 1000
    assert response.load_duration_ns == 100
    assert response.prompt_eval_duration_ns == 300
    assert response.eval_duration_ns == 600


def test_generate_maps_thinking_true_as_boolean_and_omits_seed_when_none():
    transport = FakeTransport(_responses())
    adapter = OllamaModelAdapter("qwen3.5:4b", transport=transport)
    adapter.generate(_request(thinking=True, seed=None))
    payload = [call[2] for call in transport.calls if call[1] == "/api/chat"][0]
    assert payload["think"] is True
    assert "seed" not in payload["options"]


def test_generate_rejects_blank_content_and_hidden_thinking_when_disabled():
    blank = FakeTransport(_responses(content="   "))
    with pytest.raises(ModelProtocolError, match="message.content"):
        OllamaModelAdapter("qwen3.5:4b", transport=blank).generate(_request())

    hidden = FakeTransport(_responses(thinking="secret reasoning"))
    with pytest.raises(ModelProtocolError, match="thinking"):
        OllamaModelAdapter("qwen3.5:4b", transport=hidden).generate(_request())


def test_malformed_descriptor_numeric_metadata_raises_protocol_error():
    responses = _responses()
    responses[("POST", "/api/show")]["model_info"]["general.parameter_count"] = "not-an-int"
    with pytest.raises(ModelProtocolError, match="parameter_count"):
        OllamaModelAdapter("qwen3.5:4b", transport=FakeTransport(responses)).inspect()


def test_descriptor_is_cached_after_success_but_failure_is_not_cached():
    transport = FakeTransport(_responses())
    adapter = OllamaModelAdapter("qwen3.5:4b", transport=transport)
    first = adapter.inspect()
    second = adapter.inspect()
    assert first is second
    assert len(transport.calls) == 3

    calls = {"count": 0}
    responses = _responses()
    def flaky(payload):
        calls["count"] += 1
        if calls["count"] == 1:
            raise ModelUnavailableError("temporary")
        return _responses()[("POST", "/api/show")]
    responses[("POST", "/api/show")] = flaky
    flaky_adapter = OllamaModelAdapter("qwen3.5:4b", transport=FakeTransport(responses))
    with pytest.raises(ModelUnavailableError):
        flaky_adapter.inspect()
    descriptor = flaky_adapter.inspect()
    assert descriptor.model_name == "qwen3.5:4b"
    assert calls["count"] == 2


class _FakeHttpResponse:
    def __init__(self, body: bytes):
        self._body = body

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self):
        return self._body


def test_urllib_transport_maps_timeout_unavailable_http_and_invalid_json(monkeypatch):
    transport = UrllibJsonTransport("http://127.0.0.1:11434")

    def raise_timeout(*args, **kwargs):
        raise socket.timeout("slow")
    monkeypatch.setattr("flywire_asca.model.ollama.urlopen", raise_timeout)
    with pytest.raises(ModelTimeoutError):
        transport.request_json("GET", "/api/version", None, 1.0)

    def raise_unavailable(*args, **kwargs):
        raise urllib.error.URLError("refused")
    monkeypatch.setattr("flywire_asca.model.ollama.urlopen", raise_unavailable)
    with pytest.raises(ModelUnavailableError):
        transport.request_json("GET", "/api/version", None, 1.0)

    def raise_http(*args, **kwargs):
        raise urllib.error.HTTPError(
            "http://127.0.0.1:11434/api/version",
            500,
            "server error",
            hdrs=None,
            fp=io.BytesIO(b"sensitive backend body"),
        )
    monkeypatch.setattr("flywire_asca.model.ollama.urlopen", raise_http)
    with pytest.raises(ModelProtocolError, match="HTTP 500") as exc:
        transport.request_json("GET", "/api/version", None, 1.0)
    assert "sensitive backend body" not in str(exc.value)

    monkeypatch.setattr(
        "flywire_asca.model.ollama.urlopen",
        lambda *args, **kwargs: _FakeHttpResponse(b"not-json"),
    )
    with pytest.raises(ModelProtocolError, match="JSON"):
        transport.request_json("GET", "/api/version", None, 1.0)

    monkeypatch.setattr(
        "flywire_asca.model.ollama.urlopen",
        lambda *args, **kwargs: _FakeHttpResponse(b"[]"),
    )
    with pytest.raises(ModelProtocolError, match="object"):
        transport.request_json("GET", "/api/version", None, 1.0)
