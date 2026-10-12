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
