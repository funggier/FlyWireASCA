from dataclasses import replace
from pathlib import Path
import subprocess,shutil,copy,json
import pytest
from .conftest import api
@pytest.fixture(scope="module")
def source_repo(tmp_path_factory):
    root=tmp_path_factory.mktemp("a015-source")/"repo"
    actual=Path(__file__).resolve().parents[2]
    subprocess.run(["git","clone","--quiet","--local","--no-hardlinks",str(actual),str(root)],check=True,capture_output=True)
    paths=set(actual.glob("src/project_asca/**/*.py"))|set(actual.glob("scripts/*agent_runtime*a015*.py"))
    extra=actual/"scripts/verify_a015_physical_evidence.py"
    if extra.exists():paths.add(extra)
    for p in paths:
        dest=root/p.relative_to(actual);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dest)
    subprocess.run(["git","add","src/project_asca","scripts"],cwd=root,check=True,capture_output=True)
    subprocess.run(["git","-c","user.name=A015 Test","-c","user.email=a015-test@example.invalid","commit","--allow-empty","-m","Test isolated behavior source"],cwd=root,check=True,capture_output=True)
    return root
def head(root):return subprocess.check_output(["git","rev-parse","HEAD"],cwd=root,text=True).strip()
def test_source_identity_covers_declared_runtime_and_dependency_closure(source_repo,workload):
    from project_asca.evaluation.evidence import source_fingerprint
    s=source_fingerprint(source_repo,head(source_repo),workload.lock["source_universe"])
    names={r["path"] for r in s.files}
    assert "src/project_asca/evaluation/evidence.py" in names
    assert "src/flywire_asca/contracts/memory.py" in names and "src/flywire_asca/model/ollama.py" in names
    assert "scripts/verify_a015_physical_evidence.py" in names
    assert "fixtures/a015/stage-a-v1/freeze.lock.json" in names
    assert all(r["mode"] and r["blob"] for r in s.files)
def test_generated_docs_excluded_but_dirty_behavior_rejected(source_repo,workload):
    from project_asca.evaluation.evidence import source_fingerprint
    s=source_fingerprint(source_repo,head(source_repo),workload.lock["source_universe"])
    docs=source_repo/"docs/development/qualification/test-generated.json";docs.write_text("{}",encoding="utf-8")
    assert source_fingerprint(source_repo,head(source_repo),workload.lock["source_universe"]).fingerprint==s.fingerprint
    p=source_repo/"src/project_asca/agent_runtime/values.py";old=p.read_bytes()
    try:
        p.write_bytes(old+b"\n# source drift\n")
        with pytest.raises(ValueError,match="dirty"):source_fingerprint(source_repo,head(source_repo),workload.lock["source_universe"])
    finally:p.write_bytes(old)
@pytest.fixture(scope="module")
def evidence(source_repo):
    from .evidence_helpers import make_contract_evidence
    from project_asca.evaluation.fixture import load_frozen_workload
    return make_contract_evidence(load_frozen_workload(source_repo/"fixtures/a015/stage-a-v1"),root=source_repo)
def test_structural_harness_evidence_cannot_claim_physical_preference(evidence,source_repo):
    from project_asca.evaluation.evidence import verify_evidence
    v=verify_evidence(evidence,root=source_repo)
    assert v.valid and not v.physical and evidence.outcome.value=="INVALID/INCOMPLETE"
@pytest.mark.parametrize("target",["prompt","output","result","trace","source","identity","counter","denominator","outcome"])
def test_resealed_individual_tamper_is_rejected(evidence,source_repo,target):
    from project_asca.evaluation.evidence import evidence_to_wire,decode_evidence,verify_evidence,wire_fingerprint
    raw=copy.deepcopy(evidence_to_wire(evidence))
    trial=raw["trials"][0]
    if target=="prompt":
        t=next(t for t in raw["trials"] if t["model_records"])
        t["model_records"][0]["prompt"]["messages"][-1]["content"]+=" corrupt"
    elif target=="output":
        t=next(t for t in raw["trials"] if t["model_records"])
        t["model_records"][0]["output"]="corrupt"
    elif target=="result":trial["result"]["answer"]+=" corrupt"
    elif target=="trace":trial["result"]["trace"][-1]["payload"]["reason"]="corrupt"
    elif target=="source":raw["metadata"]["source"]["files"][0]["mode"]="100755"
    elif target=="identity":raw["metadata"]["identity_after"]["model_digest"]="0"*64
    elif target=="counter":trial["result"]["metrics"]["counters"]["model_invocations"]=trial["result"]["metrics"]["counters"].get("model_invocations",0)+1
    elif target=="denominator":raw["totals"]["variants"]["UNIFIED_RUNTIME"]["solvable_requests"]-=1
    else:raw["outcome"]="UNIFIED_RUNTIME_JUSTIFIED"
    raw["payload_hash"]=wire_fingerprint(raw)
    try:changed=decode_evidence(raw,reference_contents=evidence.reference_contents)
    except ValueError:return
    assert not verify_evidence(changed,root=source_repo).valid
def test_unknown_usage_is_incomplete_and_never_zero(evidence,source_repo):
    from project_asca.evaluation.evidence import evidence_to_wire,decode_evidence,verify_evidence,wire_fingerprint
    # Trusted new evidence built from unknown raw usage, rather than inconsistent tampering.
    from .evidence_helpers import with_unknown_usage
    changed=with_unknown_usage(evidence,source_repo)
    v=verify_evidence(changed,root=source_repo)
    assert v.valid and not v.usage_complete
    assert changed.totals.variants["DIRECT_PINNED_MODEL"].prompt_tokens is None
    assert changed.outcome.value=="INVALID/INCOMPLETE"
def test_artifact_round_trip_checks_actual_files(evidence,source_repo,tmp_path):
    from project_asca.evaluation.evidence import write_evidence,load_evidence,verify_evidence
    output=tmp_path/"evidence.json";write_evidence(evidence,output)
    loaded=load_evidence(output)
    assert verify_evidence(loaded,root=source_repo).valid
    directory=output.with_suffix("")
    path=next(directory.glob("*.json"));path.write_text("{}",encoding="utf-8")
    with pytest.raises(ValueError,match="reference"):load_evidence(output)
