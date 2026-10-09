from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
TASKS=ROOT/"docs"/"development"/"tasks"
A007=ROOT/"docs"/"development"/"reports"/"ASCA-20261009-A007-surprise-uncertainty-expansion.md"

def read(p): return p.read_text(encoding="utf-8")

def test_current_points_to_planned_a009_after_a008_closure_candidate():
    text=read(TASKS/"CURRENT.md")
    assert "Current task: A009" in text
    assert "Status: PLANNED" in text
    assert "GitHub Issue: not created" in text
    assert "A008 deterministic qualification: GREEN" in text

def test_roadmap_a008_done_a009_a011_planned():
    text=read(TASKS/"ROADMAP.md")
    assert "| A008 | Procedural Memory / Skill Chunking | DONE |" in text
    assert "| A009 | Integrated Cognitive Loop | PLANNED |" in text
    assert "| A011 | ASCA v0.x Qualification | PLANNED |" in text

def test_a008_task_records_approved_boundaries():
    text=read(TASKS/"A008-procedural-memory-skill-chunking.md")
    assert "Status: DONE" in text
    assert "GitHub Issue: #8" in text
    assert "FLAT" in text and "CHUNKED" in text and "BLIND_CHUNKED" in text
    assert "max_call_depth = 8" in text
    assert "EXACT" in text
    assert "real tool" in text.lower()
    assert "qwen3.5:4b" in text
    assert "Ollama" in text
    assert "typed graph" in text.lower() or "semantic graph" in text.lower()
    assert "retry" in text.lower()
    assert "FlyWireLLM" in text and "paused" in text.lower()

def test_readme_current_stage_a008():
    text=read(ROOT/"README.md")
    assert "A008" in text
    assert "Procedural Memory" in text
    assert "CHUNKED" in text

def test_a007_closure_remains_supported_historical_evidence():
    text=read(A007)
    assert "Final A007 hypothesis outcome: `SUPPORTED`" in text

REPORT_A008 = ROOT / "docs" / "development" / "reports" / "ASCA-20261009-A008-procedural-memory-skill-chunking.md"

def test_a008_closure_report_records_exact_qualification():
    text=read(REPORT_A008)
    assert "0bfee1dfc424934ed783150f6c4d86140c6502d2" in text
    assert "37956221852" in text
    assert "370 passed" in text
    assert "f52fbd4ab018386ff3cbfb62a68cc44a4b40e54ec4fd9a3b2e885dd2c5663fc6" in text
    assert "Final A008 hypothesis outcome: `SUPPORTED`" in text
    assert "FLAT root-visible dispatches: 13" in text
    assert "CHUNKED root-visible dispatches: 8" in text
    assert "maximum deliberative compression ratio: 2.0" in text
    assert "heat-water" in text
    assert "BLIND_CHUNKED" in text
    assert "FlyWireLLM" in text and "paused" in text.lower()

def test_a008_report_has_exactly_one_primary_outcome():
    text=read(REPORT_A008)
    assert text.count("Final A008 hypothesis outcome:") == 1
    assert "Final A008 hypothesis outcome: `SUPPORTED`" in text
    assert "Final A008 hypothesis outcome: `MIXED`" not in text
    assert "Final A008 hypothesis outcome: `NOT_SUPPORTED`" not in text

def test_a008_closure_transitions_to_planned_a009_without_issue():
    task=read(TASKS/"A008-procedural-memory-skill-chunking.md")
    assert "Status: DONE" in task
    roadmap=read(TASKS/"ROADMAP.md")
    assert "| A008 | Procedural Memory / Skill Chunking | DONE |" in roadmap
    assert "| A009 | Integrated Cognitive Loop | PLANNED |" in roadmap
    current=read(TASKS/"CURRENT.md")
    assert "Current task: A009" in current
    assert "Status: PLANNED" in current
    assert "GitHub Issue: not created" in current

def test_a008_report_keeps_claims_and_integration_boundaries():
    text=read(REPORT_A008).lower()
    assert "deterministic simulator" in text
    assert "no real tool" in text
    assert "no ollama" in text
    assert "no automatic retry" in text
    assert "control-state" in text
    assert "do not establish" in text
    assert "a007" in text and "supported" in text

def test_a008_report_records_post_review_hardening():
    text=read(REPORT_A008)
    assert "b0ad2f1abed08683ea8218861c97f3c2d47384d3" in text
    assert "37959983484" in text
    assert "Important" in text
    assert "max_call_depth" in text
    assert "invalid-library" in text
    assert "count/reuse" in text
    assert "post-review deterministic qualification" in text.lower()
    assert "Final A008 hypothesis outcome: `SUPPORTED`" in text
    assert "FLAT / CHUNKED root-visible dispatches: 13 / 8" in text
    assert "fixture fingerprint unchanged" in text.lower()


def test_a008_task_marks_whole_branch_review_resolved():
    text=read(TASKS/"A008-procedural-memory-skill-chunking.md")
    assert "- [x] Whole-branch review Critical/Important findings resolved." in text
    assert "b0ad2f1abed08683ea8218861c97f3c2d47384d3" in text
    assert "37959983484" in text

def test_a008_report_records_main_integration_evidence():
    text=read(REPORT_A008)
    assert "Main integration evidence" in text
    assert "0142973814fb67dd28a54fa454f25fa88f7dfcd9" in text
    assert "37961029994" in text
    assert "383 passed" in text
    assert "SUPPORTED" in text
    task=read(TASKS/"A008-procedural-memory-skill-chunking.md")
    assert "First final-main CI: DONE" in task


def test_current_records_a008_main_integration_green_without_starting_a009():
    text=read(TASKS/"CURRENT.md")
    assert "Current task: A009" in text
    assert "Status: PLANNED" in text
    assert "GitHub Issue: not created" in text
    assert "A008 main integration: GREEN" in text

def test_a008_report_records_closure_evidence_main_ci():
    text=read(REPORT_A008)
    assert "Closure-evidence main CI" in text
    assert "1972c98b1b7d1346bd4b66458ac92b4ef00e11cd" in text
    assert "37961779986" in text
    task=read(TASKS/"A008-procedural-memory-skill-chunking.md")
    assert "Final closure-evidence main CI: DONE" in task


def test_a008_all_acceptance_criteria_closed_before_issue_closure():
    text=read(TASKS/"A008-procedural-memory-skill-chunking.md")
    acceptance=text.split("## Acceptance Criteria",1)[1].split("## Evidence",1)[0]
    assert "- [ ]" not in acceptance
