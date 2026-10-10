from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TASKS = ROOT / "docs" / "development" / "tasks"
TASK = TASKS / "A012-relational-reasoning-structure-decision.md"
CURRENT = TASKS / "CURRENT.md"
ROADMAP = TASKS / "ROADMAP.md"
DESIGN = ROOT / "docs" / "superpowers" / "specs" / "2026-10-10-a012-relational-reasoning-structure-decision-design.md"
PLAN = ROOT / "docs" / "superpowers" / "plans" / "2026-10-10-a012-relational-reasoning-structure-decision.md"


def test_a012_planned_lifecycle_and_authority_are_coherent():
    task = TASK.read_text(encoding="utf-8")
    current = CURRENT.read_text(encoding="utf-8")
    roadmap = ROADMAP.read_text(encoding="utf-8")

    assert "Status: PLANNED" in task
    assert "GitHub Issue: not created" in task
    assert "Current task: A012" in current
    assert "Status: PLANNED" in current
    assert "GitHub Issue: not created" in current
    assert "| A012 | Relational Reasoning / Structure Decision Gate | PLANNED |" in roadmap
    assert DESIGN.exists()
    assert PLAN.exists()


def test_a012_preserves_historical_outcomes_and_decision_boundary():
    task = TASK.read_text(encoding="utf-8")
    design = DESIGN.read_text(encoding="utf-8")
    assert "VECTOR_SUFFICIENT" in task
    assert "EXPLICIT_RELATION_TRAVERSAL_JUSTIFIED" in design
    assert "VECTOR_METADATA_REMAINS_SUFFICIENT" in design
    assert "`MIXED`" in design
    assert "FlyWireLLM remains independent and untouched" in design
    for value in (
        "A006: `NOT_SUPPORTED`",
        "A007: `SUPPORTED`",
        "A008: `SUPPORTED`",
        "A009: `SUPPORTED`",
        "A010: `NOT_SUPPORTED`",
    ):
        assert value in design
