import pytest
from dataclasses import replace
from .conftest import api
from .test_strategy import goal_context,control

def validate(candidate,goal,context,configuration,registry,c):
    return api("strategy").validate_plan(candidate,goal,context,catalog=configuration.catalog,registry=registry,control=c)

def test_invalid_selected_candidate_consumes_attempt_before_dispatch(configuration,registry,schemas,clock):
    text="Add 13 and 2.";goal,context=goal_context(text,schemas,clock,configuration);c=control(text,clock)
    p=api("plans");candidate=p.ActionProposal("bad",0,(p.PlanStep("s","missing","1",{}),),{})
    result=validate(candidate,goal,context,configuration,registry,c)
    assert result.rejection and c.snapshot().metrics.strategy_attempts==1
    assert c.snapshot().metrics.primitive_actions==0

@pytest.mark.parametrize("raw",[
 {"type":"bounded-steps","steps":[],"bindings":{},"ExpectedOutcome":"done"},
 {"type":"stored-root","root":"approve","bindings":{},"authorization":True},
 {"type":"bounded-steps","steps":[{"id":"s","capability":"sum","version":"1","inputs":{},"policy":"override"}],"bindings":{}},
])
def test_model_cannot_supply_outcome_or_authorization(raw):
    with pytest.raises(ValueError):api("strategy").parse_plan_proposal(raw)

def test_forward_output_reference_and_wrong_version_are_rejected(configuration,registry,schemas,clock):
    text="Add 13 and 2.";goal,context=goal_context(text,schemas,clock,configuration);p=api("plans")
    for step in (p.PlanStep("s","sum","1",{"items":p.ValueBinding("step","later")}),
                 p.PlanStep("s","sum","wrong",{"items":p.ValueBinding("literal",value=[13,2])})):
        result=validate(p.ActionProposal("bad",0,(step,),{}),goal,context,configuration,registry,control(text,clock))
        assert result.rejection

def test_registered_root_recursion_and_depth_nine_fail_before_execution(configuration,registry,schemas,clock):
    text="Please approve invoice I1 under its valid limit policy."
    goal,context=goal_context(text,schemas,clock,configuration);p=api("plans")
    cycle=tuple(dict(r,steps=(("call","approve"),)) if r["id"]=="approve" else r for r in configuration.catalog.procedures)
    catalog=p.StrategyCatalog(configuration.catalog.descriptors,cycle)
    candidate=p.ActionProposal("cycle",0,(),{"entity":"I1"},"approve")
    result=api("strategy").validate_plan(candidate,goal,context,catalog=catalog,registry=registry,control=control(text,clock))
    assert result.rejection
    long=[]
    for i in range(9):
        long.append({"id":"approve" if i==0 else "child"+str(i),"version":"1","task":"approve",
          "steps":(("call","child"+str(i+1)),) if i<8 else (("approve",{"entity":"$entity"}),)})
    catalog=p.StrategyCatalog(configuration.catalog.descriptors,tuple(long))
    result=api("strategy").validate_plan(candidate,goal,context,catalog=catalog,registry=registry,control=control(text,clock))
    assert result.rejection

def test_thirty_three_and_large_values_rejected_by_typed_boundary():
    p=api("plans")
    with pytest.raises(ValueError):p.ActionProposal("wide",0,tuple(p.PlanStep(str(i),"sum","1",{}) for i in range(33)),{})
    with pytest.raises(ValueError):p.PlanStep("s","format","1",{"items":["x"*65537]})


def test_ambiguous_duplicate_legacy_call_paths_rejected_before_execution(configuration,registry,schemas,clock):
    text="Please approve invoice I1 under its valid limit policy."
    goal,context=goal_context(text,schemas,clock,configuration);p=api("plans")
    procedures=tuple(dict(r,steps=(("call","policy-check"),("call","policy-check"),
                    ("approve",{"entity":"$entity"}))) if r["id"]=="approve" else r
                    for r in configuration.catalog.procedures)
    catalog=p.StrategyCatalog(configuration.catalog.descriptors,procedures)
    candidate=p.ActionProposal("duplicate-call",0,(),{"entity":"I1"},"approve")
    c=control(text,clock)
    result=api("strategy").validate_plan(candidate,goal,context,catalog=catalog,registry=registry,control=c)
    assert result.rejection and c.snapshot().metrics.primitive_actions==0
