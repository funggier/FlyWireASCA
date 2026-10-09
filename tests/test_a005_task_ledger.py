from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TASKS = ROOT / "docs" / "development" / "tasks"
REPORT = ROOT / "docs" / "development" / "reports" / "ASCA-20261009-A005-vector-memory-retrieval.md"


def _read(path: Path) -> str:
    assert path.exists(), f"{path.relative_to(ROOT)} must exist"
    return path.read_text(encoding="utf-8")


def test_current_points_to_planned_a006_after_a005_closure():
    text = _read(TASKS / "CURRENT.md")
    assert "Current task: A006" in text
    assert "Status: PLANNED" in text
    assert "GitHub Issue: not created" in text


def test_a005_task_is_done_and_records_vector_decision_gate():
    text = _read(TASKS / "A005-semantic-vector-memory-retrieval.md")
    assert "Status: DONE" in text
    assert "GitHub Issue: #5" in text
    assert "VECTOR_SUFFICIENT" in text
    assert "0.5037018224299838" in text
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


def test_roadmap_marks_a005_done_and_a006_remains_planned():
    text = _read(TASKS / "ROADMAP.md")
    assert "| A005 | Semantic Vector Memory Retrieval | DONE |" in text
    assert "| A006 | Working Set / Selective Activation | PLANNED |" in text
    assert "| A007 | Surprise, Uncertainty & Expansion | PLANNED |" in text
    assert "Graph" not in text


def test_a005_closure_report_records_exact_candidate_physical_and_ci_evidence():
    text = _read(REPORT)
    assert "78099fe3e36e8e1292085425f1553a05b95a820e" in text
    assert "151 passed" in text
    assert "37906978728" in text
    assert "ac6da0dfba84a81fdbfbaf330198c33cd77c4cdfc53e8bc50eb581914a15621d" in text
    assert "0.5037018224299838" in text
    assert "6/6" in text
    assert "VECTOR_SUFFICIENT" in text
    assert "controlled" in text.lower()
    assert "FlyWireLLM" in text
    assert "paused" in text.lower()


def test_a005_report_has_exactly_one_decision_outcome_section_value():
    text = _read(REPORT)
    marker = "Final graph decision: \u0060VECTOR_SUFFICIENT\u0060"
    assert text.count(marker) == 1
    assert "Final graph decision: \u0060VECTOR_NEEDS_INDEX_OR_METADATA\u0060" not in text
    assert "Final graph decision: \u0060GRAPH_JUSTIFIED\u0060" not in text


def test_a005_closure_does_not_auto_create_graph_task():
    task_names = {path.name.lower() for path in TASKS.glob("*.md")}
    assert not any("graph" in name for name in task_names)
