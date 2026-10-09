from __future__ import annotations

from typing import Protocol

from .contracts import ModelDescriptor, ModelRequest, ModelResponse


class ModelAdapter(Protocol):
    def inspect(self) -> ModelDescriptor:
        ...

    def generate(self, request: ModelRequest) -> ModelResponse:
        ...
