"""Exclusive external artifact store and validated atomic pack publication."""
from __future__ import annotations
from dataclasses import dataclass, field
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import stat
import tempfile
from uuid import uuid4

from .manifest import encode_pack, json_value, manifest_issues
from .profile import EXPECTED_PROFILE_SHA256, EXPECTED_PROTECTED_SHA256, load_frozen_profile
from .records import ArtifactRecord, QualificationError, Reason, Scope

METADATA_FILES = frozenset(("qualification.json", "qualification.md", "artifact-index.json"))


def _is_link(info):
    return stat.S_ISLNK(info.st_mode) or bool(getattr(info, "st_file_attributes", 0) &
                                            getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400))


def _ancestors_safe(path):
    for item in reversed((path,) + tuple(path.parents)):
        try:
            info = item.lstat()
        except FileNotFoundError:
            continue
        if _is_link(info):
            raise QualificationError("EVIDENCE_INVALID", f"Linked path/ancestor refused: {item}")
        if item != path and not stat.S_ISDIR(info.st_mode):
            raise QualificationError("EVIDENCE_INVALID", "Artifact ancestor is not a directory")


def _relative(value, *, metadata=False):
    if type(value) is not str:
        raise QualificationError("EVIDENCE_INVALID", "Artifact path must be a string")
    path = PurePosixPath(value)
    if (not value or "\\" in value or ":" in value or path.is_absolute() or
        any(part in ("", ".", "..") for part in value.split("/")) or str(path) != value or
        not metadata and value in METADATA_FILES):
        raise QualificationError("EVIDENCE_INVALID", "Unsafe or circular artifact path")
    return path


def _regular(path):
    _ancestors_safe(path)
    info = path.lstat()
    if not stat.S_ISREG(info.st_mode) or _is_link(info) or info.st_nlink != 1:
        raise QualificationError("EVIDENCE_INVALID", "Artifact must be regular and nonlinked")
    return info


@dataclass
class ArtifactStore:
    root: Path
    _root_identity: tuple[int, int]
    _records: dict[str, ArtifactRecord] = field(default_factory=dict, repr=False)
    _published: bool = False

    @classmethod
    def create(cls, repo_root, output_dir=None):
        repo = Path(repo_root).resolve()
        destination = Path(output_dir) if output_dir is not None else (
            Path(tempfile.gettempdir()) / "flywire-asca-a011" / uuid4().hex)
        if ".." in destination.parts:
            raise QualificationError("EVIDENCE_INVALID", "Output path traversal refused")
        destination = destination.absolute()
        _ancestors_safe(destination)
        if destination.resolve().is_relative_to(repo):
            raise QualificationError("EVIDENCE_INVALID", "Output directory must be outside checkout")
        if destination.exists():
            raise QualificationError("EVIDENCE_INVALID", "Output directory already exists; no overwrite")
        try:
            destination.parent.mkdir(parents=True, exist_ok=True)
            _ancestors_safe(destination.parent)
            destination.mkdir(exist_ok=False)
            _ancestors_safe(destination)
            root = destination.resolve()
            info = root.lstat()
            return cls(root, (info.st_dev, info.st_ino))
        except OSError as exc:
            raise QualificationError("ARTIFACT_WRITE_FAILED", f"Cannot create exclusive output: {exc}") from exc

    def _check_root(self):
        _ancestors_safe(self.root)
        info = self.root.lstat()
        if (not stat.S_ISDIR(info.st_mode) or
            (info.st_dev, info.st_ino) != self._root_identity or self.root.resolve() != self.root):
            raise QualificationError("EVIDENCE_INVALID", "Artifact root was replaced")

    def write_raw(self, relative_path, data, kind):
        rel = _relative(relative_path)
        if type(data) is not bytes or type(kind) is not str or not kind:
            raise QualificationError("EVIDENCE_INVALID", "Raw artifact requires bytes and kind")
        if self._published:
            raise QualificationError("EVIDENCE_INVALID", "Published artifact store is immutable")
        self._check_root()
        path = self.root / str(rel)
        _ancestors_safe(path)
        if path.exists() or relative_path in self._records:
            raise QualificationError("EVIDENCE_INVALID", "Raw artifact exists; no overwrite")
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            _ancestors_safe(path.parent)
            descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0), 0o600)
            with os.fdopen(descriptor, "wb") as stream:
                stream.write(data)
                stream.flush()
                os.fsync(stream.fileno())
            info = _regular(path)
            if info.st_size != len(data):
                raise OSError("Incomplete raw artifact write")
            self._check_root()
            record = ArtifactRecord(relative_path, kind, hashlib.sha256(data).hexdigest(), len(data))
            self._records[relative_path] = record
            return record
        except OSError as exc:
            raise QualificationError("ARTIFACT_WRITE_FAILED", f"Cannot write raw artifact: {exc}") from exc

    def index(self):
        return tuple(self._records[key] for key in sorted(self._records))


def artifact_issues(pack, root, *, _manifest_check=None):
    issues = list((_manifest_check or manifest_issues)(pack))
    root = Path(root).absolute()
    def issue(code, message, refs=()):
        issues.append(Reason(code, "P09_PACK_VALIDATION", message, refs))
    try:
        _ancestors_safe(root)
        info = root.lstat()
        if not stat.S_ISDIR(info.st_mode):
            raise QualificationError("EVIDENCE_INVALID", "Pack root is not directory")
        indexed = set()
        profiles = []
        for record in pack.artifact_index:
            _relative(record.path)
            path = root/record.path
            info = _regular(path)
            if not path.resolve().is_relative_to(root):
                raise QualificationError("EVIDENCE_INVALID", "Artifact path escapes pack")
            data = path.read_bytes()
            if info.st_size != record.byte_length or len(data) != record.byte_length or hashlib.sha256(data).hexdigest() != record.sha256:
                issue("EVIDENCE_INVALID", "Artifact bytes/hash/length differ", (record.path,))
            indexed.add(record.path)
            if record.kind == "profile":
                profiles.append((record, data))
        if len(profiles) != 1:
            issue("EVIDENCE_INVALID", "Exactly one indexed frozen profile copy is required")
        else:
            record, raw = profiles[0]
            if (record.sha256 != pack.profile.sha256 or
                pack.profile.expected_sha256 != EXPECTED_PROFILE_SHA256 or
                pack.profile.id != "asca-v0x-a011-v1"):
                issue("PROFILE_DRIFT", "Copied profile and manifest profile differ", (record.path,))
            try:
                load_frozen_profile(raw)
            except QualificationError:
                source_gate = next((g for g in pack.gates if g.gate_id == "P00_PROFILE_SOURCE"), None)
                recorded_drift = source_gate is not None and source_gate.status.value == "FAIL" and any(
                    r.code == "PROFILE_DRIFT" and r.gate_id == source_gate.gate_id and
                    record.path in r.evidence_refs for r in pack.errors)
                if not recorded_drift:
                    issue("PROFILE_DRIFT", "Invalid copied profile lacks an explicit failed source gate", (record.path,))
                # Diagnostic drift bytes are retained, never consumed as expectations.
            if (pack.source.protected_sha256 is not None and
                pack.source.protected_sha256 != EXPECTED_PROTECTED_SHA256 and
                not any(r.code == "SOURCE_MISMATCH" for r in pack.errors)):
                issue("SOURCE_MISMATCH", "Manifest protected source differs from frozen profile", (record.path,))
        for path in root.rglob("*"):
            _ancestors_safe(path)
            relative = path.relative_to(root).as_posix()
            if path.is_file():
                _regular(path)
                if relative not in indexed and relative not in METADATA_FILES:
                    issue("EVIDENCE_INVALID", "Unindexed raw file in qualification pack")
    except (OSError, QualificationError) as exc:
        issue(exc.code if isinstance(exc, QualificationError) else "EVIDENCE_INVALID", str(exc))
    return tuple(issues)


def _text(value):
    return str(value).replace("|", "\\|").replace("\n", " ")


def render_pack_markdown(pack):
    issues = manifest_issues(pack)
    if issues:
        raise QualificationError("EVIDENCE_INVALID", "Cannot render invalid manifest: " +
                                 "; ".join(r.message for r in issues))
    verdict = pack.engineering_verdict.value if pack.engineering_verdict else "null"
    lines = ["# ASCA v0.x qualification", "",
        f"Scope: {pack.scope.value}; is_final={str(pack.is_final).lower()}; engineering_verdict={verdict}.",
        f"Portable status: {pack.portable_status.value}.", "",
        f"Source: `{pack.source.commit}`; profile: `{pack.profile.sha256}`.",
        f"Protected source: `{pack.source.protected_sha256}`.", "",
        "| Milestone | Frozen research outcome | Fresh observations |",
        "| --- | --- | --- |"]
    for research in pack.research_evidence:
        observations = "; ".join(f"{o.role.value}: {o.outcome.value} ({o.freshness.value}, {o.evidence_ref})"
                                 for o in research.observations) or "Not executed; historical references retained"
        lines.append(f"| {research.milestone} | {research.expected_outcome.value} | {_text(observations)} |")
    lines += ["", "| Gate | Scope | Status | Exit |", "| --- | --- | --- | --- |"]
    for gate in pack.gates:
        lines.append(f"| {gate.gate_id} | {gate.scope.value} | {gate.status.value} | {gate.exit_code} |")
    lines += ["", "Errors: " + str(len(pack.errors)) + "; blockers: " + str(len(pack.blockers)) + "."]
    for reason in pack.errors + pack.blockers:
        lines.append(f"- {_text(reason.gate_id)} / {_text(reason.code)}: {_text(reason.message)}")
    if pack.physical_environment is not None:
        environment = pack.physical_environment
        lines += ["", f"Physical environment: {_text(environment.hostname)} / {_text(environment.platform)}.",
                  f"Python: {_text(environment.python_version)}; Ollama: {_text(environment.ollama_version)}; endpoint: {_text(environment.endpoint)}."]
        for name in ("terminal", "embedding"):
            descriptor = getattr(environment, name)
            if descriptor is not None:
                lines.append(f"{name}: {_text(descriptor['model'])} / {_text(descriptor['digest'])}; dimension={descriptor['dimension']}.")
    lines += ["", "Claims boundary:", ""]
    lines.extend("- " + statement for statement in pack.claims_boundary)
    lines += ["", "Raw artifact hashes are recorded in qualification.json and artifact-index.json.", ""]
    return "\n".join(lines)


def _atomic_write(store, name, data):
    store._check_root()
    destination = store.root/name
    temporary = store.root/(".publish-" + uuid4().hex + ".tmp")
    _ancestors_safe(destination)
    # Reserve exclusively before atomic replace. Only this run's empty reservation
    # is replaced; a previous run/user file is never overwritten.
    reserved = os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0), 0o600)
    reserved_info = os.fstat(reserved)
    os.close(reserved)
    descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0), 0o600)
    with os.fdopen(descriptor, "wb") as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())
    current = _regular(destination)
    if (current.st_dev, current.st_ino) != (reserved_info.st_dev, reserved_info.st_ino):
        raise QualificationError("EVIDENCE_INVALID", "Publication reservation was replaced")
    store._check_root()
    os.replace(temporary, destination)
    _regular(destination)


def publish_pack(store, pack):
    store._check_root()
    issues = artifact_issues(pack, store.root)
    if pack.artifact_index != store.index():
        issues += (Reason("EVIDENCE_INVALID", "P09_PACK_VALIDATION", "Manifest/store artifact indices differ", ()),)
    if issues:
        raise QualificationError("EVIDENCE_INVALID", "Publication refused: " +
                                 "; ".join(r.message for r in issues))
    if store._published or any((store.root/name).exists() for name in METADATA_FILES):
        raise QualificationError("EVIDENCE_INVALID", "Publication already exists; no overwrite")
    manifest = encode_pack(pack)
    report = render_pack_markdown(pack).encode("utf-8")
    index = json.dumps(json_value(pack.artifact_index), ensure_ascii=False, sort_keys=True,
                       separators=(",", ":"), allow_nan=False).encode("utf-8")
    try:
        for name, data in (("qualification.json", manifest), ("qualification.md", report),
                           ("artifact-index.json", index)):
            _atomic_write(store, name, data)
        store._published = True
    except (OSError, QualificationError) as exc:
        raise QualificationError("ARTIFACT_WRITE_FAILED", f"Required publication failed: {exc}") from exc
    return store.root/"qualification.json", store.root/"qualification.md"
