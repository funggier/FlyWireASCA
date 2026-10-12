"""Bounded compact events with capacity retained for terminal evidence."""
from dataclasses import dataclass
import uuid
from .values import FrozenRecord, canonical_bytes, count, nonblank
from .budgets import BudgetStop, IntegrityStop

@dataclass(frozen=True,slots=True)
class TraceEvent(FrozenRecord):
    sequence:int
    kind:str
    run_id:str
    payload:object
    def __post_init__(self):
        super(TraceEvent,self).__post_init__()
        count(self.sequence);nonblank(self.kind);nonblank(self.run_id)

@dataclass(frozen=True,slots=True)
class TraceReservation:
    reservation_id:str
    ledger_id:str
    upper_bound:int

class TraceLedger:
    def __init__(self,profile):
        self.profile=profile
        self._id=str(uuid.uuid4())
        self._events=[]
        self._bytes=0
        self._reserved=0
        self._open={}
        self._terminal_count=0

    def reserve(self,event_bytes_upper_bound):
        count(event_bytes_upper_bound)
        if len(self._events)+len(self._open)>=self.profile.trace_events-2:
            raise BudgetStop(message="trace event limit")
        if self._bytes+self._reserved+event_bytes_upper_bound>self.profile.trace_bytes-2048:
            raise BudgetStop(message="trace byte limit")
        r=TraceReservation(str(uuid.uuid4()),self._id,event_bytes_upper_bound)
        self._open[r.reservation_id]=r
        self._reserved+=r.upper_bound
        return r

    def append(self,reservation,event):
        if (reservation.ledger_id!=self._id or self._open.get(reservation.reservation_id)!=reservation
            or event.sequence!=len(self._events)):
            raise IntegrityStop(message="trace identity/order")
        actual=len(canonical_bytes(event))
        if actual>reservation.upper_bound:raise IntegrityStop(message="trace exceeds reservation")
        self._open.pop(reservation.reservation_id)
        self._reserved-=reservation.upper_bound
        self._bytes+=actual
        self._events.append(event)

    def terminal(self,event):
        if self._terminal_count>=2 or event.sequence!=len(self._events):
            raise IntegrityStop(message="terminal trace order/capacity")
        actual=len(canonical_bytes(event))
        if actual>1024 or self._bytes+self._reserved+actual>self.profile.trace_bytes:
            raise IntegrityStop(message="terminal evidence too large")
        self._events.append(event);self._bytes+=actual;self._terminal_count+=1

    def freeze(self):return tuple(self._events)
