from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from flywire_asca.contracts import ActivationBudget
from flywire_asca.contracts.validation import require_nonempty


class ExpansionTrigger(str, Enum):
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"
    MEMORY_BUDGET_TRUNCATED = "MEMORY_BUDGET_TRUNCATED"
    WORKING_SET_BUDGET_TRUNCATED = "WORKING_SET_BUDGET_TRUNCATED"
    MEMORY_BOUNDARY_TIE = "MEMORY_BOUNDARY_TIE"
    WORKING_SET_BOUNDARY_TIE = "WORKING_SET_BOUNDARY_TIE"


class ExpansionDecisionKind(str, Enum):
    STOP = "STOP"
    EXPAND = "EXPAND"
    EXHAUSTED = "EXHAUSTED"


class ExpansionPolicy(str, Enum):
    NO_EXPANSION = "NO_EXPANSION"
    SIGNAL_DRIVEN = "SIGNAL_DRIVEN"
    ALWAYS_EXPAND = "ALWAYS_EXPAND"


class ExpansionTerminationReason(str, Enum):
    CONTROLLER_STOP = "CONTROLLER_STOP"
    CONTROLLER_EXHAUSTED = "CONTROLLER_EXHAUSTED"
    POLICY_NO_EXPANSION = "POLICY_NO_EXPANSION"
    POLICY_MAX_SCOPE = "POLICY_MAX_SCOPE"


_TRIGGER_ORDER = {
    trigger: index
    for index, trigger in enumerate(ExpansionTrigger)
}


def _require_nonnegative_int(name: str, value: int) -> None:
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise ValueError(f"{name} must be a nonnegative integer")


def _require_positive_int(name: str, value: int) -> None:
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        raise ValueError(f"{name} must be a positive integer")


def _validate_scope_budget(budget: ActivationBudget) -> None:
    if not isinstance(budget, ActivationBudget):
        raise ValueError("budget must be an ActivationBudget")
    if budget.max_working_set_items > budget.max_memory_nodes:
        raise ValueError(
            "max_working_set_items must be <= max_memory_nodes"
        )
    if budget.max_relation_hops != 0:
        raise ValueError("max_relation_hops must be 0 for A007")
    if budget.max_expansions != 0:
        raise ValueError("max_expansions must be 0 for A007 nested A006 scopes")
    if budget.max_model_input_tokens != 0:
        raise ValueError("max_model_input_tokens must be 0 for A007")


@dataclass(frozen=True, slots=True)
class ExpansionScope:
    round_index: int
    enabled_cue_tier_count: int
    top_k: int
    budget: ActivationBudget

    def __post_init__(self) -> None:
        _require_nonnegative_int("round_index", self.round_index)
        _require_positive_int(
            "enabled_cue_tier_count",
            self.enabled_cue_tier_count,
        )
        _require_positive_int("top_k", self.top_k)
        _validate_scope_budget(self.budget)


def _scope_shape(scope: ExpansionScope) -> tuple[int, int, int, int]:
    return (
        scope.enabled_cue_tier_count,
        scope.top_k,
        scope.budget.max_memory_nodes,
        scope.budget.max_working_set_items,
    )


def _validate_wider_scope(previous: ExpansionScope, current: ExpansionScope) -> None:
    if current.enabled_cue_tier_count < previous.enabled_cue_tier_count:
        raise ValueError("enabled_cue_tier_count must not decrease")
    if current.top_k < previous.top_k:
        raise ValueError("top_k must not decrease")
    if current.budget.max_memory_nodes < previous.budget.max_memory_nodes:
        raise ValueError("max_memory_nodes must not decrease")
    if (
        current.budget.max_working_set_items
        < previous.budget.max_working_set_items
    ):
        raise ValueError("max_working_set_items must not decrease")
    if _scope_shape(current) == _scope_shape(previous):
        raise ValueError("expansion scope must not be a no-op")


@dataclass(frozen=True, slots=True)
class ExpansionProfile:
    profile_name: str
    scopes: tuple[ExpansionScope, ...]

    def __post_init__(self) -> None:
        require_nonempty("profile_name", self.profile_name)
        if not self.scopes:
            raise ValueError("scopes must not be empty")
        if any(not isinstance(scope, ExpansionScope) for scope in self.scopes):
            raise ValueError("scopes must contain only ExpansionScope values")
        if self.scopes[0].round_index != 0:
            raise ValueError("first scope round_index must be 0")
        for index, scope in enumerate(self.scopes):
            if scope.round_index != index:
                raise ValueError("scope round_index values must be contiguous")
            if index:
                _validate_wider_scope(self.scopes[index - 1], scope)


@dataclass(frozen=True, slots=True)
class ExpansionDecision:
    round_index: int
    kind: ExpansionDecisionKind
    triggers: tuple[ExpansionTrigger, ...]
    current_scope: ExpansionScope
    next_scope: ExpansionScope | None

    def __post_init__(self) -> None:
        _require_nonnegative_int("round_index", self.round_index)
        if not isinstance(self.kind, ExpansionDecisionKind):
            raise ValueError("kind must be an ExpansionDecisionKind")
        if not isinstance(self.current_scope, ExpansionScope):
            raise ValueError("current_scope must be an ExpansionScope")
        if self.round_index != self.current_scope.round_index:
            raise ValueError("round_index must equal current_scope.round_index")
        if self.next_scope is not None and not isinstance(
            self.next_scope,
            ExpansionScope,
        ):
            raise ValueError("next_scope must be an ExpansionScope or None")

        normalized: list[ExpansionTrigger] = []
        for trigger in self.triggers:
            if not isinstance(trigger, ExpansionTrigger):
                raise ValueError("triggers must contain ExpansionTrigger values")
            normalized.append(trigger)
        canonical = tuple(
            sorted(set(normalized), key=lambda value: _TRIGGER_ORDER[value])
        )
        object.__setattr__(self, "triggers", canonical)

        if self.kind is ExpansionDecisionKind.STOP:
            if canonical or self.next_scope is not None:
                raise ValueError("STOP requires no triggers and no next_scope")
            return

        if self.kind is ExpansionDecisionKind.EXPAND:
            if not canonical or self.next_scope is None:
                raise ValueError("EXPAND requires triggers and next_scope")
            if self.next_scope.round_index != self.current_scope.round_index + 1:
                raise ValueError("EXPAND next_scope must be the next round")
            _validate_wider_scope(self.current_scope, self.next_scope)
            return

        if self.kind is ExpansionDecisionKind.EXHAUSTED:
            if not canonical or self.next_scope is not None:
                raise ValueError("EXHAUSTED requires triggers and no next_scope")
            return

        raise ValueError("unsupported ExpansionDecisionKind")


def build_a007_primary_profile() -> ExpansionProfile:
    return ExpansionProfile(
        profile_name="a007-structural-expansion-v1",
        scopes=(
            ExpansionScope(
                round_index=0,
                enabled_cue_tier_count=1,
                top_k=12,
                budget=ActivationBudget(8, 0, 4, 0, 0),
            ),
            ExpansionScope(
                round_index=1,
                enabled_cue_tier_count=2,
                top_k=24,
                budget=ActivationBudget(12, 0, 8, 0, 0),
            ),
            ExpansionScope(
                round_index=2,
                enabled_cue_tier_count=3,
                top_k=32,
                budget=ActivationBudget(16, 0, 12, 0, 0),
            ),
        ),
    )
