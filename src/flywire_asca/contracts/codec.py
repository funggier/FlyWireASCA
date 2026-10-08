from __future__ import annotations

import json
import types
from dataclasses import fields, is_dataclass
from enum import Enum
from typing import Any, Union, get_args, get_origin, get_type_hints


def _to_primitive(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if is_dataclass(value) and not isinstance(value, type):
        return {
            field.name: _to_primitive(getattr(value, field.name))
            for field in fields(value)
        }
    if isinstance(value, tuple):
        return [_to_primitive(item) for item in value]
    if isinstance(value, list):
        return [_to_primitive(item) for item in value]
    if isinstance(value, dict):
        return {
            str(key): _to_primitive(item)
            for key, item in value.items()
        }
    return value


def dumps_contract(record: Any) -> str:
    if not is_dataclass(record) or isinstance(record, type):
        raise TypeError("contract serialization requires a dataclass instance")
    return json.dumps(
        _to_primitive(record),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def _from_primitive(type_hint: Any, value: Any) -> Any:
    if type_hint is Any:
        return value

    origin = get_origin(type_hint)
    args = get_args(type_hint)

    if origin is tuple:
        if not isinstance(value, list):
            raise TypeError("tuple contract field must decode from a JSON array")
        if len(args) == 2 and args[1] is Ellipsis:
            return tuple(_from_primitive(args[0], item) for item in value)
        if len(args) != len(value):
            raise TypeError("fixed tuple contract field has the wrong length")
        return tuple(
            _from_primitive(item_type, item)
            for item_type, item in zip(args, value, strict=True)
        )

    if origin in (Union, types.UnionType):
        if value is None and type(None) in args:
            return None
        candidates = tuple(arg for arg in args if arg is not type(None))
        if len(candidates) == 1:
            return _from_primitive(candidates[0], value)
        last_error: Exception | None = None
        for candidate in candidates:
            try:
                return _from_primitive(candidate, value)
            except (TypeError, ValueError) as exc:
                last_error = exc
        raise TypeError(f"value does not match union {type_hint!r}") from last_error

    if isinstance(type_hint, type) and issubclass(type_hint, Enum):
        return type_hint(value)

    if isinstance(type_hint, type) and is_dataclass(type_hint):
        if not isinstance(value, dict):
            raise TypeError(f"{type_hint.__name__} must decode from a JSON object")
        hints = get_type_hints(type_hint)
        kwargs = {
            field.name: _from_primitive(hints[field.name], value[field.name])
            for field in fields(type_hint)
            if field.name in value
        }
        return type_hint(**kwargs)

    return value


def loads_contract(record_type: type[Any], payload: str) -> Any:
    if not isinstance(record_type, type) or not is_dataclass(record_type):
        raise TypeError("contract deserialization requires a dataclass type")
    primitive = json.loads(payload)
    return _from_primitive(record_type, primitive)
