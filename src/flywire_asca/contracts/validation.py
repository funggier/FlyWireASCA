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


def require_mapping(
    name: str,
    value: object,
    *,
    error_type: type[Exception] = ValueError,
) -> dict[str, object]:
    if not isinstance(value, dict):
        raise error_type(f"{name} must be an object")
    return value


def require_list(
    name: str,
    value: object,
    *,
    error_type: type[Exception] = ValueError,
) -> list[object]:
    if not isinstance(value, list):
        raise error_type(f"{name} must be an array")
    return value


def require_string(
    name: str,
    value: object,
    *,
    error_type: type[Exception] = ValueError,
) -> str:
    if not isinstance(value, str) or not value.strip():
        raise error_type(f"{name} must be a nonblank string")
    return value


def optional_string(
    name: str,
    value: object,
    *,
    error_type: type[Exception] = ValueError,
) -> str | None:
    if value is None:
        return None
    return require_string(name, value, error_type=error_type)


def optional_nonnegative_int(
    name: str,
    value: object,
    *,
    error_type: type[Exception] = ValueError,
) -> int | None:
    if value is None:
        return None
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise error_type(f"{name} must be a nonnegative integer")
    return value
