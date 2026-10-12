from collections import Counter
from pathlib import Path
import importlib,shutil,json
import pytest

ROOT=Path(__file__).resolve().parents[2]
FIXTURE=ROOT/"fixtures/a015/stage-a-v1"

def module(name):
    try:return importlib.import_module("project_asca.evaluation."+name)
    except ImportError as exc:pytest.fail(str(exc),pytrace=False)

def load():
    return module("fixture").load_frozen_workload(FIXTURE)

def test_exact_bilingual_counts_and_status_denominators():
    w=load()
    assert len(w.cases)==64
    assert len({c.pair_id for c in w.cases})==32
    assert Counter(c.language for c in w.cases)=={"en":32,"th":32}
    assert len(Counter(c.family for c in w.cases))==8
    assert set(Counter(c.family for c in w.cases).values())=={8}
    assert Counter(o.status for o in w.oracle.values())=={
        "SUCCEEDED":48,"NEEDS_CLARIFICATION":4,"UNSUPPORTED":4,"BOUNDED_FAILURE":8}
    assert len({c.case_id for c in w.cases})==64
    assert all(c.request().request_id!=c.case_id for c in w.cases)

def test_public_fixture_contains_no_case_oracle_controls():
    w=load()
    payload=json.dumps(w.public)
    for name in ("case_id","pair_id","family","required_values","recovery_required","expected"):
        assert name not in payload
    from project_asca.agent_runtime.domain import load_public_configuration
    config=load_public_configuration(w.public,w.profile)
    assert config.dependency_reachable
    alex=[e for e in config.knowledge.entities if e["name"]=="Alex"]
    assert len(alex)==2 and alex[0]["id"]!=alex[1]["id"]

def test_full_direct_prompt_fits_every_case():
    w=load();f=module("fixture");bounds=f.bounds_from_workload(w)
    for case in w.cases:
        prompt=f.render_direct_prompt(case.text,w.public)
        user=json.loads(prompt.messages[1].content)
        assert user["public"]==w.public and user["text"]==case.text
        assert bounds.bound(prompt).upper_tokens+1024<=8192

def test_frozen_inputs_and_all_templates_match_lock():
    w=load();v=module("freeze").validate_freeze(w,module("fixture").bounds_from_workload(w))
    assert v.valid,v.errors
    assert v.aggregate_hash==w.lock["aggregate_hash"]
    assert v.aggregate_hash=="774bc3352242bee5cb588f499f6597a264c67f612feb518828058dc4c1efa882"
    assert v.components=={'a014-router-prompt': 'b48568801f32579e36f2e633b740a3d6cc0a276ffa6dcaa05d035f790b5f6a8d', 'assembled-templates': 'a82b751eee25fb531c776a0feab687375190d980b58bfb0faf62850ddde23f3b', 'direct-prompt-instances': '59e5162264ef3a62de1eb3ddafc4e6730e3b1b51ec8706d2bd1a7dfe0b745b51', 'oracle.json': 'c09f5a2c7c8508b642a7e7557387dc90fb9ce940526e6d7bc1de44a9a3260cd5', 'profile.json': 'bf79b82546c6ead3e545f998ffda61af6cb74b1bea2725c6b76604acb3bf6a0f', 'public.json': '54baba1b778ee042be70e1e5a64eed58acb28130829392ed6281702323d92eec', 'requests.json': '14d9d183a26e364ed6423b4098a0053cbc3c04371c0b078ee148bbf200a8ace5', 'schemas.json': 'c97b8c95af61486aa44ceb4958ae3956d40b1cb89d775e96758ae99c7d6d151a', 'source-universe-policy': '3639fcce2384570f5601b28353807bedb38a03f899390318f5a7818eeb2b5ac5', 'token-bound-certificate.json': '252b76df1d5171f35486013a74856adb4edaf97375eeb1378d621790ca816b65'}

@pytest.mark.parametrize("name",["requests.json","public.json","oracle.json","schemas.json","profile.json"])
def test_changed_frozen_component_is_detected(tmp_path,name):
    copy=tmp_path/"v1";shutil.copytree(FIXTURE,copy)
    p=copy/name;data=json.loads(p.read_text(encoding="utf-8"))
    if name=="requests.json":data[0]["text"]+="!"
    elif name=="oracle.json":next(iter(data["cases"].values()))["required_values"]="tampered"
    else:data["tamper"]=True
    p.write_text(json.dumps(data),encoding="utf-8")
    try:
        w=module("fixture").load_frozen_workload(copy)
        v=module("freeze").validate_freeze(w,module("fixture").bounds_from_workload(w))
        assert not v.valid
    except ValueError:
        pass

def test_changed_assembled_template_and_certificate_are_detected(tmp_path,monkeypatch):
    from project_asca.agent_runtime import prompts
    w=load()
    monkeypatch.setitem(prompts.CORES,"INTENT",prompts.CORES["INTENT"]+"changed")
    v=module("freeze").validate_freeze(w,module("fixture").bounds_from_workload(w))
    assert not v.valid
    copy=tmp_path/"certificate";shutil.copytree(FIXTURE,copy)
    p=copy/"token-bound-certificate.json";value=json.loads(p.read_text(encoding="utf-8"))
    value["tokenizer_metadata"]["byte_alphabet_complete"]=False
    p.write_text(json.dumps(value),encoding="utf-8")
    with pytest.raises(ValueError):module("fixture").bounds_from_workload(module("fixture").load_frozen_workload(copy))
