class EmbeddingAdapterError(RuntimeError):
    """Base error for embedding adapter failures."""


class EmbeddingUnavailableError(EmbeddingAdapterError):
    """The configured embedding backend cannot be reached."""


class EmbeddingModelNotFoundError(EmbeddingAdapterError):
    """The requested embedding model is unavailable."""


class EmbeddingIdentityMismatchError(EmbeddingAdapterError):
    """The resolved embedding model identity differs from the pinned target."""


class EmbeddingProtocolError(EmbeddingAdapterError):
    """The embedding backend returned malformed or unsupported data."""


class EmbeddingTimeoutError(EmbeddingAdapterError):
    """The embedding backend request exceeded its configured timeout."""
