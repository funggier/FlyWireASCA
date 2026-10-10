from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
PROFILE_PATH = ROOT / "docs" / "development" / "qualification" / "a011-v0x-profile-v1.json"
EXPECTED_PROFILE_SHA256 = "add06f285bf6decc7d492b987d3769dc64db4cb3d0177c8c6586d50ee5f6d46d"
EXPECTED_PROTECTED_SHA256 = "8df49f05fe54de43667ab2f8ef5de2caae9376ffedf2cb8f8d26f0e4abcca6b6"
EXPECTED_PROTECTED_PATH_COUNT = 67


def _git(root: Path, *args: str) -> bytes:
    result = subprocess.run(
        ["git", *args],
        cwd=root,
        capture_output=True,
        check=False,
        shell=False,
    )
    if result.returncode != 0:
        raise RuntimeError(
            result.stderr.decode("utf-8", errors="replace").strip()
            or "git command failed"
        )
    return result.stdout


def _listed_protected_sha256(root: Path, paths: tuple[str, ...]) -> str:
    raw = _git(root, "ls-tree", "-rz", "--full-tree", "HEAD")
    entries: dict[str, tuple[str, str, str]] = {}
    for line in raw.split(b"\0"):
        if not line:
            continue
        metadata, path = line.split(b"\t", 1)
        mode, kind, blob = metadata.decode("ascii").split()
        entries[path.decode("utf-8")] = (mode, kind, blob)

    records: list[dict[str, str]] = []
    for name in sorted(paths):
        if name not in entries:
            raise RuntimeError(f"missing protected path: {name}")
        mode, kind, blob = entries[name]
        if mode not in {"100644", "100755"} or kind != "blob":
            raise RuntimeError(f"protected path is not a regular blob: {name}")
        records.append({"path": name, "mode": mode, "blob": blob})

    canonical = json.dumps(
        records,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def run_check(root: Path = ROOT) -> dict[str, object]:
    root = Path(root).resolve()
    errors: list[str] = []

    profile_path = root / PROFILE_PATH.relative_to(ROOT)
    try:
        profile_bytes = profile_path.read_bytes()
    except OSError as exc:
        return {
            "preservation_valid": False,
            "errors": [f"cannot read A011 frozen profile: {exc}"],
        }

    profile_sha = hashlib.sha256(profile_bytes).hexdigest()
    if profile_sha != EXPECTED_PROFILE_SHA256:
        errors.append("A011 frozen profile bytes changed")

    try:
        profile = json.loads(profile_bytes.decode("utf-8"))
        protected = profile["protected_source"]
        paths = tuple(protected["paths"])
        profile_protected_sha = protected["sha256"]
    except (KeyError, TypeError, ValueError, UnicodeError) as exc:
        errors.append(f"A011 frozen profile structure invalid: {exc}")
        paths = ()
        profile_protected_sha = None

    if len(paths) != EXPECTED_PROTECTED_PATH_COUNT:
        errors.append("A011 frozen protected path count changed")
    if len(paths) != len(set(paths)):
        errors.append("A011 frozen protected paths are not unique")
    if profile_protected_sha != EXPECTED_PROTECTED_SHA256:
        errors.append("A011 profile protected-source anchor changed")

    observed_sha: str | None = None
    if paths:
        try:
            observed_sha = _listed_protected_sha256(root, paths)
        except (OSError, RuntimeError, ValueError) as exc:
            errors.append(f"cannot inspect A011 protected Git blobs: {exc}")
        else:
            if observed_sha != EXPECTED_PROTECTED_SHA256:
                errors.append("A011 protected Git blobs changed")

        try:
            status = _git(
                root,
                "status",
                "--porcelain=v1",
                "--untracked-files=all",
                "--",
                *paths,
            )
        except (OSError, RuntimeError) as exc:
            errors.append(f"cannot inspect A011 protected worktree paths: {exc}")
        else:
            if status:
                errors.append("A011 protected worktree paths are dirty")

    return {
        "preservation_valid": not errors,
        "profile_sha256": profile_sha,
        "protected_sha256": observed_sha,
        "protected_path_count": len(paths),
        "boundary": (
            "historical A011 frozen-profile preservation only; "
            "this does not qualify the current HEAD as A011/v0.x"
        ),
        "errors": errors,
    }


def main() -> int:
    payload = run_check()
    print(json.dumps(payload, sort_keys=True, separators=(",", ":")))
    return 0 if payload["preservation_valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
