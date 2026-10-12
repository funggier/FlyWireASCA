"""Typed remedies and semantic progress; opaque IDs never create recovery credit."""
from .values import fingerprint,EvidenceKind,Phase,TerminalReason
from .semantics import RecoveryDecision
from .budgets import Resource

def context_fingerprint(context):
    if context is None:return fingerprint(None)
    records=tuple(sorted((r for r in context.items if r.kind not in (EvidenceKind.USER_INPUT,EvidenceKind.OBSERVATION)),
                          key=lambda r:r.evidence_id))
    return fingerprint({"snapshot":context.snapshot_id,"records":records,
                        "required":sorted(context.coverage.required),"satisfied":sorted(context.coverage.satisfied),
                        "relation_complete":context.coverage.required_relation_complete})

def plan_fingerprint(plan):
    if plan is None:return fingerprint(None)
    positions={s.step_id:i for i,s in enumerate(plan.steps)}
    steps=[]
    for step in plan.steps:
        inputs={name:{"source":b.source,"reference":positions.get(b.reference,b.reference) if b.source=="step" else b.reference,
                      "value":b.value} for name,b in step.inputs.items()}
        steps.append({"capability":step.capability_id,"version":step.capability_version,"inputs":inputs})
    return fingerprint({"root":plan.root_ref,"steps":steps,"bindings":plan.bindings})

class RecoveryEngine:
    def __init__(self):self.seen=set()
    def decide(self,goal,context,plan,attempt,deficits,*,control):
        control.check_dispatch()
        base_context=context_fingerprint(context);base_plan=plan_fingerprint(plan)
        kinds={d.kind for d in deficits}
        fatal=kinds&{"IDENTITY_MISMATCH","PROVENANCE_INVALID","CONTROL_VIOLATION","AMBIGUOUS_INPUT",
                     "MODEL_UNAVAILABLE","NO_VALID_PLAN","INSUFFICIENT_CONFIDENCE","MISSING_EVIDENCE_UNAVAILABLE"}
        if fatal:
            reason=sorted(fatal)[0]
            if reason=="MISSING_EVIDENCE_UNAVAILABLE":reason="MISSING_EVIDENCE"
            return RecoveryDecision(Phase.TERMINAL.value,{},base_context,base_plan,reason)
        acquire=bool(kinds&{"MISSING_EVIDENCE","CONTEXT_CAPACITY","ROUTING_UNRESOLVED"})
        next_phase=Phase.ACQUIRING if acquire else Phase.RESOLVING
        refs=tuple(sorted({r for d in deficits for r in d.required_refs}))
        observations=tuple(sorted({r for d in deficits for r in d.observation_refs}))
        remedy={"kind":"acquire" if acquire else "repair","required_refs":refs,
                "observation_refs":observations,"causes":tuple(sorted(kinds))}
        key=fingerprint({"goal":fingerprint(goal),"context":base_context,"plan":base_plan,
                         "kind":remedy["kind"],"causes":remedy["causes"],"required_refs":refs})
        if key in self.seen:
            return RecoveryDecision(Phase.TERMINAL.value,remedy,base_context,base_plan,TerminalReason.NO_PROGRESS.value)
        reservation=control.ledger.reserve(Resource.RECOVERY_ROUNDS,1)
        control.ledger.reconcile(reservation,1);control.ledger.record("recovery_rounds")
        self.seen.add(key)
        control.event("recovery",{"next":next_phase.value,"remedy":remedy,"context":base_context,"plan":base_plan})
        return RecoveryDecision(next_phase.value,remedy,base_context,base_plan,"CHANGE_REQUIRED")
    @staticmethod
    def progressed(decision,context,plan):
        return (context_fingerprint(context)!=decision.baseline_context_fingerprint
                or plan_fingerprint(plan)!=decision.baseline_plan_fingerprint)
