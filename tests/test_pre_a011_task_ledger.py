from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TASKS = ROOT / "docs" / "development" / "tasks"


def read(path: Path) -> str:
    assert path.exists(), f"{path.name} must exist"
    return path.read_text(encoding="utf-8")


def test_pre_a011_is_active_without_mutating_research_roadmap():
    current = read(TASKS / "CURRENT.md")
    roadmap = read(TASKS / "ROADMAP.md")
    task = read(TASKS / "PRE-A011-architecture-process-stabilization.md")
    assert "Current task: PRE-A011" in current
    assert "Status: ACTIVE" in current
    assert "GitHub Issue: #11" in current
    assert "| A011 | ASCA v0.x Qualification | PLANNED |" in roadmap
    assert "PRE-A011" not in roadmap
    assert "Status: ACTIVE" in task
    assert "GitHub Issue: #11" in task


def test_pre_a011_task_records_approved_spec_plan_and_boundaries():
    task = read(TASKS / "PRE-A011-architecture-process-stabilization.md")
    assert "2026-10-10-pre-a011-architecture-process-stabilization-design.md" in task
    assert "2026-10-10-pre-a011-architecture-process-stabilization.md" in task
    assert "c8211fff43523b80c66fcfecff9088970d6c9981" in task
    assert "38020908291" in task
    assert "531 passed" in task
    assert "A006" in task and "NOT_SUPPORTED" in task
    assert "A007" in task and "SUPPORTED" in task
    assert "A008" in task and "SUPPORTED" in task
    assert "A009" in task and "SUPPORTED" in task
    assert "A010" in task and "NOT_SUPPORTED" in task
    assert "A011" in task and "PLANNED" in task
    assert "FlyWireLLM" in task and "untouched" in task.lower()