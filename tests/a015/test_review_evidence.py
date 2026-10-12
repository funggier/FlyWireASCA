"""Adversarial resealing must fail on semantic provenance, not stale hashes."""
from dataclasses import replace
import pytest
from .test_evidence import evidence,source_repo
from project_asca.evaluation.evidence import build_evidence,verify_evidence

@pytest.mark.parametrize("target",["terminal_execution","observation","retrieval","answer"])
def test_fully_rebuilt_evidence_rejects_corrupted_execution_or_claim(evidence,source_repo,target):
    trials=list(evidence.trials)
    index=next(i for i,t in enumerate(trials) if t.result.status.value=="SUCCEEDED"
        and (target!="retrieval" or any(e.kind=="retrieval" for e in t.result.trace)))
    trial=trials[index];result=trial.result
    if target=="terminal_execution":
        result=replace(result,verification=replace(result.verification,execution_id="forged-unexecuted"))
    elif target=="observation":
        trace=list(result.trace);i=next(i for i,e in enumerate(trace) if e.kind=="action")
        trace[i]=replace(trace[i],payload={**dict(trace[i].payload),"observation_ref":"0"*64})
        result=replace(result,trace=tuple(trace))
    elif target=="retrieval":
        counters=dict(result.metrics.counters)
        counters["actual_retrieval_queries"]=0;counters["vectors_scored"]=0
        result=replace(result,metrics=replace(result.metrics,counters=counters))
    else:result=replace(result,answer="Verified result: invented unsupported fact")
    trials[index]=replace(trial,result=result)
    changed=build_evidence(tuple(trials),evidence.metadata)
    validation=verify_evidence(changed,root=source_repo)
    assert not validation.valid, target
