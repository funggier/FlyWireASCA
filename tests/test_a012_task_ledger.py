from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TASKS = ROOT / "docs" / "development" / "tasks"
TASK = TASKS / "A012-relational-reasoning-structure-decision.md"
CURRENT = TASKS / "CURRENT.md"
ROADMAP = TASKS / "ROADMAP.md"
DESIGN = ROOT / "docs" / "superpowers" / "specs" / "2026-10-10-a012-relational-reasoning-structure-decision-design.md"
PLAN = ROOT / "docs" / "superpowers" / "plans" / "2026-10-10-a012-relational-reasoning-structure-decision.md"
REPORT = ROOT / "docs" / "development" / "reports" / "ASCA-20261010-A012-relational-reasoning-structure-decision.md"
HANDOFF = ROOT / "docs" / "development" / "reports" / "ASCA-20261010-full-session-handoff-a012-completed.md"


def test_a012_done_lifecycle_and_authority_are_coherent():
    task = TASK.read_text(encoding="utf-8")
    current = CURRENT.read_text(encoding="utf-8")
    roadmap = ROADMAP.read_text(encoding="utf-8")

    assert "Status: DONE" in task
    assert "GitHub Issue: #14" in task
    assert "Current task: A012" in current
    assert "Status: DONE" in current
    assert "GitHub Issue: #14" in current
    assert "| A012 | Relational Reasoning / Structure Decision Gate | DONE |" in roadmap
    assert DESIGN.exists()
    assert PLAN.exists()
    assert REPORT.exists()
    assert HANDOFF.exists()


def test_a012_final_report_records_exact_integration_and_decision():
    report = REPORT.read_text(encoding="utf-8")
    assert "Primary architecture decision: `EXPLICIT_RELATION_TRAVERSAL_JUSTIFIED`" in report
    assert "0728ddab442b774dcedb60a3fb7870444a95ffcb" in report
    assert "38067495867" in report
    assert "38067628031" in report
    assert "48dfc64bca60d62528787b57d04a01df04fac30d" in report
    assert "38067737917" in report
    assert "760cad31a867c6f52613d1e3c5aa7a879528ac386dcbb570cb5cd9c587c86340" in report
    assert "35cbe908737f259f917d20bc67c779dbb7107df1393488cedd08899bbe441455" in report
    assert "A005 remains `VECTOR_SUFFICIENT`" in report
    assert "FlyWireLLM was not modified" in report


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
