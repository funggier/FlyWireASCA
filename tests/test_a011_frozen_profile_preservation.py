from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "verify_a011_frozen_profile_preservation.py"


def load():
    spec = importlib.util.spec_from_file_location("a011_preserve", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_current_tree_preserves_a011_frozen_profile_without_requalifying_a012():
    m = load()
    payload = m.run_check(ROOT)
    assert payload["preservation_valid"] is True
    assert payload["profile_sha256"] == m.EXPECTED_PROFILE_SHA256
    assert payload["protected_sha256"] == m.EXPECTED_PROTECTED_SHA256
    assert payload["protected_path_count"] == 67
    assert "does not qualify the current HEAD" in payload["boundary"]


def test_preservation_check_fails_closed_on_anchor_drift(monkeypatch):
    m = load()
    monkeypatch.setattr(m, "EXPECTED_PROTECTED_SHA256", "0" * 64)
    payload = m.run_check(ROOT)
    assert payload["preservation_valid"] is False
    assert any("protected" in item.lower() for item in payload["errors"])


def test_preservation_check_fails_closed_on_profile_anchor_drift(monkeypatch):
    m = load()
    monkeypatch.setattr(m, "EXPECTED_PROFILE_SHA256", "0" * 64)
    payload = m.run_check(ROOT)
    assert payload["preservation_valid"] is False
    assert any("profile" in item.lower() for item in payload["errors"])
