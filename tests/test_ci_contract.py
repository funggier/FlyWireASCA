from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "ci.yml"


def test_ci_fetches_parent_commit_for_diff_check():
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "fetch-depth: 2" in text
    assert "git diff --check HEAD^ HEAD" in text
