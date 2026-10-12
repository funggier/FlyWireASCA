def test_portable_qualification_discloses_scripted_model_and_keeps_all_trials(workload):
    from project_asca.evaluation.portable import run_portable_qualification
    r=run_portable_qualification(workload)
    assert r.evidence_kind=="PORTABLE_ENGINEERING" and not r.physical
    assert r.scripted_usage and r.architecture_outcome is None
    assert len(r.trials)==128 and {t.variant.value for t in r.trials}=={"UNIFIED_RUNTIME","DIRECT_PINNED_MODEL"}
    assert all(t.request_fingerprint for t in r.trials) and r.freeze_valid
    assert all(v.cost_requests==64 for v in r.totals.variants.values())
def test_portable_has_no_runtime_oracle_channel(workload,monkeypatch):
    from project_asca.evaluation.portable import run_portable_qualification
    from project_asca.evaluation import oracle
    calls=0;original=oracle.evaluate_trial
    def tracked(case,expected,result):
        nonlocal calls
        calls+=1
        assert result.trace[-1].kind=="terminal"
        return original(case,expected,result)
    monkeypatch.setattr(oracle,"evaluate_trial",tracked)
    assert len(run_portable_qualification(workload).trials)==128 and calls==128


def test_portable_engineering_gate_requires_zero_false_success_and_correct_controls(workload):
    from project_asca.evaluation.portable import run_portable_qualification
    r=run_portable_qualification(workload)
    assert all(v.false_success==0 and v.controls_correct==16 and v.bounded_failures_correct==8 for v in r.totals.variants.values())
    assert r.engineering_valid

def test_portable_cli_serializes_public_json_shapes(workload,tmp_path,monkeypatch):
    import importlib.util,json,sys
    from pathlib import Path
    path=Path(__file__).resolve().parents[2]/"scripts/qualify_agent_runtime_a015.py"
    spec=importlib.util.spec_from_file_location("a015_portable_cli_test",path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    output=tmp_path/"portable.json"
    monkeypatch.setattr(sys,"argv",["qualify","--fixture",str(workload.root),"--output",str(output)])
    module.main()
    raw=json.loads(output.read_text(encoding="utf-8"))
    first=raw["trials"][0]["result"]
    assert isinstance(first["metrics"]["counters"],dict) and "_values" not in first["metrics"]["counters"]
    assert "transitions" in first["metrics"]["counters"]
    assert first["trace"][0]["payload"]["to"]=="INTERPRETING"
