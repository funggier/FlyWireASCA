"""Neutral plan/catalog/observation contracts; legacy types stay in adapters."""
from __future__ import annotations
from collections.abc import Mapping
from dataclasses import dataclass,field
from .values import FrozenRecord, EffectClass, canonical_bytes, count, nonblank
from .semantics import StateSnapshot,Deficit

@dataclass(frozen=True,slots=True)
class CapabilityDescriptor(FrozenRecord):
    capability_id:str
    version:str
    input_schema:Mapping
    output_schema:Mapping
    preconditions:tuple=()
    effect_class:EffectClass=EffectClass.PURE
    cost:int=1
    def __post_init__(self):
        super(CapabilityDescriptor,self).__post_init__()
        nonblank(self.capability_id);nonblank(self.version);count(self.cost)
        object.__setattr__(self,"effect_class",EffectClass(self.effect_class))

@dataclass(frozen=True,slots=True)
class StrategyDescriptor(FrozenRecord):
    strategy_id:str
    version:str
    task_kinds:tuple
    root_ref:str
    schemas:Mapping
    preconditions:tuple=()
    effects:tuple=()
    goal_compatibility:Mapping=field(default_factory=dict)
    evidence_requirements:tuple=()
    cost:int=1
    description:Mapping=field(default_factory=dict)

@dataclass(frozen=True,slots=True)
class StrategyCatalog(FrozenRecord):
    descriptors:tuple[StrategyDescriptor,...]
    procedures:tuple
    def __post_init__(self):
        super(StrategyCatalog,self).__post_init__()
        if len({d.strategy_id for d in self.descriptors})!=len(self.descriptors):
            raise ValueError("duplicate strategy identity")

@dataclass(frozen=True,slots=True)
class ValueBinding(FrozenRecord):
    source:str
    reference:str|None=None
    value:object=None
    def __post_init__(self):
        super(ValueBinding,self).__post_init__()
        if self.source not in ("literal","request","context","step"):raise ValueError("binding source")
        if self.source!="literal":nonblank(self.reference)

@dataclass(frozen=True,slots=True)
class PlanStep(FrozenRecord):
    step_id:str
    capability_id:str
    capability_version:str
    inputs:Mapping
    def __post_init__(self):
        super(PlanStep,self).__post_init__()
        for v in (self.step_id,self.capability_id,self.capability_version):nonblank(v)
        if len(canonical_bytes(self.inputs))>65536:raise ValueError("step input bound")

@dataclass(frozen=True,slots=True)
class ActionProposal(FrozenRecord):
    plan_id:str
    revision:int
    steps:tuple[PlanStep,...]
    bindings:Mapping
    root_ref:str|None=None
    def __post_init__(self):
        super(ActionProposal,self).__post_init__()
        nonblank(self.plan_id);count(self.revision)
        if len(self.steps)>32:raise ValueError("plan primitive limit")
        if self.root_ref is None and not self.steps:raise ValueError("empty plan")
        if len({s.step_id for s in self.steps})!=len(self.steps):raise ValueError("duplicate step identity")
        if len(canonical_bytes(self.bindings))>65536:raise ValueError("plan bindings bound")

@dataclass(frozen=True,slots=True)
class ValidatedPlan(FrozenRecord):
    proposal:ActionProposal
    goal_id:str
    capability_fingerprint:str
    primitive_count:int
    max_depth:int
    def __post_init__(self):
        nonblank(self.goal_id);nonblank(self.capability_fingerprint)
        count(self.primitive_count,limit=32);count(self.max_depth,limit=8)
        if self.primitive_count==0 or self.max_depth==0:raise ValueError("nonempty finite execution")

@dataclass(frozen=True,slots=True)
class PlanValidation(FrozenRecord):
    plan:ValidatedPlan|None=None
    deficits:tuple[Deficit,...]=()
    rejection:str|None=None

@dataclass(frozen=True,slots=True)
class Observation(FrozenRecord):
    run_id:str
    attempt_id:str
    execution_id:str
    step_id:str
    capability_id:str
    capability_version:str
    executed:bool
    result:object=None
    error:str|None=None
    state_ref:str|None=None
    def __post_init__(self):
        super(Observation,self).__post_init__()
        for v in (self.run_id,self.attempt_id,self.execution_id,self.step_id,self.capability_id,self.capability_version):nonblank(v)
        if not isinstance(self.executed,bool):raise ValueError("executed flag")
        if not self.executed and self.error is None:raise ValueError("blocked observation requires reason")

@dataclass(frozen=True,slots=True)
class AttemptResult(FrozenRecord):
    execution_id:str
    procedure_state:str
    observations:tuple[Observation,...]
    output:object
    final_state:StateSnapshot
    deficits:tuple[Deficit,...]=()

@dataclass(frozen=True,slots=True)
class Resolution(FrozenRecord):
    candidate:ActionProposal|None=None
    deficits:tuple[Deficit,...]=()
    unsupported:str|None=None

@dataclass(frozen=True,slots=True)
class AuthorizationDecision(FrozenRecord):
    allowed:bool
    reason:str

@dataclass(frozen=True,slots=True)
class EffectEntry(FrozenRecord):
    logical_operation_id:str
    execution_id:str
    step_id:str
    capability_id:str
    state:str
    observation_ref:str|None=None

@dataclass(frozen=True,slots=True)
class CompensationProposal(FrozenRecord):
    logical_operation_id:str
    capability_id:str
    inputs:Mapping

@dataclass(frozen=True,slots=True)
class RetryDescriptor:
    max_automatic_retries:int=0
    idempotency_class:str="INTERNAL"
    def __post_init__(self):
        if self.max_automatic_retries!=0:raise ValueError("Stage A has no hidden retry")
