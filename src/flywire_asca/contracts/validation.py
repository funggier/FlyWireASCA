from __future__ import annotations

import math
from collections.abc import Iterable


def require_nonempty(name: str, value: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a nonempty string")
    return value


def require_probability(name: str, value: float) -> float:
    value = float(value)
    if not math.isfinite(value) or not 0.0 <= value <= 1.0:
        raise ValueError(f"{name} must be finite and within [0, 1]")
    return value


def require_finite(name: str, value: float) -> float:
    value = float(value)
    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite")
    return value


def require_unique_nonempty(name: str, values: Iterable[str]) -> tuple[str, ...]:
    normalized = tuple(values)
    for value in normalized:
        require_nonempty(name, value)
    if len(set(normalized)) != len(normalized):
        raise ValueError(f"{name} must contain unique values")
    return normalized
