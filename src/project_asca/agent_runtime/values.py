"""Dependency-free immutable JSON values and closed semantic vocabularies."""
from __future__ import annotations
from collections.abc import Mapping
from dataclasses import dataclass, fields, is_dataclass
from enum import Enum
import hashlib
import json
import math

JsonValue = str | int | float | bool | None | tuple["JsonValue", ...] | Mapping[str, "JsonValue"]

@dataclass(frozen=True, slots=True, init=False)
class FrozenMap(Mapping):
    _values: tuple
    def __init__(self, value):
        if not isinstance(value, Mapping): raise ValueError("JSON object required")
        if any(not isinstance(k,str) for k in value): raise ValueError("string keys required")
        object.__setattr__(self,"_values",tuple((k,freeze_json(v)) for k,v in sorted(value.items())))
    def __getitem__(self,key):
        for k,v in self._values:
            if key==k:return v
        raise KeyError(key)
    def __iter__(self): return (k for k,_ in self._values)
    def __len__(self): return len(self._values)

def freeze_json(value):
    if isinstance(value,FrozenMap): return value
    if isinstance(value,Mapping): return FrozenMap(value)
    if isinstance(value,(tuple,list)): return tuple(freeze_json(v) for v in value)
    if isinstance(value,Enum): return value
    if is_dataclass(value) and value.__dataclass_params__.frozen: return value
    if value is None or isinstance(value,(bool,int)): return value
    if isinstance(value,str):
        value.encode("utf-8")
        return value
    if isinstance(value,float) and math.isfinite(value): return value
    raise ValueError("value must be immutable finite JSON data")

def thaw_json(value):
    if isinstance(value,Mapping):return {k:thaw_json(v) for k,v in value.items()}
    if isinstance(value,(tuple,list)):return [thaw_json(v) for v in value]
    if isinstance(value,Enum):return value.value
    if is_dataclass(value):return {f.name:thaw_json(getattr(value,f.name)) for f in fields(value) if not f.name.startswith("_")}
    return value

def canonical_bytes(value):
    return json.dumps(thaw_json(value),ensure_ascii=False,sort_keys=True,separators=(",",":"),allow_nan=False).encode("utf-8")

def fingerprint(value):return hashlib.sha256(canonical_bytes(value)).hexdigest()

def nonblank(value,name="identity"):
    if not isinstance(value,str) or not value.strip():raise ValueError(name+" must be nonblank")
    value.encode("utf-8")
    return value

def count(value,name="count",limit=None):
    if not isinstance(value,int) or isinstance(value,bool) or value<0:raise ValueError(name+" must be nonnegative integer")
    if limit is not None and value>limit:raise ValueError(name+" exceeds limit")
    return value

class FrozenRecord:
    def __post_init__(self):
        for f in fields(self):
            value=getattr(self,f.name)
            if isinstance(value,(Mapping,list,tuple)):
                object.__setattr__(self,f.name,freeze_json(value))

class TerminalStatus(str,Enum):
    SUCCEEDED="SUCCEEDED"
    NEEDS_CLARIFICATION="NEEDS_CLARIFICATION"
    UNSUPPORTED="UNSUPPORTED"
    BOUNDED_FAILURE="BOUNDED_FAILURE"
    REJECTED="REJECTED"
    CANCELLED="CANCELLED"

class TerminalReason(str,Enum):
    VERIFIED="VERIFIED"
    INVALID_INPUT="INVALID_INPUT"
    AMBIGUOUS_INPUT="AMBIGUOUS_INPUT"
    UNSUPPORTED_CAPABILITY="UNSUPPORTED_CAPABILITY"
    MISSING_EVIDENCE="MISSING_EVIDENCE"
    INSUFFICIENT_CONFIDENCE="INSUFFICIENT_CONFIDENCE"
    INVALID_PLAN="INVALID_PLAN"
    NO_VALID_PLAN="NO_VALID_PLAN"
    PRECONDITION_UNSATISFIED="PRECONDITION_UNSATISFIED"
    OBSERVED_MISMATCH="OBSERVED_MISMATCH"
    NO_PROGRESS="NO_PROGRESS"
    BUDGET_EXHAUSTED="BUDGET_EXHAUSTED"
    DEADLINE_EXCEEDED="DEADLINE_EXCEEDED"
    MODEL_UNAVAILABLE="MODEL_UNAVAILABLE"
    IDENTITY_MISMATCH="IDENTITY_MISMATCH"
    PROVENANCE_INVALID="PROVENANCE_INVALID"
    CONTROL_VIOLATION="CONTROL_VIOLATION"
    CANCELLED="CANCELLED"

class Phase(str,Enum):
    RECEIVED="RECEIVED"
    INTERPRETING="INTERPRETING"
    ACQUIRING="ACQUIRING"
    RESOLVING="RESOLVING"
    EXECUTING="EXECUTING"
    OBSERVING="OBSERVING"
    VERIFYING="VERIFYING"
    RECOVERING="RECOVERING"
    MODEL_ASSIST="MODEL_ASSIST"
    TERMINAL="TERMINAL"

class TaskKind(str,Enum):
    FACT="FACT"
    RELATION="RELATION"
    TRANSFORM="TRANSFORM"
    STATE_GOAL="STATE_GOAL"

class EffectClass(str,Enum):
    PURE="PURE"
    IN_MEMORY="IN_MEMORY"
    EXTERNAL_READ="EXTERNAL_READ"
    EXTERNAL_WRITE="EXTERNAL_WRITE"

class ModelPurpose(str,Enum):
    INTENT="INTENT"
    STRUCTURAL_ROUTING="STRUCTURAL_ROUTING"
    QUERY_PROPOSAL="QUERY_PROPOSAL"
    PLAN_PROPOSAL="PLAN_PROPOSAL"
    PLAN_REPAIR="PLAN_REPAIR"

class BaselinePurpose(str,Enum):
    DIRECT_SOLUTION="DIRECT_SOLUTION"

class RunVariant(str,Enum):
    UNIFIED_RUNTIME="UNIFIED_RUNTIME"
    DIRECT_PINNED_MODEL="DIRECT_PINNED_MODEL"

class EvidenceKind(str,Enum):
    USER_INPUT="USER_INPUT"
    STORED_FACT="STORED_FACT"
    VECTOR_HIT="VECTOR_HIT"
    RELATION_PATH="RELATION_PATH"
    CATALOG_ENTRY="CATALOG_ENTRY"
    OBSERVATION="OBSERVATION"
    HYPOTHESIS="HYPOTHESIS"

class PredicateOperator(str,Enum):
    FACT_EQUALS="FACT_EQUALS"
    RELATION_PATH="RELATION_PATH"
    TRANSFORM_RESULT="TRANSFORM_RESULT"
    STATE_EQUALS="STATE_EQUALS"
    STATE_RANGE="STATE_RANGE"
    POLICY_VALID="POLICY_VALID"
    SCHEMA_MATCH="SCHEMA_MATCH"
