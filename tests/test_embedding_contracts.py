from __future__ import annotations

from dataclasses import FrozenInstanceError
import math
from typing import get_type_hints

import pytest

from flywire_asca.embedding import (
    EmbeddingAdapter,
    EmbeddingDescriptor,
    EmbeddingInputKind,
    EmbeddingRequest,
    EmbeddingResponse,
    EmbeddingVector,
    normalize_embedding_values,
)


def test_embedding_input_kind_vocabulary_is_backend_neutral():
    assert tuple(kind.value for kind in EmbeddingInputKind) == ("document", "query")


def test_embedding_request_is_frozen_and_validates_runtime_values():
    request = EmbeddingRequest(
        "req-1",
        EmbeddingInputKind.DOCUMENT,
        ("hello", "สวัสดี"),
    )
    assert request.texts == ("hello", "สวัสดี")
    with pytest.raises(FrozenInstanceError):
        request.request_id = "changed"  # type: ignore[misc]

    with pytest.raises(ValueError, match="request_id"):
        EmbeddingRequest("", EmbeddingInputKind.DOCUMENT, ("x",))
    with pytest.raises(ValueError, match="input_kind"):
        EmbeddingRequest("req", "document", ("x",))  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="texts"):
        EmbeddingRequest("req", EmbeddingInputKind.DOCUMENT, ())
    with pytest.raises(ValueError, match="texts"):
        EmbeddingRequest("req", EmbeddingInputKind.DOCUMENT, (" ",))
    with pytest.raises(ValueError, match="texts"):
        EmbeddingRequest("req", EmbeddingInputKind.DOCUMENT, (1,))  # type: ignore[arg-type]


def test_normalize_embedding_values_returns_unit_vector():
    vector = normalize_embedding_values((3.0, 4.0))
    assert vector.dimension == 2
    assert vector.values == pytest.approx((0.6, 0.8))
    assert math.sqrt(sum(value * value for value in vector.values)) == pytest.approx(
        1.0,
        abs=1e-12,
    )


def test_embedding_vector_guards_empty_zero_nonfinite_dimension_and_runtime_types():
    with pytest.raises(ValueError, match="values"):
        normalize_embedding_values(())
    with pytest.raises(ValueError, match="norm"):
        normalize_embedding_values((0.0, 0.0))
    with pytest.raises(ValueError, match="norm"):
        normalize_embedding_values((1e-14, 0.0))
    with pytest.raises(ValueError, match="finite"):
        normalize_embedding_values((math.nan, 1.0))
    with pytest.raises(ValueError, match="finite"):
        normalize_embedding_values((math.inf, 1.0))
    with pytest.raises(ValueError, match="expected_dimension"):
        normalize_embedding_values((1.0, 0.0), expected_dimension=3)
    with pytest.raises(ValueError, match="numeric"):
        normalize_embedding_values((True, 1.0))  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="numeric"):
        normalize_embedding_values(("1", 1.0))  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="unit"):
        EmbeddingVector((3.0, 4.0), 2)


def test_embedding_descriptor_validates_identity_dimension_capabilities_and_counts():
    descriptor = EmbeddingDescriptor(
        backend_name="local",
        backend_version="1",
        model_name="embedder",
        model_digest="digest",
        architecture="embed",
        parameter_count=123,
        parameter_size="123M",
        quantization="Q4",
        context_length=8192,
        embedding_dimension=1024,
        capabilities=("embedding",),
    )
    assert descriptor.embedding_dimension == 1024

    with pytest.raises(ValueError, match="embedding_dimension"):
        EmbeddingDescriptor(
            "b", "1", "m", None, None, None, None, None, None, 0, ()
        )
    with pytest.raises(ValueError, match="capabilities"):
        EmbeddingDescriptor(
            "b", "1", "m", None, None, None, None, None, None, 1,
            ("z", "a"),
        )
    with pytest.raises(ValueError, match="parameter_count"):
        EmbeddingDescriptor(
            "b", "1", "m", None, None, -1, None, None, None, 1, ()
        )


def test_embedding_response_validates_vector_count_and_optional_metrics():
    vector = normalize_embedding_values((1.0, 0.0))
    response = EmbeddingResponse(
        request_id="req",
        model_name="embedder",
        model_digest="digest",
        vectors=(vector,),
        input_count=1,
        prompt_tokens=3,
        total_duration_ns=10,
        load_duration_ns=2,
    )
    assert response.input_count == 1

    with pytest.raises(ValueError, match="input_count"):
        EmbeddingResponse(
            "req", "m", None, (vector,), 2, None, None, None
        )
    with pytest.raises(ValueError, match="prompt_tokens"):
        EmbeddingResponse(
            "req", "m", None, (vector,), 1, -1, None, None
        )


def test_generic_embedding_contracts_do_not_name_ollama_or_qwen():
    names = " ".join(
        cls.__name__
        for cls in (
            EmbeddingInputKind,
            EmbeddingRequest,
            EmbeddingDescriptor,
            EmbeddingVector,
            EmbeddingResponse,
            EmbeddingAdapter,
        )
    ).lower()
    assert "ollama" not in names
    assert "qwen" not in names

    hints = get_type_hints(EmbeddingAdapter.embed)
    assert hints["request"] is EmbeddingRequest
    assert hints["return"] is EmbeddingResponse
