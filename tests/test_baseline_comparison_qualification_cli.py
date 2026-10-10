import importlib.util
import io
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "qualify_baseline_comparison_a010.py"


def load():
    assert SCRIPT.exists()
    spec = importlib.util.spec_from_file_location("a010q", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def test_cli_frozen_identity_and_actual_negative_outcome():
    m = load()
    assert m.QUALIFICATION_SCOPE == "deterministic_dense_nonselective_baseline_a010"
    assert m.FIXTURE_VERSION == "a010-deterministic-v1"
    assert m.EXPECTED_FIXTURE_FINGERPRINT == "a1792f471409db74e436f63765d6c0330a6544575edfd45585b9eef30767dd68"
    assert m.VARIANTS == [
        "ASCA_PRIMARY",
        "DENSE_EXHAUSTIVE",
        "ASCA_ALWAYS_MAX_SCOPE",
        "ASCA_NO_STRUCTURAL_EXPANSION",
        "ASCA_FAMILIARITY_DISABLED",
    ]
    payload = m.run_qualification()
    assert payload["experiment_valid"] is True
    assert payload["primary_hypothesis_outcome"] == "NOT_SUPPORTED"
    assert payload["fixture_fingerprint"] == m.EXPECTED_FIXTURE_FINGERPRINT
    assert len(payload["case_ids"]) == 12
    aggregate = payload["aggregate_metrics"]
    assert aggregate["asca_query_count"] == 28
    assert aggregate["dense_query_count"] == 27
    assert aggregate["asca_scored_vector_count"] == 1984
    assert aggregate["dense_scored_vector_count"] == 1440
    assert aggregate["asca_cumulative_selected_count"] == 66
    assert aggregate["dense_cumulative_selected_count"] == 480
    assert aggregate["dense_only_success_count"] == 1


def test_cli_validator_rejects_aggregate_fingerprint_policy_and_outcome_drift():
    m = load()

    payload = m.run_qualification()
    payload["aggregate_metrics"]["asca_query_count"] += 1
    assert any("asca_query_count" in item for item in m.validate_qualification_payload(payload))

    payload = m.run_qualification()
    payload["cases"][0]["shared_input_fingerprint"] = "0" * 64
    assert any("fingerprint" in item.lower() for item in m.validate_qualification_payload(payload))

    payload = m.run_qualification()
    payload["dense_top_k_policy"] = "32"
    assert any("dense_top_k_policy" in item for item in m.validate_qualification_payload(payload))

    payload = m.run_qualification()
    payload["primary_hypothesis_outcome"] = "SUPPORTED"
    assert any("outcome" in item.lower() for item in m.validate_qualification_payload(payload))


def test_cli_validator_rejects_duplicate_execution_ids_and_case_order_drift():
    m = load()
    payload = m.run_qualification()
    case = next(item for item in payload["cases"] if item["case_id"] == "procedure-recovery-one-scope")
    primary = next(item for item in case["runs"] if item["variant"] == "ASCA_PRIMARY")
    primary["execution_ids"] = [primary["execution_ids"][0], primary["execution_ids"][0]]
    assert any("execution_ids" in item for item in m.validate_qualification_payload(payload))

    payload = m.run_qualification()
    payload["case_ids"] = list(reversed(payload["case_ids"]))
    assert any("case_ids" in item for item in m.validate_qualification_payload(payload))


def test_stdout_and_output_bytes_match_utf8(monkeypatch, tmp_path):
    m = load()
    raw = io.BytesIO()
    stdout = io.TextIOWrapper(raw, encoding="cp1252", errors="strict")
    monkeypatch.setattr(m.sys, "stdout", stdout)
    out = tmp_path / "a010.json"

    rc = m.main(["--output", str(out), "--note", "ภาษาไทย"])
    stdout.flush()

    assert rc == 0
    assert raw.getvalue() == out.read_bytes()
    payload = json.loads(raw.getvalue().decode("utf-8"))
    assert payload["note"] == "ภาษาไทย"
    assert payload["primary_hypothesis_outcome"] == "NOT_SUPPORTED"


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
