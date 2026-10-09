import importlib.util
import io
import json
from pathlib import Path

import pytest

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/"scripts"/"qualify_integrated_loop_a009.py"


def load():
    assert SCRIPT.exists()
    spec=importlib.util.spec_from_file_location("a009q",SCRIPT)
    module=importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def test_cli_frozen_constants_and_fixture_identity():
    m=load()
    assert m.QUALIFICATION_SCOPE=="deterministic_integrated_cognitive_loop_a009"
    assert m.FIXTURE_VERSION=="a009-deterministic-v1"
    assert m.MAX_SCOPE_COUNT==3
    assert m.MAX_PROCEDURE_ATTEMPTS==3
    assert m.PRIMARY_SELECTOR=="SINGLE_BEST"
    assert m.PRIMARY_PROCEDURE_MODE=="CHUNKED"
    assert m.POLICIES==[
        "NO_PROCEDURE_RECOVERY",
        "MISMATCH_DRIVEN_RECOVERY",
        "ALWAYS_MAX_SCOPE",
    ]
    assert m.EXPECTED_FIXTURE_FINGERPRINT=="2f92b5092de346f62879ac2cbb9f96d6de5d6f919e12d0693345c8228b01ab2a"
    cases=m.build_a009_deterministic_fixture()
    assert m.fixture_fingerprint(cases)==m.EXPECTED_FIXTURE_FINGERPRINT


def test_cli_payload_is_valid_supported_and_contains_raw_policy_evidence():
    m=load()
    payload=m.run_qualification()
    assert payload["experiment_valid"] is True
    assert payload["primary_hypothesis_outcome"]=="SUPPORTED"
    assert payload["primary_selector"]=="SINGLE_BEST"
    assert payload["primary_procedure_mode"]=="CHUNKED"
    assert payload["max_scope_count"]==3
    assert payload["max_procedure_attempts"]==3
    assert len(payload["case_ids"])==10
    aggregate=payload["aggregate_metrics"]
    assert aggregate["genuine_recovery_count"]==2
    assert aggregate["regression_count"]==0
    assert aggregate["primary_total_scope_evaluations"] < aggregate["always_total_scope_evaluations"]
    assert aggregate["max_procedure_attempt_count"]<=3
    assert aggregate["max_scope_index"]<=2
    assert payload["cases"]
    lower=json.dumps(payload).lower()
    for forbidden in ("127.0.0.1:11434","ollama pull","ollama run","lconnect","bconnect"):
        assert forbidden not in lower


def test_cli_validator_recomputes_outcome_and_rejects_drift():
    m=load()
    payload=m.run_qualification()
    payload["primary_hypothesis_outcome"]="NOT_SUPPORTED"
    errors=m.validate_qualification_payload(payload)
    assert any("outcome" in item.lower() for item in errors)


@pytest.mark.parametrize(
    ("metric","value"),
    (
        ("max_procedure_attempt_count",4),
        ("max_scope_index",3),
        ("duplicate_execution_id_failure_count",1),
    ),
)
def test_cli_validator_rejects_boundedness_or_identity_breach(metric,value):
    m=load()
    payload=m.run_qualification()
    payload["aggregate_metrics"][metric]=value
    payload["primary_hypothesis_outcome"]="MIXED"
    errors=m.validate_qualification_payload(payload)
    assert any(metric in item for item in errors)


def test_cli_validator_rejects_fixture_and_policy_drift():
    m=load()
    payload=m.run_qualification()
    payload["fixture_fingerprint"]="0"*64
    payload["policies"]=list(reversed(payload["policies"]))
    errors=m.validate_qualification_payload(payload)
    assert any("fixture_fingerprint" in item for item in errors)
    assert any("policies" in item for item in errors)


def test_stdout_and_output_bytes_match_and_support_utf8(monkeypatch,tmp_path):
    m=load()
    raw=io.BytesIO()
    stdout=io.TextIOWrapper(raw,encoding="cp1252",errors="strict")
    monkeypatch.setattr(m.sys,"stdout",stdout)
    out=tmp_path/"a009.json"
    rc=m.main(["--output",str(out),"--note","ภาษาไทย"])
    stdout.flush()
    assert rc==0
    assert raw.getvalue()==out.read_bytes()
    payload=json.loads(raw.getvalue().decode("utf-8"))
    assert payload["note"]=="ภาษาไทย"


def test_valid_negative_outcome_exits_zero(monkeypatch,capsys):
    m=load()
    payload=m.run_qualification()
    payload["aggregate_metrics"]["genuine_recovery_count"]=0
    payload["primary_hypothesis_outcome"]="NOT_SUPPORTED"
    monkeypatch.setattr(m,"run_qualification",lambda:payload)
    rc=m.main([])
    assert rc==0
    assert json.loads(capsys.readouterr().out)["primary_hypothesis_outcome"]=="NOT_SUPPORTED"


def test_invalid_payload_exits_nonzero(monkeypatch,capsys):
    m=load()
    payload=m.run_qualification()
    payload["fixture_fingerprint"]="0"*64
    monkeypatch.setattr(m,"run_qualification",lambda:payload)
    rc=m.main([])
    assert rc==1
    emitted=json.loads(capsys.readouterr().out)
    assert emitted["experiment_valid"] is False
    assert emitted["errors"]


def test_cli_validator_rejects_per_case_duplicate_execution_ids_and_scope_skip():
    m=load()
    payload=m.run_qualification()
    case=next(item for item in payload["cases"] if item["case_id"]=="procedure-recovery-round-one")
    primary=next(item for item in case["policy_results"] if item["policy"]=="MISMATCH_DRIVEN_RECOVERY")
    primary["execution_ids"]=[primary["execution_ids"][0],primary["execution_ids"][0]]
    errors=m.validate_qualification_payload(payload)
    assert any("execution_ids" in item for item in errors)

    payload=m.run_qualification()
    case=next(item for item in payload["cases"] if item["case_id"]=="procedure-recovery-round-two")
    primary=next(item for item in case["policy_results"] if item["policy"]=="MISMATCH_DRIVEN_RECOVERY")
    primary["evaluated_scope_indices"]=[0,2]
    errors=m.validate_qualification_payload(payload)
    assert any("scope" in item.lower() for item in errors)


def test_cli_validator_rejects_model_control_leakage_evidence():
    m=load()
    payload=m.run_qualification()
    payload["aggregate_metrics"]["model_control_leakage_failure_count"]=1
    payload["primary_hypothesis_outcome"]="MIXED"
    errors=m.validate_qualification_payload(payload)
    assert any("model_control_leakage_failure_count" in item for item in errors)
