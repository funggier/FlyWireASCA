from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TASKS = ROOT / "docs" / "development" / "tasks"
REPORT = ROOT / "docs" / "development" / "reports" / "ASCA-20261009-A006-working-set-selective-activation.md"
REPORT_A005 = ROOT / "docs" / "development" / "reports" / "ASCA-20261009-A005-vector-memory-retrieval.md"


def _read(path: Path) -> str:
    assert path.exists(), f"{path.relative_to(ROOT)} must exist"
    return path.read_text(encoding="utf-8")


def test_a006_report_records_a007_was_planned_at_closure():
    text = _read(REPORT)
    assert "A007" in text
    assert "PLANNED" in text


def test_a006_task_is_done_and_preserves_scope_and_physical_outcome():
    text = _read(TASKS / "A006-working-set-selective-activation.md")
    assert "Status: DONE" in text
    assert "GitHub Issue: #6" in text
    assert "does not build or traverse a typed graph" in text
    assert "does not call" in text
    assert "NOT_SUPPORTED" in text
    assert "0.5037018224299838" in text
    assert "top_k = 12" in text
    assert "max_memory_nodes = 8" in text
    assert "max_working_set_items = 4" in text
    for heading in (
        "## Goal",
        "## Scope",
        "## Phases",
        "## Acceptance Criteria",
        "## Evidence",
        "## Current Action",
        "## Next Action",
    ):
        assert heading in text


def test_live_roadmap_preserves_a006_done_while_a007_can_advance():
    text = _read(TASKS / "ROADMAP.md")
    assert "| A005 | Semantic Vector Memory Retrieval | DONE |" in text
    assert "| A006 | Working Set / Selective Activation | DONE |" in text
    assert "| A007 | Surprise, Uncertainty & Expansion |" in text
    assert "| A011 | ASCA v0.x Qualification | PLANNED |" in text


def test_a006_report_records_non_compute_active_state_claim_boundary():
    text = _read(REPORT)
    lower = text.lower()
    assert "a006" in lower
    assert "NOT_SUPPORTED" in text
    assert "active-state" in lower
    assert "compute" in lower
    assert "does not" in lower
    assert "qwen3.5:4b" in text


def test_a006_closure_report_records_exact_branch_portable_and_physical_evidence():
    text = _read(REPORT)
    assert "224864cc9d70228d4feb80a9fcbc07f2776808d3" in text
    assert "238 passed" in text
    assert "37927165972" in text
    assert "ac6da0dfba84a81fdbfbaf330198c33cd77c4cdfc53e8bc50eb581914a15621d" in text
    assert "0.5037018224299838" in text
    assert "e51fea2e58186e94d7affc964509e96d96fc656759677d7dcc073e5b36b91035" in text
    assert "0.942652329749104" in text
    assert "0.35294117647058826" in text
    assert "embedding request count: 21" in text
    assert "embedding input count: 52" in text
    assert "prompt tokens total: 943" in text
    assert "Final A006 hypothesis outcome: `NOT_SUPPORTED`" in text
    assert "convergence recovery count: 0" in text
    assert "convergence regression count: 0" in text
    assert "required-memory coverage: 1.0" in text
    assert "FlyWireLLM" in text
    assert "paused" in text.lower()


def test_a006_report_has_exactly_one_final_hypothesis_outcome():
    text = _read(REPORT)
    assert text.count("Final A006 hypothesis outcome:") == 1
    assert "Final A006 hypothesis outcome: `NOT_SUPPORTED`" in text
    assert "Final A006 hypothesis outcome: `SUPPORTED`" not in text
    assert "Final A006 hypothesis outcome: `MIXED`" not in text


def test_a006_closure_did_not_create_graph_and_report_remains_historical():
    task_names = {path.name.lower() for path in TASKS.glob("*.md")}
    assert not any("graph" in name for name in task_names)
    text = _read(REPORT)
    assert "A007" in text
    assert "PLANNED" in text


def test_a005_closure_report_remains_historical_evidence():
    text = _read(REPORT_A005)
    assert "Final graph decision: `VECTOR_SUFFICIENT`" in text
    assert "0.5037018224299838" in text
    assert "ac6da0dfba84a81fdbfbaf330198c33cd77c4cdfc53e8bc50eb581914a15621d" in text

def test_a006_report_records_merged_main_ci_evidence():
    text = _read(REPORT)
    assert "90ee1709bfd6a827246f5c6292e73f264bf07c2c" in text
    assert "37932246076" in text
    assert "Main integration evidence" in text

def test_a006_report_records_closure_evidence_ci():
    text = _read(REPORT)
    assert "65438ed73a81d86c1c8fa7b6231d2f8466e7e3c2" in text
    assert "37932522003" in text
    task = _read(TASKS / "A006-working-set-selective-activation.md")
    assert "Final closure-evidence main CI: DONE" in task