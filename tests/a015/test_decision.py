import pytest
from dataclasses import replace
def totals():
    from project_asca.evaluation.decision import VariantTotals,ComparisonTotals
    recovery={(r,l):1 for r in (1,2,3) for l in ("en","th")}
    groups={("en","development"):72,("th","development"):72}
    u=VariantTotals(cost_requests=192,solvable_requests=144,bounded_failure_requests=24,control_requests=48,
       completed=144,controls_correct=48,bounded_failures_correct=24,model_calls=60,prompt_tokens=4000,
       output_tokens=1000,genuine_recoveries=6,by_repetition={str(r):{"cost_requests":64,"solvable_requests":48,"bounded_failure_requests":8,"control_requests":16} for r in (1,2,3)},recovery_by_rep_language=recovery,completion_by_language_family=groups)
    return ComparisonTotals({"UNIFIED_RUNTIME":u,"DIRECT_PINNED_MODEL":replace(u,model_calls=192,prompt_tokens=6000,genuine_recoveries=0)},0,0)
def classify(t):
    from project_asca.evaluation.decision import classify_comparison,EvidenceValidation
    return classify_comparison(t,EvidenceValidation(True,True,True)).value
def change(t,variant="UNIFIED_RUNTIME",**kwargs):
    v=dict(t.variants);v[variant]=replace(v[variant],**kwargs);return replace(t,variants=v)
def test_justified_requires_every_predeclared_condition():
    assert classify(totals())=="UNIFIED_RUNTIME_JUSTIFIED"
@pytest.mark.parametrize("alter",[{"false_success":1},{"controls_correct":47},{"bounded_failures_correct":23},{"invariant_failures":1},{"completed":0},{"genuine_recoveries":0}])
def test_safety_and_no_recovery_precede_preference(alter):
    assert classify(change(totals(),**alter))=="UNIFIED_RUNTIME_NOT_SUPPORTED"
def test_unknown_usage_or_nonphysical_never_gets_positive_preference():
    from project_asca.evaluation.decision import classify_comparison,EvidenceValidation
    for v in (EvidenceValidation(False,True,True),EvidenceValidation(True,False,True),EvidenceValidation(True,True,False)):
        assert classify_comparison(totals(),v).value=="INVALID/INCOMPLETE"
def test_baseline_safe_dominance_with_no_unified_only_success():
    t=change(replace(totals(),baseline_only_successes=1),completed=143,model_calls=200,prompt_tokens=7000)
    assert classify(t)=="DIRECT_MODEL_PREFERRED"
def test_preserved_success_but_more_tokens_is_mixed():
    assert classify(change(totals(),prompt_tokens=10000))=="MIXED"
def test_missing_per_language_recovery_is_mixed():
    t=totals();r=dict(t.variants["UNIFIED_RUNTIME"].recovery_by_rep_language);r[(3,"th")]=0
    assert classify(change(t,recovery_by_rep_language=r))=="MIXED"
def test_missing_requests_or_denominators_is_incomplete():
    assert classify(change(totals(),cost_requests=191))=="INVALID/INCOMPLETE"
def test_aggregate_recomputes_raw_denominators(workload,configuration,clock):
    from project_asca.evaluation.oracle import RawTrial,evaluate_trial,aggregate_trials
    from tests.agent_runtime.test_public_runtime import build
    from project_asca.agent_runtime.values import RunVariant,fingerprint
    runtime,_=build(configuration,clock);trials=[]
    for r in (1,2,3):
        for c in workload.cases:
            result=runtime.run(c.text);v=evaluate_trial(c,workload.oracle[c.case_id],result)
            for variant in RunVariant:trials.append(RawTrial(c.case_id,variant,r,fingerprint(c.text),result,v,(),0.0))
    for v in aggregate_trials(tuple(trials)).variants.values():
        assert v.cost_requests==192 and v.solvable_requests==144
        assert v.bounded_failure_requests==24 and v.control_requests==48

def test_missing_repetition_cannot_be_justified():
    assert classify(change(totals(),by_repetition={}))=="INVALID/INCOMPLETE"
