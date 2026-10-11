from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TASKS = ROOT / "docs" / "development" / "tasks"
TASK = TASKS / "A014-structural-need-inference.md"
DESIGN = ROOT / "docs" / "superpowers" / "specs" / "2026-10-11-a014-structural-need-inference-design.md"
PLAN = ROOT / "docs" / "superpowers" / "plans" / "2026-10-11-a014-structural-need-inference.md"
REPORT = ROOT / "docs" / "development" / "reports" / "ASCA-20261011-A014-structural-need-inference.md"
HANDOFF = ROOT / "docs" / "development" / "reports" / "ASCA-20261011-full-session-handoff-a014-completed.md"


def test_a014_completed_lifecycle_is_recorded_self_contained():
    task = TASK.read_text(encoding="utf-8")

    assert "Status: DONE" in task
    assert "GitHub Issue: #18" in task
    assert "Historical branch: research/a014-structural-need-inference" in task
    assert "Activation base: 4549951e3d2dbdbd877559d6b06ad501999e71f6" in task
    assert DESIGN.exists()
    assert PLAN.exists()
    assert REPORT.exists()
    assert HANDOFF.exists()

    report = REPORT.read_text(encoding="utf-8")
    assert "HYBRID_STRUCTURAL_ROUTING_JUSTIFIED" in report
    assert "38116882068" in report
    assert "38152301384" in report
    assert "1162 passed in 98.61s" in report
    assert "71.875%" in report


def test_a014_task_preserves_boundaries():
    text = TASK.read_text(encoding="utf-8")
    lower = text.lower()
    assert "target-free" in lower
    assert "english" in lower
    assert "thai" in lower
    assert "qwen3.5:4b" in text
    assert "FlyWireLLM" in text
    assert "A011-protected" in text
    assert "A015" in text
    assert "end-to-end" in lower
