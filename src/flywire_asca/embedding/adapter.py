from __future__ import annotations

from typing import Protocol

from .contracts import EmbeddingDescriptor, EmbeddingRequest, EmbeddingResponse


class EmbeddingAdapter(Protocol):
    def inspect(self) -> EmbeddingDescriptor:
        ...

    def embed(self, request: EmbeddingRequest) -> EmbeddingResponse:
        ...
