from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "qualify_repository.py"


def _load_qualifier():
    assert SCRIPT.exists(), "repository qualifier must exist"
    spec = importlib.util.spec_from_file_location("flywire_asca_qualifier", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.qualify_repository


def _task_text(task_id: str, status: str, issue: str, *, checked: bool = True) -> str:
    box = "x" if checked else " "
    return f"""# {task_id} — Fixture task

Status: {status}
GitHub Issue: {issue}

## Goal

Fixture.

## Acceptance Criteria

- [{box}] fixture acceptance.

## Current Action

Fixture current action.

## Next Action

Fixture next action.
"""


def _fixture_root(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    tasks = root / "docs" / "development" / "tasks"
    tasks.mkdir(parents=True)
    (root / "src" / "flywire_asca").mkdir(parents=True)
    (root / "LICENSE").write_text(
        "MIT License\nPermission is hereby granted, free of charge\n",
        encoding="utf-8",
    )
    (root / "README.md").write_text(
        "FlyWireASCA is independent from FlyWireLLM.\n",
        encoding="utf-8",
    )
    (tasks / "ROADMAP.md").write_text(
        "# Roadmap\n\n"
        "| Task | Milestone | Status |\n"
        "| --- | --- | --- |\n"
        "| A001 | One | DONE |\n"
        "| A002 | Two | PLANNED |\n",
        encoding="utf-8",
    )
    (tasks / "CURRENT.md").write_text(
        "Current task: A002\nStatus: PLANNED\nGitHub Issue: not created\n",
        encoding="utf-8",
    )
    (tasks / "A001-one.md").write_text(
        _task_text("A001", "DONE", "#1"),
        encoding="utf-8",
    )
    (tasks / "A002-two.md").write_text(
        _task_text("A002", "PLANNED", "not created"),
        encoding="utf-8",
    )
    (root / "src" / "flywire_asca" / "__init__.py").write_text(
        "__version__ = '0.1.0.dev0'\n",
        encoding="utf-8",
    )
    return root


def test_valid_repository_has_no_qualification_errors():
    qualify_repository = _load_qualifier()
    assert qualify_repository(ROOT) == []


def test_valid_fixture_has_no_qualification_errors(tmp_path: Path):
    qualify_repository = _load_qualifier()
    assert qualify_repository(_fixture_root(tmp_path)) == []


def test_missing_license_is_reported(tmp_path: Path):
    qualify_repository = _load_qualifier()
    root = _fixture_root(tmp_path)
    (root / "LICENSE").unlink()
    assert any("LICENSE" in error for error in qualify_repository(root))


def test_missing_current_task_pointer_is_reported(tmp_path: Path):
    qualify_repository = _load_qualifier()
    root = _fixture_root(tmp_path)
    (root / "docs" / "development" / "tasks" / "CURRENT.md").unlink()
    assert any("CURRENT.md" in error for error in qualify_repository(root))


def test_readme_missing_flywirellm_independence_boundary_is_reported(tmp_path: Path):
    qualify_repository = _load_qualifier()
    root = _fixture_root(tmp_path)
    (root / "README.md").write_text("FlyWireASCA research project\n", encoding="utf-8")
    assert any("FlyWireLLM" in error for error in qualify_repository(root))


def test_machine_local_absolute_path_in_package_source_is_reported(tmp_path: Path):
    qualify_repository = _load_qualifier()
    root = _fixture_root(tmp_path)
    (root / "src" / "flywire_asca" / "bad.py").write_text(
        'CACHE = r"T:\\Users\\someone\\private"\n',
        encoding="utf-8",
    )
    errors = qualify_repository(root)
    assert any("absolute machine-local path" in error for error in errors)


def test_duplicate_roadmap_task_id_is_reported(tmp_path: Path):
    qualify_repository = _load_qualifier()
    root = _fixture_root(tmp_path)
    roadmap = root / "docs" / "development" / "tasks" / "ROADMAP.md"
    roadmap.write_text(
        roadmap.read_text(encoding="utf-8") + "| A001 | Duplicate | DONE |\n",
        encoding="utf-8",
    )
    assert any("duplicate ROADMAP task ID A001" in e for e in qualify_repository(root))


def test_non_monotonic_roadmap_task_ids_are_reported(tmp_path: Path):
    qualify_repository = _load_qualifier()
    root = _fixture_root(tmp_path)
    roadmap = root / "docs" / "development" / "tasks" / "ROADMAP.md"
    text = roadmap.read_text(encoding="utf-8")
    text = text.replace(
        "| A001 | One | DONE |\n| A002 | Two | PLANNED |",
        "| A002 | Two | PLANNED |\n| A001 | One | DONE |",
    )
    roadmap.write_text(text, encoding="utf-8")
    assert any("monotonic" in e for e in qualify_repository(root))


def test_invalid_roadmap_status_is_reported(tmp_path: Path):
    qualify_repository = _load_qualifier()
    root = _fixture_root(tmp_path)
    roadmap = root / "docs" / "development" / "tasks" / "ROADMAP.md"
    roadmap.write_text(
        roadmap.read_text(encoding="utf-8").replace("A002 | Two | PLANNED", "A002 | Two | STALE"),
        encoding="utf-8",
    )
    assert any("invalid ROADMAP status" in e for e in qualify_repository(root))


def test_a_numbered_current_status_must_match_roadmap(tmp_path: Path):
    qualify_repository = _load_qualifier()
    root = _fixture_root(tmp_path)
    current = root / "docs" / "development" / "tasks" / "CURRENT.md"
    current.write_text(
        "Current task: A002\nStatus: ACTIVE\nGitHub Issue: #2\n",
        encoding="utf-8",
    )
    assert any("CURRENT status ACTIVE does not match ROADMAP status PLANNED" in e for e in qualify_repository(root))


def test_pre_current_is_allowed_with_matching_maintenance_task(tmp_path: Path):
    qualify_repository = _load_qualifier()
    root = _fixture_root(tmp_path)
    tasks = root / "docs" / "development" / "tasks"
    (tasks / "CURRENT.md").write_text(
        "Current task: PRE-A011\nStatus: ACTIVE\nGitHub Issue: #11\n",
        encoding="utf-8",
    )
    (tasks / "PRE-A011-architecture-process-stabilization.md").write_text(
        _task_text("PRE-A011", "ACTIVE", "#11"),
        encoding="utf-8",
    )
    assert qualify_repository(root) == []


def test_pre_current_is_rejected_without_matching_maintenance_task(tmp_path: Path):
    qualify_repository = _load_qualifier()
    root = _fixture_root(tmp_path)
    current = root / "docs" / "development" / "tasks" / "CURRENT.md"
    current.write_text(
        "Current task: PRE-A011\nStatus: ACTIVE\nGitHub Issue: #11\n",
        encoding="utf-8",
    )
    assert any("maintenance task document" in e for e in qualify_repository(root))


def test_planned_current_rejects_guessed_numeric_issue(tmp_path: Path):
    qualify_repository = _load_qualifier()
    root = _fixture_root(tmp_path)
    current = root / "docs" / "development" / "tasks" / "CURRENT.md"
    current.write_text(
        "Current task: A002\nStatus: PLANNED\nGitHub Issue: #99\n",
        encoding="utf-8",
    )
    assert any("PLANNED current task must not record a numeric GitHub issue" in e for e in qualify_repository(root))


def test_active_current_requires_numeric_issue_in_own_task_file(tmp_path: Path):
    qualify_repository = _load_qualifier()
    root = _fixture_root(tmp_path)
    tasks = root / "docs" / "development" / "tasks"
    (tasks / "ROADMAP.md").write_text(
        (tasks / "ROADMAP.md").read_text(encoding="utf-8").replace("A002 | Two | PLANNED", "A002 | Two | ACTIVE"),
        encoding="utf-8",
    )
    (tasks / "CURRENT.md").write_text(
        "Current task: A002\nStatus: ACTIVE\nGitHub Issue: #2\n",
        encoding="utf-8",
    )
    (tasks / "A002-two.md").write_text(
        _task_text("A002", "ACTIVE", "not created"),
        encoding="utf-8",
    )
    assert any("ACTIVE task file must record a numeric GitHub issue" in e for e in qualify_repository(root))


def test_done_task_rejects_unchecked_acceptance(tmp_path: Path):
    qualify_repository = _load_qualifier()
    root = _fixture_root(tmp_path)
    task = root / "docs" / "development" / "tasks" / "A001-one.md"
    task.write_text(_task_text("A001", "DONE", "#1", checked=False), encoding="utf-8")
    assert any("DONE task A001 contains unchecked acceptance" in e for e in qualify_repository(root))


def test_done_task_filename_and_heading_id_must_match(tmp_path: Path):
    qualify_repository = _load_qualifier()
    root = _fixture_root(tmp_path)
    task = root / "docs" / "development" / "tasks" / "A001-one.md"
    task.write_text(_task_text("A999", "DONE", "#1"), encoding="utf-8")
    assert any("filename task ID A001 does not match heading task ID A999" in e for e in qualify_repository(root))


def test_broken_repository_relative_markdown_link_is_reported(tmp_path: Path):
    qualify_repository = _load_qualifier()
    root = _fixture_root(tmp_path)
    docs = root / "docs"
    (docs / "broken.md").write_text(
        "[missing](does-not-exist.md)\n[external](https://example.com)\n",
        encoding="utf-8",
    )
    assert any("broken relative Markdown link" in e for e in qualify_repository(root))

def test_duplicate_current_fields_are_rejected(tmp_path: Path):
    qualify_repository = _load_qualifier()
    root = _fixture_root(tmp_path)
    current = root / "docs" / "development" / "tasks" / "CURRENT.md"
    current.write_text(
        "Current task: A002\n"
        "Current task: A001\n"
        "Status: PLANNED\n"
        "GitHub Issue: not created\n",
        encoding="utf-8",
    )
    assert any("duplicate CURRENT.md field Current task" in e for e in qualify_repository(root))


def test_active_current_issue_must_match_task_document_issue(tmp_path: Path):
    qualify_repository = _load_qualifier()
    root = _fixture_root(tmp_path)
    tasks = root / "docs" / "development" / "tasks"
    (tasks / "ROADMAP.md").write_text(
        (tasks / "ROADMAP.md")
        .read_text(encoding="utf-8")
        .replace("A002 | Two | PLANNED", "A002 | Two | ACTIVE"),
        encoding="utf-8",
    )
    (tasks / "CURRENT.md").write_text(
        "Current task: A002\nStatus: ACTIVE\nGitHub Issue: #99\n",
        encoding="utf-8",
    )
    (tasks / "A002-two.md").write_text(
        _task_text("A002", "ACTIVE", "#2"),
        encoding="utf-8",
    )
    assert any("CURRENT GitHub Issue #99 does not match task GitHub Issue #2" in e for e in qualify_repository(root))


def test_pre_current_issue_must_match_maintenance_task_issue(tmp_path: Path):
    qualify_repository = _load_qualifier()
    root = _fixture_root(tmp_path)
    tasks = root / "docs" / "development" / "tasks"
    (tasks / "CURRENT.md").write_text(
        "Current task: PRE-A011\nStatus: ACTIVE\nGitHub Issue: #99\n",
        encoding="utf-8",
    )
    (tasks / "PRE-A011-architecture-process-stabilization.md").write_text(
        _task_text("PRE-A011", "ACTIVE", "#11"),
        encoding="utf-8",
    )
    assert any("CURRENT GitHub Issue #99 does not match task GitHub Issue #11" in e for e in qualify_repository(root))


def test_malformed_a_numbered_roadmap_row_is_rejected(tmp_path: Path):
    qualify_repository = _load_qualifier()
    root = _fixture_root(tmp_path)
    roadmap = root / "docs" / "development" / "tasks" / "ROADMAP.md"
    roadmap.write_text(
        roadmap.read_text(encoding="utf-8") + "| A003 | malformed row |\n",
        encoding="utf-8",
    )
    assert any("malformed ROADMAP task row A003" in e for e in qualify_repository(root))
