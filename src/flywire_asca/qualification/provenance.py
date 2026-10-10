"""One clean candidate, identified with HEAD Git objects rather than checkout line endings."""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess

from .profile import EXPECTED_PROTECTED_SHA256, FrozenProfile
from .records import QualificationError, Reason, SourceSnapshot, _hex

SOURCE_GATE = "P00_PROFILE_SOURCE"


def _git(root, *args, input=None):
    result = subprocess.run(["git", *args], cwd=Path(root), input=input,
                            capture_output=True, shell=False, check=False)
    if result.returncode:
        raise QualificationError("SOURCE_MISMATCH", "Git source inspection failed: " +
                                 result.stderr.decode("utf-8", errors="replace").strip())
    return result.stdout


def protected_tree_sha256(repo_root, paths):
    try:
        if type(paths) is not tuple or not paths or len(set(paths)) != len(paths):
            raise ValueError("Protected paths must be unique")
        entries = {}
        raw = _git(repo_root, "ls-tree", "-rz", "--full-tree", "HEAD")
        for line in raw.split(b"\0"):
            if not line:
                continue
            metadata, path = line.split(b"\t", 1)
            mode, kind, blob = metadata.decode("ascii").split()
            name = path.decode("utf-8")
            entries[name] = (mode, kind, blob)
        observed_cognitive = {name for name in entries if name.startswith("src/flywire_asca/")
            and name.endswith(".py") and not name.startswith("src/flywire_asca/qualification/")}
        expected_cognitive = {name for name in paths if name.startswith("src/flywire_asca/")}
        if observed_cognitive != expected_cognitive:
            raise ValueError("Missing or additional protected cognitive/contract Python source")
        records = []
        for name in sorted(paths):
            mode, kind, blob = entries[name]
            if mode not in ("100644", "100755") or kind != "blob" or not _hex(blob, 40):
                raise ValueError("Protected path is not a regular Git blob")
            records.append({"path": name, "mode": mode, "blob": blob})
        batch = _git(repo_root, "cat-file", "--batch-check",
                     input=("\n".join(r["blob"] for r in records) + "\n").encode("ascii"))
        lines = batch.decode("ascii").splitlines()
        if len(lines) != len(records) or any(
            len(line.split()) != 3 or line.split()[0] != record["blob"] or
            line.split()[1] != "blob" for line, record in zip(lines, records)):
            raise ValueError("Missing protected blob object")
        canonical = json.dumps(records, ensure_ascii=False, sort_keys=True,
                               separators=(",", ":")).encode("utf-8")
        return hashlib.sha256(canonical).hexdigest()
    except (OSError, ValueError, KeyError, UnicodeError) as exc:
        raise QualificationError("SOURCE_MISMATCH", f"Invalid protected Git tree: {exc}") from exc


def capture_source(repo_root, profile_path, protected_paths):
    root = Path(repo_root).resolve()
    commit = clean = protected = profile_hash = None
    try:
        top = Path(_git(root, "rev-parse", "--show-toplevel").decode("utf-8").strip()).resolve()
        if top != root:
            raise QualificationError("SOURCE_MISMATCH", "Candidate path is not repository root")
        observed = _git(root, "rev-parse", "HEAD").decode("ascii").strip()
        if _hex(observed, 40):
            commit = observed
        clean = not bool(_git(root, "status", "--porcelain=v1", "--untracked-files=all"))
    except (OSError, ValueError, UnicodeError):
        pass
    try:
        protected = protected_tree_sha256(root, protected_paths)
    except (OSError, QualificationError):
        pass
    try:
        profile_hash = hashlib.sha256(Path(profile_path).read_bytes()).hexdigest()
    except OSError:
        pass
    return SourceSnapshot(commit, clean, protected, profile_hash,
                          datetime.now(timezone.utc).isoformat())


def source_issues(before, after, expected_commit, profile):
    messages = []
    if not _hex(expected_commit, 40):
        messages.append("Expected candidate must be an exact 40-hex Git SHA")
    for label, snapshot in (("before", before), ("after", after)):
        if snapshot.commit != expected_commit:
            messages.append(f"{label}: candidate HEAD differs or is unavailable")
        if snapshot.clean is not True:
            messages.append(f"{label}: checkout is dirty or uninspectable")
        if snapshot.protected_sha256 != EXPECTED_PROTECTED_SHA256:
            messages.append(f"{label}: protected cognitive/qualifier source differs or is unavailable")
        if snapshot.profile_sha256 != profile.sha256:
            messages.append(f"{label}: profile bytes differ or are unavailable")
    return tuple(Reason("SOURCE_MISMATCH", SOURCE_GATE, message, ()) for message in messages)
