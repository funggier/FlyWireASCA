from __future__ import annotations

import importlib.util
from pathlib import Path
import shutil


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "qualify_repository.py"


def _load_qualifier():
    assert SCRIPT.exists(), "repository qualifier must exist"
    spec = importlib.util.spec_from_file_location("flywire_asca_qualifier", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.qualify_repository


def _fixture_root(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    (root / "docs" / "development" / "tasks").mkdir(parents=True)
    (root / "src" / "flywire_asca").mkdir(parents=True)
    (root / "LICENSE").write_text(
        "MIT License\nPermission is hereby granted, free of charge\n",
        encoding="utf-8",
    )
    (root / "README.md").write_text(
        "FlyWireASCA is independent from FlyWireLLM.\n",
        encoding="utf-8",
    )
    (root / "docs" / "development" / "tasks" / "CURRENT.md").write_text(
        "Current task: A001\nStatus: ACTIVE\n",
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
