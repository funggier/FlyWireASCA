"""Immutable goal, evidence and knowledge values; no evaluator truth."""
from __future__ import annotations
from dataclasses import dataclass, field
from collections.abc import Mapping
from .values import (FrozenRecord, FrozenMap, TaskKind, EffectClass, EvidenceKind,
                     PredicateOperator, canonical_bytes, fingerprint, nonblank, count)

@dataclass(frozen=True, slots=True)
class SpanBinding(FrozenRecord):
    name: str
    value: object
    original_start: int
    original_end: int
    def __post_init__(self):
        super(SpanBinding,self).__post_init__()
        nonblank(self.name)
        count(self.original_start); count(self.original_end)
        if self.original_end < self.original_start: raise ValueError("invalid original span")

@dataclass(frozen=True, slots=True)
class TaskIntent(FrozenRecord):
    kind: TaskKind
    bindings: Mapping
    constraints: Mapping = field(default_factory=dict)
    output_shape: str = "value"
    ambiguities: tuple = ()
    def __post_init__(self):
        super(TaskIntent,self).__post_init__()
        object.__setattr__(self,"kind",TaskKind(self.kind))

@dataclass(frozen=True, slots=True)
class GoalPredicate(FrozenRecord):
    predicate_id: str
    operator: PredicateOperator
    arguments: Mapping
    def __post_init__(self):
        super(GoalPredicate,self).__post_init__()
        nonblank(self.predicate_id)
        object.__setattr__(self,"operator",PredicateOperator(self.operator))

@dataclass(frozen=True, slots=True)
class GoalContract(FrozenRecord):
    goal_id: str
    kind: TaskKind
    parameters: Mapping
    predicates: tuple[GoalPredicate,...]
    required_evidence: tuple[str,...] = ()
    effect_scope: tuple[EffectClass,...] = (EffectClass.PURE,)
    def __post_init__(self):
        super(GoalContract,self).__post_init__()
        nonblank(self.goal_id)
        object.__setattr__(self,"kind",TaskKind(self.kind))
        if not self.predicates or any(not isinstance(p,GoalPredicate) for p in self.predicates):
            raise ValueError("applicable trusted predicates required")
        if len({p.predicate_id for p in self.predicates})!=len(self.predicates):
            raise ValueError("duplicate goal predicate")
        if any(EffectClass(e) not in (EffectClass.PURE,EffectClass.IN_MEMORY) for e in self.effect_scope):
            raise ValueError("Stage A goal effect scope")

@dataclass(frozen=True, slots=True)
class EvidenceRecord(FrozenRecord):
    evidence_id: str
    kind: EvidenceKind
    origin_id: str
    snapshot_id: str
    payload: Mapping
    constituent_ids: tuple[str,...] = ()
    def __post_init__(self):
        super(EvidenceRecord,self).__post_init__()
        for v in (self.evidence_id,self.origin_id,self.snapshot_id):nonblank(v)
        object.__setattr__(self,"kind",EvidenceKind(self.kind))

@dataclass(frozen=True, slots=True)
class Deficit(FrozenRecord):
    kind: str
    required_refs: tuple[str,...] = ()
    observation_refs: tuple[str,...] = ()
    explanation: str = ""
    def __post_init__(self):
        super(Deficit,self).__post_init__()
        nonblank(self.kind)

@dataclass(frozen=True, slots=True)
class EvidenceCoverage(FrozenRecord):
    required: tuple[str,...] = ()
    satisfied: tuple[str,...] = ()
    required_relation_complete: bool = False
    @property
    def complete(self): return all(r in self.satisfied for r in self.required)

@dataclass(frozen=True, slots=True)
class WorkingContext(FrozenRecord):
    context_id: str
    snapshot_id: str
    items: tuple[EvidenceRecord,...] = ()
    coverage: EvidenceCoverage = field(default_factory=EvidenceCoverage)
    deficits: tuple[Deficit,...] = ()
    canonical_bytes: int = 0
    fingerprint: str = ""
    def __post_init__(self):
        super(WorkingContext,self).__post_init__()
        nonblank(self.context_id); nonblank(self.snapshot_id)
        if len(self.items)>24:raise ValueError("context item limit")
        if len({i.evidence_id for i in self.items})!=len(self.items):raise ValueError("duplicate context identity")
        payload={"snapshot":self.snapshot_id,"items":self.items,"coverage":self.coverage}
        actual=len(canonical_bytes(payload))
        if actual>16384:raise ValueError("context byte limit")
        if self.canonical_bytes not in (0,actual):raise ValueError("context bytes mismatch")
        actual_hash=fingerprint(payload)
        if self.fingerprint not in ("",actual_hash):raise ValueError("context hash mismatch")
        object.__setattr__(self,"canonical_bytes",actual)
        object.__setattr__(self,"fingerprint",actual_hash)

@dataclass(frozen=True, slots=True)
class KnowledgeSnapshot(FrozenRecord):
    snapshot_id: str
    entities: tuple
    facts: tuple
    edges: tuple
    memories: tuple
    def __post_init__(self):
        super(KnowledgeSnapshot,self).__post_init__(); nonblank(self.snapshot_id)

@dataclass(frozen=True, slots=True)
class StateSnapshot(FrozenRecord):
    snapshot_id: str
    revision: int
    values: Mapping
    def __post_init__(self):
        super(StateSnapshot,self).__post_init__()
        nonblank(self.snapshot_id); count(self.revision)
        if len(canonical_bytes(self.values))>65536:raise ValueError("state byte limit")

@dataclass(frozen=True, slots=True)
class PredicateVerdict(FrozenRecord):
    predicate_id: str
    status: str
    evidence_refs: tuple[str,...] = ()
    explanation: str = ""
    def __post_init__(self):
        super(PredicateVerdict,self).__post_init__()
        nonblank(self.predicate_id)
        if self.status not in ("PASS","FAIL","UNRESOLVED"):raise ValueError("predicate verdict")

@dataclass(frozen=True, slots=True)
class VerificationRecord(FrozenRecord):
    goal_id: str
    predicates: tuple[PredicateVerdict,...]
    observation_refs: tuple[str,...]
    state_ref: str | None
    integrity: bool
    def __post_init__(self):
        super(VerificationRecord,self).__post_init__()
        nonblank(self.goal_id)
        if not isinstance(self.integrity,bool):raise ValueError("integrity must be boolean")
    @property
    def passed(self):
        return bool(self.predicates) and self.integrity and all(p.status=="PASS" for p in self.predicates)

@dataclass(frozen=True, slots=True)
class RetrievalQuery(FrozenRecord):
    text: str
    index_kind: str = "memory"
    filters: Mapping = field(default_factory=dict)
    top_k: int = 8
    def __post_init__(self):
        super(RetrievalQuery,self).__post_init__()
        nonblank(self.text);count(self.top_k,limit=24)
        if self.top_k==0 or self.index_kind not in ("memory","catalog"):raise ValueError("query shape")

@dataclass(frozen=True, slots=True)
class RetrievalBatch(FrozenRecord):
    hits: tuple
    actual_queries: int = 0
    cache_hits: int = 0
    vectors_scored: int = 0

@dataclass(frozen=True, slots=True)
class RouteDecision(FrozenRecord):
    status: str
    relation_types: tuple[str,...] = ()
    requires_path_provenance: bool = False
    evidence_refs: tuple[str,...] = ()
    @property
    def relational(self):return self.status=="DECIDED_RELATIONAL"

@dataclass(frozen=True, slots=True)
class RelationBatch(FrozenRecord):
    paths: tuple
    visited_ids: tuple[str,...]
    scanned_edges: int

@dataclass(frozen=True, slots=True)
class Interpretation(FrozenRecord):
    intent: TaskIntent | None = None
    clarification: str | None = None
    unsupported: str | None = None
    failure: str | None = None
    def __post_init__(self):
        super(Interpretation,self).__post_init__()
        if sum(v is not None for v in (self.intent,self.clarification,self.unsupported,self.failure))!=1:
            raise ValueError("interpretation must have exactly one outcome")

@dataclass(frozen=True, slots=True)
class RecoveryDecision(FrozenRecord):
    next_phase: str
    remedy: Mapping
    baseline_context_fingerprint: str
    baseline_plan_fingerprint: str
    reason: str

@dataclass(frozen=True,slots=True)
class RetrievalHit(FrozenRecord):
    evidence:EvidenceRecord
    similarity:float
    query_id:str
    entity_ids:tuple[str,...]
    embedding_name:str
    embedding_digest:str
    embedding_profile:str="a015-qwen-embedding-v1"
    def __post_init__(self):
        import math
        super(RetrievalHit,self).__post_init__()
        if isinstance(self.similarity,bool) or not isinstance(self.similarity,(int,float)) or not math.isfinite(self.similarity) or not -1<=self.similarity<=1:
            raise ValueError("retrieval similarity")
        for value in (self.query_id,self.embedding_name,self.embedding_digest,self.embedding_profile):nonblank(value)
