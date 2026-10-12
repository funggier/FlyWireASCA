from dataclasses import replace,asdict
from .conftest import api
from project_asca.evaluation.fixture import FrozenCase,OracleExpectation
from tests.agent_runtime.test_public_runtime import build
def case(text):return FrozenCase("dev","pair","development","en",text)
def expected(value=None,state=None,status="SUCCEEDED",reason="VERIFIED",recovery=False):
    return OracleExpectation(status,reason,value,state or {},recovery)
def judge(c,e,r):
    from project_asca.evaluation.oracle import evaluate_trial
    return evaluate_trial(c,e,r)
def test_wrong_goal_is_independently_false_success(configuration,clock):
    runtime,_=build(configuration,clock)
    result=runtime.run("Please add 13 and 7 for a development check.")
    v=judge(case("Please add 13 and 2 for a development check."),expected(15),result)
    assert result.verification.passed and v.false_success and not v.task_completed and not v.answer_correct
def test_missing_required_state_output_is_false_success(configuration,clock):
    runtime,_=build(configuration,clock)
    result=runtime.run("Please pack order O1 and seal it securely.")
    v=judge(case("Please pack order O1 in a protective package."),
            expected(state={"O1":{"package":"protective","sealed":True,"status":"packed"}}),result)
    assert v.false_success and not v.state_correct
def test_control_reason_is_checked_independently():
    r=api("contracts").AgentResult("r","run",api("values").TerminalStatus.BOUNDED_FAILURE,api("values").TerminalReason.NO_PROGRESS)
    v=judge(case("Unavailable development fact"),expected(status="BOUNDED_FAILURE",reason="MISSING_EVIDENCE"),r)
    assert v.status_correct and not v.control_correct and not v.bounded_failure_correct
def test_exact_numeric_normalizer_excludes_bool_and_missing_outputs():
    from project_asca.evaluation.oracle import semantic_equal,normalize_answer
    assert semantic_equal(15,15.0) and not semantic_equal(True,1)
    assert not semantic_equal({"sum":15},{"sum":15,"values":[13,2]})
    assert normalize_answer({"list":[13,2],"sum":15})=={"values":[13,2],"sum":15}
    assert not semantic_equal(["a","b"],["b","a"])
def test_successful_avoidance_has_no_manufactured_recovery_credit(configuration,clock):
    runtime,_=build(configuration,clock);text="Please pack order O1 and seal it securely."
    v=judge(case(text),expected(state={"O1":{"status":"packed","sealed":True}},recovery=True),runtime.run(text))
    assert v.task_completed and not v.false_success and not v.genuine_recovery
def test_real_observed_recovery_requires_changed_context_and_fresh_execution(configuration,clock):
    public=api("values").thaw_json(configuration.public)
    public["facts"] += [["dev-flag","I1","requires_department",True],["dev-approval","I1","department_approval",True]]
    config=api("domain").load_public_configuration(public,asdict(configuration.profile))
    runtime,_=build(config,clock);search=runtime._knowledge.search;calls=0
    def missing(query,*,control):
        nonlocal calls
        result=search(query,control=control)
        if query.index_kind=="memory":
            calls+=1
            if calls==1:return replace(result,hits=tuple(h for h in result.hits if h.evidence.payload.get("field")!="department_approval"))
        return result
    runtime._knowledge.search=missing;text="Please approve invoice I1 under its valid limit policy."
    result=runtime.run(text);e=expected(state={"I1":{"status":"approved"}},recovery=True)
    v=judge(case(text),e,result)
    assert v.task_completed and v.genuine_recovery
    tampered=replace(result,trace=tuple(x for x in result.trace if x.kind!="attempt"))
    assert not judge(case(text),e,tampered).genuine_recovery
