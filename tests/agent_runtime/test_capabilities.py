import math
import pytest
from .conftest import api

def execute(cap,inputs,configuration,registry):
    p=api("plans");s=api("semantics")
    session=api("state").InMemorySession(configuration.initial_state,"execution")
    context=s.WorkingContext("empty",configuration.knowledge.snapshot_id)
    return api("capabilities").execute_operation(p.PlanStep("s",cap,"1",inputs),{},
                                                 context=context,session=session,registry=registry)

def test_stable_sort_empty_sum_and_grouping(configuration,registry):
    sorted_=execute("sort",{"items":[{"k":2,"name":"a"},{"k":1,"name":"b"},{"k":2,"name":"c"}],"field":"k"},configuration,registry)
    assert [v["name"] for v in sorted_.result]==["b","a","c"]
    assert execute("sum",{"items":[]},configuration,registry).result==0
    result=execute("group",{"items":[{"k":"x","v":2},{"k":"y","v":3},{"k":"x","v":4}],"key":"k","value":"v"},configuration,registry)
    assert dict(result.result)=={"x":6,"y":3}

@pytest.mark.parametrize("items",[[1,float("nan")],[True,3],[1]*257])
def test_nonfinite_bool_and_oversize_arrays_are_blocked(configuration,registry,items):
    # Nonfinite data may be rejected by the immutable step before dispatch.
    try:result=execute("sum",{"items":items},configuration,registry)
    except ValueError:return
    assert not result.executed and result.error

def test_forward_binding_and_unknown_capability_are_not_executed(configuration,registry):
    p=api("plans")
    out=execute("sum",{"items":p.ValueBinding("step","future")},configuration,registry)
    assert not out.executed and out.error
    with pytest.raises(ValueError):registry.get("email","1")

def test_policy_dependency_missing_then_bound_evidence_changes_outcome(configuration,registry):
    p=api("plans");s=api("semantics");v=api("values")
    session=api("state").InMemorySession(configuration.initial_state,"execution")
    def context(fields):
        return s.WorkingContext("ctx",configuration.knowledge.snapshot_id,tuple(
            s.EvidenceRecord(f["id"],v.EvidenceKind.STORED_FACT,f["id"],configuration.knowledge.snapshot_id,f)
            for f in configuration.knowledge.facts if f["subject"]=="I2" and f["field"] in fields))
    step=p.PlanStep("approve","approve","1",{"entity":"I2"})
    blocked=api("capabilities").execute_operation(step,{},context=context({"amount","limit","requires_department"}),session=session,registry=registry)
    assert not blocked.executed and "I2.department_approval" in blocked.unmet_evidence
    assert session.snapshot().values["I2"]["status"]=="pending"
    passed=api("capabilities").execute_operation(step,{},context=context({"amount","limit","requires_department","department_approval"}),session=session,registry=registry)
    assert passed.executed and session.snapshot().values["I2"]["status"]=="approved"

def test_stage_a_rejects_external_effects(registry,clock):
    c=api("contracts");control=api("control").RunControl.create(c.AgentRequest("dev task"),clock=clock)
    external=api("plans").CapabilityDescriptor("external-write","1",{}, {},effect_class=api("values").EffectClass.EXTERNAL_WRITE)
    decision=api("capabilities").StageAAuthorization().authorize(external,control=control)
    assert not decision.allowed and control.snapshot().metrics.primitive_actions==0
