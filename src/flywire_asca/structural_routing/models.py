from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from flywire_asca.contracts.validation import require_nonempty
from flywire_asca.relational_activation import StructuralNeed


class RoutingPolicy(str, Enum):
    RULE_ONLY = "RULE_ONLY"
    MODEL_ONLY = "MODEL_ONLY"
    HYBRID_RULE_THEN_MODEL = "HYBRID_RULE_THEN_MODEL"


class RoutingInferenceStatus(str, Enum):
    DECIDED_RELATIONAL = "DECIDED_RELATIONAL"
    DECIDED_NON_RELATIONAL = "DECIDED_NON_RELATIONAL"
    ABSTAINED = "ABSTAINED"
    INVALID_MODEL_OUTPUT = "INVALID_MODEL_OUTPUT"
    MODEL_ERROR = "MODEL_ERROR"


class RoutingInferenceSource(str, Enum):
    RULE = "RULE"
    MODEL = "MODEL"
    FAIL_CLOSED = "FAIL_CLOSED"


class StructuralRoutingDecision(str, Enum):
    HYBRID_STRUCTURAL_ROUTING_JUSTIFIED = "HYBRID_STRUCTURAL_ROUTING_JUSTIFIED"
    RULE_ROUTING_SUFFICIENT = "RULE_ROUTING_SUFFICIENT"
    MODEL_ROUTING_PREFERRED = "MODEL_ROUTING_PREFERRED"
    STRUCTURAL_ROUTING_NOT_SUPPORTED = "STRUCTURAL_ROUTING_NOT_SUPPORTED"
    MIXED = "MIXED"


def _canonical_strings(name: str, values: tuple[str, ...]) -> tuple[str, ...]:
    parsed: list[str] = []
    for value in values:
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{name} must contain only nonempty strings")
        parsed.append(value)
    return tuple(sorted(set(parsed)))


def _optional_nonempty(name: str, value: str | None) -> None:
    if value is not None:
        require_nonempty(name, value)


def _optional_nonnegative_int(name: str, value: int | None) -> None:
    if value is None:
        return
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise ValueError(f"{name} must be a nonnegative integer or None")


@dataclass(frozen=True, slots=True)
class StructuralRoutingRequest:
    request_id: str
    query_text: str
    language_hint: str | None = None

    def __post_init__(self) -> None:
        require_nonempty("request_id", self.request_id)
        require_nonempty("query_text", self.query_text)
        if self.language_hint not in (None, "en", "th"):
            raise ValueError('language_hint must be None, "en", or "th"')


@dataclass(frozen=True, slots=True)
class StructuralRoutingResult:
    request_id: str
    policy: RoutingPolicy
    status: RoutingInferenceStatus
    source: RoutingInferenceSource
    structural_need: StructuralNeed
    model_invoked: bool
    rule_evidence_ids: tuple[str, ...] = ()
    model_name: str | None = None
    model_digest: str | None = None
    raw_model_output: str | None = None
    prompt_tokens: int | None = None
    generated_tokens: int | None = None
    total_duration_ns: int | None = None

    def __post_init__(self) -> None:
        require_nonempty("request_id", self.request_id)
        if not isinstance(self.policy, RoutingPolicy):
            raise ValueError("policy must be a RoutingPolicy")
        if not isinstance(self.status, RoutingInferenceStatus):
            raise ValueError("status must be a RoutingInferenceStatus")
        if not isinstance(self.source, RoutingInferenceSource):
            raise ValueError("source must be a RoutingInferenceSource")
        if not isinstance(self.structural_need, StructuralNeed):
            raise ValueError("structural_need must be a StructuralNeed")
        if not isinstance(self.model_invoked, bool):
            raise ValueError("model_invoked must be a boolean")
        object.__setattr__(
            self,
            "rule_evidence_ids",
            _canonical_strings("rule_evidence_ids", self.rule_evidence_ids),
        )
        _optional_nonempty("model_name", self.model_name)
        _optional_nonempty("model_digest", self.model_digest)
        if self.raw_model_output is not None and not isinstance(self.raw_model_output, str):
            raise ValueError("raw_model_output must be a string or None")
        for name in ("prompt_tokens", "generated_tokens", "total_duration_ns"):
            _optional_nonnegative_int(name, getattr(self, name))

        if self.status is RoutingInferenceStatus.DECIDED_RELATIONAL:
            if not self.structural_need.active:
                raise ValueError("DECIDED_RELATIONAL requires active StructuralNeed")
        elif self.structural_need.active:
            raise ValueError(
                f"{self.status.value} requires an empty StructuralNeed"
            )

        model_evidence = (
            self.model_name,
            self.model_digest,
            self.raw_model_output,
            self.prompt_tokens,
            self.generated_tokens,
            self.total_duration_ns,
        )
        if not self.model_invoked and any(value is not None for value in model_evidence):
            raise ValueError("model evidence fields require model_invoked=True")
