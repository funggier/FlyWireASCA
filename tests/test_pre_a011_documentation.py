from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / "docs" / "architecture" / "ASCA-PRE-A011-SNAPSHOT.md"
MATRIX = ROOT / "docs" / "development" / "QUALIFICATION-MATRIX.md"
INITIAL = ROOT / "docs" / "superpowers" / "specs" / "2026-10-08-asca-architecture-design.md"
TASK_README = ROOT / "docs" / "development" / "tasks" / "README.md"
A009_TASK = ROOT / "docs" / "development" / "tasks" / "A009-integrated-cognitive-loop.md"
A010_REPORT = ROOT / "docs" / "development" / "reports" / "ASCA-20261010-A010-dense-nonselective-baseline-comparison.md"


def read(path: Path) -> str:
    assert path.exists(), f"{path.relative_to(ROOT)} must exist"
    return path.read_text(encoding="utf-8")


def test_pre_a011_snapshot_records_current_implemented_architecture_and_outcomes():
    text = read(SNAPSHOT)
    for milestone in ("A002", "A003", "A004", "A005", "A006", "A007", "A008", "A009", "A010"):
        assert milestone in text
    assert "A006: `NOT_SUPPORTED`" in text
    assert "A007: `SUPPORTED`" in text
    assert "A008: `SUPPORTED`" in text
    assert "A009: `SUPPORTED`" in text
    assert "A010: `NOT_SUPPORTED`" in text
    assert "Implemented" in text
    assert "Deferred" in text
    assert "A004-qwen-insertion.md" in text
    assert "A011" in text and "PLANNED" in text
    assert "7" in text and "8" in text
    assert "66" in text and "480" in text
    assert "28" in text and "27" in text
    assert "1984" in text and "1440" in text


def test_initial_architecture_design_is_archived_without_rewriting_historical_roadmap():
    text = read(INITIAL)
    assert "Historical initial design" in text
    assert "A004-qwen-insertion.md" in text
    assert "ASCA-PRE-A011-SNAPSHOT.md" in text
    assert "### A004 - Associative Memory and Recall" in text
    assert "### A010 - First ASCA Qualification" in text


def test_qualification_matrix_declares_portable_and_physical_topology():
    text = read(MATRIX)
    for milestone in ("A003", "A004", "A005", "A006", "A007", "A008", "A009", "A010"):
        assert milestone in text
    for command in (
        "python -m pytest -q",
        "python scripts/audit_architecture_contract.py",
        "python scripts/qualify_repository.py",
        "python scripts/run_familiarity_benchmark_a003.py --qualify",
        "python scripts/qualify_procedural_memory_a008.py",
        "python scripts/qualify_integrated_loop_a009.py",
        "python scripts/qualify_baseline_comparison_a010.py",
        "python scripts/qualify_qwen_a004.py",
        "python scripts/qualify_vector_memory_a005.py",
        "python scripts/qualify_selective_activation_a006.py",
        "python scripts/qualify_uncertainty_expansion_a007.py",
        "python scripts/qualify_integrated_loop_a009_physical.py --portable-primary-outcome SUPPORTED",
        "python scripts/qualify_baseline_comparison_a010_physical.py --portable-primary-outcome NOT_SUPPORTED",
    ):
        assert command in text
    assert "local-only" in text.lower()
    assert "valid `NOT_SUPPORTED`" in text
    assert "qwen3.5:4b" in text
    assert "qwen3-embedding:0.6b" in text


def test_task_workflow_defines_current_state_and_evidence_roles():
    text = read(TASK_README)
    assert "current task state" in text.lower()
    assert "PLANNED" in text and "ACTIVE" in text and "BLOCKED" in text
    for term in (
        "Activation base",
        "Qualified behavior SHA",
        "Reviewed behavior SHA",
        "Integration SHA",
        "Repository closure state",
        "Closure metadata commit",
    ):
        assert term in text


def test_a009_done_ledger_no_longer_says_final_evidence_or_issue_closure_remain_pending():
    text = read(A009_TASK)
    assert "Status: DONE" in text
    assert "final evidence commit exact-main CI and Issue #9 closure remain pending" not in text
    assert "GitHub Issue: #9 (closed as completed)" in text


def test_a010_physical_evidence_table_has_no_bullet_rows_inside_table():
    text = read(A010_REPORT)
    assert "| Procedure attempts | 1 | 1 |\n| Cumulative selected count | 3 | 3 |" in text
    assert "- ASCA physical query/scored-vector | 1 / 3" in text
    assert "- Dense physical query/scored-vector | 3 / 9" in text
    section = text.split("Observed physical comparison:", 1)[1].split("The physical case", 1)[0]
    assert section.index("| Cumulative selected count | 3 | 3 |") < section.index("- ASCA physical query/scored-vector | 1 / 3")

def test_task_workflow_requires_staged_whitespace_check_before_commit():
    text = read(TASK_README)
    assert "git diff --cached --check" in text
