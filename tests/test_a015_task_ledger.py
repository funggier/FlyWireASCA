from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TASKS = ROOT / "docs/development/tasks"


def test_a015_owns_mutable_ledger_only():
    task = TASKS / "A015-unified-agent-runtime.md"
    assert task.is_file(), "A015 task must be created at the approved activation gate"
    task_text = task.read_text(encoding="utf-8")
    current = (TASKS / "CURRENT.md").read_text(encoding="utf-8")
    roadmap = (TASKS / "ROADMAP.md").read_text(encoding="utf-8")
    assert "Current task: A015" in current
    assert current.count("Current task:") == 1
    assert "Status: ACTIVE" in current and "Status: ACTIVE" in task_text
    assert "GitHub Issue: #19" in current and "GitHub Issue: #19" in task_text
    assert "Activation base: 4ca246df6976c7aa21ad07826017f167f0ee27da" in task_text
    assert "research/a015-unified-agent-runtime" in task_text
    assert "Execution method: Native" in task_text
    assert "Stage A" in task_text and "Stage B/C" in task_text
    assert "FlyWireLLM" in task_text and "A011" in task_text
    assert "freeze" in task_text.lower()
    assert roadmap.count("| A015 |") == 1
    assert "| A015 | End-to-End Unified Agent Runtime | ACTIVE |" in roadmap
    for number in range(1, 15):
        row = next(line for line in roadmap.splitlines() if f"| A{number:03d} |" in line)
        assert row.rstrip().endswith("| DONE |")
    a014 = (TASKS / "A014-structural-need-inference.md").read_text(encoding="utf-8")
    assert "Status: DONE" in a014 and "GitHub Issue: #18" in a014

def test_a015_report_preserves_verified_negative_physical_result():
    import json
    evidence = ROOT / "docs/development/qualification/a015-agent-runtime-physical-v1.json"
    report = ROOT / "docs/development/reports/ASCA-20261012-A015-unified-agent-runtime.md"
    assert report.is_file()
    physical = json.loads(evidence.read_text(encoding="utf-8"))
    text = report.read_text(encoding="utf-8")
    assert physical["outcome"] in text
    assert physical["payload_hash"] in text
    assert physical["metadata"]["behavior_commit"] in text
    assert "genuine successful recovery" in text
    assert "0/144" in text and "138/144" in text
    assert physical["totals"]["variants"]["UNIFIED_RUNTIME"]["genuine_recoveries"] == 0
    task = (TASKS / "A015-unified-agent-runtime.md").read_text(encoding="utf-8")
    for link in (report.name, evidence.name, "A015-UNIFIED-AGENT-RUNTIME.md"):
        assert link in task


def test_a015_qualification_matrix_exposes_stage_a_and_cost_boundaries():
    text = (ROOT / "docs/development/QUALIFICATION-MATRIX.md").read_text(encoding="utf-8")
    assert "| A015 |" in text
    for boundary in (
        "Stage A", "PURE", "IN_MEMORY", "genuine successful recovery",
        "UNIFIED_RUNTIME_NOT_SUPPORTED", "portable engineering",
        "retrieval queries", "2048", "1024", "384", "no real external actions",
    ):
        assert boundary in text, boundary
