from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TASKS = ROOT / "docs" / "development" / "tasks"
REPORT = ROOT / "docs" / "development" / "reports" / "ASCA-20261010-A009-integrated-cognitive-loop.md"
A006 = ROOT / "docs" / "development" / "reports" / "ASCA-20261009-A006-working-set-selective-activation.md"
A007 = ROOT / "docs" / "development" / "reports" / "ASCA-20261009-A007-surprise-uncertainty-expansion.md"
A008 = ROOT / "docs" / "development" / "reports" / "ASCA-20261009-A008-procedural-memory-skill-chunking.md"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_current_points_to_planned_a010_without_issue_after_a009_closure():
    text = read(TASKS / "CURRENT.md")
    assert "Current task: A010" in text
    assert "Status: ACTIVE" in text
    assert "GitHub Issue: #10" in text
    assert "A009 deterministic qualification: GREEN" in text
    assert "A009 physical qualification: GREEN" in text


def test_roadmap_marks_a009_done_a010_a011_planned():
    text = read(TASKS / "ROADMAP.md")
    assert "| A008 | Procedural Memory / Skill Chunking | DONE |" in text
    assert "| A009 | Integrated Cognitive Loop | DONE |" in text
    assert "| A010 | Dense/Non-selective Baseline Comparison | ACTIVE |" in text
    assert "| A011 | ASCA v0.x Qualification | PLANNED |" in text


def test_a009_task_ledger_is_done_and_preserves_architecture_boundaries():
    text = read(TASKS / "A009-integrated-cognitive-loop.md")
    assert "Status: DONE" in text
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


def test_a009_task_ledger_records_branch_qualification_and_physical_evidence():
    text = read(TASKS / "A009-integrated-cognitive-loop.md")
    assert "eecca7d842753fd2b39e8c565c704fb2e6303896" in text
    assert "37992245085" in text
    assert "2f92b5092de346f62879ac2cbb9f96d6de5d6f919e12d0693345c8228b01ab2a" in text
    assert "SUPPORTED" in text
    assert "qwen3-embedding:0.6b" in text
    assert "qwen3.5:4b" in text
    assert "physical" in text.lower() and "GREEN" in text


def test_a009_report_records_exact_branch_qualification_and_outcome():
    text = read(REPORT)
    assert "eecca7d842753fd2b39e8c565c704fb2e6303896" in text
    assert "37992245085" in text
    assert "455 passed" in text
    assert "2f92b5092de346f62879ac2cbb9f96d6de5d6f919e12d0693345c8228b01ab2a" in text
    assert "Primary A009 hypothesis outcome: `SUPPORTED`" in text
    assert "genuine_recovery_count | 2" in text
    assert "regression_count | 0" in text
    assert "primary_total_scope_evaluations | 19" in text
    assert "always_total_scope_evaluations | 27" in text
    assert "model_control_leakage_failure_count | 0" in text


def test_a009_report_records_physical_integration_without_rewriting_portable_result():
    text = read(REPORT)
    assert "qwen3-embedding:0.6b" in text
    assert "ac6da0dfba84a81fdbfbaf330198c33cd77c4cdfc53e8bc50eb581914a15621d" in text
    assert "0.5037018224299838" in text
    assert "qwen3.5:4b" in text
    assert "2a654d98e6fba55d452b7043684e9b57a947e393bbffa62485a7aac05ee4eefd" in text
    assert "prompt tokens reported: 151" in text
    assert "generated tokens reported: 256" in text
    assert "Physical integration validity:" in text
    assert "`true`" in text
    assert "Physical evidence is secondary" in text
    assert "portable primary" in text.lower()


def test_a009_report_has_exactly_one_primary_outcome_declaration():
    text = read(REPORT)
    assert text.count("Primary A009 hypothesis outcome:") == 1
    assert "Primary A009 hypothesis outcome: `SUPPORTED`" in text
    assert "Primary A009 hypothesis outcome: `MIXED`" not in text
    assert "Primary A009 hypothesis outcome: `NOT_SUPPORTED`" not in text


def test_readme_current_stage_records_a009_supported_and_a010_planned():
    text = read(ROOT / "README.md")
    assert "A009" in text
    assert "Integrated Cognitive Loop" in text
    assert "SUPPORTED" in text
    assert "A010" in text
    assert "Dense/Non-selective Baseline Comparison" in text
    assert "ACTIVE" in text
    assert "SINGLE_BEST" in text
    assert "CHUNKED" in text


def test_historical_a006_a007_a008_outcomes_remain_unchanged():
    assert "Final A006 hypothesis outcome: `NOT_SUPPORTED`" in read(A006)
    assert "Final A007 hypothesis outcome: `SUPPORTED`" in read(A007)
    assert "Final A008 hypothesis outcome: `SUPPORTED`" in read(A008)

def test_a009_report_records_whole_branch_review_and_exact_post_review_ci():
    text = read(REPORT)
    assert "4796d28e9285dc395240010987126a45c4e5ed5d" in text
    assert "37999918527" in text
    assert "463 passed" in text
    assert "Critical findings: 0" in text
    assert "Important findings: 5" in text
    assert "author self-review" in text.lower()
    assert "independent reviewer" in text.lower()
    assert "completed primitive" in text.lower()
    assert "initial_world_state_ref" in text
    assert "TERMINAL_MODEL_DIGEST" in text
    assert "aggregate" in text.lower() and "case evidence" in text.lower()
    assert "model_control_isolated" in text


def test_a009_task_ledger_records_post_review_green_pending_final_main():
    text = read(TASKS / "A009-integrated-cognitive-loop.md")
    assert "Whole-branch review: GREEN" in text
    assert "4796d28e9285dc395240010987126a45c4e5ed5d" in text
    assert "37999918527" in text
    assert "Important findings: 5" in text
    assert "final-main" in text.lower()

def test_a009_report_records_reviewed_main_integration_evidence():
    text = read(REPORT)
    assert "Main integration: GREEN" in text
    assert "05d3c743df84c4bf12fb8d2c1389db4d3afa39b5" in text
    assert "38000327254" in text
    assert "465 passed" in text
    assert "fast-forward" in text.lower()
    assert "merge commit" in text.lower()


def test_a009_task_and_current_mark_final_main_gate_green_pending_issue_close():
    task = read(TASKS / "A009-integrated-cognitive-loop.md")
    current = read(TASKS / "CURRENT.md")
    assert "- [x] Exact branch CI, whole-branch review, final-main CI and synchronization pass." in task
    assert "Main integration: GREEN" in task
    assert "05d3c743df84c4bf12fb8d2c1389db4d3afa39b5" in task
    assert "38000327254" in task
    assert "A009 main integration: GREEN" in current
    assert "A009 exact final-main CI: GREEN" in current
    assert "Current task: A010" in current
    assert "GitHub Issue: #10" in current

def test_a009_repository_closure_state_is_final_not_pending():
    task = read(TASKS / "A009-integrated-cognitive-loop.md")
    current = read(TASKS / "CURRENT.md")
    report = read(REPORT)
    assert "Status: DONE" in task
    assert "GitHub Issue: #9 (closed as completed)" in task
    assert "A009 GitHub Issue #9: CLOSED (completed)" in current
    assert "A009 repository state: DONE" in report
    assert "GitHub Issue #9 closure: completed" in report
    assert "remains open" not in task.lower()
    assert "remains open" not in current.lower()
