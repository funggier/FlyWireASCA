"""One-use validated execution seam; legacy library types never enter core."""
import uuid
from dataclasses import replace
from .values import fingerprint
from .plans import ExecutionReceipt
from .strategy import execution_permit_key,root_layout
from .ports import ExecutionPort
from .budgets import Resource,IntegrityStop

def execute_attempt(plan,goal,context,*,initial,catalog,registry,authorization,control,executor:ExecutionPort):
    control.check_dispatch()
    if plan.goal_id!=goal.goal_id or plan.capability_fingerprint!=registry.fingerprint:
        raise IntegrityStop(message="validated execution goal/registry identity")
    key=execution_permit_key(plan,goal,context)
    permits=getattr(control,"validation_permits",{})
    if permits.get(key,0)<=0:raise IntegrityStop(message="one validation required for every execution")
    permits[key]-=1
    attempt_id=control.run_id+":attempt:"+str(uuid.uuid4())
    execution_id=control.run_id+":execution:"+str(uuid.uuid4())
    reservation=control.ledger.reserve(Resource.ACTIONS,plan.primitive_count,attempt_id=attempt_id)
    expected=tuple(s for s,_,_ in root_layout(catalog,plan.proposal.root_ref)[0]) if plan.proposal.root_ref else plan.proposal.steps
    control.execution_receipt=ExecutionReceipt(control.run_id,fingerprint(goal),fingerprint(plan),
        plan.proposal.revision,registry.fingerprint,attempt_id,execution_id,
        tuple((s.step_id,s.capability_id,s.capability_version) for s in expected),initial.snapshot_id)
    before=control.ledger.snapshot().counters.get("primitive_action_attempts",0)
    try:
        result=executor.execute(plan,goal,context,initial=initial,catalog=catalog,registry=registry,
              authorization=authorization,control=control,attempt_id=attempt_id,execution_id=execution_id)
        control.check_dispatch()
        if result.execution_id!=execution_id or not result.observations:
            raise IntegrityStop(message="fresh execution observation required")
        if len(result.observations)>len(expected):raise IntegrityStop(message="extra execution observation")
        seen=set()
        for step,observation in zip(expected,result.observations):
            if (observation.run_id!=control.run_id or observation.attempt_id!=attempt_id
                or observation.execution_id!=execution_id or observation.step_id in seen
                or observation.step_id!=step.step_id or observation.capability_id!=step.capability_id
                or observation.capability_version!=step.capability_version):
                raise IntegrityStop(message="observation provenance mismatch")
            registry.get(observation.capability_id,observation.capability_version)
            seen.add(observation.step_id)
        if result.final_state.snapshot_id!=result.observations[-1].state_ref:
            raise IntegrityStop(message="final state/observation mismatch")
        control.execution_receipt=replace(control.execution_receipt,final_state_ref=result.final_state.snapshot_id,
             final_state_revision=result.final_state.revision,observation_fingerprint=fingerprint(result.observations))
        return result
    finally:
        dispatched=control.ledger.snapshot().counters.get("primitive_action_attempts",0)-before
        control.ledger.reconcile(reservation,dispatched)
