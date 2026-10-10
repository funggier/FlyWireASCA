from __future__ import annotations

import json
import math
import socket
from functools import partial
from typing import Protocol
import urllib.error
from urllib.request import Request, urlopen

from flywire_asca.contracts.validation import (
    optional_nonnegative_int as _shared_optional_nonnegative_int,
    optional_string as _shared_optional_string,
    require_list as _shared_require_list,
    require_mapping as _shared_require_mapping,
    require_nonempty,
    require_string as _shared_require_string,
)

from .contracts import (
    EmbeddingDescriptor,
    EmbeddingInputKind,
    EmbeddingRequest,
    EmbeddingResponse,
    normalize_embedding_values,
)
from .errors import (
    EmbeddingIdentityMismatchError,
    EmbeddingModelNotFoundError,
    EmbeddingProtocolError,
    EmbeddingTimeoutError,
    EmbeddingUnavailableError,
)


QUERY_INSTRUCTION = (
    "Instruct: Retrieve stored memories that are semantically relevant to the query.\n"
    "Query: "
)


class EmbeddingJsonTransport(Protocol):
    def request_json(
        self,
        method: str,
        path: str,
        payload: dict[str, object] | None,
        timeout_seconds: float,
    ) -> dict[str, object]:
        ...


class UrllibEmbeddingJsonTransport:
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
            raise EmbeddingProtocolError(
                f"backend returned HTTP {exc.code} for {path}"
            ) from exc
        except (socket.timeout, TimeoutError) as exc:
            raise EmbeddingTimeoutError(
                f"embedding backend request timed out for {path}"
            ) from exc
        except urllib.error.URLError as exc:
            if isinstance(exc.reason, (socket.timeout, TimeoutError)):
                raise EmbeddingTimeoutError(
                    f"embedding backend request timed out for {path}"
                ) from exc
            raise EmbeddingUnavailableError(
                f"embedding backend unavailable for {path}"
            ) from exc

        try:
            decoded = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise EmbeddingProtocolError(
                f"backend returned invalid JSON for {path}"
            ) from exc
        if not isinstance(decoded, dict):
            raise EmbeddingProtocolError(
                f"backend JSON response for {path} must be an object"
            )
        return decoded


_require_mapping = partial(
    _shared_require_mapping,
    error_type=EmbeddingProtocolError,
)
_require_list = partial(_shared_require_list, error_type=EmbeddingProtocolError)
_require_string = partial(
    _shared_require_string,
    error_type=EmbeddingProtocolError,
)
_optional_string = partial(
    _shared_optional_string,
    error_type=EmbeddingProtocolError,
)
_optional_nonnegative_int = partial(
    _shared_optional_nonnegative_int,
    error_type=EmbeddingProtocolError,
)


class OllamaEmbeddingAdapter:
    def __init__(
        self,
        model_name: str,
        *,
        base_url: str = "http://127.0.0.1:11434",
        expected_digest: str | None = None,
        expected_dimension: int | None = None,
        timeout_seconds: float = 120.0,
        keep_alive: str = "5m",
        transport: EmbeddingJsonTransport | None = None,
    ) -> None:
        require_nonempty("model_name", model_name)
        require_nonempty("base_url", base_url)
        if expected_digest is not None:
            require_nonempty("expected_digest", expected_digest)
        if expected_dimension is not None and (
            not isinstance(expected_dimension, int)
            or isinstance(expected_dimension, bool)
            or expected_dimension <= 0
        ):
            raise ValueError("expected_dimension must be a positive integer")
        timeout = float(timeout_seconds)
        if not math.isfinite(timeout) or timeout <= 0.0:
            raise ValueError("timeout_seconds must be finite and positive")
        require_nonempty("keep_alive", keep_alive)
        self._model_name = model_name
        self._expected_digest = expected_digest
        self._expected_dimension = expected_dimension
        self._timeout_seconds = timeout
        self._keep_alive = keep_alive
        self._transport = transport or UrllibEmbeddingJsonTransport(base_url)
        self._descriptor: EmbeddingDescriptor | None = None
        self._observed_dimension: int | None = None

    def inspect(self) -> EmbeddingDescriptor:
        if self._descriptor is not None:
            return self._descriptor

        version_payload = self._transport.request_json(
            "GET", "/api/version", None, self._timeout_seconds
        )
        version = _require_string("version", version_payload.get("version"))

        tags_payload = self._transport.request_json(
            "GET", "/api/tags", None, self._timeout_seconds
        )
        models = _require_list("models", tags_payload.get("models"))
        selected: dict[str, object] | None = None
        for item in models:
            model = _require_mapping("models[]", item)
            if model.get("name") == self._model_name:
                selected = model
                break
        if selected is None:
            raise EmbeddingModelNotFoundError(
                f"embedding model tag not found: {self._model_name}"
            )
        digest = _require_string("model digest", selected.get("digest"))
        if self._expected_digest is not None and digest != self._expected_digest:
            raise EmbeddingIdentityMismatchError(
                "embedding model digest mismatch: "
                f"expected {self._expected_digest}, observed {digest}"
            )

        show_payload = self._transport.request_json(
            "POST",
            "/api/show",
            {"model": self._model_name},
            self._timeout_seconds,
        )
        model_info = _require_mapping("model_info", show_payload.get("model_info"))
        details = _require_mapping("details", show_payload.get("details"))
        architecture = _optional_string(
            "general.architecture",
            model_info.get("general.architecture"),
        )
        parameter_count = _optional_nonnegative_int(
            "parameter_count",
            model_info.get("general.parameter_count"),
        )
        context_key = f"{architecture}.context_length" if architecture else None
        embedding_key = f"{architecture}.embedding_length" if architecture else None
        context_length = _optional_nonnegative_int(
            "context_length",
            model_info.get(context_key) if context_key else None,
        )
        embedding_dimension = _optional_nonnegative_int(
            "embedding_dimension",
            model_info.get(embedding_key) if embedding_key else None,
        )
        if embedding_dimension is None or embedding_dimension <= 0:
            raise EmbeddingProtocolError(
                "embedding_dimension must be a positive integer"
            )
        if (
            self._expected_dimension is not None
            and embedding_dimension != self._expected_dimension
        ):
            raise EmbeddingIdentityMismatchError(
                "embedding dimension mismatch: "
                f"expected {self._expected_dimension}, observed {embedding_dimension}"
            )

        capabilities_raw = show_payload.get("capabilities", [])
        capabilities_list = _require_list("capabilities", capabilities_raw)
        capabilities = tuple(
            sorted(
                {
                    _require_string("capabilities[]", item)
                    for item in capabilities_list
                }
            )
        )
        parameter_size = _optional_string(
            "parameter_size", details.get("parameter_size")
        )
        quantization = _optional_string(
            "quantization", details.get("quantization_level")
        )
        descriptor = EmbeddingDescriptor(
            backend_name="ollama",
            backend_version=version,
            model_name=self._model_name,
            model_digest=digest,
            architecture=architecture,
            parameter_count=parameter_count,
            parameter_size=parameter_size,
            quantization=quantization,
            context_length=context_length,
            embedding_dimension=embedding_dimension,
            capabilities=capabilities,
        )
        self._descriptor = descriptor
        self._observed_dimension = embedding_dimension
        return descriptor

    def embed(self, request: EmbeddingRequest) -> EmbeddingResponse:
        descriptor = self.inspect()
        texts = list(request.texts)
        if request.input_kind is EmbeddingInputKind.QUERY:
            texts = [QUERY_INSTRUCTION + text for text in texts]

        payload: dict[str, object] = {
            "model": self._model_name,
            "input": texts,
            "truncate": False,
            "keep_alive": self._keep_alive,
        }
        response = self._transport.request_json(
            "POST",
            "/api/embed",
            payload,
            self._timeout_seconds,
        )
        model = _require_string("model", response.get("model"))
        if model != self._model_name:
            raise EmbeddingProtocolError(
                f"response model mismatch: {model}"
            )
        embeddings = _require_list("embeddings", response.get("embeddings"))
        if len(embeddings) != len(request.texts):
            raise EmbeddingProtocolError(
                "embedding vector count must equal input text count"
            )

        expected_dimension = self._observed_dimension or descriptor.embedding_dimension
        vectors = []
        for raw_vector in embeddings:
            raw_values = _require_list("embeddings[]", raw_vector)
            try:
                vector = normalize_embedding_values(
                    raw_values,
                    expected_dimension=expected_dimension,
                )
            except ValueError as exc:
                raise EmbeddingProtocolError(str(exc)) from exc
            if self._observed_dimension is None:
                self._observed_dimension = vector.dimension
                expected_dimension = vector.dimension
            elif vector.dimension != self._observed_dimension:
                raise EmbeddingProtocolError(
                    "embedding dimension drift detected"
                )
            vectors.append(vector)

        return EmbeddingResponse(
            request_id=request.request_id,
            model_name=model,
            model_digest=descriptor.model_digest,
            vectors=tuple(vectors),
            input_count=len(request.texts),
            prompt_tokens=_optional_nonnegative_int(
                "prompt_eval_count",
                response.get("prompt_eval_count"),
            ),
            total_duration_ns=_optional_nonnegative_int(
                "total_duration",
                response.get("total_duration"),
            ),
            load_duration_ns=_optional_nonnegative_int(
                "load_duration",
                response.get("load_duration"),
            ),
        )