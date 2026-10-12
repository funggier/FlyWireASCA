"""Unchanged A008 CHUNKED engine with trusted, context-bound action observations."""
from dataclasses import dataclass
from ..values import fingerprint
from ..plans import Observation,AttemptResult
from ..semantics import Deficit
from ..state import InMemorySession
from ..capabilities import execute_operation
from ..budgets import IntegrityStop
from ..strategy import root_layout
from flywire_asca.contracts.procedure import ProcedureRef,Observation as LegacyObservation
from flywire_asca.contracts.enums import ObservationKind
from flywire_asca.procedural_memory.models import (ProcedureDefinition,ProcedureStep,ProcedureStepKind,
                                                  ExpectedOutcome,ProcedureExecutionMode)
from flywire_asca.procedural_memory.library import ProcedureLibrary,flatten_procedure,canonical_primitive_step_path
from flywire_asca.procedural_memory.runner import run_procedure

@dataclass(frozen=True,slots=True)
class CompiledProcedure:
    library:ProcedureLibrary
    root_id:str
    action_bindings:dict
    success_markers:dict
    completion_markers:dict

def compile_procedure(plan,catalog,registry):
    proposal=plan.proposal;definitions=[];bindings={};markers={};completions={}
    by_id={r["id"]:r for r in catalog.procedures}
    reachable=[]
    def visit(root):
        if root in reachable:return
        reachable.append(root)
        for op,args in by_id[root]["steps"]:
            if op=="call":visit(args)
    root=proposal.root_ref or "composed:"+proposal.plan_id
    if proposal.root_ref:
        root_layout(catalog,root)
        visit(root)
    else:reachable=[root]
    for identifier in reachable:
        version=by_id[identifier]["version"] if proposal.root_ref else "1"
        completion="procedure-complete:"+identifier+":"+version
        completions[identifier]=completion
        steps=[]
        source=by_id[identifier]["steps"] if proposal.root_ref else tuple((step.capability_id,step) for step in proposal.steps)
        for index,(op,args) in enumerate(source,1):
            local="s"+str(index)
            if op=="call":
                child=args;child_version=by_id[child]["version"]
                outcome=ExpectedOutcome("child:"+identifier+":"+local,ObservationKind.RESULT,
                                        "procedure-complete:"+child+":"+child_version)
                steps.append(ProcedureStep(local,ProcedureStepKind.CALL_PROCEDURE,outcome,callee_procedure_id=child))
            else:
                if proposal.root_ref:
                    from ..plans import PlanStep,ValueBinding
                    inputs={name:ValueBinding("request",value[1:]) if isinstance(value,str) and value.startswith("$")
                            else ValueBinding("literal",value=value) for name,value in args.items()}
                    neutral=PlanStep(identifier+"::"+local,op,version,inputs)
                else:neutral=args
                descriptor=registry.get(neutral.capability_id,neutral.capability_version)
                action=identifier+"::"+local
                marker="capability-ok:"+descriptor.capability_id+":"+descriptor.version
                markers[action]=marker;bindings[action]=neutral
                outcome=ExpectedOutcome("operation:"+action,ObservationKind.RESULT,marker)
                steps.append(ProcedureStep(local,ProcedureStepKind.ACTION,outcome,action_ref=action))
        definitions.append(ProcedureDefinition(ProcedureRef(identifier,identifier,version),
            tuple(steps),ExpectedOutcome("complete:"+identifier,ObservationKind.RESULT,completion)))
    library=ProcedureLibrary(tuple(definitions),max_call_depth=8)
    if len(flatten_procedure(library,root))!=plan.primitive_count or library.static_call_depth(root)!=plan.max_depth:
        raise IntegrityStop(message="compiled procedure bounds disagree with validated plan")
    return CompiledProcedure(library,root,bindings,markers,completions)

class ContextBoundProcedureExecutor:
    def __init__(self,compiled,plan,context,session,registry,authorization,control,attempt_id,execution_id):
        self.compiled=compiled;self.plan=plan;self.context=context;self.session=session
        self.registry=registry;self.authorization=authorization;self.control=control
        self.attempt_id=attempt_id;self.execution_id=execution_id
        self.observations=[];self.deficits=[];self.outputs={};self.paths=[]
        self.allowed={item.primitive_step_path:item.action_ref for item in flatten_procedure(compiled.library,compiled.root_id)}
        self.completed=set()
    def execute_action(self,*,action_ref,execution_id,call_path,step_id):
        self.control.check_dispatch()
        path=canonical_primitive_step_path(call_path,step_id)
        if execution_id!=self.execution_id or self.allowed.get(path)!=action_ref or path in self.completed:
            raise IntegrityStop(message="action execution/path ownership")
        step=self.compiled.action_bindings[action_ref]
        descriptor=self.registry.get(step.capability_id,step.capability_version)
        decision=self.authorization.authorize(descriptor,control=self.control)
        if not decision.allowed:raise IntegrityStop(message="Stage A authorization rejected")
        if len(self.observations)>=self.plan.primitive_count:raise IntegrityStop(message="unexpected extra primitive")
        trace=self.control.trace.reserve(1024)
        self.control.ledger.record("primitive_action_attempts")
        result=execute_operation(step,{**dict(self.plan.proposal.bindings),**self.outputs},
                context=self.context,session=self.session,registry=self.registry)
        self.completed.add(path)
        if result.executed:
            self.control.ledger.record("primitive_actions")
            self.outputs["step:"+step.step_id]=result.result;self.paths.append(path)
        error="PRECONDITION_UNSATISFIED" if result.error=="MISSING_EVIDENCE" else result.error
        observed_step_id=path if self.plan.proposal.root_ref else step.step_id
        observation=Observation(self.control.run_id,self.attempt_id,self.execution_id,
             observed_step_id,step.capability_id,step.capability_version,result.executed,result.result,error,
             result.state.snapshot_id,result.state.revision)
        self.observations.append(observation)
        self.control.trace.capture(observation)
        self.control.ledger.peak("artifact_bytes_peak",self.control.trace.artifact_bytes)
        if result.error:
            self.deficits.append(Deficit(result.error,result.unmet_evidence,(fingerprint(observation),),
                                         "registered operation precondition/result failed"))
        from ..trace import TraceEvent
        self.control.trace.append(trace,TraceEvent(len(self.control.trace.freeze()),"action",self.control.run_id,
            {"execution_id":self.execution_id,"step_id":observed_step_id,"capability":step.capability_id,
             "executed":result.executed,"error":error,"observation_ref":fingerprint(observation)}))
        self.control.check_dispatch()
        return LegacyObservation("operation-observation:"+fingerprint(observation),
            ObservationKind.RESULT if result.executed else ObservationKind.ERROR,
            self.compiled.success_markers[action_ref] if result.executed else "blocked:"+str(error),
            evidence_ids=(fingerprint(observation),))
    def observe_procedure_completion(self,*,procedure_id,execution_id,call_path):
        self.control.check_dispatch()
        if execution_id!=self.execution_id or not call_path or call_path[-1]!=procedure_id:
            raise IntegrityStop(message="completion identity")
        expected={p for p in self.allowed if p.startswith("/".join(call_path)+"::")}
        # Include nested descendants under this child, not another caller.
        expected.update(p for p in self.allowed if p.startswith("/".join(call_path)+"/"))
        if not expected or not expected<=self.completed:
            raise IntegrityStop(message="missing child action completion")
        if any(o.error for o in self.observations):raise IntegrityStop(message="failed action cannot complete child")
        return LegacyObservation("completion:"+self.execution_id+":"+procedure_id,ObservationKind.RESULT,
                                 self.compiled.completion_markers[procedure_id])
    def world_state_ref(self):return self.session.snapshot().snapshot_id
    def executed_primitive_step_paths(self):return tuple(self.paths)

class ProcedureExecutionAdapter:
    def execute(self,plan,goal,context,*,initial,catalog,registry,authorization,control,attempt_id,execution_id):
        compiled=compile_procedure(plan,catalog,registry)
        session=InMemorySession(initial,execution_id)
        executor=ContextBoundProcedureExecutor(compiled,plan,context,session,registry,authorization,
                                               control,attempt_id,execution_id)
        result=run_procedure(compiled.library,root_procedure_id=compiled.root_id,
                mode=ProcedureExecutionMode.CHUNKED,executor=executor,execution_id=execution_id)
        control.ledger.record("a008_attempted_actions",result.metrics.primitive_action_count)
        control.ledger.record("procedure_calls",result.metrics.procedure_call_count)
        control.ledger.record("procedure_attempts")
        control.event("procedure_summary",{"execution_id":execution_id,
            "attempted_actions":result.metrics.primitive_action_count,"calls":result.metrics.procedure_call_count})
        output=executor.observations[-1].result if executor.observations else None
        return AttemptResult(execution_id,result.state.value,tuple(executor.observations),output,
                             session.snapshot(),tuple(executor.deficits))
