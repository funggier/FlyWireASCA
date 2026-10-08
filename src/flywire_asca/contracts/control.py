from __future__ import annotations

from dataclasses import dataclass

from .enums import RetrievalState, WorkingSetKind
from .validation import (
    require_finite,
    require_nonempty,
    require_probability,
    require_unique_nonempty,
)


def _require_positive_int(name: str, value: int) -> None:
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        raise ValueError(f"{name} must be a positive integer")


def _require_nonnegative_int(name: str, value: int) -> None:
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise ValueError(f"{name} must be a nonnegative integer")


@dataclass(frozen=True, slots=True)
class ActivationBudget:
    max_memory_nodes: int
    max_relation_hops: int
    max_working_set_items: int
    max_model_input_tokens: int
    max_expansions: int

    def __post_init__(self) -> None:
        _require_positive_int("max_memory_nodes", self.max_memory_nodes)
        _require_nonnegative_int("max_relation_hops", self.max_relation_hops)
        _require_positive_int("max_working_set_items", self.max_working_set_items)
        _require_nonnegative_int("max_model_input_tokens", self.max_model_input_tokens)
        _require_nonnegative_int("max_expansions", self.max_expansions)


@dataclass(frozen=True, slots=True)
class ActivationState:
    node_id: str
    activation: float
    hop: int
    source_cue_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        require_nonempty("node_id", self.node_id)
        require_finite("activation", self.activation)
        _require_nonnegative_int("hop", self.hop)
        require_unique_nonempty("source_cue_ids", self.source_cue_ids)


@dataclass(frozen=True, slots=True)
class WorkingSetEntry:
    ref_id: str
    kind: WorkingSetKind
    activation: float
    reason: str

    def __post_init__(self) -> None:
        require_nonempty("ref_id", self.ref_id)
        require_finite("activation", self.activation)
        require_nonempty("reason", self.reason)


@dataclass(frozen=True, slots=True)
class WorkingSet:
    entries: tuple[WorkingSetEntry, ...]
    retrieval_state: RetrievalState
    budget: ActivationBudget

    def __post_init__(self) -> None:
        refs = tuple(entry.ref_id for entry in self.entries)
        if len(set(refs)) != len(refs):
            raise ValueError("working set contains duplicate ref_id values")
        if len(self.entries) > self.budget.max_working_set_items:
            raise ValueError("working set exceeds max_working_set_items budget")


@dataclass(frozen=True, slots=True)
class UncertaintySignal:
    uncertainty: float
    surprise: float
    risk: float
    reasons: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        require_probability("uncertainty", self.uncertainty)
        require_probability("surprise", self.surprise)
        require_probability("risk", self.risk)
        require_unique_nonempty("reasons", self.reasons)
