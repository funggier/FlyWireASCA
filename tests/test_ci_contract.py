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

def test_ci_runs_a009_deterministic_integrated_loop_qualification():
    text = WORKFLOW.read_text(encoding="utf-8")
    lower = text.lower()
    assert "python scripts/qualify_integrated_loop_a009.py" in text
    assert "python scripts/qualify_integrated_loop_a009_physical.py" not in text
    assert "qualify_vector_memory_a005.py" not in lower
    assert "qualify_selective_activation_a006.py" not in lower
    assert "qualify_uncertainty_expansion_a007.py" not in lower
    assert "ollama pull" not in lower
    assert "ollama run" not in lower
    assert "127.0.0.1:11434" not in lower
    assert "localhost" not in lower

def test_ci_runs_a010_portable_baseline_qualification_only():
    text = WORKFLOW.read_text(encoding="utf-8")
    lower = text.lower()
    assert "python scripts/qualify_baseline_comparison_a010.py" in text
    assert "qualify_baseline_comparison_a010_physical.py" not in text
    assert "ollama pull" not in lower
    assert "ollama run" not in lower
    assert "127.0.0.1:11434" not in lower
    assert "localhost" not in lower


def test_ci_preserves_historical_a011_without_requalifying_post_a011_head():
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "python scripts/verify_a011_frozen_profile_preservation.py" in text
    assert "python scripts/qualify_asca_v0x_a011.py" not in text
    assert "a011-portable-" not in text


def test_ci_runs_a012_portable_qualification_and_uploads_evidence():
    text = WORKFLOW.read_text(encoding="utf-8")
    lower = text.lower()
    assert "python scripts/qualify_relational_reasoning_a012.py" in text
    assert "qualify_relational_reasoning_a012_physical.py" not in text
    assert "Upload A012 portable qualification evidence" in text
    assert "actions/upload-artifact@v4" in text
    assert "if-no-files-found: error" in text
    assert "ollama pull" not in lower
    assert "ollama run" not in lower
    assert "127.0.0.1:11434" not in lower
    assert "localhost" not in lower

MATRIX = ROOT / "docs" / "development" / "QUALIFICATION-MATRIX.md"


def _commands_under_heading(text: str, heading: str) -> tuple[str, ...]:
    section = text.split(heading, 1)[1]
    block = section.split("```text", 1)[1].split("```", 1)[0]
    return tuple(line.strip() for line in block.splitlines() if line.strip())


def test_ci_explicitly_points_to_canonical_qualification_matrix():
    workflow = WORKFLOW.read_text(encoding="utf-8")
    assert "docs/development/QUALIFICATION-MATRIX.md" in workflow


def test_qualification_matrix_and_ci_command_topology_match():
    workflow = WORKFLOW.read_text(encoding="utf-8")
    matrix = MATRIX.read_text(encoding="utf-8")
    portable = _commands_under_heading(matrix, "## 3. Portable GitHub CI commands")
    physical = _commands_under_heading(matrix, "## 4. Local-only physical commands")
    for command in portable:
        assert command in workflow, command
    for command in physical:
        script = command.split("python ", 1)[1].split(" ", 1)[0]
        assert script not in workflow, script
    assert "local-only" in matrix.lower()
    assert "A006: `NOT_SUPPORTED`" in matrix
    assert "A007: `SUPPORTED`" in matrix
    assert "A008: `SUPPORTED`" in matrix
    assert "A009: `SUPPORTED`" in matrix
    assert "A010: `NOT_SUPPORTED`" in matrix
    assert "A012" in matrix
    assert "EXPLICIT_RELATION_TRAVERSAL_JUSTIFIED" in matrix
    assert "A valid `NOT_SUPPORTED` result" in matrix
