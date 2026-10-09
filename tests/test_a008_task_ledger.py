from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
TASKS=ROOT/"docs"/"development"/"tasks"
A007=ROOT/"docs"/"development"/"reports"/"ASCA-20261009-A007-surprise-uncertainty-expansion.md"

def read(p): return p.read_text(encoding="utf-8")

def test_current_activates_a008_issue_8_branch():
    text=read(TASKS/"CURRENT.md")
    assert "Current task: A008" in text
    assert "Status: ACTIVE" in text
    assert "GitHub Issue: #8" in text
    assert "Branch: research/a008-procedural-memory" in text

def test_roadmap_a008_active_a009_a011_planned():
    text=read(TASKS/"ROADMAP.md")
    assert "| A008 | Procedural Memory / Skill Chunking | ACTIVE |" in text
    assert "| A009 | Integrated Cognitive Loop | PLANNED |" in text
    assert "| A011 | ASCA v0.x Qualification | PLANNED |" in text

def test_a008_task_records_approved_boundaries():
    text=read(TASKS/"A008-procedural-memory-skill-chunking.md")
    assert "Status: ACTIVE" in text
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
