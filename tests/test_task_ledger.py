from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TASKS = ROOT / "docs" / "development" / "tasks"


def _read(name: str) -> str:
    path = TASKS / name
    assert path.exists(), f"{name} must exist"
    return path.read_text(encoding="utf-8")


def test_current_points_to_exactly_one_next_planned_task_a003():
    text = _read("CURRENT.md")
    assert "Current task: A003" in text
    assert "Status: PLANNED" in text
    assert "GitHub Issue: not created" in text
    assert text.count("Current task:") == 1


def test_a002_contains_recovery_and_evidence_sections():
    text = _read("A002-asca-architecture-contract.md")
    assert "Status: DONE" in text
    for heading in (
        "## Goal",
        "## Scope",
        "## Acceptance Criteria",
        "## Evidence",
        "## Current Action",
        "## Next Action",
    ):
        assert heading in text


def test_a001_contains_recovery_and_evidence_sections():
    text = _read("A001-repository-research-foundation.md")
    assert "Status: DONE" in text
    for heading in (
        "## Goal",
        "## Scope",
        "## Acceptance Criteria",
        "## Evidence",
        "## Current Action",
        "## Next Action",
    ):
        assert heading in text


def test_roadmap_lists_a001_through_a010_exactly_once():
    text = _read("ROADMAP.md")
    for number in range(1, 11):
        task_id = f"A{number:03d}"
        assert text.count(task_id) == 1, task_id


def test_task_readme_documents_states_and_authoritative_source_rule():
    text = _read("README.md")
    assert "PLANNED / ACTIVE / BLOCKED / DONE" in text
    lower = text.lower()
    assert "git/github/runtime" in lower
    assert "stale" in lower


def test_a001_closure_report_records_exact_qualification():
    report = ROOT / "docs" / "development" / "reports" / "ASCA-20261008-A001-repository-foundation.md"
    assert report.exists(), "A001 closure report must exist"
    text = report.read_text(encoding="utf-8")
    assert "08868b099da4ae2bd31154201dd3ac9d0568fe5d" in text
    assert "14 passed" in text
    assert "37759237750" in text
    assert "PUBLIC" in text
    assert "FlyWireLLM" in text


def test_a001_closure_report_has_no_trailing_whitespace():
    report = ROOT / "docs" / "development" / "reports" / "ASCA-20261008-A001-repository-foundation.md"
    lines = report.read_text(encoding="utf-8").splitlines()
    assert [index for index, line in enumerate(lines, 1) if line != line.rstrip()] == []

def test_a002_closure_report_records_exact_qualification():
    report = ROOT / "docs" / "development" / "reports" / "ASCA-20261008-A002-architecture-contract.md"
    assert report.exists(), "A002 closure report must exist"
    text = report.read_text(encoding="utf-8")
    assert "c70e11f1af9cf652b8526f300a9c1d7317e5b6de" in text
    assert "41 passed" in text
    assert "37793506259" in text
    assert "architecture_contract_audit=PASS" in text
    assert "FlyWireLLM" in text
