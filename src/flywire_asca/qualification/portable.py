"""Portable orchestration of existing frozen qualifiers; no cognition imported."""
from __future__ import annotations
from dataclasses import dataclass, replace
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tomllib
from collections.abc import Mapping
from uuid import uuid4

from .artifacts import ArtifactStore, artifact_issues
from .classifier import _decision, classify_full, classify_portable
from .evidence import AdapterResult, LegacyValidator, normalize_child
from .manifest import json_value, manifest_issues, validate_completed_evidence
from .process import CommandSpec, ProcessEvidence, ProcessRunner
from .profile import (
    EXPECTED_PROFILE_SHA256, EXPECTED_PROTECTED_SHA256, FrozenProfile, load_frozen_profile,
)
from .provenance import capture_source, source_issues
from .records import (
    CLAIMS_BOUNDARY, PHYSICAL_GATE_IDS, PORTABLE_GATE_IDS, RESEARCH_OUTCOMES,
    EngineeringVerdict, FrozenCheck, GateEvidence, GateStatus, ProfileIdentity,
    QualificationError, QualificationPack, Reason, ReplayIdentity, ReplayObservation,
    ResearchEvidence, Scope, SourceIdentity,
)

CHILD_SCRIPTS = {
    "P02_ARCHITECTURE": "scripts/audit_architecture_contract.py",
    "P03_REPOSITORY": "scripts/qualify_repository.py",
    "P04_A003": "scripts/run_familiarity_benchmark_a003.py",
    "P05_A008": "scripts/qualify_procedural_memory_a008.py",
    "P06_A009": "scripts/qualify_integrated_loop_a009.py",
    "P07_A010": "scripts/qualify_baseline_comparison_a010.py",
    "H01_A004": "scripts/qualify_qwen_a004.py",
    "H02_A005": "scripts/qualify_vector_memory_a005.py",
    "H03_A006": "scripts/qualify_selective_activation_a006.py",
    "H04_A007": "scripts/qualify_uncertainty_expansion_a007.py",
    "H05_A009": "scripts/qualify_integrated_loop_a009_physical.py",
    "H06_A010": "scripts/qualify_baseline_comparison_a010_physical.py",
}
CHILD_MILESTONES = {
    "P05_A008": "A008", "P06_A009": "A009", "P07_A010": "A010",
    "H03_A006": "A006", "H04_A007": "A007",
}
HISTORICAL_REFS = (
    "docs/development/reports/ASCA-20261009-A006-working-set-selective-activation.md",
    "docs/development/reports/ASCA-20261009-A007-surprise-uncertainty-expansion.md",
    "docs/development/tasks/A008-procedural-memory-skill-chunking.md",
    "docs/development/tasks/A009-integrated-cognitive-loop.md",
    "docs/development/tasks/A010-dense-nonselective-baseline-comparison.md",
)


@dataclass(frozen=True)
class RunContext:
    repo_root: Path
    expected_commit: str
    profile_path: Path
    store: ArtifactStore
    runner: ProcessRunner
    validators: Mapping[str, LegacyValidator]


def now():
    return datetime.now(timezone.utc).isoformat()


def write_json(store, path, value, kind="audit"):
    data = json.dumps(json_value(value), ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")
    return store.write_raw(path, data, kind)


def _git_identity(root, *args):
    result = subprocess.run(["git", *args], cwd=root, capture_output=True, shell=False, check=False)
    if result.returncode:
        raise QualificationError("SOURCE_MISMATCH", "Cannot capture Git child identity")
    return result.stdout.decode("ascii").strip()


def not_run(gate_id, cause):
    return GateEvidence(gate_id, Scope.PORTABLE_ONLY if gate_id.startswith("P") else Scope.FULL_SYSTEM,
        GateStatus.NOT_RUN, None, None, None, None, (), (), (cause,))


class _PackBuilder:
    def __init__(self, context):
        self.context = context
        self.profile = None
        self.profile_error = None
        self.profile_available = True
        try:
            raw = context.profile_path.read_bytes()
        except OSError as exc:
            raw = b""
            self.profile_available = False
            self.profile_error = "Source profile unavailable; retained zero-byte diagnostic copy: " + str(exc)
        self.profile_record = context.store.write_raw("profile.json", raw, "profile")
        try:
            self.profile = load_frozen_profile(raw)
        except QualificationError as exc:
            self.profile_error = self.profile_error or str(exc)
        self.profile_identity = ProfileIdentity("asca-v0x-a011-v1", 1,
            hashlib.sha256(raw).hexdigest(), EXPECTED_PROFILE_SHA256,
            "qualification.profile.EXPECTED_PROFILE_SHA256")
        self.paths = tuple(self.profile.values["protected_source"]["paths"]) if self.profile else ()
        self.before = capture_source(context.repo_root, context.profile_path, self.paths)
        self.after = self.before
        self.gates = []
        self.checks = []
        self.observations = {name: [] for name in RESEARCH_OUTCOMES}
        self.replays = []
        self.environment = None
        self.pack_id = uuid4().hex
        self.child_root = None

    def frozen(self, identity, expected, observed, refs):
        valid = observed is not None and json.dumps(json_value(expected), sort_keys=True) == json.dumps(json_value(observed), sort_keys=True)
        self.checks.append(FrozenCheck(identity, expected, observed,
                                      GateStatus.PASS if valid else GateStatus.FAIL, tuple(refs)))

    def start_source(self):
        context = self.context
        start = now()
        before_ref = "source/before.json"
        audit_ref = "raw/P00_PROFILE_SOURCE/audit.json"
        write_json(context.store, before_ref, self.before, "source")
        errors = []
        if self.profile_error:
            errors.append(Reason("PROFILE_DRIFT", "P00_PROFILE_SOURCE", self.profile_error, ("profile.json",)))
        if self.profile:
            errors.extend(replace(r, evidence_refs=(before_ref, "profile.json")) for r in
                source_issues(self.before, self.before, context.expected_commit, self.profile))
        else:
            if self.before.clean is not True or self.before.commit != context.expected_commit:
                errors.append(Reason("SOURCE_MISMATCH", "P00_PROFILE_SOURCE",
                    "Candidate dirty, unavailable, or different from requested SHA", (before_ref,)))
        try:
            observed_version = tomllib.loads((context.repo_root/"pyproject.toml").read_text(encoding="utf-8"))["project"]["version"]
        except (OSError, ValueError, KeyError):
            observed_version = None
        expected_version = self.profile.values["package_version"] if self.profile else "0.1.0.dev0"
        self.frozen("package.version", expected_version, observed_version, (audit_ref,))
        if observed_version != expected_version or type(observed_version) is not str:
            errors.append(Reason("IDENTITY_DRIFT", "P00_PROFILE_SOURCE",
                "Package version differs from frozen 0.1.0.dev0", (audit_ref,)))
        self.frozen("profile.sha256", EXPECTED_PROFILE_SHA256, self.profile_identity.sha256, ("profile.json",))
        # Unknown protected measurement on a rejected profile is explicit absence.
        self.frozen("source.protected_sha256", EXPECTED_PROTECTED_SHA256, self.before.protected_sha256, (before_ref,))
        self.frozen("source.expected_commit", context.expected_commit, self.before.commit, (before_ref,))
        write_json(context.store, audit_ref, {
            "profile_available": self.profile_available,
            "expected_profile_sha256": EXPECTED_PROFILE_SHA256,
            "observed_copy_sha256": self.profile_identity.sha256,
            "expected_commit": context.expected_commit, "source": self.before,
            "observed_package_version": observed_version,
            "errors": tuple(errors)}, "audit")
        self.gates.append(GateEvidence("P00_PROFILE_SOURCE", Scope.PORTABLE_ONLY,
            GateStatus.FAIL if errors else GateStatus.PASS,
            ("a011-internal", "profile-and-source-v1"), start, now(), 1 if errors else 0,
            ("profile.json", before_ref, audit_ref), tuple(errors), ()))
        return not errors

    def finish_source(self, after_ref="source/after.json"):
        context = self.context
        self.after = capture_source(context.repo_root, context.profile_path, self.paths)
        write_json(context.store, after_ref, self.after, "source")
        errors = []
        if self.profile:
            errors.extend(replace(r, evidence_refs=(after_ref,)) for r in
                source_issues(self.before, self.after, context.expected_commit, self.profile))
        elif self.after.commit != self.before.commit or self.after.clean is not True:
            errors.append(Reason("SOURCE_MISMATCH", "P00_PROFILE_SOURCE",
                                "Rejected-profile source changed or remained uninspectable", (after_ref,)))
        gate = self.gates[0]
        # P00 is the before/after source gate; its interval surrounds execution.
        merged = gate.errors + tuple(r for r in errors if r not in gate.errors)
        self.gates[0] = replace(gate, status=GateStatus.FAIL if merged else GateStatus.PASS,
            finished_at=now(), exit_code=1 if merged else 0, errors=merged,
            artifacts=gate.artifacts + (after_ref,))

    def pack(self, scope=Scope.PORTABLE_ONLY, completing_gate=None):
        full = scope == Scope.FULL_SYSTEM
        errors = tuple(r for g in self.gates if g.status == GateStatus.FAIL for r in g.errors)
        blockers = tuple(r for g in self.gates if g.status == GateStatus.BLOCKED for r in g.errors)
        portable_required = tuple(g for g in PORTABLE_GATE_IDS if g != completing_gate)
        portable_status = _decision(tuple(self.gates), errors, blockers, portable_required)
        verdict = None
        if full:
            required = tuple(g for g in PORTABLE_GATE_IDS + PHYSICAL_GATE_IDS if g != completing_gate)
            status = _decision(tuple(self.gates), errors, blockers, required)
            verdict = {GateStatus.PASS: EngineeringVerdict.ENGINEERING_QUALIFIED,
                GateStatus.FAIL: EngineeringVerdict.ENGINEERING_NOT_QUALIFIED,
                GateStatus.BLOCKED: EngineeringVerdict.QUALIFICATION_BLOCKED}[status]
        historical = self.profile.values["historical_refs"] if self.profile else HISTORICAL_REFS
        research = tuple(ResearchEvidence(milestone, outcome, tuple(self.observations[milestone]),
            (historical[index],)) for index, (milestone, outcome) in enumerate(RESEARCH_OUTCOMES.items()))
        return QualificationPack(1, self.profile_identity,
            SourceIdentity("funggier/FlyWireASCA", self.before.commit, self.before.protected_sha256,
                           self.before, self.after), scope, full, portable_status, verdict,
            tuple(self.gates), tuple(self.checks), research,
            ReplayIdentity(self.pack_id, self.before.commit, self.profile_identity.sha256, tuple(self.replays)),
            self.environment if full else None, errors, blockers, self.context.store.index(), CLAIMS_BOUNDARY)

    def command(self, gate_id, output_path=None):
        prefix = (sys.executable, "-X", "utf8")
        if gate_id == "P01_TESTS":
            argv = prefix + ("-m", "pytest", "-q")
        else:
            argv = prefix + (str((self.context.repo_root/CHILD_SCRIPTS[gate_id]).resolve()),)
            if gate_id == "P04_A003":
                argv += ("--qualify",)
            if gate_id == "H02_A005":
                argv += ("--threshold", repr(self.profile.values["a005_threshold"]))
            if gate_id in ("H05_A009", "H06_A010"):
                milestone = "A009" if gate_id == "H05_A009" else "A010"
                argv += ("--portable-primary-outcome", self.profile.values["research_outcomes"][milestone])
            if output_path is not None:
                argv += ("--output", str(output_path))
        return CommandSpec(gate_id, argv, self.context.repo_root, output_path, None)

    def execute_child(self, logical_gate, parent_gate=None, run_index=1):
        parent = parent_gate or logical_gate
        milestone = CHILD_MILESTONES.get(logical_gate)
        prefix = "raw/" + parent + ("/" + milestone if run_index == 2 else "")
        output_path = None
        if logical_gate not in ("P01_TESTS", "P02_ARCHITECTURE", "P03_REPOSITORY", "P04_A003"):
            if self.child_root is None:
                self.child_root = ArtifactStore.create(self.context.repo_root,
                    self.context.store.root.parent / (self.context.store.root.name+"-children-"+uuid4().hex)).root
            output_path = self.child_root/(logical_gate+f"-run{run_index}.json")
        command = self.command(logical_gate, output_path)
        try:
            child_commit = _git_identity(self.context.repo_root, "rev-parse", "HEAD")
        except QualificationError:
            child_commit = None
        try:
            evidence = self.context.runner.run(command)
        except OSError as exc:
            stamp = now()
            evidence = ProcessEvidence(command, stamp, stamp, None, b"", b"", f"{type(exc).__name__}: {exc}")
        paths = []
        for name, data in (("stdout.log", evidence.stdout), ("stderr.log", evidence.stderr)):
            relative = prefix+"/"+name
            self.context.store.write_raw(relative, data, "log")
            paths.append(relative)
        output = None
        if output_path is not None:
            try:
                output = output_path.read_bytes()
            except OSError:
                pass
            if output is not None:
                relative = prefix+"/output.json"
                self.context.store.write_raw(relative, output, "child-json")
                paths.append(relative)
        metadata = {
            "gate_id": logical_gate, "parent_gate_id": parent, "run_index": run_index,
            "argv": command.argv, "cwd": str(command.cwd),
            "output_path": str(output_path) if output_path is not None else None,
            "timeout_seconds": command.timeout_seconds, "source_commit": child_commit,
            "profile_sha256": self.profile_identity.sha256,
            "started_at": evidence.started_at, "finished_at": evidence.finished_at,
            "exit_code": evidence.exit_code, "execution_error": evidence.execution_error,
        }
        process_ref = prefix+"/process.json"
        write_json(self.context.store, process_ref, metadata, "process")
        paths.append(process_ref)
        validator = self.context.validators.get(milestone) if milestone else None
        result = normalize_child(logical_gate, evidence, output, self.profile, validator)
        actual_ref = prefix+"/output.json" if output is not None else prefix+"/stdout.log"
        errors = tuple(replace(r, gate_id=parent, evidence_refs=(actual_ref,)) for r in result.errors)
        checks = tuple(replace(c, identity=(f"{milestone}.run{run_index}."+c.identity if milestone and logical_gate.startswith("P") else c.identity),
            evidence_refs=(actual_ref,)) for c in result.frozen_checks)
        if child_commit != self.before.commit:
            errors += (Reason("SOURCE_MISMATCH", parent, "Child source context differs from candidate", (process_ref,)),)
        if logical_gate.startswith("P") and milestone:
            expected = self.profile.values["portable_payloads"][milestone]["semantic_sha256"]
            checks += (FrozenCheck(f"{milestone}.run{run_index}.semantic_sha256", expected,
                result.semantic_sha256, GateStatus.PASS if result.semantic_sha256 == expected else GateStatus.FAIL,
                (actual_ref,)),)
        status = GateStatus.FAIL if errors else result.status
        observation = replace(result.observation, evidence_ref=actual_ref) if result.observation and status == GateStatus.PASS else None
        result = replace(result, status=status, errors=errors, frozen_checks=checks, observation=observation)
        self.checks.extend(checks)
        if status == GateStatus.PASS and milestone and logical_gate.startswith("P"):
            try:
                blob = _git_identity(self.context.repo_root, "rev-parse",
                                     child_commit+":"+CHILD_SCRIPTS[logical_gate])
                rule = self.profile.values["portable_payloads"][milestone]
                replay = ReplayObservation(milestone, run_index, rule["fixture_version"],
                    result.payload["fixture_fingerprint"], result.semantic_sha256, blob,
                    child_commit, self.profile_identity.sha256, actual_ref)
                self.replays.append(replay)
            except (QualificationError, ValueError) as exc:
                errors += (Reason("SOURCE_MISMATCH", parent, str(exc), (process_ref,)),)
                result = replace(result, status=GateStatus.FAIL, errors=errors, observation=None)
        if result.observation and run_index == 1:
            name = milestone or ("A009" if logical_gate == "H05_A009" else "A010")
            self.observations[name].append(result.observation)
        validation_ref = prefix+"/validation.json"
        write_json(self.context.store, validation_ref, {
            "gate_id": logical_gate, "parent_gate_id": parent, "status": result.status,
            "errors": result.errors, "frozen_checks": result.frozen_checks,
            "semantic_sha256": result.semantic_sha256}, "validation")
        paths.append(validation_ref)
        gate = GateEvidence(logical_gate, Scope.PORTABLE_ONLY if logical_gate.startswith("P") else Scope.FULL_SYSTEM,
            result.status, command.argv, evidence.started_at, evidence.finished_at, evidence.exit_code,
            tuple(paths), result.errors, ())
        return gate, result, evidence

    def repeat_audit(self):
        start = now()
        paths, errors = [], []
        for gate_id in ("P05_A008", "P06_A009", "P07_A010"):
            gate, result, _ = self.execute_child(gate_id, "P08_FROZEN_AUDIT", 2)
            paths.extend(gate.artifacts)
            errors.extend(result.errors)
            if result.status != GateStatus.PASS:
                break
        ref = "raw/P08_FROZEN_AUDIT/audit.json"
        write_json(self.context.store, ref, {"status": GateStatus.FAIL if errors else GateStatus.PASS,
            "errors": tuple(errors), "replays": tuple(self.replays)}, "audit")
        paths.append(ref)
        self.gates.append(GateEvidence("P08_FROZEN_AUDIT", Scope.PORTABLE_ONLY,
            GateStatus.FAIL if errors else GateStatus.PASS, ("a011-internal", "fresh-frozen-repeat-v1"),
            start, now(), 1 if errors else 0, tuple(paths), tuple(errors), ()))

    def final_gate(self, gate_id, scope):
        start = now()
        prefix_pack = self.pack(scope, completing_gate=gate_id)
        issues = validate_completed_evidence(prefix_pack, gate_id, self.context.store.root)
        ref = "raw/"+gate_id+"/audit.json"
        errors = tuple(Reason(r.code, gate_id, r.message, (ref,)) for r in issues)
        write_json(self.context.store, ref, {"status": GateStatus.FAIL if errors else GateStatus.PASS,
            "validation_phase": gate_id, "completed_gate_ids": tuple(g.gate_id for g in self.gates),
            "errors": errors}, "audit")
        self.gates.append(GateEvidence(gate_id, scope, GateStatus.FAIL if errors else GateStatus.PASS,
            ("a011-internal", "completed-evidence-v1", gate_id), start, now(),
            1 if errors else 0, (ref,), errors, ()))

    def validate_pack(self, scope):
        pack = self.pack(scope)
        issues = manifest_issues(pack)
        if issues:
            raise QualificationError("EVIDENCE_INVALID", "Invalid completed manifest: " +
                                     "; ".join(r.message for r in issues))
        return pack


def _run_portable_builder(context):
    builder = _PackBuilder(context)
    ready = builder.start_source()
    cause = "P00_PROFILE_SOURCE" if not ready else None
    for gate_id in PORTABLE_GATE_IDS[1:8]:
        if cause:
            builder.gates.append(not_run(gate_id, cause))
            continue
        gate, _, _ = builder.execute_child(gate_id)
        builder.gates.append(gate)
        if gate.status != GateStatus.PASS:
            cause = gate.gate_id
    if cause:
        builder.gates.append(not_run("P08_FROZEN_AUDIT", cause))
    else:
        builder.repeat_audit()
    builder.finish_source()
    builder.final_gate("P09_PACK_VALIDATION", Scope.PORTABLE_ONLY)
    builder.validate_pack(Scope.PORTABLE_ONLY)
    return builder


def run_portable(context):
    return _run_portable_builder(context).validate_pack(Scope.PORTABLE_ONLY)
