from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "ci.yml"


def test_ci_fetches_parent_commit_for_diff_check():
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "fetch-depth: 2" in text
    assert "git diff --check HEAD^ HEAD" in text


def test_ci_runs_architecture_contract_audit_explicitly():
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "python scripts/audit_architecture_contract.py" in text

def test_ci_runs_a003_familiarity_benchmark_qualification():
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "python scripts/run_familiarity_benchmark_a003.py --qualify" in text

def test_ci_keeps_a004_qwen_physical_qualification_local_only():
    text = WORKFLOW.read_text(encoding="utf-8").lower()
    assert "ollama pull" not in text
    assert "ollama run" not in text
    assert "qualify_qwen_a004.py" not in text
    assert "127.0.0.1:11434" not in text
    assert "localhost" not in text
    assert "python -m pytest -q" in text
    assert "python scripts/run_familiarity_benchmark_a003.py --qualify" in text

def test_ci_keeps_a005_embedding_physical_qualification_local_only():
    text = WORKFLOW.read_text(encoding="utf-8").lower()
    assert "ollama pull" not in text
    assert "ollama run" not in text
    assert "/api/embed" not in text
    assert "qualify_vector_memory_a005.py" not in text
    assert "127.0.0.1:11434" not in text
    assert "localhost" not in text
    assert "python -m pytest -q" in text
    assert "python scripts/run_familiarity_benchmark_a003.py --qualify" in text

def test_ci_keeps_a006_selective_activation_physical_qualification_local_only():
    text = WORKFLOW.read_text(encoding="utf-8").lower()
    assert "qualify_selective_activation_a006.py" not in text
    assert "ollama pull" not in text
    assert "ollama run" not in text
    assert "127.0.0.1:11434" not in text
    assert "localhost" not in text
    assert "python -m pytest -q" in text
    assert "python scripts/run_familiarity_benchmark_a003.py --qualify" in text

def test_ci_keeps_a007_uncertainty_expansion_physical_qualification_local_only():
    text = WORKFLOW.read_text(encoding="utf-8").lower()
    assert "qualify_uncertainty_expansion_a007.py" not in text
    assert "ollama pull" not in text
    assert "ollama run" not in text
    assert "127.0.0.1:11434" not in text
    assert "localhost" not in text
    assert "python -m pytest -q" in text
    assert "python scripts/run_familiarity_benchmark_a003.py --qualify" in text

def test_ci_runs_a008_deterministic_procedural_qualification():
    text = WORKFLOW.read_text(encoding="utf-8")
    lower = text.lower()
    assert "python scripts/qualify_procedural_memory_a008.py" in text
    assert "python -m pytest -q" in text
    assert "python scripts/audit_architecture_contract.py" in text
    assert "python scripts/qualify_repository.py" in text
    assert "python scripts/run_familiarity_benchmark_a003.py --qualify" in text
    assert "qualify_qwen_a004.py" not in lower
    assert "qualify_vector_memory_a005.py" not in lower
    assert "qualify_selective_activation_a006.py" not in lower
    assert "qualify_uncertainty_expansion_a007.py" not in lower
    assert "ollama pull" not in lower
    assert "ollama run" not in lower
    assert "127.0.0.1:11434" not in lower
    assert "localhost" not in lower
