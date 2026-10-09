from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import math

from flywire_asca.contracts.validation import require_nonempty, require_unique_nonempty


class ModelRole(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


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


@dataclass(frozen=True, slots=True)
class ModelMessage:
    role: ModelRole
    content: str

    def __post_init__(self) -> None:
        require_nonempty("content", self.content)


@dataclass(frozen=True, slots=True)
class ModelRequest:
    request_id: str
    messages: tuple[ModelMessage, ...]
    max_output_tokens: int = 256
    context_limit: int = 8192
    temperature: float = 0.0
    seed: int | None = 0
    thinking: bool = False

    def __post_init__(self) -> None:
        require_nonempty("request_id", self.request_id)
        if not self.messages:
            raise ValueError("messages must not be empty")
        _require_positive_int("max_output_tokens", self.max_output_tokens)
        _require_positive_int("context_limit", self.context_limit)
        temperature = float(self.temperature)
        if not math.isfinite(temperature) or temperature < 0.0:
            raise ValueError("temperature must be finite and nonnegative")
        if self.seed is not None and (
            not isinstance(self.seed, int) or isinstance(self.seed, bool)
        ):
            raise ValueError("seed must be an integer or None")
        if not isinstance(self.thinking, bool):
            raise ValueError("thinking must be bool")


@dataclass(frozen=True, slots=True)
class ModelDescriptor:
    backend_name: str
    backend_version: str
    model_name: str
    model_digest: str | None
    architecture: str | None
    parameter_count: int | None
    parameter_size: str | None
    quantization: str | None
    context_length: int | None
    embedding_length: int | None
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
        _require_optional_nonnegative_int("embedding_length", self.embedding_length)
        require_unique_nonempty("capabilities", self.capabilities)
        if self.capabilities != tuple(sorted(self.capabilities)):
            raise ValueError("capabilities must be sorted in canonical order")


@dataclass(frozen=True, slots=True)
class ModelResponse:
    request_id: str
    model_name: str
    model_digest: str | None
    content: str
    finish_reason: str | None
    prompt_tokens: int | None
    generated_tokens: int | None
    total_duration_ns: int | None
    load_duration_ns: int | None
    prompt_eval_duration_ns: int | None
    eval_duration_ns: int | None

    def __post_init__(self) -> None:
        require_nonempty("request_id", self.request_id)
        require_nonempty("model_name", self.model_name)
        _require_optional_text("model_digest", self.model_digest)
        _require_optional_text("finish_reason", self.finish_reason)
        for name in (
            "prompt_tokens",
            "generated_tokens",
            "total_duration_ns",
            "load_duration_ns",
            "prompt_eval_duration_ns",
            "eval_duration_ns",
        ):
            _require_optional_nonnegative_int(name, getattr(self, name))
