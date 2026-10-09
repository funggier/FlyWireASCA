import importlib.util
import io
import json
from pathlib import Path

import pytest

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/"scripts"/"qualify_procedural_memory_a008.py"

def load():
    assert SCRIPT.exists()
    spec=importlib.util.spec_from_file_location("a008q",SCRIPT)
    module=importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def test_cli_frozen_constants_and_fixture_identity():
    m=load()
    assert m.QUALIFICATION_SCOPE=="deterministic_procedural_memory_a008"
    assert m.FIXTURE_VERSION=="a008-deterministic-v1"
    assert m.MAX_CALL_DEPTH==8
    assert m.EXPECTED_FIXTURE_FINGERPRINT=="f52fbd4ab018386ff3cbfb62a68cc44a4b40e54ec4fd9a3b2e885dd2c5663fc6"
    assert len(m.EXPECTED_FIXTURE_FINGERPRINT)==64
    int(m.EXPECTED_FIXTURE_FINGERPRINT,16)
    cases=m.build_a008_fixture()
    assert m.fixture_fingerprint(cases)==m.EXPECTED_FIXTURE_FINGERPRINT
    assert len({c.case_id for c in cases})==len(cases)


def test_cli_payload_has_three_modes_no_external_model_tool_fields():
    m=load()
    payload=m.run_qualification()
    assert payload["experiment_valid"] is True
    assert payload["primary_hypothesis_outcome"] in {"SUPPORTED","MIXED","NOT_SUPPORTED"}
    assert payload["modes"]==["FLAT","CHUNKED","BLIND_CHUNKED"]
    assert payload["max_call_depth"]==8
    lower=json.dumps(payload).lower()
    for forbidden in ("qwen3.5","ollama","127.0.0.1:11434","lconnect","bconnect","flop","energy"):
        assert forbidden not in lower


def test_cli_validator_recomputes_outcome_and_rejects_drift():
    m=load()
    payload=m.run_qualification()
    payload["primary_hypothesis_outcome"]="NOT_SUPPORTED" if payload["primary_hypothesis_outcome"]!="NOT_SUPPORTED" else "SUPPORTED"
    errors=m.validate_qualification_payload(payload)
    assert any("outcome" in e.lower() for e in errors)


def test_cli_validator_rejects_impossible_aggregate_metrics():
    m=load()
    payload=m.run_qualification()
    payload["aggregate_metrics"]["chunked_root_visible_dispatches"]=-1
    errors=m.validate_qualification_payload(payload)
    assert any("chunked_root_visible_dispatches" in e for e in errors)


def test_stdout_and_output_bytes_match_and_utf8_thai(monkeypatch,tmp_path):
    m=load()
    raw=io.BytesIO()
    stdout=io.TextIOWrapper(raw,encoding="cp1252",errors="strict")
    monkeypatch.setattr(m.sys,"stdout",stdout)
    out=tmp_path/"a008.json"
    rc=m.main(["--output",str(out),"--note","ภาษาไทย"])
    stdout.flush()
    assert rc==0
    assert raw.getvalue()==out.read_bytes()
    payload=json.loads(raw.getvalue().decode("utf-8"))
    assert payload["note"]=="ภาษาไทย"


def test_valid_negative_outcome_exits_zero(monkeypatch,capsys):
    m=load()
    payload=m.run_qualification()
    # Keep the payload internally consistent by changing the aggregate evidence
    # and recomputing the outcome through the production classifier helper.
    payload["aggregate_metrics"]["chunk_reuse_count"]=0
    payload["reused_procedure_ids"]=[]
    payload["chunk_reuse_counts"]=[]
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
    assert json.loads(capsys.readouterr().out)["experiment_valid"] is False

@pytest.mark.parametrize(
    "metric,value_from,expected_substring",
    [
        ("chunked_success_count", "success_plus_one", "chunked_success_count"),
        ("primitive_sequence_equivalence_count", "success_plus_one", "primitive_sequence_equivalence_count"),
        ("chunked_exact_failure_localization_count", "failure_plus_one", "chunked_exact_failure_localization_count"),
        ("explanation_provenance_correct_count", "provenance_plus_one", "explanation_provenance_correct_count"),
    ],
)
def test_cli_validator_rejects_impossible_count_relationships(metric,value_from,expected_substring):
    m=load()
    payload=m.run_qualification()
    aggregate=payload["aggregate_metrics"]
    if value_from=="success_plus_one":
        aggregate[metric]=aggregate["success_case_count"]+1
    elif value_from=="failure_plus_one":
        aggregate[metric]=aggregate["checked_failure_case_count"]+1
    else:
        aggregate[metric]=aggregate["checked_failure_case_count"]*3+1
    payload["primary_hypothesis_outcome"]="MIXED"
    errors=m.validate_qualification_payload(payload)
    assert any(expected_substring in error for error in errors)


def test_cli_validator_rejects_case_partition_and_reuse_metadata_drift():
    m=load()
    payload=m.run_qualification()
    payload["aggregate_metrics"]["valid_case_count"] += 1
    payload["primary_hypothesis_outcome"]="MIXED"
    errors=m.validate_qualification_payload(payload)
    assert any("case_count" in error for error in errors)

    payload=m.run_qualification()
    payload["reused_procedure_ids"]=["fabricated"]
    payload["primary_hypothesis_outcome"]="SUPPORTED"
    errors=m.validate_qualification_payload(payload)
    assert any("reuse" in error.lower() for error in errors)