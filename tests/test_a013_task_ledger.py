from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TASKS = ROOT / "docs" / "development" / "tasks"
TASK = TASKS / "A013-selective-relational-activation.md"
CURRENT = TASKS / "CURRENT.md"
ROADMAP = TASKS / "ROADMAP.md"
DESIGN = ROOT / "docs" / "superpowers" / "specs" / "2026-10-11-a013-selective-relational-activation-design.md"
PLAN = ROOT / "docs" / "superpowers" / "plans" / "2026-10-11-a013-selective-relational-activation.md"


def test_a013_active_lifecycle_and_authority_are_coherent():
    task = TASK.read_text(encoding="utf-8")
    current = CURRENT.read_text(encoding="utf-8")
    roadmap = ROADMAP.read_text(encoding="utf-8")

    assert "Status: ACTIVE" in task
    assert "GitHub Issue: #16" in task
    assert "Current task: A013" in current
    assert "Status: ACTIVE" in current
    assert "GitHub Issue: #16" in current
    assert (
        "| A013 | Selective Relational Activation / Hybrid Recall Integration Gate | ACTIVE |"
        in roadmap
    )
    assert DESIGN.exists()
    assert PLAN.exists()


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
