from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TASKS = ROOT / "docs" / "development" / "tasks"
REPORT_A006 = ROOT / "docs" / "development" / "reports" / "ASCA-20261009-A006-working-set-selective-activation.md"


def _read(path: Path) -> str:
    assert path.exists(), f"{path.relative_to(ROOT)} must exist"
    return path.read_text(encoding="utf-8")


def test_current_points_to_active_a007_issue_7_and_branch():
    text = _read(TASKS / "CURRENT.md")
    assert "Current task: A007" in text
    assert "Status: ACTIVE" in text
    assert "GitHub Issue: #7" in text
    assert "Branch: research/a007-uncertainty-expansion" in text


def test_a007_task_records_required_scope_and_boundaries():
    text = _read(TASKS / "A007-surprise-uncertainty-expansion.md")
    assert "Status: ACTIVE" in text
    assert "GitHub Issue: #7" in text
    assert "NOT_SUPPORTED" in text
    assert "SINGLE_BEST" in text
    assert "0.5037018224299838" in text
    assert "top_k = 12" in text
    assert "top_k = 24" in text
    assert "top_k = 32" in text
    assert "scalar surprise" in text.lower()
    assert "does not" in text.lower()
    assert "typed graph" in text.lower()
    assert "qwen3.5:4b" in text
    assert "FlyWireLLM" in text
    assert "paused" in text.lower()
    assert "A008" in text
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


def test_roadmap_activates_a007_and_keeps_a008_through_a011_planned():
    text = _read(TASKS / "ROADMAP.md")
    assert "| A006 | Working Set / Selective Activation | DONE |" in text
    assert "| A007 | Surprise, Uncertainty & Expansion | ACTIVE |" in text
    assert "| A008 | Procedural Memory / Skill Chunking | PLANNED |" in text
    assert "| A011 | ASCA v0.x Qualification | PLANNED |" in text


def test_readme_current_stage_is_a007_and_preserves_a006_negative_result():
    text = _read(ROOT / "README.md")
    lower = text.lower()
    assert "a007" in lower
    assert "surprise, uncertainty & expansion" in lower
    assert "NOT_SUPPORTED" in text
    assert "SINGLE_BEST" in text
    assert "qwen3.5:4b" in text
    assert "typed graph" in lower


def test_a006_closure_report_remains_historical_evidence():
    text = _read(REPORT_A006)
    assert "Final A006 hypothesis outcome: `NOT_SUPPORTED`" in text
    assert "0.5037018224299838" in text
    assert "37932789283" in text or "37932522003" in text
