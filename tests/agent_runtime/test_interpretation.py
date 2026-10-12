import pytest
from .conftest import api

class NoBroker:
    def generate(self,*args,**kwargs):raise AssertionError("deterministic development task must not call model")

def interpret(text,schemas,clock):
    c=api("contracts");control=api("control").RunControl.create(c.AgentRequest(text),clock=clock)
    out=api("interpretation").Interpreter(schemas,NoBroker()).interpret(control.request,control=control)
    from types import SimpleNamespace
    goal=api("goals").GoalCompiler().compile(out.intent,control.request,schemas) if out.intent else None
    v=api("values")
    status=v.TerminalStatus.NEEDS_CLARIFICATION if out.clarification else v.TerminalStatus.UNSUPPORTED if out.unsupported else v.TerminalStatus.BOUNDED_FAILURE if out.failure else None
    return SimpleNamespace(goal=goal,terminal_status=status,interpretation=out)

def test_normalization_preserves_original_spans():
    t=api("interpretation");text="บวก  １１  และ  ６ ให้หน่อย"
    n=t.normalize_with_spans(text)
    assert "11" in n.text and "6" in n.text
    start,end=n.original_span(n.text.index("11"),n.text.index("11")+2)
    assert text[start:end]=="１１"
    assert "ให้" in n.text

@pytest.mark.parametrize("text",["Add 11, 19 and 2.","บวก 11, 19 และ 2","Sort 9, 1 and 4 ascending.","เรียง 9, 1 และ 4 จากน้อยไปมาก"])
def test_bilingual_development_transform_compiles_without_answers(text,schemas,clock):
    out=interpret(text,schemas,clock)
    assert out.goal and out.goal.kind==api("values").TaskKind.TRANSFORM
    assert out.goal.parameters["source"]["literal"] in ((11,19,2),(9,1,4))
    assert "expected" not in repr(out.goal).lower()

@pytest.mark.parametrize("text",["Which employer does the person Alex work for?","Set the in-memory tray to 18.","ตั้งค่าถาดในหน่วยความจำเป็น 18"])
def test_material_ambiguity_never_tie_breaks(text,schemas,clock):
    out=interpret(text,schemas,clock)
    assert out.terminal_status==api("values").TerminalStatus.NEEDS_CLARIFICATION

def test_impossible_supported_bounds_remain_a_goal(schemas,clock):
    out=interpret("Set in-memory tray T2 to at least 9 and at most 2 simultaneously.",schemas,clock)
    assert out.goal and out.goal.parameters["min"]==9 and out.goal.parameters["max"]==2

@pytest.mark.parametrize("field",["goal_code","authorization","expected_answer_ids","retrieval_policy"])
def test_model_cannot_supply_goal_code_or_grants(schemas,field):
    raw={"kind":"TRANSFORM","task":"transform","parameters":{},"spans":[],field:True}
    with pytest.raises(ValueError):api("interpretation").validate_intent_proposal(raw,api("contracts").AgentRequest("Add 8 and 9."),schemas)

def test_model_expression_cannot_invent_verification_value(schemas):
    text="Set tray T2 to the sum of 8 and 3, then verify 11."
    raw={"kind":"STATE_GOAL","task":"set","parameters":{"entity":"T2","field":"quantity",
           "value":{"sum":[8,3],"verify":99}},"spans":[
           {"name":"entity","value":"T2","start":9,"end":11},
           {"name":"field","value":"quantity","start":0,"end":len(text)},
           {"name":"value","value":{"sum":[8,3],"verify":99},"start":0,"end":len(text)}]}
    with pytest.raises(ValueError):api("interpretation").validate_intent_proposal(raw,api("contracts").AgentRequest(text),schemas)

def test_model_cannot_invent_a_literal_input(schemas):
    text="Add 8 and 3."
    raw={"kind":"TRANSFORM","task":"transform","parameters":{"source":{"literal":[8,100]},
          "operations":[{"op":"sum"}],"outputs":["value"]},
          "spans":[{"name":"source","value":[8,100],"start":0,"end":len(text)}]}
    with pytest.raises(ValueError):api("interpretation").validate_intent_proposal(raw,api("contracts").AgentRequest(text),schemas)

def test_valid_model_source_span_is_accepted_with_immutable_values(schemas):
    text="Add 8 and 3."
    raw={"kind":"TRANSFORM","task":"transform","parameters":{"source":{"literal":[8,3]},
         "operations":[{"op":"sum"}],"outputs":["value"]},
         "spans":[{"name":"source","value":[8,3],"start":4,"end":11}]}
    out=api("interpretation").validate_intent_proposal(raw,api("contracts").AgentRequest(text),schemas)
    assert out.intent.bindings["parameters"]["source"]["literal"]==(8,3)
