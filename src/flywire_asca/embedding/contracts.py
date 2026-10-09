from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from enum import Enum
import math

from flywire_asca.contracts.validation import require_nonempty, require_unique_nonempty


_RAW_NORM_EPSILON = 1e-12
_UNIT_NORM_TOLERANCE = 1e-12


class EmbeddingInputKind(str, Enum):
    DOCUMENT = "document"
    QUERY = "query"


def _require_positive_int(name: str, value: int) -> None:
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        raise ValueError(f"{name} must be a positive integer")


def _require_optional_nonnegative_int(name: str, value: int | None) -> None:
    if value is None:
        return
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise ValueError(f"{name} must be a nonnegative integer or None")


def _require_optional_text(name: str, value: str | None) -> None:
    if value is not None:
        require_nonempty(name, value)


def _l2_norm(values: tuple[float, ...]) -> float:
    return math.sqrt(sum(value * value for value in values))


@dataclass(frozen=True, slots=True)
class EmbeddingRequest:
    request_id: str
    input_kind: EmbeddingInputKind
    texts: tuple[str, ...]

    def __post_init__(self) -> None:
        require_nonempty("request_id", self.request_id)
        if not isinstance(self.input_kind, EmbeddingInputKind):
            raise ValueError("input_kind must be an EmbeddingInputKind")
        if not self.texts:
            raise ValueError("texts must not be empty")
        for text in self.texts:
            if not isinstance(text, str) or not text.strip():
                raise ValueError("texts must contain only nonempty strings")


@dataclass(frozen=True, slots=True)
class EmbeddingDescriptor:
    backend_name: str
    backend_version: str
    model_name: str
    model_digest: str | None
    architecture: str | None
    parameter_count: int | None
    parameter_size: str | None
    quantization: str | None
    context_length: int | None
    embedding_dimension: int
    capabilities: tuple[str, ...]

    def __post_init__(self) -> None:
        require_nonempty("backend_name", self.backend_name)
        require_nonempty("backend_version", self.backend_version)
        require_nonempty("model_name", self.model_name)
        _require_optional_text("model_digest", self.model_digest)
        _require_optional_text("architecture", self.architecture)
        _require_optional_text("parameter_size", self.parameter_size)
        _require_optional_text("quantization", self.quantization)
        _require_optional_nonnegative_int("parameter_count", self.parameter_count)
        _require_optional_nonnegative_int("context_length", self.context_length)
        _require_positive_int("embedding_dimension", self.embedding_dimension)
        require_unique_nonempty("capabilities", self.capabilities)
        if self.capabilities != tuple(sorted(self.capabilities)):
            raise ValueError("capabilities must be sorted in canonical order")


@dataclass(frozen=True, slots=True)
class EmbeddingVector:
    values: tuple[float, ...]
    dimension: int

    def __post_init__(self) -> None:
        _require_positive_int("dimension", self.dimension)
        if not self.values:
            raise ValueError("values must not be empty")
        if len(self.values) != self.dimension:
            raise ValueError("values length must equal dimension")
        parsed: list[float] = []
        for value in self.values:
            if (
                not isinstance(value, (int, float))
                or isinstance(value, bool)
            ):
                raise ValueError("values must contain numeric values")
            numeric = float(value)
            if not math.isfinite(numeric):
                raise ValueError("values must be finite")
            parsed.append(numeric)
        norm = _l2_norm(tuple(parsed))
        if norm <= _RAW_NORM_EPSILON:
            raise ValueError("vector norm must be greater than 1e-12")
        if not math.isclose(
            norm,
            1.0,
            rel_tol=0.0,
            abs_tol=_UNIT_NORM_TOLERANCE,
        ):
            raise ValueError("EmbeddingVector values must have unit L2 norm")


def normalize_embedding_values(
    values: Iterable[float],
    *,
    expected_dimension: int | None = None,
) -> EmbeddingVector:
    raw = tuple(values)
    if not raw:
        raise ValueError("values must not be empty")
    parsed: list[float] = []
    for value in raw:
        if (
            not isinstance(value, (int, float))
            or isinstance(value, bool)
        ):
            raise ValueError("values must contain numeric values")
        numeric = float(value)
        if not math.isfinite(numeric):
            raise ValueError("values must be finite")
        parsed.append(numeric)
    dimension = len(parsed)
    if expected_dimension is not None:
        _require_positive_int("expected_dimension", expected_dimension)
        if dimension != expected_dimension:
            raise ValueError(
                "expected_dimension does not match vector dimension"
            )
    norm = _l2_norm(tuple(parsed))
    if norm <= _RAW_NORM_EPSILON:
        raise ValueError("vector norm must be greater than 1e-12")
    normalized = tuple(value / norm for value in parsed)
    return EmbeddingVector(normalized, dimension)


@dataclass(frozen=True, slots=True)
class EmbeddingResponse:
    request_id: str
    model_name: str
    model_digest: str | None
    vectors: tuple[EmbeddingVector, ...]
    input_count: int
    prompt_tokens: int | None
    total_duration_ns: int | None
    load_duration_ns: int | None

    def __post_init__(self) -> None:
        require_nonempty("request_id", self.request_id)
        require_nonempty("model_name", self.model_name)
        _require_optional_text("model_digest", self.model_digest)
        if any(not isinstance(v, EmbeddingVector) for v in self.vectors):
            raise ValueError("vectors must contain only EmbeddingVector values")
        if not isinstance(self.input_count, int) or isinstance(self.input_count, bool):
            raise ValueError("input_count must be a nonnegative integer")
        if self.input_count < 0:
            raise ValueError("input_count must be a nonnegative integer")
        if self.input_count != len(self.vectors):
            raise ValueError("input_count must equal len(vectors)")
        for name in (
            "prompt_tokens",
            "total_duration_ns",
            "load_duration_ns",
        ):
            _require_optional_nonnegative_int(name, getattr(self, name))
