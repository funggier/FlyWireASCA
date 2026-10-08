from __future__ import annotations

import importlib.util
from pathlib import Path
import tomllib


ROOT = Path(__file__).resolve().parents[1]


def _read_pyproject() -> dict:
    path = ROOT / "pyproject.toml"
    assert path.exists(), "pyproject.toml must exist"
    return tomllib.loads(path.read_text(encoding="utf-8"))


def test_package_is_importable_from_repository_contract():
    assert importlib.util.find_spec("flywire_asca") is not None


def test_project_metadata_declares_name_python_and_mit():
    payload = _read_pyproject()
    project = payload["project"]
    assert project["name"] == "FlyWireASCA"
    assert project["requires-python"].startswith(">=")
    major_minor = tuple(int(part) for part in project["requires-python"][2:].split(".")[:2])
    assert major_minor >= (3, 11)
    license_value = project["license"]
    if isinstance(license_value, dict):
        license_value = license_value.get("text")
    assert license_value == "MIT"


def test_license_contains_standard_mit_grant():
    path = ROOT / "LICENSE"
    assert path.exists(), "LICENSE must exist"
    text = path.read_text(encoding="utf-8")
    assert "Permission is hereby granted, free of charge" in text
    assert "Copyright (c) 2026 funggier" in text


def test_readme_states_architecture_workflow_and_independence_boundary():
    path = ROOT / "README.md"
    assert path.exists(), "README.md must exist"
    text = path.read_text(encoding="utf-8")
    lower = text.lower()
    assert "Associative Selective Cognition Architecture" in text
    assert "task-driven" in lower
    assert "evidence-driven" in lower
    assert "FlyWireLLM" in text
    assert "independent" in lower
