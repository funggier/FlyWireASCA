from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TASKS = ROOT / "docs" / "development" / "tasks"
REPORT = ROOT / "docs" / "development" / "reports" / "ASCA-20261009-A007-surprise-uncertainty-expansion.md"
REPORT_A006 = ROOT / "docs" / "development" / "reports" / "ASCA-20261009-A006-working-set-selective-activation.md"


def _read(path: Path) -> str:
    assert path.exists(), f"{path.relative_to(ROOT)} must exist"
    return path.read_text(encoding="utf-8")


def test_current_points_to_planned_a008_after_a007_closure():
    text = _read(TASKS / "CURRENT.md")
    assert "Current task: A008" in text
    assert "Status: PLANNED" in text
    assert "GitHub Issue: not created" in text


def test_a007_task_is_done_and_preserves_scope_boundaries():
    text = _read(TASKS / "A007-surprise-uncertainty-expansion.md")
    assert "Status: DONE" in text
    assert "GitHub Issue: #7" in text
    assert "SUPPORTED" in text
    assert "SINGLE_BEST" in text
    assert "0.5037018224299838" in text
    assert "NOT_SUPPORTED" in text
    assert "A006" in text
    assert "does not" in text.lower()
    assert "scalar surprise" in text.lower()
    assert "typed graph" in text.lower()
    assert "qwen3.5:4b" in text
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


def test_roadmap_marks_a007_done_and_a008_planned():
    text = _read(TASKS / "ROADMAP.md")
    assert "| A006 | Working Set / Selective Activation | DONE |" in text
    assert "| A007 | Surprise, Uncertainty & Expansion | DONE |" in text
    assert "| A008 | Procedural Memory / Skill Chunking | PLANNED |" in text
    assert "| A011 | ASCA v0.x Qualification | PLANNED |" in text


def test_readme_records_a007_supported_result_without_prediction_surprise_overclaim():
    text = _read(ROOT / "README.md")
    lower = text.lower()
    assert "a007" in lower
    assert "SUPPORTED" in text
    assert "signal_driven" in text.lower()
    assert "prediction surprise" in lower
    assert "does not" in lower
    assert "qwen3.5:4b" in text


def test_a007_closure_report_records_exact_branch_portable_and_physical_evidence():
    text = _read(REPORT)
    assert "d76084178a3fca84208794efca7a46330785eb6e" in text
    assert "308 passed" in text
    assert "37940884611" in text
    assert "59f95ef115534fe24e59570cb281c0564ab75aadf364f4c26feba0d4078213c9" in text
    assert "ac6da0dfba84a81fdbfbaf330198c33cd77c4cdfc53e8bc50eb581914a15621d" in text
    assert "0.5037018224299838" in text
    assert "NO_EXPANSION required-memory coverage: 0.5714285714285714" in text
    assert "SIGNAL_DRIVEN required-memory coverage: 1.0" in text
    assert "ALWAYS_EXPAND required-memory coverage: 1.0" in text
    assert "SIGNAL_DRIVEN recovery count: 3" in text
    assert "SIGNAL_DRIVEN regression count: 0" in text
    assert "SIGNAL_DRIVEN total rounds: 15" in text
    assert "ALWAYS_EXPAND total rounds: 24" in text
    assert "setup embedding requests: 8" in text
    assert "SIGNAL_DRIVEN embedding requests: 24" in text
    assert "ALWAYS_EXPAND embedding requests: 48" in text
    assert "portable SIGNAL_DRIVEN recovery count: 2" in text
    assert "portable SIGNAL_DRIVEN total rounds: 21" in text
    assert "portable ALWAYS_EXPAND total rounds: 33" in text
    assert "Final A007 hypothesis outcome: `SUPPORTED`" in text
    assert "FlyWireLLM" in text
    assert "paused" in text.lower()


def test_a007_report_has_exactly_one_primary_hypothesis_outcome():
    text = _read(REPORT)
    assert text.count("Final A007 hypothesis outcome:") == 1
    assert "Final A007 hypothesis outcome: `SUPPORTED`" in text
    assert "Final A007 hypothesis outcome: `MIXED`" not in text
    assert "Final A007 hypothesis outcome: `NOT_SUPPORTED`" not in text


def test_a007_closure_does_not_claim_true_prediction_surprise_or_create_a008_issue():
    text = _read(REPORT)
    lower = text.lower()
    assert "prediction surprise is not qualified" in lower
    assert "scalar uncertainty" in lower
    current = _read(TASKS / "CURRENT.md")
    assert "GitHub Issue: not created" in current


def test_a006_negative_physical_result_remains_historical_evidence():
    text = _read(REPORT_A006)
    assert "Final A006 hypothesis outcome: `NOT_SUPPORTED`" in text
    assert "convergence recovery count: 0" in text

def test_a007_report_records_post_review_hardening_and_physical_rerun():
    text = _read(REPORT)
    assert "5495ca909d141a8ad27dd29863d3926f24254b46" in text
    assert "37942219656" in text
    assert "Important" in text
    assert "research-outcome drift" in text
    assert "metric-counter relationships" in text
    assert "post-review physical rerun" in text.lower()
    assert "recovery count: 3" in text
    assert "regression count: 0" in text
    assert "rounds: 8/15/24" in text
    assert "fixture fingerprint unchanged" in text.lower()


def test_a007_task_marks_whole_branch_review_resolved():
    text = _read(TASKS / "A007-surprise-uncertainty-expansion.md")
    assert "- [x] Whole-branch review Critical/Important findings resolved." in text
    assert "5495ca909d141a8ad27dd29863d3926f24254b46" in text
    assert "37942219656" in text

def test_a007_report_records_merged_main_integration_evidence():
    text = _read(REPORT)
    assert "Main integration evidence" in text
    assert "61cf9053b39f8d4aed413058cd99e4ec664c8a42" in text
    assert "37945417867" in text
    assert "318 passed" in text
    task = _read(TASKS / "A007-surprise-uncertainty-expansion.md")
    assert "- [x] Final-main CI and clean/synchronized 0/0 integration gates pass." in task


def test_current_no_longer_says_a007_integration_is_pending():
    text = _read(TASKS / "CURRENT.md")
    assert "Current task: A008" in text
    assert "Status: PLANNED" in text
    assert "A007 integration: GREEN" in text
    assert "must complete whole-branch review" not in text

def test_a007_report_records_closure_evidence_main_ci():
    text = _read(REPORT)
    assert "Closure-evidence main CI" in text
    assert "794428389e632c241fbd8c15100b86c84cbd7dd4" in text
    assert "37945872610" in text
    task = _read(TASKS / "A007-surprise-uncertainty-expansion.md")
    assert "Final closure-evidence main CI: DONE" in task


def test_a007_all_acceptance_criteria_are_closed_before_issue_closure():
    text = _read(TASKS / "A007-surprise-uncertainty-expansion.md")
    acceptance = text.split("## Acceptance Criteria", 1)[1].split("## Evidence", 1)[0]
    assert "- [ ]" not in acceptance
