"""One run's mutable control; DTOs remain immutable and dependency acyclic."""
from contextlib import contextmanager
from dataclasses import dataclass
import threading
import time
import uuid
from .contracts import AgentRequest,RunSnapshot
from .values import Phase,RunVariant,ModelPurpose,BaselinePurpose,TerminalReason
from .profile import RuntimeProfile
from .budgets import BudgetLedger,Resource,BudgetStop,CancelledStop,IntegrityStop
from .trace import TraceLedger,TraceEvent

class MonotonicClock:
    def now(self):return time.monotonic()

class Cancellation:
    def __init__(self):self._event=threading.Event()
    def cancel(self):self._event.set()
    def cancelled(self):return self._event.is_set()

@dataclass
class RunControl:
    run_id:str
    request:AgentRequest
    profile:RuntimeProfile
    ledger:BudgetLedger
    trace:TraceLedger
    clock:object
    cancellation:object
    variant:RunVariant=RunVariant.UNIFIED_RUNTIME
    phase:Phase=Phase.RECEIVED
    terminal:bool=False
    phase_hook:object=None
    execution_receipt:object=None

    @classmethod
    def create(cls,request,profile=None,clock=None,cancellation=None,variant=RunVariant.UNIFIED_RUNTIME):
        profile=profile or RuntimeProfile();clock=clock or MonotonicClock()
        ledger=BudgetLedger(profile,clock,clock.now())
        ledger.context_applicable=variant is RunVariant.UNIFIED_RUNTIME
        return cls(str(uuid.uuid4()),request,profile,ledger,TraceLedger(profile),
                   clock,cancellation or Cancellation(),variant)

    def check_dispatch(self):
        if self.terminal:raise IntegrityStop(message="post-terminal task work")
        if self.cancellation.cancelled():raise CancelledStop("cancelled")
        if self.clock.now()>=self.ledger.deadline:
            raise BudgetStop(TerminalReason.DEADLINE_EXCEEDED,"deadline")
        if self.ledger.snapshot().integrity_failures:
            raise IntegrityStop(message="prior integrity failure")

    def snapshot(self):
        return RunSnapshot(self.run_id,self.phase,self.ledger.snapshot(),self.terminal,
                           self.ledger.deadline,not bool(self.ledger.snapshot().integrity_failures),self.execution_receipt,
                           {r.value:getattr(self.profile,r.value) for r in Resource},
                           self.clock.now(),self.cancellation.cancelled())

    def event(self,kind,payload,upper_bound=4096):
        self.check_dispatch()
        r=self.trace.reserve(upper_bound)
        self.trace.append(r,TraceEvent(len(self.trace.freeze()),kind,self.run_id,payload))

    @contextmanager
    def model_assist(self,purpose,prompt_fingerprint):
        self.check_dispatch()
        if self.variant is RunVariant.UNIFIED_RUNTIME:
            if not isinstance(purpose,ModelPurpose):raise IntegrityStop(message="baseline role on unified run")
        elif not isinstance(purpose,BaselinePurpose):
            raise IntegrityStop(message="runtime role on direct run")
        previous=self.phase
        start=self.clock.now()
        if self.phase_hook is not None:self.phase_hook(Phase.MODEL_ASSIST)
        try:
            yield
        finally:
            self.ledger.record_span("model_assist",max(0.0,self.clock.now()-start))
            if self.phase_hook is not None and not self.terminal:self.phase_hook(previous)
