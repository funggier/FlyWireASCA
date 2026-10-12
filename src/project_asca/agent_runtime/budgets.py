"""Monotonic global admissions; unknown work never receives an invented refund."""
from __future__ import annotations
from collections import defaultdict
from dataclasses import dataclass
from enum import Enum
import math
import uuid
from .contracts import MetricSnapshot
from .profile import RuntimeProfile
from .values import TerminalReason, count

class BudgetStop(RuntimeError):
    def __init__(self, reason=TerminalReason.BUDGET_EXHAUSTED, message="resource limit"):
        super().__init__(message)
        self.reason=TerminalReason(reason)

class IntegrityStop(RuntimeError):
    def __init__(self, reason=TerminalReason.CONTROL_VIOLATION, message="integrity violation"):
        super().__init__(message)
        self.reason=TerminalReason(reason)

class CancelledStop(RuntimeError):
    reason=TerminalReason.CANCELLED

class Resource(str,Enum):
    MODEL_CALLS="model_calls"
    PROMPT_TOKENS="prompt_tokens"
    OUTPUT_TOKENS="output_tokens"
    CONTEXT_ROUNDS="context_rounds"
    RETRIEVAL_QUERIES="retrieval_queries"
    VECTORS_SCORED="vectors_scored"
    RELATION_INVOCATIONS="relation_invocations"
    RELATION_VISITS="relation_visits"
    RELATION_EDGES="relation_edges"
    STRATEGY_ATTEMPTS="strategy_attempts"
    RECOVERY_ROUNDS="recovery_rounds"
    ACTIONS="actions"
    TRANSITIONS="transitions"

@dataclass(frozen=True,slots=True)
class Reservation:
    reservation_id:str
    ledger_id:str
    resource:Resource
    upper_bound:int
    attempt_id:str|None=None

class BudgetLedger:
    def __init__(self,profile:RuntimeProfile,clock,started_at:float):
        self.profile=profile
        self.clock=clock
        self.deadline=started_at+profile.deadline_seconds
        self._id=str(uuid.uuid4())
        self._charged=defaultdict(int)
        self._reported=defaultdict(int)
        self._counters=defaultdict(int)
        self._attempts=defaultdict(int)
        self._open={}
        self._unknown=set()
        self._stage_seconds=defaultdict(float)
        self.context_applicable=True

    def reserve(self,resource,upper_bound,*,attempt_id=None):
        return self.reserve_bundle({resource:upper_bound},attempt_id=attempt_id)[0]

    def reserve_bundle(self,charges,*,attempt_id=None):
        if self.clock.now()>=self.deadline:
            raise BudgetStop(TerminalReason.DEADLINE_EXCEEDED,"request deadline")
        admitted={Resource(k):count(v) for k,v in charges.items()}
        for resource,n in admitted.items():
            if self._charged[resource.value]+n>getattr(self.profile,resource.value):
                raise BudgetStop(message=resource.value+" exhausted")
            local_limit=None
            if resource is Resource.ACTIONS:local_limit=self.profile.actions_per_attempt
            elif resource is Resource.RETRIEVAL_QUERIES:local_limit=self.profile.queries_per_round
            if local_limit is not None and attempt_id is not None:
                if self._attempts[(attempt_id,resource.value)]+n>local_limit:
                    raise BudgetStop(message="per-attempt "+resource.value+" exhausted")
        reservations=[]
        for resource,n in admitted.items():
            r=Reservation(str(uuid.uuid4()),self._id,resource,n,attempt_id)
            self._open[r.reservation_id]=r
            self._charged[resource.value]+=n
            if attempt_id is not None:self._attempts[(attempt_id,resource.value)]+=n
            reservations.append(r)
        return tuple(reservations)

    def reconcile(self,reservation,observed):
        if (reservation.ledger_id!=self._id
            or self._open.get(reservation.reservation_id)!=reservation):
            self.record("integrity_failures")
            raise IntegrityStop(message="reservation identity or duplicate reconciliation")
        if observed is not None:count(observed)
        self._open.pop(reservation.reservation_id)
        key=reservation.resource.value
        if observed is None:
            self._unknown.add(key)
            return
        self._reported[key]+=observed
        self._charged[key]+=observed-reservation.upper_bound
        if reservation.attempt_id is not None:
            self._attempts[(reservation.attempt_id,key)]+=observed-reservation.upper_bound
        if observed>reservation.upper_bound:
            self.record("integrity_failures")
            raise IntegrityStop(message="reported use exceeds reservation")

    def record(self,name,amount=1):
        count(amount)
        if not isinstance(name,str) or not name:raise ValueError("metric name")
        self._counters[name]+=amount

    def peak(self,name,value):
        count(value)
        self._counters[name]=max(self._counters[name],value)

    def record_span(self,name,seconds):
        if isinstance(seconds,bool) or not isinstance(seconds,(float,int)) or not math.isfinite(seconds) or seconds<0:
            raise ValueError("invalid stage latency")
        self._stage_seconds[name]+=seconds

    def snapshot(self):
        return MetricSnapshot(dict(self._counters),dict(self._charged),
                              dict(self._reported),tuple(sorted(self._unknown)),
                              self.context_applicable,dict(self._stage_seconds))
