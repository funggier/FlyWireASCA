from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TASKS = ROOT / "docs" / "development" / "tasks"


def _read(path: Path) -> str:
    assert path.exists(), f"{path.relative_to(ROOT)} must exist"
    return path.read_text(encoding="utf-8")


def test_current_points_to_active_a005_issue_5_and_branch():
    text = _read(TASKS / "CURRENT.md")
    assert "Current task: A005" in text
    assert "Status: ACTIVE" in text
    assert "GitHub Issue: #5" in text
    assert "Branch: research/a005-vector-memory" in text


def test_a005_task_records_vector_only_scope_and_decision_gate():
    text = _read(TASKS / "A005-semantic-vector-memory-retrieval.md")
    assert "Status: ACTIVE" in text
    assert "GitHub Issue: #5" in text
    assert "Vector + Metadata" in text
    assert "typed graph" in text.lower()
    assert "VECTOR_SUFFICIENT" in text
    assert "VECTOR_NEEDS_INDEX_OR_METADATA" in text
    assert "GRAPH_JUSTIFIED" in text
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


def test_roadmap_renames_only_a005_and_keeps_future_tasks_planned():
    text = _read(TASKS / "ROADMAP.md")
    assert "| A005 | Semantic Vector Memory Retrieval | ACTIVE |" in text
    assert "| A006 | Working Set / Selective Activation | PLANNED |" in text
    assert "| A011 | ASCA v0.x Qualification | PLANNED |" in text
    assert "Associative Memory & Recall" not in text


def test_readme_states_vector_metadata_experiment_and_graph_is_deferred():
    text = _read(ROOT / "README.md")
    lower = text.lower()
    assert "a005" in lower
    assert "vector + metadata" in lower
    assert "graph" in lower
    assert "deferred" in lower
    assert "qwen3.5:4b" in text
