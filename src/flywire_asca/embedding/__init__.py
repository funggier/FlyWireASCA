from .adapter import EmbeddingAdapter
from .contracts import (
    EmbeddingDescriptor,
    EmbeddingInputKind,
    EmbeddingRequest,
    EmbeddingResponse,
    EmbeddingVector,
    normalize_embedding_values,
)
from .ollama import OllamaEmbeddingAdapter, UrllibEmbeddingJsonTransport
from .errors import (
    EmbeddingAdapterError,
    EmbeddingIdentityMismatchError,
    EmbeddingModelNotFoundError,
    EmbeddingProtocolError,
    EmbeddingTimeoutError,
    EmbeddingUnavailableError,
)

__all__ = [
    "OllamaEmbeddingAdapter",
    "UrllibEmbeddingJsonTransport",
    "EmbeddingAdapter",
    "EmbeddingAdapterError",
    "EmbeddingDescriptor",
    "EmbeddingIdentityMismatchError",
    "EmbeddingInputKind",
    "EmbeddingModelNotFoundError",
    "EmbeddingProtocolError",
    "EmbeddingRequest",
    "EmbeddingResponse",
    "EmbeddingTimeoutError",
    "EmbeddingUnavailableError",
    "EmbeddingVector",
    "normalize_embedding_values",
]