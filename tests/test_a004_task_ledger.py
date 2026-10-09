from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TASKS = ROOT / "docs" / "development" / "tasks"
REPORT = ROOT / "docs" / "development" / "reports" / "ASCA-20261009-A004-qwen-adapter-baseline.md"


def _read(path: Path) -> str:
    assert path.exists(), f"{path.relative_to(ROOT)} must exist"
    return path.read_text(encoding="utf-8")


def test_current_points_to_planned_a005_after_a004_closure():
    text = _read(TASKS / "CURRENT.md")
    assert "Current task: A005" in text
    assert "Status: PLANNED" in text
    assert "GitHub Issue: not created" in text


def test_a004_task_is_done_with_required_recovery_sections():
    text = _read(TASKS / "A004-local-model-adapter-qwen-baseline.md")
    assert "Status: DONE" in text
    assert "GitHub Issue: #4" in text
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


def test_roadmap_is_migrated_and_a004_done_a005_planned():
    text = _read(TASKS / "ROADMAP.md")
    for number in range(1, 12):
        task_id = f"A{number:03d}"
        assert text.count(task_id) == 1, task_id
    assert "| A001 | Repository & Research Foundation | DONE |" in text
    assert "| A002 | ASCA Architecture Contract | DONE |" in text
    assert "| A003 | Familiarity System | DONE |" in text
    assert "| A004 | Local Model Adapter & Qwen3.5:4B Baseline | DONE |" in text
    assert "| A005 | Associative Memory & Recall | PLANNED |" in text
    assert "| A011 | ASCA v0.x Qualification | PLANNED |" in text


def test_roadmap_migration_maps_old_future_numbers_without_rewriting_history():
    path = ROOT / "docs" / "development" / "roadmap-migrations" / "A004-qwen-insertion.md"
    text = _read(path)
    expected = (
        ("old A004", "new A005", "Associative Memory & Recall"),
        ("old A005", "new A006", "Working Set / Selective Activation"),
        ("old A006", "new A007", "Surprise, Uncertainty & Expansion"),
        ("old A007", "new A008", "Procedural Memory / Skill Chunking"),
        ("old A008", "new A009", "Integrated Cognitive Loop"),
        ("old A009", "new A010", "Dense/Non-selective Baseline Comparison"),
        ("old A010", "new A011", "ASCA v0.x Qualification"),
    )
    lower = text.lower()
    for old, new, name in expected:
        assert old.lower() in lower
        assert new.lower() in lower
        assert name in text
    assert "A001" in text and "A002" in text and "A003" in text
    assert "historical" in lower


def test_readme_states_model_agnostic_boundary_and_current_qwen_model_under_test():
    text = _read(ROOT / "README.md")
    lower = text.lower()
    assert "model-agnostic" in lower
    assert "qwen3.5:4b" in text
    assert "model-under-test" in lower
    assert "FlyWireLLM" in text
    assert "future adapter candidate" in lower


def test_a004_closure_report_records_exact_physical_and_ci_evidence():
    text = _read(REPORT)
    assert "c7b710a36f2cdc8f97177418ccf371d995817d94" in text
    assert "101 passed" in text
    assert "37891675731" in text
    assert "2a654d98e6fba55d452b7043684e9b57a947e393bbffa62485a7aac05ee4eefd" in text
    assert "pass_rate: 1.0" in text
    assert "qwen3.5:4b" in text
    assert "FlyWireLLM" in text
    assert "paused" in text.lower()
