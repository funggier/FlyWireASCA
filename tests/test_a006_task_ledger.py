from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TASKS = ROOT / "docs" / "development" / "tasks"
REPORT_A005 = ROOT / "docs" / "development" / "reports" / "ASCA-20261009-A005-vector-memory-retrieval.md"


def _read(path: Path) -> str:
    assert path.exists(), f"{path.relative_to(ROOT)} must exist"
    return path.read_text(encoding="utf-8")


def test_current_points_to_active_a006_issue_6_and_branch():
    text = _read(TASKS / "CURRENT.md")
    assert "Current task: A006" in text
    assert "Status: ACTIVE" in text
    assert "GitHub Issue: #6" in text
    assert "Branch: research/a006-working-set" in text


def test_a006_task_records_required_scope_profile_and_next_milestone():
    text = _read(TASKS / "A006-working-set-selective-activation.md")
    assert "Status: ACTIVE" in text
    assert "GitHub Issue: #6" in text
    assert "VectorMemoryResult" in text
    assert "does not build or traverse a typed graph" in text
    assert "qwen3.5:4b" in text
    assert "does not call" in text
    assert "0.5037018224299838" in text
    assert "top_k = 12" in text
    assert "max_memory_nodes = 8" in text
    assert "max_working_set_items = 4" in text
    assert "A007" in text
    for heading in (
        "## Goal",
        "## Scope",
        "## Phases",
        "## Acceptance Criteria",
        "## Evidence",
        "## Current Action",
        "## Next Action",
    ):
        assert heading in text


def test_roadmap_activates_a006_and_keeps_a007_through_a011_planned():
    text = _read(TASKS / "ROADMAP.md")
    assert "| A005 | Semantic Vector Memory Retrieval | DONE |" in text
    assert "| A006 | Working Set / Selective Activation | ACTIVE |" in text
    assert "| A007 | Surprise, Uncertainty & Expansion | PLANNED |" in text
    assert "| A011 | ASCA v0.x Qualification | PLANNED |" in text


def test_readme_current_stage_is_a006_without_graph_or_generation_claim():
    text = _read(ROOT / "README.md")
    lower = text.lower()
    assert "a006" in lower
    assert "working set / selective activation" in lower
    assert "typed graph" in lower
    assert "does not" in lower
    assert "qwen3.5:4b" in text


def test_a005_closure_report_remains_historical_evidence():
    text = _read(REPORT_A005)
    assert "Final graph decision: `VECTOR_SUFFICIENT`" in text
    assert "0.5037018224299838" in text
    assert "ac6da0dfba84a81fdbfbaf330198c33cd77c4cdfc53e8bc50eb581914a15621d" in text
