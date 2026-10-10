from __future__ import annotations

import importlib.util
import io
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "qualify_relational_activation_a013.py"


def load():
    assert SCRIPT.exists()
    spec = importlib.util.spec_from_file_location("a013q", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_cli_frozen_identity_and_actual_architecture_decision():
    m = load()
    payload = m.run_qualification()

    assert m.QUALIFICATION_SCOPE == "deterministic_relational_activation_a013"
    assert m.FIXTURE_VERSION == "a013-deterministic-v1"
    assert (
        m.EXPECTED_FIXTURE_FINGERPRINT
        == "fcd805a5229bfad43f8eed6999be37ae61168dda1a8560f04370b3df0262baa5"
    )
    assert payload["experiment_valid"] is True
    assert payload["primary_architecture_decision"] == "SIGNAL_GATED_RELATION_JUSTIFIED"
    assert payload["fixture_fingerprint"] == m.EXPECTED_FIXTURE_FINGERPRINT
    assert payload["case_ids"] == list(m.EXPECTED_CASE_IDS)
    assert payload["policies"] == [
        "VECTOR_ONLY",
        "ALWAYS_RELATION",
        "SIGNAL_GATED_RELATION",
    ]
    assert payload["case_count"] == 17
    assert payload["valid_case_count"] == 16
    assert payload["invalid_case_count"] == 1
    assert payload["vector_success_count"] == 10
    assert payload["always_success_count"] == 16
    assert payload["signal_success_count"] == 16
    assert payload["signal_relation_invocation_count"] == 10
    assert payload["always_relation_invocation_count"] == 16
    assert payload["signal_relation_scanned_edge_count"] == 11
    assert payload["always_relation_scanned_edge_count"] == 16


def test_validator_rejects_fingerprint_case_order_decision_and_metric_drift():
    m = load()

    payload = m.run_qualification()
    payload["fixture_fingerprint"] = "0" * 64
    assert any("fixture" in item.lower() for item in m.validate_qualification_payload(payload))

    payload = m.run_qualification()
    payload["case_ids"] = list(reversed(payload["case_ids"]))
    assert any("case_ids" in item for item in m.validate_qualification_payload(payload))

    payload = m.run_qualification()
    payload["primary_architecture_decision"] = "MIXED"
    assert any("decision" in item.lower() for item in m.validate_qualification_payload(payload))

    payload = m.run_qualification()
    payload["signal_relation_scanned_edge_count"] += 1
    assert any(
        "signal_relation_scanned_edge_count" in item
        for item in m.validate_qualification_payload(payload)
    )


def test_validator_rejects_raw_path_or_provenance_drift():
    m = load()
    payload = m.run_qualification()
    case = next(
        item
        for item in payload["cases"]
        if item["case_id"] == "ownership-workplace-one-hop"
    )
    signal = next(
        item
        for item in case["runs"]
        if item["policy"] == "SIGNAL_GATED_RELATION"
    )
    signal["relation_path_edge_ids"] = [["invented-edge"]]
    errors = m.validate_qualification_payload(payload)
    assert any("raw evidence" in item.lower() or "cases" in item.lower() for item in errors)


def test_stdout_and_output_bytes_match_utf8(monkeypatch, tmp_path):
    m = load()
    raw = io.BytesIO()
    stdout = io.TextIOWrapper(raw, encoding="cp1252", errors="strict")
    monkeypatch.setattr(m.sys, "stdout", stdout)
    out = tmp_path / "a013.json"

    rc = m.main(["--output", str(out), "--note", "ภาษาไทย"])
    stdout.flush()

    assert rc == 0
    assert raw.getvalue() == out.read_bytes()
    payload = json.loads(raw.getvalue().decode("utf-8"))
    assert payload["note"] == "ภาษาไทย"
    assert payload["primary_architecture_decision"] == "SIGNAL_GATED_RELATION_JUSTIFIED"


def test_invalid_payload_exits_nonzero(monkeypatch, capsys):
    m = load()
    payload = m.run_qualification()
    payload["fixture_fingerprint"] = "0" * 64
    monkeypatch.setattr(m, "run_qualification", lambda: payload)

    rc = m.main([])
    assert rc == 1
    emitted = json.loads(capsys.readouterr().out)
    assert emitted["experiment_valid"] is False
    assert emitted["errors"]


def test_valid_negative_or_mixed_vocabulary_is_not_equated_with_process_failure():
    m = load()
    assert m.VALID_DECISIONS == {
        "SIGNAL_GATED_RELATION_JUSTIFIED",
        "ALWAYS_RELATION_PREFERRED",
        "RELATION_INTEGRATION_NOT_JUSTIFIED",
        "MIXED",
    }
