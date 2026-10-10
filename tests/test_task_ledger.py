from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TASKS = ROOT / "docs" / "development" / "tasks"


def _read(name: str) -> str:
    path = TASKS / name
    assert path.exists(), f"{name} must exist"
    return path.read_text(encoding="utf-8")


def test_current_points_to_exactly_one_planned_task_a010():
    text = _read("CURRENT.md")
    assert "Current task: A010" in text
    assert "Status: ACTIVE" in text
    assert "GitHub Issue: #10" in text
    assert text.count("Current task:") == 1


def test_a003_contains_recovery_and_evidence_sections():
    text = _read("A003-familiarity-system.md")
    assert "Status: DONE" in text
    for heading in (
        "## Goal",
        "## Scope",
        "## Acceptance Criteria",
        "## Evidence",
        "## Current Action",
        "## Next Action",
    ):
        assert heading in text


def test_a002_contains_recovery_and_evidence_sections():
    text = _read("A002-asca-architecture-contract.md")
    assert "Status: DONE" in text
    for heading in (
        "## Goal",
        "## Scope",
        "## Acceptance Criteria",
        "## Evidence",
        "## Current Action",
        "## Next Action",
    ):
        assert heading in text


def test_a001_contains_recovery_and_evidence_sections():
    text = _read("A001-repository-research-foundation.md")
    assert "Status: DONE" in text
    for heading in (
        "## Goal",
        "## Scope",
        "## Acceptance Criteria",
        "## Evidence",
        "## Current Action",
        "## Next Action",
    ):
        assert heading in text


def test_roadmap_lists_a001_through_a011_exactly_once():
    text = _read("ROADMAP.md")
    for number in range(1, 12):
        task_id = f"A{number:03d}"
        assert text.count(task_id) == 1, task_id


def test_task_readme_documents_states_and_authoritative_source_rule():
    text = _read("README.md")
    assert "PLANNED / ACTIVE / BLOCKED / DONE" in text
    lower = text.lower()
    assert "git/github/runtime" in lower
    assert "stale" in lower


def test_a001_closure_report_records_exact_qualification():
    report = ROOT / "docs" / "development" / "reports" / "ASCA-20261008-A001-repository-foundation.md"
    assert report.exists(), "A001 closure report must exist"
    text = report.read_text(encoding="utf-8")
    assert "08868b099da4ae2bd31154201dd3ac9d0568fe5d" in text
    assert "14 passed" in text
    assert "37759237750" in text
    assert "PUBLIC" in text
    assert "FlyWireLLM" in text


def test_a001_closure_report_has_no_trailing_whitespace():
    report = ROOT / "docs" / "development" / "reports" / "ASCA-20261008-A001-repository-foundation.md"
    lines = report.read_text(encoding="utf-8").splitlines()
    assert [index for index, line in enumerate(lines, 1) if line != line.rstrip()] == []

def test_a002_closure_report_records_exact_qualification():
    report = ROOT / "docs" / "development" / "reports" / "ASCA-20261008-A002-architecture-contract.md"
    assert report.exists(), "A002 closure report must exist"
    text = report.read_text(encoding="utf-8")
    assert "c70e11f1af9cf652b8526f300a9c1d7317e5b6de" in text
    assert "41 passed" in text
    assert "37793506259" in text
    assert "architecture_contract_audit=PASS" in text
    assert "FlyWireLLM" in text

def test_a003_closure_report_records_exact_qualification():
    report = ROOT / "docs" / "development" / "reports" / "ASCA-20261008-A003-familiarity-system.md"
    assert report.exists(), "A003 closure report must exist"
    text = report.read_text(encoding="utf-8")
    assert "6c9534cb743123c60184e9e00244f836c3e901e1" in text
    assert "66 passed" in text
    assert "37803237340" in text
    assert "classification_accuracy: 1.0" in text
    assert "exact_logical_probes: 9" in text
    assert "exhaustive_logical_probes: 2367" in text
    assert "same-name ambiguity" in text.lower()
    assert "FlyWireLLM" in text

def test_a004_closure_report_records_qwen_physical_qualification():
    report = ROOT / "docs" / "development" / "reports" / "ASCA-20261009-A004-qwen-adapter-baseline.md"
    assert report.exists(), "A004 closure report must exist"
    text = report.read_text(encoding="utf-8")
    assert "c7b710a36f2cdc8f97177418ccf371d995817d94" in text
    assert "101 passed" in text
    assert "37891675731" in text
    assert "pass_rate: 1.0" in text
    assert "FlyWireLLM" in text

def test_a005_closure_report_records_vector_retrieval_decision():
    report = ROOT / "docs" / "development" / "reports" / "ASCA-20261009-A005-vector-memory-retrieval.md"
    assert report.exists(), "A005 closure report must exist"
    text = report.read_text(encoding="utf-8")
    assert "78099fe3e36e8e1292085425f1553a05b95a820e" in text
    assert "37906978728" in text
    assert "0.5037018224299838" in text
    assert "VECTOR_SUFFICIENT" in text

def test_a006_closure_report_records_selective_activation_result():
    report = ROOT / "docs" / "development" / "reports" / "ASCA-20261009-A006-working-set-selective-activation.md"
    assert report.exists(), "A006 closure report must exist"
    text = report.read_text(encoding="utf-8")
    assert "224864cc9d70228d4feb80a9fcbc07f2776808d3" in text
    assert "37927165972" in text
    assert "Final A006 hypothesis outcome: `NOT_SUPPORTED`" in text

def test_a007_closure_report_records_structural_expansion_result():
    report = ROOT / "docs" / "development" / "reports" / "ASCA-20261009-A007-surprise-uncertainty-expansion.md"
    assert report.exists(), "A007 closure report must exist"
    text = report.read_text(encoding="utf-8")
    assert "d76084178a3fca84208794efca7a46330785eb6e" in text
    assert "37940884611" in text
    assert "Final A007 hypothesis outcome: `SUPPORTED`" in text