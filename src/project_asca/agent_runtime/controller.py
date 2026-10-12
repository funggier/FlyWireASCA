"""New top-level lifecycle; semantic operations and infrastructure stay in components."""
from dataclasses import dataclass
from .contracts import AgentRequest,AgentResult,parse_agent_request
from .values import Phase,TerminalStatus,TerminalReason,TaskKind,fingerprint
from .control import RunControl
from .budgets import Resource,BudgetStop,CancelledStop,IntegrityStop
from .trace import TraceEvent
from .semantics import Deficit
from .execution import execute_attempt
from .strategy import validate_plan
from .verification import verify_completion,candidate_from_attempt
from .rendering import render_result_data

NEXT={
 Phase.RECEIVED:{Phase.INTERPRETING,Phase.TERMINAL},
 Phase.INTERPRETING:{Phase.ACQUIRING,Phase.RESOLVING,Phase.MODEL_ASSIST,Phase.TERMINAL},
 Phase.ACQUIRING:{Phase.RESOLVING,Phase.RECOVERING,Phase.MODEL_ASSIST,Phase.TERMINAL},
 Phase.RESOLVING:{Phase.EXECUTING,Phase.RECOVERING,Phase.MODEL_ASSIST,Phase.TERMINAL},
 Phase.EXECUTING:{Phase.OBSERVING},Phase.OBSERVING:{Phase.VERIFYING},
 Phase.VERIFYING:{Phase.TERMINAL,Phase.RECOVERING},
 Phase.RECOVERING:{Phase.ACQUIRING,Phase.RESOLVING,Phase.MODEL_ASSIST,Phase.TERMINAL},
 Phase.MODEL_ASSIST:set(),Phase.TERMINAL:set(),
}

class TerminalLatch:
    def __init__(self):self.result=None
    def publish(self,result):
        if self.result is None:self.result=result
        return self.result

class StateMachine:
    def __init__(self,control):
        self.control=control;self.requesting=None;self.entered=control.clock.now()
        self.protected=control.ledger.reserve(Resource.TRANSITIONS,min(3,control.profile.transitions))
    def _record(self,target,*,terminal=False):
        c=self.control;now=c.clock.now();prior=c.phase
        c.ledger.record_span("phase:"+prior.value,max(0.0,now-self.entered))
        event=TraceEvent(len(c.trace.freeze()),"phase",c.run_id,{"from":prior.value,"to":target.value})
        if terminal:c.trace.terminal(event)
        else:
            reservation=c.trace.reserve(1024);c.trace.append(reservation,event)
        c.ledger.record("transitions");c.phase=target;self.entered=now
    def move(self,target):
        c=self.control;c.check_dispatch();target=Phase(target)
        if c.phase is Phase.MODEL_ASSIST:
            if target is not self.requesting:raise IntegrityStop(message="model-assist requesting state")
        elif target not in NEXT[c.phase]:raise IntegrityStop(message="illegal controller transition")
        if target is Phase.TERMINAL:return self.finish()
        reservation=c.ledger.reserve(Resource.TRANSITIONS,1)
        try:self._record(target)
        except Exception:
            c.ledger.reconcile(reservation,0);raise
        c.ledger.reconcile(reservation,1)
        if target is Phase.MODEL_ASSIST:self.requesting=Phase(c.trace.freeze()[-1].payload["from"])
        elif self.requesting is target:self.requesting=None
    def finish(self):
        c=self.control
        if c.terminal:return
        original=c.phase
        chain=((Phase.OBSERVING,Phase.VERIFYING,Phase.TERMINAL) if original is Phase.EXECUTING else
               (Phase.VERIFYING,Phase.TERMINAL) if original is Phase.OBSERVING else
               (self.requesting,Phase.TERMINAL) if original is Phase.MODEL_ASSIST else (Phase.TERMINAL,))
        for target in chain:
            if target is None:raise IntegrityStop(message="missing model requesting state")
            now=c.clock.now()
            c.ledger.record_span("phase:"+c.phase.value,max(0.0,now-self.entered))
            c.phase=target;self.entered=now;c.ledger.record("transitions")
        c.trace.terminal(TraceEvent(len(c.trace.freeze()),"phase",c.run_id,
             {"from":original.value,"to":Phase.TERMINAL.value,"unwind":tuple(p.value for p in chain)}))
        c.ledger.reconcile(self.protected,len(chain))
        c.terminal=True;c.phase_hook=None

@dataclass
class RunComponents:
    interpreter:object
    compiler:object
    schemas:object
    acquirer:object
    resolver:object
    recovery:object
    executor:object
    registry:object
    authorization:object
    broker:object

class _Run:
    def __init__(self,configuration,ports,components,request,cancellation):
        self.configuration=configuration;self.ports=ports;self.start=ports.clock.now()
        self.control=RunControl.create(request,configuration.profile,ports.clock,cancellation)
        self.machine=StateMachine(self.control);self.control.phase_hook=self.machine.move
        self.parts=components(self.control);self.latch=TerminalLatch()
        self.goal=None;self.context=None;self.proposal=None;self.attempt=None
        self.candidate=None;self.verification=None;self.deficits=();self.pending=None
        self.invariants=(fingerprint(request),fingerprint(configuration.initial_state),fingerprint(configuration.profile))
        self.goal_identity=None
    def check(self):
        self.control.check_dispatch()
        if self.invariants!=(fingerprint(self.control.request),fingerprint(self.configuration.initial_state),fingerprint(self.configuration.profile)):
            raise IntegrityStop(message="immutable request/state/profile changed")
        if self.goal_identity is not None and fingerprint(self.goal)!=self.goal_identity:
            raise IntegrityStop(message="immutable accepted goal changed")
    def publish(self,status,reason,*,explanation=""):
        c=self.control
        if self.latch.result is not None:return self.latch.result
        if status is TerminalStatus.SUCCEEDED:self.check()
        language=c.request.language_hint or ("th" if any("\u0e00"<=x<="\u0e7f" for x in c.request.text) else "en")
        answer=(render_result_data(self.candidate,self.verification,language=language) if status is TerminalStatus.SUCCEEDED else
                ("งานยังไม่เสร็จ: " if language=="th" else "Task not completed: ")+reason.value+
                ("; "+explanation if explanation else ""))
        self.machine.finish()
        c.ledger.record_span("end_to_end",max(0.0,c.clock.now()-self.start))
        c.trace.terminal(TraceEvent(len(c.trace.freeze()),"terminal",c.run_id,
            {"status":status.value,"reason":reason.value,"goal":self.goal.goal_id if self.goal else None,
             "verification":fingerprint(self.verification) if self.verification else None}))
        result=AgentResult(c.request.request_id,c.run_id,status,reason,self.goal,answer,
            self.candidate.data if self.candidate else None,self.verification,
            self.candidate.evidence_refs if self.candidate else (),
            self.attempt.final_state.snapshot_id if self.attempt else None,
            c.ledger.snapshot(),c.trace.freeze(),status is not TerminalStatus.SUCCEEDED and self.attempt is not None,
            explanation)
        return self.latch.publish(result)
    def interpret(self):
        self.machine.move(Phase.INTERPRETING);self.check()
        found=self.parts.interpreter.interpret(self.control.request,control=self.control);self.check()
        if found.clarification:return self.publish(TerminalStatus.NEEDS_CLARIFICATION,TerminalReason.AMBIGUOUS_INPUT,explanation=found.clarification)
        if found.unsupported:return self.publish(TerminalStatus.UNSUPPORTED,TerminalReason.UNSUPPORTED_CAPABILITY)
        if found.failure:return self.stop(found.failure)
        self.goal=self.parts.compiler.compile(found.intent,self.control.request,self.parts.schemas)
        self.goal_identity=fingerprint(self.goal)
        self.control.event("goal",{"goal":self.goal.goal_id,"fingerprint":self.goal_identity,"kind":self.goal.kind.value})
        return None
    def acquire(self):
        source=self.goal.parameters.get("source",{})
        self_contained=(self.goal.kind is TaskKind.TRANSFORM and "literal" in source) or (
            self.goal.kind is TaskKind.STATE_GOAL and self.goal.parameters.get("task") in ("set","state_range"))
        if self.control.phase is not Phase.ACQUIRING and not self_contained:self.machine.move(Phase.ACQUIRING)
        self.check()
        self.context=self.parts.acquirer.acquire(self.goal,self.control.request,previous=self.context,
                                                deficits=self.deficits,control=self.control)
        self.check()
        if self.pending and not self.parts.recovery.progressed(self.pending,self.context,self.proposal):
            return self.stop(TerminalReason.NO_PROGRESS.value)
        self.pending=None
        if not self.context.coverage.complete:
            self.deficits=tuple(d for d in self.context.deficits if d.kind in
                                ("MISSING_EVIDENCE","CONTEXT_CAPACITY","ROUTING_UNRESOLVED","PROVENANCE_INVALID"))
            return self.recover()
        self.machine.move(Phase.RESOLVING);return None
    def resolve(self):
        if self.control.phase is not Phase.RESOLVING:self.machine.move(Phase.RESOLVING)
        self.check()
        resolution=self.parts.resolver.resolve(self.goal,self.context,previous=self.proposal,
                                               deficits=self.deficits,control=self.control)
        self.check()
        if resolution.unsupported:return self.publish(TerminalStatus.UNSUPPORTED,TerminalReason.UNSUPPORTED_CAPABILITY)
        candidate=resolution.candidate
        if self.pending and not self.parts.recovery.progressed(self.pending,self.context,candidate):
            return self.stop(TerminalReason.NO_PROGRESS.value)
        self.pending=None
        if candidate is None:
            self.deficits=resolution.deficits or (Deficit("NO_VALID_PLAN"),);return self.recover()
        checked=validate_plan(candidate,self.goal,self.context,catalog=self.configuration.catalog,
                              registry=self.parts.registry,control=self.control)
        self.proposal=candidate
        if checked.plan is None:self.deficits=checked.deficits;return self.recover()
        self.machine.move(Phase.EXECUTING);self.check()
        self.attempt=execute_attempt(checked.plan,self.goal,self.context,initial=self.configuration.initial_state,
             catalog=self.configuration.catalog,registry=self.parts.registry,authorization=self.parts.authorization,
             control=self.control,executor=self.parts.executor)
        self.machine.move(Phase.OBSERVING);self.check()
        self.candidate=candidate_from_attempt(self.goal,self.context,self.attempt)
        self.machine.move(Phase.VERIFYING);self.check()
        self.verification=verify_completion(self.goal,self.candidate,knowledge=self.configuration.knowledge,
                           final_state=self.attempt.final_state,control_snapshot=self.control.snapshot())
        self.control.event("verification",{"passed":self.verification.passed,
                          "verification_ref":fingerprint(self.verification),
                          "execution_id":self.attempt.execution_id,"state_ref":self.attempt.final_state.snapshot_id})
        if self.verification.passed:return self.publish(TerminalStatus.SUCCEEDED,TerminalReason.VERIFIED)
        if not self.verification.integrity and not self.attempt.deficits:
            raise IntegrityStop(TerminalReason.PROVENANCE_INVALID,"completion integrity")
        self.deficits=self.attempt.deficits or tuple(Deficit("OBSERVED_MISMATCH",observation_refs=self.verification.observation_refs)
                                                    for p in self.verification.predicates if p.status!="PASS")
        return self.recover()
    def recover(self):
        if self.control.phase is not Phase.RECOVERING:self.machine.move(Phase.RECOVERING)
        self.check()
        decision=self.parts.recovery.decide(self.goal,self.context,self.proposal,self.attempt,self.deficits,control=self.control)
        if decision.next_phase==Phase.TERMINAL.value:return self.stop(decision.reason)
        self.pending=decision
        self.machine.move(Phase(decision.next_phase))
        return None
    def stop(self,reason):
        try:typed=TerminalReason(reason)
        except ValueError:typed=TerminalReason.NO_VALID_PLAN
        if typed in (TerminalReason.IDENTITY_MISMATCH,TerminalReason.PROVENANCE_INVALID,TerminalReason.CONTROL_VIOLATION):
            return self.publish(TerminalStatus.REJECTED,typed)
        if typed is TerminalReason.CANCELLED:return self.publish(TerminalStatus.CANCELLED,typed)
        return self.publish(TerminalStatus.BOUNDED_FAILURE,typed)
    def run(self):
        try:
            result=self.interpret()
            if result:return result
            while not self.control.terminal:
                self.check()
                phase=self.control.phase
                if phase in (Phase.INTERPRETING,Phase.ACQUIRING):result=self.acquire()
                elif phase is Phase.RESOLVING:result=self.resolve()
                else:raise IntegrityStop(message="unhandled lifecycle phase")
                if result:return result
        except CancelledStop:return self.publish(TerminalStatus.CANCELLED,TerminalReason.CANCELLED)
        except BudgetStop as exc:return self.publish(TerminalStatus.BOUNDED_FAILURE,exc.reason)
        except IntegrityStop as exc:
            if not self.control.ledger.snapshot().integrity_failures:self.control.ledger.record("integrity_failures")
            return self.publish(TerminalStatus.REJECTED,exc.reason)
        except Exception as exc:
            self.control.ledger.record("integrity_failures")
            return self.publish(TerminalStatus.REJECTED,TerminalReason.CONTROL_VIOLATION,explanation=type(exc).__name__)

class AgentRuntime:
    def __init__(self,configuration,ports,components,*,setup_metrics,knowledge):
        self.configuration=configuration;self.ports=ports;self._components=components
        self.setup_metrics=setup_metrics;self._knowledge=knowledge;self.model_records=[]
    def run(self,request,*,cancellation=None):
        try:request=parse_agent_request(request)
        except (ValueError,TypeError):
            safe=AgentRequest("Rejected invalid public input")
            c=RunControl.create(safe,self.configuration.profile,self.ports.clock,cancellation)
            machine=StateMachine(c);machine.finish()
            c.trace.terminal(TraceEvent(len(c.trace.freeze()),"terminal",c.run_id,{"status":"REJECTED","reason":"INVALID_INPUT"}))
            return AgentResult(safe.request_id,c.run_id,TerminalStatus.REJECTED,TerminalReason.INVALID_INPUT,
                               answer="Invalid input.",metrics=c.ledger.snapshot(),trace=c.trace.freeze())
        run=_Run(self.configuration,self.ports,self._components,request,cancellation)
        try:return run.run()
        finally:
            self.model_records.extend(run.parts.broker.records)
            self._knowledge.cache={key:value for key,value in self._knowledge.cache.items() if key[0]!=run.control.run_id}
