from dataclasses import replace
import hashlib
import json
from pathlib import Path
import subprocess
import pytest
from flywire_asca.qualification.profile import load_frozen_profile
from flywire_asca.qualification.provenance import capture_source, protected_tree_sha256, source_issues
from flywire_asca.qualification.records import QualificationError

ROOT = Path(__file__).resolve().parents[2]
PROFILE_REL = "docs/development/qualification/a011-v0x-profile-v1.json"
PROTECTED = "8df49f05fe54de43667ab2f8ef5de2caae9376ffedf2cb8f8d26f0e4abcca6b6"


def git(root, *args, check=True):
    return subprocess.run(["git", *args], cwd=root, capture_output=True, check=check)


@pytest.fixture
def source_repo(tmp_path, request, prepare_frozen_a011_candidate):
    root = tmp_path / "shallow"
    autocrlf = "true" if request.node.name == "test_crlf_checkout_keeps_protected_git_identity" else "false"
    result = subprocess.run(["git", "-c", f"core.autocrlf={autocrlf}", "clone", "--depth=1",
        "--no-tags", ROOT.as_uri(), str(root)], capture_output=True)
    assert result.returncode == 0, result.stderr
    prepare_frozen_a011_candidate(root)
    assert not (root / "src/flywire_asca/relational_reasoning").exists()
    raw = (ROOT / PROFILE_REL).read_bytes()
    dest = root / PROFILE_REL
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(raw)
    git(root, "config", "user.email", "a011-tests@example.invalid")
    git(root, "config", "user.name", "A011 provenance tests")
    git(root, "config", "core.autocrlf", autocrlf)
    git(root, "add", PROFILE_REL)
    if git(root, "diff", "--cached", "--quiet", check=False).returncode:
        git(root, "commit", "-m", "Test fixture profile")
    profile = load_frozen_profile(raw)
    return root, dest, profile, tuple(profile.values["protected_source"]["paths"])


def test_shallow_checkout_needs_only_head_blobs(source_repo):
    root, path, profile, paths = source_repo
    assert git(root, "cat-file", "-e", "c1498e8e30a23fb67965239d13f0531d5326079e", check=False).returncode != 0
    snap = capture_source(root, path, paths)
    assert snap.clean is True
    assert snap.protected_sha256 == PROTECTED
    assert source_issues(snap, snap, snap.commit, profile) == ()


def test_crlf_checkout_keeps_protected_git_identity(source_repo):
    root, path, profile, paths = source_repo
    git(root, "config", "core.autocrlf", "true")
    git(root, "config", "core.safecrlf", "false")
    for rel in paths:
        blob = git(root, "show", f"HEAD:{rel}").stdout
        assert b"\r\n" not in blob
        (root / rel).write_bytes(blob.replace(b"\n", b"\r\n"))
    snap = capture_source(root, path, paths)
    assert snap.clean is True
    assert snap.protected_sha256 == PROTECTED
    assert source_issues(snap, snap, snap.commit, profile) == ()


@pytest.mark.parametrize("mutation", ["missing", "mode", "blob", "extra"])
def test_missing_mode_blob_or_extra_cognitive_path_is_source_mismatch(source_repo, mutation):
    root, path, profile, paths = source_repo
    if mutation == "missing":
        git(root, "rm", paths[0])
    elif mutation == "mode":
        git(root, "update-index", "--chmod=+x", paths[0])
    elif mutation == "blob":
        p = root / paths[0]
        p.write_bytes(p.read_bytes() + b"\n# frozen source drift\n")
        git(root, "add", paths[0])
    else:
        extra = root / "src/flywire_asca/familiarity/extra.py"
        extra.write_text("pass\n", encoding="utf-8")
        git(root, "add", str(extra))
    git(root, "commit", "-m", "Test source drift")
    snap = capture_source(root, path, paths)
    issues = source_issues(snap, snap, snap.commit, profile)
    assert issues and issues[0].code == "SOURCE_MISMATCH"


@pytest.mark.parametrize("mutation", ["dirty", "head", "profile", "untracked"])
def test_dirty_or_changed_head_profile_is_source_mismatch(source_repo, mutation):
    root, path, profile, paths = source_repo
    before = capture_source(root, path, paths)
    if mutation == "dirty":
        p = root / paths[0]
        p.write_bytes(p.read_bytes() + b"\n# dirty\n")
    elif mutation == "head":
        git(root, "commit", "--allow-empty", "-m", "Different candidate")
    elif mutation == "profile":
        path.write_bytes(path.read_bytes() + b"\n")
    else:
        (root / "untracked.txt").write_text("untracked", encoding="utf-8")
    after = capture_source(root, path, paths)
    issues = source_issues(before, after, before.commit, profile)
    assert issues and issues[0].code == "SOURCE_MISMATCH"


def test_mid_run_source_change_is_failure(source_repo):
    root, path, profile, paths = source_repo
    before = capture_source(root, path, paths)
    after = replace(before, commit="d" * 40)
    assert source_issues(before, after, before.commit, profile)[0].code == "SOURCE_MISMATCH"
