import importlib.util,sys,pytest
from pathlib import Path
def load_script(name):
    path=Path(__file__).resolve().parents[2]/"scripts"/name
    assert path.exists(),"physical CLI missing"
    spec=importlib.util.spec_from_file_location("a015_cli_contract",path)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def test_physical_cli_uses_exact_fixed_protocol(workload,tmp_path,monkeypatch):
    m=load_script("qualify_agent_runtime_a015_physical.py");seen=[]
    def stopped(w,*,output,repetitions,seed):
        seen.append((output,repetitions,seed));raise RuntimeError("contract stop before inference")
    monkeypatch.setattr(m,"run_physical_comparison",stopped)
    output=tmp_path/"evidence.json"
    monkeypatch.setattr(sys,"argv",["qualify","--fixture",str(workload.root),"--repetitions","3","--seed","0","--output",str(output)])
    with pytest.raises(RuntimeError,match="contract stop"):m.main()
    assert seen==[(output,3,0)] and not output.exists()
def test_physical_cli_refuses_nonprimary_schedule(workload,tmp_path,monkeypatch):
    m=load_script("qualify_agent_runtime_a015_physical.py")
    monkeypatch.setattr(m,"run_physical_comparison",lambda *a,**k:pytest.fail("nonprimary inference dispatched"))
    monkeypatch.setattr(sys,"argv",["qualify","--fixture",str(workload.root),"--repetitions","2","--seed","0","--output",str(tmp_path/"bad.json")])
    with pytest.raises(SystemExit):m.main()
