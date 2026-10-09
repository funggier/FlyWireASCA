from __future__ import annotations

import json
import math
import socket
from typing import Protocol
import urllib.error
from urllib.request import Request, urlopen

from flywire_asca.contracts.validation import require_nonempty

from .contracts import (
    ModelDescriptor,
    ModelMessage,
    ModelRequest,
    ModelResponse,
)
from .errors import (
    ModelAdapterError,
    ModelIdentityMismatchError,
    ModelNotFoundError,
    ModelProtocolError,
    ModelTimeoutError,
    ModelUnavailableError,
)


class JsonTransport(Protocol):
    def request_json(
        self,
        method: str,
        path: str,
        payload: dict[str, object] | None,
        timeout_seconds: float,
    ) -> dict[str, object]:
        ...


class UrllibJsonTransport:
    def __init__(self, base_url: str) -> None:
        require_nonempty("base_url", base_url)
        self._base_url = base_url.rstrip("/")

    def request_json(
        self,
        method: str,
        path: str,
        payload: dict[str, object] | None,
        timeout_seconds: float,
    ) -> dict[str, object]:
        url = self._base_url + path
        data = None
        headers = {"Accept": "application/json"}
        if payload is not None:
            data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            headers["Content-Type"] = "application/json"
        request = Request(url, data=data, headers=headers, method=method)
        try:
            with urlopen(request, timeout=timeout_seconds) as response:
                raw = response.read()
        except urllib.error.HTTPError as exc:
            raise ModelProtocolError(
                f"backend returned HTTP {exc.code} for {path}"
            ) from exc
        except (socket.timeout, TimeoutError) as exc:
            raise ModelTimeoutError(
                f"backend request timed out for {path}"
            ) from exc
        except urllib.error.URLError as exc:
            if isinstance(exc.reason, (socket.timeout, TimeoutError)):
                raise ModelTimeoutError(
                    f"backend request timed out for {path}"
                ) from exc
            raise ModelUnavailableError(
                f"backend unavailable for {path}"
            ) from exc

        try:
            decoded = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ModelProtocolError(
                f"backend returned invalid JSON for {path}"
            ) from exc
        if not isinstance(decoded, dict):
            raise ModelProtocolError(
                f"backend JSON response for {path} must be an object"
            )
        return decoded


def _require_mapping(name: str, value: object) -> dict[str, object]:
    if not isinstance(value, dict):
        raise ModelProtocolError(f"{name} must be an object")
    return value


def _require_list(name: str, value: object) -> list[object]:
    if not isinstance(value, list):
        raise ModelProtocolError(f"{name} must be an array")
    return value


def _require_string(name: str, value: object) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ModelProtocolError(f"{name} must be a nonblank string")
    return value


def _optional_string(name: str, value: object) -> str | None:
    if value is None:
        return None
    return _require_string(name, value)


def _optional_nonnegative_int(name: str, value: object) -> int | None:
    if value is None:
        return None
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise ModelProtocolError(f"{name} must be a nonnegative integer")
    return value


class OllamaModelAdapter:
    def __init__(
        self,
        model_name: str,
        *,
        base_url: str = "http://127.0.0.1:11434",
        expected_digest: str | None = None,
        timeout_seconds: float = 120.0,
        keep_alive: str = "5m",
        transport: JsonTransport | None = None,
    ) -> None:
        require_nonempty("model_name", model_name)
        require_nonempty("base_url", base_url)
        if expected_digest is not None:
            require_nonempty("expected_digest", expected_digest)
        timeout = float(timeout_seconds)
        if not math.isfinite(timeout) or timeout <= 0.0:
            raise ValueError("timeout_seconds must be finite and positive")
        require_nonempty("keep_alive", keep_alive)
        self._model_name = model_name
        self._expected_digest = expected_digest
        self._timeout_seconds = timeout
        self._keep_alive = keep_alive
        self._transport = transport or UrllibJsonTransport(base_url)
        self._descriptor: ModelDescriptor | None = None

    def inspect(self) -> ModelDescriptor:
        if self._descriptor is not None:
            return self._descriptor

        version_payload = self._transport.request_json(
            "GET",
            "/api/version",
            None,
            self._timeout_seconds,
        )
        version = _require_string(
            "version",
            version_payload.get("version"),
        )

        tags_payload = self._transport.request_json(
            "GET",
            "/api/tags",
            None,
            self._timeout_seconds,
        )
        models = _require_list("models", tags_payload.get("models"))
        selected: dict[str, object] | None = None
        for item in models:
            model = _require_mapping("models[]", item)
            if model.get("name") == self._model_name:
                selected = model
                break
        if selected is None:
            raise ModelNotFoundError(
                f"model tag not found: {self._model_name}"
            )
        digest = _require_string("model digest", selected.get("digest"))
        if (
            self._expected_digest is not None
            and digest != self._expected_digest
        ):
            raise ModelIdentityMismatchError(
                "model digest mismatch: "
                f"expected {self._expected_digest}, observed {digest}"
            )

        show_payload = self._transport.request_json(
            "POST",
            "/api/show",
            {"model": self._model_name},
            self._timeout_seconds,
        )
        model_info = _require_mapping(
            "model_info",
            show_payload.get("model_info"),
        )
        details = _require_mapping(
            "details",
            show_payload.get("details"),
        )
        capabilities_raw = _require_list(
            "capabilities",
            show_payload.get("capabilities"),
        )
        capabilities: list[str] = []
        for item in capabilities_raw:
            capabilities.append(_require_string("capabilities[]", item))
        canonical_capabilities = tuple(sorted(set(capabilities)))
        if len(canonical_capabilities) != len(capabilities):
            raise ModelProtocolError("capabilities must not contain duplicates")

        architecture = _optional_string(
            "general.architecture",
            model_info.get("general.architecture"),
        )
        parameter_count = _optional_nonnegative_int(
            "parameter_count",
            model_info.get("general.parameter_count"),
        )
        context_key = (
            f"{architecture}.context_length"
            if architecture is not None
            else None
        )
        embedding_key = (
            f"{architecture}.embedding_length"
            if architecture is not None
            else None
        )
        context_length = _optional_nonnegative_int(
            "context_length",
            model_info.get(context_key) if context_key else None,
        )
        embedding_length = _optional_nonnegative_int(
            "embedding_length",
            model_info.get(embedding_key) if embedding_key else None,
        )
        parameter_size = _optional_string(
            "parameter_size",
            details.get("parameter_size"),
        )
        quantization = _optional_string(
            "quantization",
            details.get("quantization_level"),
        )

        descriptor = ModelDescriptor(
            backend_name="ollama",
            backend_version=version,
            model_name=self._model_name,
            model_digest=digest,
            architecture=architecture,
            parameter_count=parameter_count,
            parameter_size=parameter_size,
            quantization=quantization,
            context_length=context_length,
            embedding_length=embedding_length,
            capabilities=canonical_capabilities,
        )
        self._descriptor = descriptor
        return descriptor

    def generate(self, request: ModelRequest) -> ModelResponse:
        descriptor = self.inspect()
        options: dict[str, object] = {
            "num_ctx": request.context_limit,
            "num_predict": request.max_output_tokens,
            "temperature": request.temperature,
        }
        if request.seed is not None:
            options["seed"] = request.seed
        payload: dict[str, object] = {
            "model": self._model_name,
            "messages": [
                {"role": message.role.value, "content": message.content}
                for message in request.messages
            ],
            "stream": False,
            "think": request.thinking,
            "keep_alive": self._keep_alive,
            "options": options,
        }
        response = self._transport.request_json(
            "POST",
            "/api/chat",
            payload,
            self._timeout_seconds,
        )
        response_model = _require_string(
            "model",
            response.get("model"),
        )
        if response_model != self._model_name:
            raise ModelProtocolError(
                f"response model mismatch: {response_model}"
            )
        if response.get("done") is not True:
            raise ModelProtocolError(
                "backend response done must be true for non-streaming generation"
            )
        message = _require_mapping(
            "message",
            response.get("message"),
        )
        message_role = _require_string(
            "message.role",
            message.get("role"),
        )
        if message_role != "assistant":
            raise ModelProtocolError(
                f"message.role must be assistant, observed {message_role}"
            )
        content = _require_string(
            "message.content",
            message.get("content"),
        )
        returned_thinking = message.get("thinking")
        if not request.thinking:
            thinking_is_empty = (
                returned_thinking is None
                or returned_thinking is False
                or (
                    isinstance(returned_thinking, str)
                    and not returned_thinking.strip()
                )
            )
            if not thinking_is_empty:
                raise ModelProtocolError(
                    "backend returned nonempty thinking while thinking is disabled"
                )

        return ModelResponse(
            request_id=request.request_id,
            model_name=response_model,
            model_digest=descriptor.model_digest,
            content=content,
            finish_reason=_optional_string(
                "done_reason",
                response.get("done_reason"),
            ),
            prompt_tokens=_optional_nonnegative_int(
                "prompt_eval_count",
                response.get("prompt_eval_count"),
            ),
            generated_tokens=_optional_nonnegative_int(
                "eval_count",
                response.get("eval_count"),
            ),
            total_duration_ns=_optional_nonnegative_int(
                "total_duration",
                response.get("total_duration"),
            ),
            load_duration_ns=_optional_nonnegative_int(
                "load_duration",
                response.get("load_duration"),
            ),
            prompt_eval_duration_ns=_optional_nonnegative_int(
                "prompt_eval_duration",
                response.get("prompt_eval_duration"),
            ),
            eval_duration_ns=_optional_nonnegative_int(
                "eval_duration",
                response.get("eval_duration"),
            ),
        )
