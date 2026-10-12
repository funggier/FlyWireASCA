from .conftest import api
from .test_interpretation import interpret

def test_every_requested_output_becomes_a_goal_predicate(schemas,clock):
    out=interpret("Sort 9, 1 and 4 ascending and give their sum.",schemas,clock)
    predicates=out.goal.predicates
    assert len(predicates)>=2
    assert {p.arguments.get("output") for p in predicates}>={"list","sum"}

def test_state_goal_includes_every_requested_property(schemas,clock):
    out=interpret("Prepare bench B1 so it is calibrated and ready.",schemas,clock)
    assert {p.arguments.get("field") for p in out.goal.predicates}>={"calibrated","ready"}

def test_fact_goal_is_a_grounded_lookup_not_a_literal_answer(schemas,clock):
    out=interpret("What is the office location of Nira?",schemas,clock)
    assert out.goal.parameters["entity"]=="Nira" and out.goal.parameters["field"]=="office"
    assert all("North" not in str(p.arguments) for p in out.goal.predicates)

def test_state_expression_and_explicit_verification_are_separate_constraints(schemas,clock):
    out=interpret("Set tray T2 to the sum of 8 and 3, then verify that it contains 11.",schemas,clock)
    assert len(out.goal.predicates)==2
    assert {str(p.arguments["value"]) for p in out.goal.predicates}>={"11"}
