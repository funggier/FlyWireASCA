from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TASKS = ROOT / "docs" / "development" / "tasks"


def read(path: Path) -> str:
    assert path.exists(), f"{path.name} must exist"
    return path.read_text(encoding="utf-8")


def test_pre_a011_is_done_and_records_historical_a011_resume():
    task = read(TASKS / "PRE-A011-architecture-process-stabilization.md")
    assert "Status: DONE" in task
    assert "GitHub Issue: #11 (closed as completed)" in task
    assert "- [x] CURRENT returned to A011 / PLANNED / no issue." in task


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

REPORT = ROOT / "docs" / "development" / "reports" / "ASCA-20261010-PRE-A011-architecture-process-stabilization.md"


def test_pre_a011_closure_candidate_records_portable_physical_and_frozen_identity():
    report = read(REPORT)
    assert "PRE-A011 closure candidate" in report
    assert "552 passed" in report
    assert "architecture_contract_audit=PASS" in report
    assert "repository_qualification=PASS" in report
    assert "2f92b5092de346f62879ac2cbb9f96d6de5d6f919e12d0693345c8228b01ab2a" in report
    assert "69d20542cd1e7e5c25a0fb61b9060f622379206b519da3cec7624e00bb6e5d4c" in report
    assert "A006: `NOT_SUPPORTED`" in report
    assert "A007: `SUPPORTED`" in report
    assert "A008: `SUPPORTED`" in report
    assert "A009: `SUPPORTED`" in report
    assert "A010: `NOT_SUPPORTED`" in report
    assert "qwen3.5:4b" in report
    assert "2a654d98e6fba55d452b7043684e9b57a947e393bbffa62485a7aac05ee4eefd" in report
    assert "qwen3-embedding:0.6b" in report
    assert "ac6da0dfba84a81fdbfbaf330198c33cd77c4cdfc53e8bc50eb581914a15621d" in report
    assert "0.5037018224299838" in report
    assert "A004 physical qualification: GREEN" in report
    assert "A005 physical qualification: GREEN" in report
    assert "A006 physical qualification: GREEN" in report
    assert "A007 physical qualification: GREEN" in report
    assert "A009 physical qualification: GREEN" in report
    assert "A010 physical qualification: GREEN" in report
    assert "A011 GitHub issue: not created" in report


def test_pre_a011_closure_candidate_classifies_bounded_source_cleanup():
    report = read(REPORT)
    for path in (
        "src/flywire_asca/contracts/validation.py",
        "src/flywire_asca/model/ollama.py",
        "src/flywire_asca/embedding/ollama.py",
    ):
        assert path in report
    assert "44 passed" in report
    assert "shared http transport: not refactored" in report.lower()
    assert "benchmark modules: not split" in report.lower()
    assert "retrieval scheduling: not changed" in report.lower()
    assert "behavior-preserving" in report.lower()


def test_pre_a011_task_records_completed_historical_closure_gates():
    task = read(TASKS / "PRE-A011-architecture-process-stabilization.md")
    for line in (
        "- [x] Canonical architecture/qualification documentation published.",
        "- [x] Historical lifecycle tests decoupled from mutable CURRENT/ROADMAP state.",
        "- [x] Repository lifecycle qualifier hardened.",
        "- [x] Package dependency direction/no-cycle audit enforced.",
        "- [x] CI/qualification matrix aligned.",
        "- [x] Justified maintainability cleanup completed.",
        "- [x] Full portable and physical verification GREEN.",
        "- [x] Whole-change review GREEN.",
        "- [x] Reviewed main integration and exact main CI GREEN.",
        "- [x] Issue #11 closed completed.",
        "- [x] CURRENT returned to A011 / PLANNED / no issue.",
    ):
        assert line in task
    assert "de7b9ab7227afc6e914ca0435b780d30b41eeea3" in task
    assert "38023542634" in task

def test_pre_a011_records_whole_change_review_before_main_integration():
    task = read(TASKS / "PRE-A011-architecture-process-stabilization.md")
    report = read(REPORT)
    for text in (task, report):
        assert "Whole-change review: GREEN" in text
        assert "author self-review" in text.lower()
        assert "independent reviewer" in text.lower()
        assert "Critical findings: 0" in text
        assert "Important findings: 3" in text
        assert "Minor findings: 1" in text
        assert "561 passed" in text
        assert "38022892597" in text
        assert "38022744129" in text
    assert "- [x] Whole-change review GREEN." in task
    assert "- [x] Reviewed main integration and exact main CI GREEN." in task

def test_pre_a011_report_records_reviewed_main_and_issue_closure():
    report = read(REPORT)
    assert "Reviewed/integration SHA" in report
    assert "de7b9ab7227afc6e914ca0435b780d30b41eeea3" in report
    assert "38023542634" in report
    assert "Issue #11: closed as completed" in report
    assert "CURRENT = A011 / PLANNED / no issue" in report
    assert "A011 GitHub issue: not created" in report
