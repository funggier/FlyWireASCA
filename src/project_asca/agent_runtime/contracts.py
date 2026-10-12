"""Immutable public input/result and metered inference/control evidence."""
from __future__ import annotations
from dataclasses import dataclass, field
from collections.abc import Mapping
import uuid
from .values import (FrozenRecord, FrozenMap, TerminalStatus, TerminalReason, Phase,
                     ModelPurpose, BaselinePurpose, RunVariant, count, nonblank)
from .semantics import GoalContract, VerificationRecord

@dataclass(frozen=True, slots=True)
class AgentRequest:
    text: str
    request_id: str | None = None
    language_hint: str | None = None
    def __post_init__(self):
        try:
            nonblank(self.text,"text")
            if len(self.text.encode("utf-8"))>8192:raise ValueError("request byte limit")
            if self.request_id is None:object.__setattr__(self,"request_id",str(uuid.uuid4()))
            else:nonblank(self.request_id,"request_id")
            if self.language_hint not in (None,"en","th"):raise ValueError("language_hint")
        except UnicodeError as exc:raise ValueError("invalid Unicode input") from exc

def parse_agent_request(value):
    if isinstance(value,AgentRequest):return value
    if isinstance(value,str):return AgentRequest(value)
    if not isinstance(value,Mapping):raise ValueError("request must be text or object")
    if set(value)-{"text","request_id","language_hint"} or "text" not in value:
        raise ValueError("unknown or missing request fields")
    try:return AgentRequest(**value)
    except TypeError as exc:raise ValueError("invalid request fields") from exc

@dataclass(frozen=True,slots=True)
class MetricSnapshot(FrozenRecord):
    counters: Mapping = field(default_factory=dict)
    reservations: Mapping = field(default_factory=dict)
    reported: Mapping = field(default_factory=dict)
    unavailable: tuple[str,...] = ()
    context_applicable: bool = True
    stage_seconds: Mapping = field(default_factory=dict)
    @property
    def unknown_usage(self):return bool(self.unavailable)
    @property
    def model_call_reservations(self):return self.reservations.get("model_calls",0)
    @property
    def prompt_token_reservations(self):return self.reservations.get("prompt_tokens",0)
    @property
    def output_token_reservations(self):return self.reservations.get("output_tokens",0)
    @property
    def action_reservations(self):return self.reservations.get("actions",0)
    @property
    def reported_prompt_tokens(self):
        return None if "prompt_tokens" in self.unavailable else self.reported.get("prompt_tokens",0)
    @property
    def reported_output_tokens(self):
        return None if "output_tokens" in self.unavailable else self.reported.get("output_tokens",0)
    @property
    def model_invocations(self):return self.counters.get("model_invocations",0)
    @property
    def actual_retrieval_queries(self):return self.counters.get("actual_retrieval_queries",0)
    @property
    def relation_invocations(self):return self.counters.get("relation_invocations",0)
    @property
    def primitive_actions(self):return self.counters.get("primitive_actions",0)
    @property
    def recovery_rounds(self):return self.counters.get("recovery_rounds",0)
    @property
    def strategy_attempts(self):return self.counters.get("strategy_attempts",0)
    @property
    def integrity_failures(self):return self.counters.get("integrity_failures",0)
    @property
    def active_context_peak(self):
        return self.counters.get("active_context_peak",0) if self.context_applicable else None

@dataclass(frozen=True,slots=True)
class RunSnapshot(FrozenRecord):
    run_id: str
    phase: Phase
    metrics: MetricSnapshot
    terminal: bool
    deadline: float
    integrity: bool

@dataclass(frozen=True,slots=True)
class AgentResult(FrozenRecord):
    request_id: str
    run_id: str
    status: TerminalStatus
    reason: TerminalReason
    interpreted_goal: GoalContract | None = None
    answer: str = ""
    data: object = None
    verification: VerificationRecord | None = None
    provenance: tuple = ()
    final_state_ref: str | None = None
    metrics: MetricSnapshot = field(default_factory=MetricSnapshot)
    trace: tuple = ()
    partial: bool = False
    explanation: str = ""
    def __post_init__(self):
        super(AgentResult,self).__post_init__()
        nonblank(self.request_id);nonblank(self.run_id)
        object.__setattr__(self,"status",TerminalStatus(self.status))
        object.__setattr__(self,"reason",TerminalReason(self.reason))
        if self.status is TerminalStatus.SUCCEEDED:
            if (not self.interpreted_goal or not self.verification or not self.verification.passed
                or self.verification.goal_id!=self.interpreted_goal.goal_id
                or self.reason is not TerminalReason.VERIFIED or self.partial):
                raise ValueError("success requires a matching verified nonempty goal")
        elif self.reason is TerminalReason.VERIFIED:
            raise ValueError("verified reason contradicts non-success status")

@dataclass(frozen=True,slots=True)
class PhysicalIdentity(FrozenRecord):
    model_name: str
    model_digest: str
    embedding_name: str
    embedding_digest: str
    embedding_dimension: int
    backend_version: str
    metadata: Mapping = field(default_factory=dict)
    def __post_init__(self):
        super(PhysicalIdentity,self).__post_init__()
        for v in (self.model_name,self.model_digest,self.embedding_name,self.embedding_digest,self.backend_version):nonblank(v)
        count(self.embedding_dimension)
        if self.embedding_dimension==0:raise ValueError("embedding dimension required")

@dataclass(frozen=True,slots=True)
class ModelMessage(FrozenRecord):
    role: str
    content: str
    def __post_init__(self):
        if self.role not in ("system","user","assistant"):raise ValueError("message role")
        nonblank(self.content)

@dataclass(frozen=True,slots=True)
class ModelPrompt(FrozenRecord):
    messages: tuple[ModelMessage,...]
    template_id: str
    template_hash: str
    def __post_init__(self):
        super(ModelPrompt,self).__post_init__()
        if not self.messages or any(not isinstance(m,ModelMessage) for m in self.messages):raise ValueError("model messages")
        nonblank(self.template_id);nonblank(self.template_hash)

@dataclass(frozen=True,slots=True)
class PromptBound:
    upper_tokens: int
    certificate_hash: str
    def __post_init__(self):count(self.upper_tokens);nonblank(self.certificate_hash)

@dataclass(frozen=True,slots=True)
class Usage:
    prompt_tokens: int | None
    output_tokens: int | None
    available: bool
    def __post_init__(self):
        for v in (self.prompt_tokens,self.output_tokens):
            if v is not None:count(v)
        if self.available != (self.prompt_tokens is not None and self.output_tokens is not None):
            raise ValueError("usage availability contradiction")

@dataclass(frozen=True,slots=True)
class BrokerModelRequest(FrozenRecord):
    subrequest_id: str
    prompt: ModelPrompt
    max_output_tokens: int
    context_limit: int = 8192
    temperature: float = 0.0
    seed: int = 0
    thinking: bool = False
    def __post_init__(self):
        nonblank(self.subrequest_id);count(self.max_output_tokens,limit=1024)
        if self.context_limit!=8192 or self.temperature!=0 or self.seed!=0 or self.thinking:
            raise ValueError("pinned inference settings")

@dataclass(frozen=True,slots=True)
class BrokerModelResponse(FrozenRecord):
    subrequest_id: str
    identity: PhysicalIdentity
    content: str
    usage: Usage
    timings: Mapping = field(default_factory=dict)
    transport_dispatches: int = 1
    abort_outcome: str = "NOT_REQUESTED"
    def __post_init__(self):
        super(BrokerModelResponse,self).__post_init__()
        nonblank(self.subrequest_id);count(self.transport_dispatches)
        if not isinstance(self.content,str) or len(self.content.encode("utf-8"))>65536:
            raise ValueError("bounded model output required")

@dataclass(frozen=True,slots=True)
class BrokerResult(FrozenRecord):
    response: BrokerModelResponse | None
    error: str | None
    reservation_id: str
    def __post_init__(self):
        if (self.response is None)==(self.error is None):raise ValueError("one broker outcome required")

@dataclass(frozen=True,slots=True)
class SetupMetrics(FrozenRecord):
    document_embedding_calls: int = 0
    document_count: int = 0
    setup_seconds: float = 0.0
    metadata: Mapping = field(default_factory=dict)
