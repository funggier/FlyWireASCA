"""Infrastructure/effect seams. No concrete transport or external action."""
from __future__ import annotations
from typing import Protocol
from .contracts import (PhysicalIdentity,ModelPrompt,PromptBound,BrokerModelRequest,BrokerModelResponse,EmbeddingBatch)
from .semantics import (RetrievalQuery,RetrievalBatch,RouteDecision,RelationBatch,StateSnapshot,GoalContract,WorkingContext)
from .plans import CapabilityDescriptor,AuthorizationDecision,EffectEntry,CompensationProposal,ValidatedPlan,AttemptResult,StrategyCatalog

class ClockPort(Protocol):
    def now(self)->float: ...

class CancellationToken(Protocol):
    def cancelled(self)->bool: ...

class IdentityPort(Protocol):
    def inspect(self)->PhysicalIdentity: ...

class ModelPort(Protocol):
    def generate(self,request:BrokerModelRequest,*,deadline:float,cancellation:CancellationToken)->BrokerModelResponse: ...

class TokenBoundPort(Protocol):
    def bound(self,prompt:ModelPrompt)->PromptBound: ...

class RetrievalPort(Protocol):
    def search(self,query:RetrievalQuery,*,control)->RetrievalBatch: ...

class RelationPort(Protocol):
    def expand(self,seed_ids:tuple[str,...],route:RouteDecision,*,control)->RelationBatch: ...

class AuthorizationPort(Protocol):
    def authorize(self,capability:CapabilityDescriptor,*,control)->AuthorizationDecision: ...

class ObservationPort(Protocol):
    def snapshot(self,execution_id:str)->StateSnapshot: ...

class EffectJournalPort(Protocol):
    def record(self,entry:EffectEntry)->None: ...

class CompensationPort(Protocol):
    def propose(self,entry:EffectEntry)->CompensationProposal|None: ...

class EmbeddingPort(Protocol):
    def embed(self,texts:tuple[str,...],*,deadline:float,cancellation:CancellationToken)->EmbeddingBatch: ...


class ExecutionPort(Protocol):
    def execute(self,plan:ValidatedPlan,goal:GoalContract,context:WorkingContext,*,
                initial:StateSnapshot,catalog:StrategyCatalog,registry,authorization:AuthorizationPort,
                control,attempt_id:str,execution_id:str)->AttemptResult: ...
