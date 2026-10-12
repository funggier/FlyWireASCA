import pytest
from dataclasses import replace
from .conftest import api
from .test_strategy import goal_context,control
from .test_interpretation import NoBroker

def plan_for(text,configuration,registry,schemas,clock,*,fields=None):
    goal,context=goal_context(text,schemas,clock,configuration,fields=fields);c=control(text,clock)
    resolver=api("strategy").StrategyResolver(configuration.catalog,registry,NoBroker())
    candidate=resolver.resolve(goal,context,previous=None,deficits=(),control=c).candidate
    checked=api("strategy").validate_plan(candidate,goal,context,catalog=configuration.catalog,registry=registry,control=c)
    assert checked.plan
    return checked.plan,goal,context,c

def execute(plan,goal,context,c,configuration,registry):
    return api("execution").execute_attempt(plan,goal,context,initial=configuration.initial_state,
       catalog=configuration.catalog,registry=registry,authorization=api("capabilities").StageAAuthorization(),
       control=c,executor=api("adapters.procedures").ProcedureExecutionAdapter())

def test_blocked_precondition_has_no_executed_effect(configuration,registry,schemas,clock):
    text="Please approve invoice I1 under its valid limit policy."
    plan,goal,context,c=plan_for(text,configuration,registry,schemas,clock,fields=())
    attempt=execute(plan,goal,context,c,configuration,registry)
    assert attempt.observations and not attempt.observations[0].executed
    assert attempt.observations[0].error=="PRECONDITION_UNSATISFIED"
    assert attempt.final_state.values==configuration.initial_state.values
    assert c.snapshot().metrics.primitive_actions==0
    assert c.snapshot().metrics.counters["a008_attempted_actions"]==1
    assert attempt.deficits

def test_attempts_use_identical_initial_state_with_new_execution_ids(configuration,registry,schemas,clock):
    text="Please pack order O1 and seal it securely."
    plan,goal,context,c=plan_for(text,configuration,registry,schemas,clock)
    first=execute(plan,goal,context,c,configuration,registry)
    checked=api("strategy").validate_plan(plan.proposal,goal,context,catalog=configuration.catalog,registry=registry,control=c)
    assert checked.plan
    second=execute(checked.plan,goal,context,c,configuration,registry)
    assert first.execution_id!=second.execution_id
    assert first.final_state.values==second.final_state.values
    assert configuration.initial_state.values["O1"]["status"]=="pending"
    assert all(o.run_id==c.run_id and o.execution_id==first.execution_id for o in first.observations)


def test_validation_permit_cannot_be_reused_or_moved_to_another_context(configuration,registry,schemas,clock):
    text="Please pack order O1 and seal it securely."
    plan,goal,context,c=plan_for(text,configuration,registry,schemas,clock)
    changed=replace(context,items=context.items[:-1],canonical_bytes=0,fingerprint="")
    class NoExecution:
        def execute(self,*args,**kwargs):raise AssertionError("unvalidated context dispatched")
    with pytest.raises(api("budgets").IntegrityStop):
        api("execution").execute_attempt(plan,goal,changed,initial=configuration.initial_state,
          catalog=configuration.catalog,registry=registry,authorization=api("capabilities").StageAAuthorization(),
          control=c,executor=NoExecution())
    execute(plan,goal,context,c,configuration,registry)
    with pytest.raises(api("budgets").IntegrityStop):
        execute(plan,goal,context,c,configuration,registry)

def test_neutral_execution_port_is_declared():
    assert hasattr(api("ports"),"ExecutionPort")

def test_composed_steps_execute_bound_prior_outputs(configuration,registry,schemas,clock):
    text="Sort 13, 2 and 7 ascending and give the sum."
    plan,goal,context,c=plan_for(text,configuration,registry,schemas,clock)
    result=execute(plan,goal,context,c,configuration,registry)
    assert result.procedure_state=="COMPLETED"
    assert result.output==22
    assert result.observations[0].result==(2,7,13)
    assert c.snapshot().metrics.primitive_actions==2


def test_goal_body_and_observation_owner_cannot_be_substituted(configuration,registry,schemas,clock):
    text="Please pack order O1 and seal it securely."
    plan,goal,context,c=plan_for(text,configuration,registry,schemas,clock)
    other_goal=replace(goal,parameters={**dict(goal.parameters),"entity":"O2"})
    with pytest.raises(api("budgets").IntegrityStop):
        execute(plan,other_goal,context,c,configuration,registry)
    class WrongOwner:
        def execute(self,*args,**kwargs):
            result=api("adapters.procedures").ProcedureExecutionAdapter().execute(*args,**kwargs)
            return replace(result,observations=(replace(result.observations[0],run_id="other-run"),))
    with pytest.raises(api("budgets").IntegrityStop):
        api("execution").execute_attempt(plan,goal,context,initial=configuration.initial_state,
          catalog=configuration.catalog,registry=registry,authorization=api("capabilities").StageAAuthorization(),
          control=c,executor=WrongOwner())


def test_registered_but_wrong_action_observation_is_rejected(configuration,registry,schemas,clock):
    text="Please pack order O1 and seal it securely."
    plan,goal,context,c=plan_for(text,configuration,registry,schemas,clock)
    class WrongAction:
        def execute(self,*args,**kwargs):
            result=api("adapters.procedures").ProcedureExecutionAdapter().execute(*args,**kwargs)
            wrong=replace(result.observations[0],capability_id="seal")
            return replace(result,observations=(wrong,)+result.observations[1:])
    with pytest.raises(api("budgets").IntegrityStop):
        api("execution").execute_attempt(plan,goal,context,initial=configuration.initial_state,
          catalog=configuration.catalog,registry=registry,authorization=api("capabilities").StageAAuthorization(),
          control=c,executor=WrongAction())
