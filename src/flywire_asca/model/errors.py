class ModelAdapterError(RuntimeError):
    """Base error for model adapter failures."""


class ModelUnavailableError(ModelAdapterError):
    """The configured model backend cannot be reached."""


class ModelNotFoundError(ModelAdapterError):
    """The requested model tag is not installed/available."""


class ModelIdentityMismatchError(ModelAdapterError):
    """The resolved model identity differs from the pinned qualification target."""


class ModelProtocolError(ModelAdapterError):
    """The backend returned a malformed or unsupported response."""


class ModelTimeoutError(ModelAdapterError):
    """The model backend request exceeded its configured timeout."""
