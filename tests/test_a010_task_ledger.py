from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TASKS = ROOT / "docs" / "development" / "tasks"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_current_activates_a010_with_actual_issue_number():
    text = read(TASKS / "CURRENT.md")
    assert "Current task: A010" in text
    assert "Status: ACTIVE" in text
    assert "GitHub Issue: #10" in text
    assert "A011" in text and "PLANNED" in text


def test_roadmap_marks_a010_active_and_a011_planned():
    text = read(TASKS / "ROADMAP.md")
    assert "| A009 | Integrated Cognitive Loop | DONE |" in text
    assert "| A010 | Dense/Non-selective Baseline Comparison | ACTIVE |" in text
    assert "| A011 | ASCA v0.x Qualification | PLANNED |" in text


def test_a010_task_ledger_records_approved_design_plan_and_boundaries():
    text = read(TASKS / "A010-dense-nonselective-baseline-comparison.md")
    assert "Status: ACTIVE" in text
    assert "GitHub Issue: #10" in text
    assert "research/a010-dense-nonselective-baseline-comparison" in text
    assert "2026-10-10-a010-dense-nonselective-baseline-comparison-design.md" in text
    assert "2026-10-10-a010-dense-nonselective-baseline-comparison.md" in text
    assert "A006" in text and "NOT_SUPPORTED" in text
    assert "A007" in text and "SUPPORTED" in text
    assert "A008" in text and "SUPPORTED" in text
    assert "A009" in text and "SUPPORTED" in text
    assert "select_exhaustive" in text
    assert "CHUNKED" in text
    assert "FlyWireLLM" in text and "untouched" in text.lower()


def test_readme_repairs_stale_a009_issue_state_and_marks_a010_active():
    text = read(ROOT / "README.md")
    assert "A009 Issue #9 remains open" not in text
    assert "A009" in text and "SUPPORTED" in text
    assert "A010" in text
    assert "Dense/Non-selective Baseline Comparison" in text
    assert "ACTIVE" in text
