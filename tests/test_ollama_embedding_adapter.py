from __future__ import annotations

import io
import math
import socket
import urllib.error

import pytest

from flywire_asca.embedding import (
    EmbeddingIdentityMismatchError,
    EmbeddingInputKind,
    EmbeddingModelNotFoundError,
    EmbeddingProtocolError,
    EmbeddingRequest,
    EmbeddingTimeoutError,
    EmbeddingUnavailableError,
    OllamaEmbeddingAdapter,
    UrllibEmbeddingJsonTransport,
)


TARGET_DIGEST = "embedding-digest"
QUERY_PREFIX = (
    "Instruct: Retrieve stored memories that are semantically relevant to the query.\n"
    "Query: "
)


class FakeTransport:
    def __init__(self, responses):
        self.responses = responses
        self.calls = []

    def request_json(self, method, path, payload, timeout_seconds):
        self.calls.append((method, path, payload, timeout_seconds))
        response = self.responses[(method, path)]
        if isinstance(response, Exception):
            raise response
        if callable(response):
            return response(payload)
        return response


def _responses(*, digest: str = TARGET_DIGEST, embeddings=None):
    if embeddings is None:
        embeddings = [[3.0, 4.0]]
    return {
        ("GET", "/api/version"): {"version": "0.32.15"},
        ("GET", "/api/tags"): {
            "models": [
                {
                    "name": "qwen3-embedding:0.6b",
                    "digest": digest,
                    "details": {
                        "format": "gguf",
                        "family": "qwen3",
                        "parameter_size": "639M",
                        "quantization_level": "Q8_0",
                    },
                }
            ]
        },
        ("POST", "/api/show"): {
            "model_info": {
                "general.architecture": "qwen3",
                "general.parameter_count": 595776512,
                "qwen3.context_length": 32768,
                "qwen3.embedding_length": 2,
            },
            "capabilities": ["embedding"],
            "details": {
                "format": "gguf",
                "family": "qwen3",
                "parameter_size": "639M",
                "quantization_level": "Q8_0",
            },
        },
        ("POST", "/api/embed"): {
            "model": "qwen3-embedding:0.6b",
            "embeddings": embeddings,
            "prompt_eval_count": 7,
            "total_duration": 100,
            "load_duration": 20,
        },
    }


def test_inspect_maps_runtime_identity_and_embedding_dimension():
    transport = FakeTransport(_responses())
    adapter = OllamaEmbeddingAdapter(
        "qwen3-embedding:0.6b",
        expected_digest=TARGET_DIGEST,
        expected_dimension=2,
        transport=transport,
    )
    descriptor = adapter.inspect()
    assert descriptor.backend_name == "ollama"
    assert descriptor.backend_version == "0.32.15"
    assert descriptor.model_name == "qwen3-embedding:0.6b"
    assert descriptor.model_digest == TARGET_DIGEST
    assert descriptor.architecture == "qwen3"
    assert descriptor.parameter_count == 595776512
    assert descriptor.parameter_size == "639M"
    assert descriptor.quantization == "Q8_0"
    assert descriptor.context_length == 32768
    assert descriptor.embedding_dimension == 2
    assert descriptor.capabilities == ("embedding",)
    assert [(method, path) for method, path, _, _ in transport.calls] == [
        ("GET", "/api/version"),
        ("GET", "/api/tags"),
        ("POST", "/api/show"),
    ]


def test_inspect_fails_closed_for_missing_model_digest_and_dimension_mismatch():
    missing = _responses()
    missing[("GET", "/api/tags")] = {"models": []}
    with pytest.raises(EmbeddingModelNotFoundError, match="qwen3-embedding:0.6b"):
        OllamaEmbeddingAdapter(
            "qwen3-embedding:0.6b",
            transport=FakeTransport(missing),
        ).inspect()

    with pytest.raises(EmbeddingIdentityMismatchError, match="digest"):
        OllamaEmbeddingAdapter(
            "qwen3-embedding:0.6b",
            expected_digest="expected",
            transport=FakeTransport(_responses(digest="other")),
        ).inspect()

    with pytest.raises(EmbeddingIdentityMismatchError, match="dimension"):
        OllamaEmbeddingAdapter(
            "qwen3-embedding:0.6b",
            expected_dimension=1024,
            transport=FakeTransport(_responses()),
        ).inspect()


def test_document_and_query_request_mapping_preserve_order_and_profile():
    doc_transport = FakeTransport(_responses(embeddings=[[1.0, 0.0], [0.0, 1.0]]))
    doc = OllamaEmbeddingAdapter(
        "qwen3-embedding:0.6b",
        expected_dimension=2,
        transport=doc_transport,
    )
    response = doc.embed(
        EmbeddingRequest(
            "doc-1",
            EmbeddingInputKind.DOCUMENT,
            ("first memory", "second memory"),
        )
    )
    call = [c for c in doc_transport.calls if c[1] == "/api/embed"][0]
    assert call[2] == {
        "model": "qwen3-embedding:0.6b",
        "input": ["first memory", "second memory"],
        "truncate": False,
        "keep_alive": "5m",
    }
    assert response.input_count == 2
    assert response.vectors[0].values == pytest.approx((1.0, 0.0))
    assert response.vectors[1].values == pytest.approx((0.0, 1.0))

    query_transport = FakeTransport(_responses())
    query = OllamaEmbeddingAdapter(
        "qwen3-embedding:0.6b",
        expected_dimension=2,
        transport=query_transport,
    )
    query.embed(
        EmbeddingRequest(
            "q-1",
            EmbeddingInputKind.QUERY,
            ("รถที่ใช้ไปเชียงใหม่",),
        )
    )
    payload = [c[2] for c in query_transport.calls if c[1] == "/api/embed"][0]
    assert payload["input"] == [QUERY_PREFIX + "รถที่ใช้ไปเชียงใหม่"]
    assert "tools" not in payload
    assert "images" not in payload


def test_embed_normalizes_vectors_and_maps_metadata():
    adapter = OllamaEmbeddingAdapter(
        "qwen3-embedding:0.6b",
        expected_digest=TARGET_DIGEST,
        expected_dimension=2,
        transport=FakeTransport(_responses(embeddings=[[3.0, 4.0]])),
    )
    response = adapter.embed(
        EmbeddingRequest("req", EmbeddingInputKind.DOCUMENT, ("memory",))
    )
    assert response.model_name == "qwen3-embedding:0.6b"
    assert response.model_digest == TARGET_DIGEST
    assert response.vectors[0].values == pytest.approx((0.6, 0.8))
    assert response.prompt_tokens == 7
    assert response.total_duration_ns == 100
    assert response.load_duration_ns == 20


@pytest.mark.parametrize(
    "embeddings, match",
    [
        ([], "count"),
        ([[0.0, 0.0]], "norm"),
        ([[1e-14, 0.0]], "norm"),
        ([[math.nan, 1.0]], "finite"),
        ([[math.inf, 1.0]], "finite"),
        ([[1.0, 0.0], [1.0, 0.0, 0.0]], "dimension"),
    ],
)
def test_embed_rejects_bad_count_vector_health_and_batch_dimensions(embeddings, match):
    text_count = 2 if len(embeddings) == 2 else 1
    texts = tuple(f"text-{i}" for i in range(text_count))
    adapter = OllamaEmbeddingAdapter(
        "qwen3-embedding:0.6b",
        transport=FakeTransport(_responses(embeddings=embeddings)),
    )
    with pytest.raises(EmbeddingProtocolError, match=match):
        adapter.embed(EmbeddingRequest("req", EmbeddingInputKind.DOCUMENT, texts))


def test_embed_rejects_dimension_drift_across_requests():
    calls = {"count": 0}
    responses = _responses()

    def changing(payload):
        calls["count"] += 1
        vector = [1.0, 0.0] if calls["count"] == 1 else [1.0, 0.0, 0.0]
        return {
            "model": "qwen3-embedding:0.6b",
            "embeddings": [vector],
            "prompt_eval_count": 1,
            "total_duration": 1,
            "load_duration": 0,
        }

    responses[("POST", "/api/embed")] = changing
    adapter = OllamaEmbeddingAdapter(
        "qwen3-embedding:0.6b",
        transport=FakeTransport(responses),
    )
    adapter.embed(EmbeddingRequest("a", EmbeddingInputKind.DOCUMENT, ("one",)))
    with pytest.raises(EmbeddingProtocolError, match="dimension"):
        adapter.embed(EmbeddingRequest("b", EmbeddingInputKind.DOCUMENT, ("two",)))


def test_successful_descriptor_is_cached_but_failure_is_not_cached():
    transport = FakeTransport(_responses())
    adapter = OllamaEmbeddingAdapter("qwen3-embedding:0.6b", transport=transport)
    assert adapter.inspect() is adapter.inspect()
    assert len(transport.calls) == 3

    responses = _responses()
    calls = {"count": 0}
    def flaky(payload):
        calls["count"] += 1
        if calls["count"] == 1:
            raise EmbeddingUnavailableError("temporary")
        return _responses()[("POST", "/api/show")]
    responses[("POST", "/api/show")] = flaky
    adapter = OllamaEmbeddingAdapter(
        "qwen3-embedding:0.6b",
        transport=FakeTransport(responses),
    )
    with pytest.raises(EmbeddingUnavailableError):
        adapter.inspect()
    assert adapter.inspect().model_name == "qwen3-embedding:0.6b"
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
    transport = UrllibEmbeddingJsonTransport("http://127.0.0.1:11434")

    def raise_timeout(*args, **kwargs):
        raise socket.timeout("slow")
    monkeypatch.setattr("flywire_asca.embedding.ollama.urlopen", raise_timeout)
    with pytest.raises(EmbeddingTimeoutError):
        transport.request_json("GET", "/api/version", None, 1.0)

    def raise_unavailable(*args, **kwargs):
        raise urllib.error.URLError("refused")
    monkeypatch.setattr("flywire_asca.embedding.ollama.urlopen", raise_unavailable)
    with pytest.raises(EmbeddingUnavailableError):
        transport.request_json("GET", "/api/version", None, 1.0)

    def raise_http(*args, **kwargs):
        raise urllib.error.HTTPError(
            "http://127.0.0.1:11434/api/version",
            500,
            "server error",
            hdrs=None,
            fp=io.BytesIO(b"sensitive body"),
        )
    monkeypatch.setattr("flywire_asca.embedding.ollama.urlopen", raise_http)
    with pytest.raises(EmbeddingProtocolError, match="HTTP 500") as exc:
        transport.request_json("GET", "/api/version", None, 1.0)
    assert "sensitive body" not in str(exc.value)

    monkeypatch.setattr(
        "flywire_asca.embedding.ollama.urlopen",
        lambda *args, **kwargs: _FakeHttpResponse(b"not-json"),
    )
    with pytest.raises(EmbeddingProtocolError, match="JSON"):
        transport.request_json("GET", "/api/version", None, 1.0)

    monkeypatch.setattr(
        "flywire_asca.embedding.ollama.urlopen",
        lambda *args, **kwargs: _FakeHttpResponse(b"[]"),
    )
    with pytest.raises(EmbeddingProtocolError, match="object"):
        transport.request_json("GET", "/api/version", None, 1.0)
