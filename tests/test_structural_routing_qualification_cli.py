from __future__ import annotations

import importlib.util
import io
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "qualify_structural_routing_a014.py"


def load():
    assert SCRIPT.exists()
    spec = importlib.util.spec_from_file_location("a014q", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_portable_qualifier_identity_role_and_nonphysical_boundary():
    m = load()
    payload = m.run_qualification()
    assert m.QUALIFICATION_SCOPE == "portable_structural_routing_a014"
    assert m.FIXTURE_VERSION == "a014-bilingual-v1"
    assert m.EVIDENCE_ROLE == "engineering_control_flow"
    assert m.EXPECTED_FIXTURE_FINGERPRINT == "c100f828265063c369d535f85db8166cbeaaba26943fbb6d276a24dc46018eca"
    assert m.EXPECTED_PROMPT_FINGERPRINT == "b48568801f32579e36f2e633b740a3d6cc0a276ffa6dcaa05d035f790b5f6a8d"
    assert payload["experiment_valid"] is True
    assert payload["evidence_role"] == "engineering_control_flow"
    assert payload["model_capability_qualified"] is False
    assert payload["physical_evidence"] is False
    assert payload["physical_architecture_decision"] is None
    assert payload["deterministic_repeat_match"] is True
    assert payload["case_count"] == 32
    assert payload["case_ids"] == list(m.EXPECTED_CASE_IDS)
    assert payload["fixture_fingerprint"] == m.EXPECTED_FIXTURE_FINGERPRINT
    assert payload["prompt_fingerprint"] == m.EXPECTED_PROMPT_FINGERPRINT
    assert payload["leakage_failure_count"] == 0


def test_portable_qualifier_pins_expected_policy_metrics_without_claiming_model_capability():
    m = load()
    payload = m.run_qualification()
    metrics = {item["policy"]: item for item in payload["policy_metrics"]}
    assert metrics["RULE_ONLY"]["downstream_success_count"] == 27
    assert metrics["RULE_ONLY"]["exact_relation_set_match_count"] == 23
    assert metrics["MODEL_ONLY"]["downstream_success_count"] == 32
    assert metrics["MODEL_ONLY"]["model_invocation_count"] == 32
    assert metrics["HYBRID_RULE_THEN_MODEL"]["downstream_success_count"] == 32
    assert metrics["HYBRID_RULE_THEN_MODEL"]["model_invocation_count"] == 9
    assert payload["model_capability_qualified"] is False


def test_validator_rejects_fixture_case_fingerprint_prompt_and_raw_evidence_drift():
    m = load()
    mutations = []
    p = m.run_qualification(); p["fixture_fingerprint"] = "0" * 64; mutations.append(p)
    p = m.run_qualification(); p["case_ids"] = list(reversed(p["case_ids"])); mutations.append(p)
    p = m.run_qualification(); p["runtime_input_fingerprints"][0][1] = "0" * 64; mutations.append(p)
    p = m.run_qualification(); p["evaluator_metadata_fingerprints"][0][1] = "0" * 64; mutations.append(p)
    p = m.run_qualification(); p["prompt_fingerprint"] = "0" * 64; mutations.append(p)
    p = m.run_qualification(); p["cases"][0]["task_success"] = not p["cases"][0]["task_success"]; mutations.append(p)
    for payload in mutations:
        assert m.validate_qualification_payload(payload)


def test_validator_rejects_metric_integrity_and_evidence_role_escalation():
    m = load()
    p = m.run_qualification(); p["policy_metrics"][0]["downstream_success_count"] += 1
    assert m.validate_qualification_payload(p)
    p = m.run_qualification(); p["leakage_failure_count"] = 1
    assert m.validate_qualification_payload(p)
    p = m.run_qualification(); p["evidence_role"] = "physical_model_capability"
    assert m.validate_qualification_payload(p)
    p = m.run_qualification(); p["model_capability_qualified"] = True
    assert m.validate_qualification_payload(p)
    p = m.run_qualification(); p["physical_evidence"] = True
    assert m.validate_qualification_payload(p)
    p = m.run_qualification(); p["physical_architecture_decision"] = "HYBRID_STRUCTURAL_ROUTING_JUSTIFIED"
    assert m.validate_qualification_payload(p)


def test_decision_vocabulary_is_exact_and_invalid_vocab_is_rejected():
    m = load()
    expected = [
        "HYBRID_STRUCTURAL_ROUTING_JUSTIFIED",
        "RULE_ROUTING_SUFFICIENT",
        "MODEL_ROUTING_PREFERRED",
        "STRUCTURAL_ROUTING_NOT_SUPPORTED",
        "MIXED",
    ]
    payload = m.run_qualification()
    assert payload["decision_vocabulary"] == expected
    payload["decision_vocabulary"] = expected + ["BOGUS"]
    assert m.validate_qualification_payload(payload)


def test_stdout_and_output_bytes_match_utf8(monkeypatch, tmp_path):
    m = load()
    raw = io.BytesIO()
    stdout = io.TextIOWrapper(raw, encoding="cp1252", errors="strict")
    monkeypatch.setattr(m.sys, "stdout", stdout)
    out = tmp_path / "a014.json"
    rc = m.main(["--output", str(out), "--note", "ภาษาไทย"])
    stdout.flush()
    assert rc == 0
    assert raw.getvalue() == out.read_bytes()
    payload = json.loads(raw.getvalue().decode("utf-8"))
    assert payload["note"] == "ภาษาไทย"
    assert payload["evidence_role"] == "engineering_control_flow"


def test_invalid_payload_exits_nonzero(monkeypatch, capsys):
    m = load()
    payload = m.run_qualification()
    payload["prompt_fingerprint"] = "0" * 64
    monkeypatch.setattr(m, "run_qualification", lambda: payload)
    rc = m.main([])
    assert rc == 1
    emitted = json.loads(capsys.readouterr().out)
    assert emitted["experiment_valid"] is False
    assert emitted["errors"]
