from __future__ import annotations

import importlib.util
from pathlib import Path
import shutil


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "audit_architecture_contract.py"
DOC = ROOT / "docs" / "architecture" / "ASCA-CONTRACT-v0.1.md"


def _load_audit():
    assert SCRIPT.exists(), "architecture audit script must exist"
    spec = importlib.util.spec_from_file_location("asca_contract_audit", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.audit_architecture_contract


def _copy_fixture(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    root.mkdir(parents=True)
    shutil.copy2(ROOT / "pyproject.toml", root / "pyproject.toml")
    shutil.copytree(
        ROOT / "src" / "flywire_asca",
        root / "src" / "flywire_asca",
    )
    (root / "docs" / "architecture").mkdir(parents=True)
    if DOC.exists():
        shutil.copy2(DOC, root / "docs" / "architecture" / DOC.name)
    return root


def test_contract_version_and_document_are_frozen_at_v01():
    import flywire_asca.contracts as contracts

    assert getattr(contracts, "CONTRACT_VERSION", None) == "0.1"
    assert DOC.exists()
    text = DOC.read_text(encoding="utf-8")
    assert "ASCA Contract v0.1" in text
    assert "FlyWireLLM" in text
    assert "activation" in text.lower()
    assert "proposition confidence" in text.lower()


def test_live_repository_passes_architecture_audit():
    audit = _load_audit()
    assert audit(ROOT) == []


def test_audit_rejects_mandatory_runtime_dependency(tmp_path: Path):
    audit = _load_audit()
    root = _copy_fixture(tmp_path)
    pyproject = root / "pyproject.toml"
    text = pyproject.read_text(encoding="utf-8")
    pyproject.write_text(
        text.replace("dependencies = []", 'dependencies = ["networkx>=3"]'),
        encoding="utf-8",
    )
    assert any("runtime dependencies" in error for error in audit(root))


def test_audit_rejects_flywirellm_source_import(tmp_path: Path):
    audit = _load_audit()
    root = _copy_fixture(tmp_path)
    injected = root / "src" / "flywire_asca" / "bad_adapter.py"
    injected.write_text("from flywire_llm import BlankCausalLM\n", encoding="utf-8")
    assert any("FlyWireLLM import" in error for error in audit(root))


def test_audit_rejects_missing_contract_document(tmp_path: Path):
    audit = _load_audit()
    root = _copy_fixture(tmp_path)
    (root / "docs" / "architecture" / "ASCA-CONTRACT-v0.1.md").unlink(missing_ok=True)
    assert any("contract document" in error for error in audit(root))

def test_contract_document_has_no_trailing_whitespace():
    lines = DOC.read_text(encoding="utf-8").splitlines()
    assert [index for index, line in enumerate(lines, 1) if line != line.rstrip()] == []

def test_audit_rejects_undeclared_reverse_package_dependency(tmp_path: Path):
    audit = _load_audit()
    root = _copy_fixture(tmp_path)
    injected = root / "src" / "flywire_asca" / "vector_memory" / "bad.py"
    injected.write_text(
        "from flywire_asca.integrated_loop import run_cognitive_loop\n",
        encoding="utf-8",
    )
    errors = audit(root)
    assert any("undeclared package dependency vector_memory -> integrated_loop" in e for e in errors)


def test_audit_rejects_cross_package_cycle_explicitly(tmp_path: Path):
    audit = _load_audit()
    root = _copy_fixture(tmp_path)
    injected = root / "src" / "flywire_asca" / "contracts" / "bad.py"
    injected.write_text(
        "from flywire_asca.model import OllamaModelAdapter\n",
        encoding="utf-8",
    )
    errors = audit(root)
    assert any("package dependency cycle" in e and "contracts" in e and "model" in e for e in errors)
