from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TASKS = ROOT / "docs" / "development" / "tasks"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")



def test_roadmap_marks_a010_done_and_a011_planned():
    text = read(TASKS / "ROADMAP.md")
    assert "| A009 | Integrated Cognitive Loop | DONE |" in text
    assert "| A010 | Dense/Non-selective Baseline Comparison | DONE |" in text
    assert "| A011 | ASCA v0.x Qualification | PLANNED |" in text


def test_a010_task_ledger_records_approved_design_plan_and_boundaries():
    text = read(TASKS / "A010-dense-nonselective-baseline-comparison.md")
    assert "Status: DONE" in text
    assert "GitHub Issue: #10 (closed as completed)" in text
    assert "research/a010-dense-nonselective-baseline-comparison" in text
    assert "2026-10-10-a010-dense-nonselective-baseline-comparison-design.md" in text
    assert "2026-10-10-a010-dense-nonselective-baseline-comparison.md" in text
    assert "A006" in text and "NOT_SUPPORTED" in text
    assert "A007" in text and "SUPPORTED" in text
    assert "A008" in text and "SUPPORTED" in text
    assert "A009" in text and "SUPPORTED" in text
    assert "select_exhaustive" in text
    assert "CHUNKED" in text
    assert "FlyWireLLM" in text and "untouched" in text.lower()


def test_readme_records_a010_done_and_a011_planned():
    text = read(ROOT / "README.md")
    assert "A009 Issue #9 remains open" not in text
    assert "A009" in text and "SUPPORTED" in text
    assert "A010" in text
    assert "Dense/Non-selective Baseline Comparison" in text
    assert "**DONE**" in text
    assert "A011" in text and "**PLANNED**" in text

REPORT = ROOT / "docs" / "development" / "reports" / "ASCA-20261010-A010-dense-nonselective-baseline-comparison.md"


def test_a010_report_records_frozen_portable_identity_and_negative_outcome():
    text = read(REPORT)
    assert "a010-deterministic-v1" in text
    assert "69d20542cd1e7e5c25a0fb61b9060f622379206b519da3cec7624e00bb6e5d4c" in text
    assert "Primary A010 hypothesis outcome: `NOT_SUPPORTED`" in text
    assert "ASCA query count | 28" in text
    assert "Dense query count | 27" in text
    assert "ASCA scored-vector count | 1984" in text
    assert "Dense scored-vector count | 1440" in text
    assert "ASCA cumulative selected count | 66" in text
    assert "Dense cumulative selected count | 480" in text
    assert "ASCA procedure success count | 7" in text
    assert "Dense procedure success count | 8" in text
    assert "Dense-only success count | 1" in text
    assert "ASCA-only success count | 0" in text


def test_a010_report_records_validity_boundedness_and_physical_secondary_evidence():
    text = read(REPORT)
    assert "designated parity reduction count | 7" in text
    assert "identity failure count | 0" in text
    assert "duplicate execution-ID failure count | 0" in text
    assert "post-completion extra-attempt failure count | 0" in text
    assert "ASCA deterministic repeat match | true" in text
    assert "Dense deterministic repeat match | true" in text
    assert "qwen3-embedding:0.6b" in text
    assert "ac6da0dfba84a81fdbfbaf330198c33cd77c4cdfc53e8bc50eb581914a15621d" in text
    assert "physical integration validity: `true`" in text.lower()
    assert "ASCA physical query/scored-vector | 1 / 3" in text
    assert "Dense physical query/scored-vector | 3 / 9" in text
    assert "secondary" in text.lower()
    assert "cannot change" in text.lower()


def test_a010_report_records_exact_task5_branch_ci_and_preserves_history():
    text = read(REPORT)
    assert "234bc090dc068447c1830fa79337745b7796f25f" in text
    assert "38014300995" in text
    assert "515 passed" in text
    assert "A006" in text and "NOT_SUPPORTED" in text
    assert "A007" in text and "SUPPORTED" in text
    assert "A008" in text and "SUPPORTED" in text
    assert "A009" in text and "SUPPORTED" in text
    assert "FlyWireLLM" in text and "untouched" in text.lower()


def test_a010_has_exactly_one_primary_outcome_declaration():
    text = read(REPORT)
    assert text.count("Primary A010 hypothesis outcome:") == 1
    assert "Primary A010 hypothesis outcome: `NOT_SUPPORTED`" in text
    assert "Primary A010 hypothesis outcome: `SUPPORTED`" not in text
    assert "Primary A010 hypothesis outcome: `MIXED`" not in text


def test_a010_qualification_evidence_remains_after_repository_closure():
    task = read(TASKS / "A010-dense-nonselective-baseline-comparison.md")
    roadmap = read(TASKS / "ROADMAP.md")
    assert "Status: DONE" in task
    assert "GitHub Issue: #10 (closed as completed)" in task
    assert "Portable qualification: GREEN" in task
    assert "Physical qualification: GREEN" in task
    assert "Exact feature-branch CI: GREEN" in task
    assert "234bc090dc068447c1830fa79337745b7796f25f" in task
    assert "38014300995" in task
    assert "Primary outcome: `NOT_SUPPORTED`" in task
    assert "| A010 | Dense/Non-selective Baseline Comparison | DONE |" in roadmap
    assert "| A011 | ASCA v0.x Qualification | PLANNED |" in roadmap


def test_readme_records_a010_qualified_candidate_without_overclaim():
    text = read(ROOT / "README.md")
    assert "A010" in text
    assert "NOT_SUPPORTED" in text
    assert "28" in text and "27" in text
    assert "1984" in text and "1440" in text
    assert "66" in text and "480" in text
    lower = text.lower()
    assert "a010 proves lower flops" not in lower
    assert "a010 proves lower energy" not in lower
    assert "a010 proves superiority over dense llms" not in lower
    assert "flywireasca does **not** currently claim:" in lower

def test_a010_records_whole_branch_review_and_post_review_ci():
    task = read(TASKS / "A010-dense-nonselective-baseline-comparison.md")
    report = read(REPORT)
    for text in (task, report):
        assert "4db95323a0b5d8476c85f114a702f4371ab76ba9" in text
        assert "38017518584" in text
        assert "528 passed" in text
        assert "Critical findings: 0" in text
        assert "Important findings: 5" in text
        assert "Minor findings: 1" in text
        assert "author self-review" in text.lower()
        assert "independent reviewer" in text.lower()
        assert "qwen3-embedding:0.6b" in text
        assert "NOT_SUPPORTED" in text
    assert "- [x] Whole-branch review GREEN." in task
    assert "Whole-branch review: GREEN" in task
    assert "reviewed main integration: green" in report.lower()

def test_a010_records_reviewed_main_integration_before_issue_close():
    task = read(TASKS / "A010-dense-nonselective-baseline-comparison.md")
    report = read(REPORT)
    for text in (task, report):
        assert "a0833c3b072ab27d331bfab9c3e8b8f509fac366" in text
        assert "38017717305" in text
        assert "529 passed" in text
        assert "Main integration: GREEN" in text
        assert "fast-forward" in text.lower()
        assert "merge commit" in text.lower()
    assert "Status: DONE" in task
    assert "GitHub Issue: #10 (closed as completed)" in task

def test_a010_repository_closure_state_is_done_and_a011_planned():
    task = read(TASKS / "A010-dense-nonselective-baseline-comparison.md")
    current = read(TASKS / "CURRENT.md")
    roadmap = read(TASKS / "ROADMAP.md")
    report = read(REPORT)
    readme = read(ROOT / "README.md")
    assert "Status: DONE" in task
    assert "GitHub Issue: #10 (closed as completed)" in task
    assert "A010 repository state: DONE" in report
    assert "GitHub Issue #10 closure: completed" in report
    assert "| A010 | Dense/Non-selective Baseline Comparison | DONE |" in roadmap
    assert "| A011 | ASCA v0.x Qualification | PLANNED |" in roadmap
    assert "A010" in readme and "NOT_SUPPORTED" in readme
    assert "A011" in readme and "PLANNED" in readme
    assert "remains open" not in task.lower()
    assert "pending" not in task.lower()