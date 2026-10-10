from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TASKS = ROOT / "docs" / "development" / "tasks"
TASK = TASKS / "A013-selective-relational-activation.md"
DESIGN = ROOT / "docs" / "superpowers" / "specs" / "2026-10-11-a013-selective-relational-activation-design.md"
PLAN = ROOT / "docs" / "superpowers" / "plans" / "2026-10-11-a013-selective-relational-activation.md"
REPORT = ROOT / "docs" / "development" / "reports" / "ASCA-20261011-A013-selective-relational-activation.md"
HANDOFF = ROOT / "docs" / "development" / "reports" / "ASCA-20261011-full-session-handoff-a013-completed.md"


def test_a013_historical_done_lifecycle_is_self_contained():
    task = TASK.read_text(encoding="utf-8")
    assert "Status: DONE" in task
    assert "GitHub Issue: #16" in task
    assert DESIGN.exists()
    assert PLAN.exists()
    assert REPORT.exists()
    assert HANDOFF.exists()


def test_a013_final_report_records_exact_integration_and_decision():
    text = REPORT.read_text(encoding="utf-8")
    assert "SIGNAL_GATED_RELATION_JUSTIFIED" in text
    assert "fcd805a5229bfad43f8eed6999be37ae61168dda1a8560f04370b3df0262baa5" in text
    assert "1dcb0d243ad82cfa53faff2279bc667119faf77c" in text
    assert "38088579496" in text
    assert "38088663875" in text
    assert "92f534a25771ffabf06f4076bc6b7deb27bd80b5" in text
    assert "38088760197" in text
    assert "7cde5442f4d905a42d312e4a11e0707d9c82c610ba489f0af185cf9f666f0b1d" in text
    assert "1033 passed" in text
    assert "target-free" in text.lower()
    assert "oracle" in text.lower()
    assert "FlyWireLLM was not modified" in text


def test_a013_design_requires_target_free_runtime_control():
    design = DESIGN.read_text(encoding="utf-8")
    lower = design.lower()
    assert "target-free" in lower
    assert "oracle" in lower
    assert "runtime retrieval and" in lower
    assert "must not receive expected target ids" in lower
    assert "`VECTOR_ONLY`" in design
    assert "`ALWAYS_RELATION`" in design
    assert "`SIGNAL_GATED_RELATION`" in design


def test_a013_preserves_historical_decision_boundaries():
    design = DESIGN.read_text(encoding="utf-8")
    for value in (
        "A005: `VECTOR_SUFFICIENT`",
        "A006: `NOT_SUPPORTED`",
        "A007: `SUPPORTED`",
        "A008: `SUPPORTED`",
        "A009: `SUPPORTED`",
        "A010: `NOT_SUPPORTED`",
        "A012: `EXPLICIT_RELATION_TRAVERSAL_JUSTIFIED`",
    ):
        assert value in design
    assert "FlyWireLLM" in design
    assert "does not edit A011-protected cognitive source blobs" in design
