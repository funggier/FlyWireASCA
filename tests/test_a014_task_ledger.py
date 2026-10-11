from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TASKS = ROOT / "docs" / "development" / "tasks"
TASK = TASKS / "A014-structural-need-inference.md"
DESIGN = ROOT / "docs" / "superpowers" / "specs" / "2026-10-11-a014-structural-need-inference-design.md"
PLAN = ROOT / "docs" / "superpowers" / "plans" / "2026-10-11-a014-structural-need-inference.md"


def test_a014_active_lifecycle_is_recorded():
    task = TASK.read_text(encoding="utf-8")
    current = (TASKS / "CURRENT.md").read_text(encoding="utf-8")
    roadmap = (TASKS / "ROADMAP.md").read_text(encoding="utf-8")

    assert "Status: ACTIVE" in task
    assert "GitHub Issue: #18" in task
    assert "Branch: research/a014-structural-need-inference" in task
    assert "Activation base: 4549951e3d2dbdbd877559d6b06ad501999e71f6" in task
    assert DESIGN.exists()
    assert PLAN.exists()

    assert "Current task: A014" in current
    assert current.count("Current task:") == 1
    assert "Status: ACTIVE" in current
    assert "GitHub Issue: #18" in current
    assert (
        "| A014 | Structural Need Inference / Query Intent Routing Gate | ACTIVE |"
        in roadmap
    )


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
