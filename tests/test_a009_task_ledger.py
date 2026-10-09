from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TASKS = ROOT / "docs" / "development" / "tasks"
A006 = ROOT / "docs" / "development" / "reports" / "ASCA-20261009-A006-working-set-selective-activation.md"
A007 = ROOT / "docs" / "development" / "reports" / "ASCA-20261009-A007-surprise-uncertainty-expansion.md"
A008 = ROOT / "docs" / "development" / "reports" / "ASCA-20261009-A008-procedural-memory-skill-chunking.md"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_current_points_to_active_a009_issue_9_and_branch():
    text = read(TASKS / "CURRENT.md")
    assert "Current task: A009" in text
    assert "Status: ACTIVE" in text
    assert "GitHub Issue: #9" in text
    assert "Branch: research/a009-integrated-cognitive-loop" in text


def test_roadmap_marks_only_a009_active_among_a009_a011():
    text = read(TASKS / "ROADMAP.md")
    assert "| A008 | Procedural Memory / Skill Chunking | DONE |" in text
    assert "| A009 | Integrated Cognitive Loop | ACTIVE |" in text
    assert "| A010 | Dense/Non-selective Baseline Comparison | PLANNED |" in text
    assert "| A011 | ASCA v0.x Qualification | PLANNED |" in text


def test_a009_task_ledger_records_approved_architecture_and_boundaries():
    text = read(TASKS / "A009-integrated-cognitive-loop.md")
    assert "Status: ACTIVE" in text
    assert "GitHub Issue: #9" in text
    assert "Branch: research/a009-integrated-cognitive-loop" in text
    assert "2026-10-10-a009-integrated-cognitive-loop-design.md" in text
    assert "2026-10-10-a009-integrated-cognitive-loop.md" in text
    assert "A006" in text and "NOT_SUPPORTED" in text
    assert "A007" in text and "SUPPORTED" in text
    assert "A008" in text and "SUPPORTED" in text
    assert "SINGLE_BEST" in text
    assert "CHUNKED" in text
    assert "MISMATCH_DRIVEN_RECOVERY" in text
    assert "PROCEDURE_OUTCOME_MISMATCH" in text
    assert "maximum procedure attempts: 3" in text.lower()
    lower = text.lower()
    assert "no real os/api/lconnect/bconnect" in lower
    assert "flywirellm" in lower and "untouched" in lower


def test_a009_task_ledger_records_activation_base_and_exact_ci():
    text = read(TASKS / "A009-integrated-cognitive-loop.md")
    assert "8d0721a77abaae5d0cc6d6c7c81d4795c5d355fa" in text
    assert "37989472394" in text
    assert "success" in text.lower()


def test_readme_current_stage_is_a009_without_rewriting_a008_result():
    text = read(ROOT / "README.md")
    assert "A009" in text
    assert "Integrated Cognitive Loop" in text
    assert "ACTIVE" in text
    assert "SINGLE_BEST" in text
    assert "CHUNKED" in text
    assert "A006" in text and "NOT_SUPPORTED" in text
    assert "A007" in text and "SUPPORTED" in text
    assert "A008" in text and "SUPPORTED" in text


def test_historical_a006_a007_a008_outcomes_remain_unchanged():
    assert "Final A006 hypothesis outcome: `NOT_SUPPORTED`" in read(A006)
    assert "Final A007 hypothesis outcome: `SUPPORTED`" in read(A007)
    assert "Final A008 hypothesis outcome: `SUPPORTED`" in read(A008)
