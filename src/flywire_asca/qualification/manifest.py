"""Strict normalized schema v1 and structural/causal pack validation."""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import fields, is_dataclass
from enum import Enum
import json
import math
from pathlib import PurePosixPath
from types import UnionType
from typing import get_args, get_origin, get_type_hints, Union

from .records import (
    BLOCKER_CODES, CLAIMS_BOUNDARY, PHYSICAL_GATE_IDS, PORTABLE_GATE_IDS,
    REASON_CODES, RESEARCH_OUTCOMES, EvidenceRole, FrozenCheck, Freshness,
    GateStatus, PhysicalEnvironment, QualificationError, QualificationPack, Reason, Scope,
)
from .classifier import classify_full, classify_portable, gate_issues, utc_time


def strict_json_object(raw):
    if type(raw) is not bytes:
        raise QualificationError("EVIDENCE_INVALID", "JSON input must be bytes")

    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError(f"Duplicate JSON key: {key}")
            result[key] = value
        return result

    def constant(value):
        raise ValueError(f"Nonfinite JSON constant: {value}")

    try:
        value = json.loads(raw.decode("utf-8"), object_pairs_hook=pairs, parse_constant=constant)
        if type(value) is not dict:
            raise ValueError("JSON root must be object")
        # JSON float overflow (1e999) is not handled by parse_constant.
        def finite(item):
            if type(item) is float and not math.isfinite(item):
                raise ValueError("Nonfinite number")
            if type(item) is dict:
                for child in item.values():
                    finite(child)
            elif type(item) is list:
                for child in item:
                    finite(child)
        finite(value)
        return value
    except (ValueError, UnicodeError, RecursionError) as exc:
        raise QualificationError("EVIDENCE_INVALID", f"Invalid strict JSON: {exc}") from exc


def json_value(value):
    if isinstance(value, Enum):
        return value.value
    if is_dataclass(value):
        return {field.name: json_value(getattr(value, field.name)) for field in fields(value)}
    if isinstance(value, Mapping):
        return {key: json_value(item) for key, item in value.items()}
    if type(value) in (tuple, list):
        return [json_value(item) for item in value]
    return value


def encode_pack(pack):
    if type(pack) is not QualificationPack:
        raise QualificationError("EVIDENCE_INVALID", "Expected QualificationPack")
    return json.dumps(json_value(pack), ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def _decode(value, hint):
    origin, args = get_origin(hint), get_args(hint)
    if origin in (Union, UnionType):
        for option in args:
            try:
                return _decode(value, option)
            except QualificationError:
                pass
        raise QualificationError("EVIDENCE_INVALID", "Wrong union value")
    if origin is tuple:
        if type(value) is not list:
            raise QualificationError("EVIDENCE_INVALID", "Expected JSON array")
        return tuple(_decode(item, args[0]) for item in value)
    if isinstance(hint, type) and issubclass(hint, Enum):
        if type(value) is not str:
            raise QualificationError("EVIDENCE_INVALID", "Expected enum string")
        try:
            return hint(value)
        except ValueError as exc:
            raise QualificationError("EVIDENCE_INVALID", "Unknown enum value") from exc
    if isinstance(hint, type) and is_dataclass(hint):
        if type(value) is not dict or set(value) != {field.name for field in fields(hint)}:
            raise QualificationError("EVIDENCE_INVALID", f"Unexpected/missing {hint.__name__} fields")
        hints = get_type_hints(hint)
        decoded = {}
        for field in fields(hint):
            if (hint is FrozenCheck and field.name in ("expected", "observed")) or (
                hint is PhysicalEnvironment and field.name in ("terminal", "embedding")):
                decoded[field.name] = value[field.name]
            else:
                decoded[field.name] = _decode(value[field.name], hints[field.name])
        return hint(**decoded)
    if type(value) is hint:
        return value
    raise QualificationError("EVIDENCE_INVALID", "Wrong primitive type")


def decode_pack(raw):
    pack = _decode(strict_json_object(raw), QualificationPack)
    issues = manifest_issues(pack)
    if issues:
        raise QualificationError("EVIDENCE_INVALID", "; ".join(r.message for r in issues))
    return pack


def manifest_issues(pack):
    issues = []
    gate_id = PORTABLE_GATE_IDS[0]

    def issue(message, gate=gate_id):
        issues.append(Reason("EVIDENCE_INVALID", gate, message, ()))

    full = pack.scope == Scope.FULL_SYSTEM
    required = PORTABLE_GATE_IDS + (PHYSICAL_GATE_IDS if full else ())
    gates = {g.gate_id: g for g in pack.gates}
    if pack.schema_version != 1 or pack.profile.schema_version != 1:
        issue("Unsupported schema version")
    if set(g.gate_id for g in pack.gates) != set(required):
        issue("Scope gate coverage differs")
    issues.extend(gate_issues(pack.gates, required))
    if pack.is_final != full or (not full and pack.engineering_verdict is not None):
        issue("Scope/finality/verdict contradiction")
    if pack.portable_status != classify_portable(pack.gates, pack.errors, pack.blockers):
        issue("Portable status contradicts evidence")
    if full and pack.engineering_verdict != classify_full(pack.gates, pack.errors, pack.blockers):
        issue("Engineering verdict contradicts evidence")
    if pack.claims_boundary != CLAIMS_BOUNDARY:
        issue("Missing declared claims boundary")

    paths = [a.path for a in pack.artifact_index]
    if len(paths) != len(set(paths)):
        issue("Duplicate artifact path")
    for path in paths:
        parsed = PurePosixPath(path)
        if (not path or "\\" in path or ":" in path or parsed.is_absolute() or
            ".." in parsed.parts or "." in path.split("/") or str(parsed) != path or
            path in ("qualification.json", "qualification.md", "artifact-index.json")):
            issue("Unsafe or circular indexed path")
    indexed = set(paths)

    def refs(values):
        if any(ref not in indexed for ref in values):
            issue("Evidence reference does not resolve to indexed artifact")

    for gate in pack.gates:
        refs(gate.artifacts)
        for reason in gate.errors:
            refs(reason.evidence_refs)
            target = pack.blockers if gate.status == GateStatus.BLOCKED else pack.errors
            if gate.status in (GateStatus.FAIL, GateStatus.BLOCKED) and reason not in target:
                issue("Gate reason missing from manifest reasons", gate.gate_id)
    for reason in pack.errors + pack.blockers:
        refs(reason.evidence_refs)
        if reason.code not in REASON_CODES or reason.gate_id not in gates:
            issue("Unknown reason code/gate")
        elif reason not in gates[reason.gate_id].errors:
            issue("Manifest reason missing from gate")
    for reason in pack.blockers:
        if reason.code not in BLOCKER_CODES or not reason.evidence_refs:
            issue("Unproved prerequisite blocker")

    hard_source = any(r.code in ("SOURCE_MISMATCH", "PROFILE_DRIFT") for r in pack.errors)
    if pack.source.repository != "funggier/FlyWireASCA":
        issue("Repository identity differs")
    if pack.profile.sha256 != pack.profile.expected_sha256 and not hard_source:
        issue("Profile drift without causal failure")
    for snapshot in (pack.source.before, pack.source.after):
        try:
            utc_time(snapshot.captured_at)
        except (ValueError, TypeError):
            issue("Invalid source snapshot time")
        if (snapshot.clean is not True or snapshot.commit != pack.source.commit or
            snapshot.commit is None or snapshot.protected_sha256 != pack.source.protected_sha256 or
            snapshot.protected_sha256 is None or snapshot.profile_sha256 != pack.profile.sha256):
            if not hard_source:
                issue("Incomplete/drifting source without causal failure")
    if (pack.replay_identity.source_commit != pack.source.commit or
        pack.replay_identity.profile_sha256 != pack.profile.sha256):
        issue("Replay source/profile differs")

    names = [r.milestone for r in pack.research_evidence]
    if len(names) != len(set(names)) or set(names) != set(RESEARCH_OUTCOMES):
        issue("Research milestone coverage differs")
    research_gates = {
        ("A006", EvidenceRole.PHYSICAL_PRIMARY): "H03_A006",
        ("A007", EvidenceRole.PHYSICAL_PRIMARY): "H04_A007",
        ("A008", EvidenceRole.PORTABLE_PRIMARY): "P05_A008",
        ("A009", EvidenceRole.PORTABLE_PRIMARY): "P06_A009",
        ("A010", EvidenceRole.PORTABLE_PRIMARY): "P07_A010",
        ("A009", EvidenceRole.PHYSICAL_SECONDARY): "H05_A009",
        ("A010", EvidenceRole.PHYSICAL_SECONDARY): "H06_A010",
    }
    for research in pack.research_evidence:
        if research.expected_outcome != RESEARCH_OUTCOMES.get(research.milestone):
            issue("Frozen research outcome differs")
        roles = [o.role for o in research.observations]
        if len(roles) != len(set(roles)):
            issue("Duplicate research observation role")
        for observation in research.observations:
            refs((observation.evidence_ref,))
            target = gates.get(research_gates.get((research.milestone, observation.role)))
            physical = observation.role != EvidenceRole.PORTABLE_PRIMARY
            if (physical and not full or observation.freshness != (
                Freshness.FRESH_PHYSICAL if physical else Freshness.FRESH_PORTABLE) or
                target is None or target.status != GateStatus.PASS or
                observation.evidence_ref not in target.artifacts or
                observation.outcome != research.expected_outcome):
                issue("Research role/freshness/execution/outcome contradiction")
        for (milestone, role), target_id in research_gates.items():
            if milestone == research.milestone and target_id in gates:
                if gates[target_id].status == GateStatus.PASS and role not in roles:
                    issue("Executed research gate lacks observation")

    seen = set()
    for replay in pack.replay_identity.observations:
        refs((replay.evidence_ref,))
        pair = (replay.milestone, replay.run_index)
        target_id = {"A008": "P05_A008", "A009": "P06_A009", "A010": "P07_A010"}.get(replay.milestone)
        if replay.run_index == 2:
            target_id = "P08_FROZEN_AUDIT"
        target = gates.get(target_id)
        if (pair in seen or replay.milestone not in ("A008", "A009", "A010") or
            replay.run_index not in (1, 2) or replay.source_commit != pack.source.commit or
            replay.profile_sha256 != pack.profile.sha256 or target is None or
            target.status != GateStatus.PASS or replay.evidence_ref not in target.artifacts):
            issue("Invalid replay observation")
        seen.add(pair)
    if gates.get("P08_FROZEN_AUDIT") and gates["P08_FROZEN_AUDIT"].status == GateStatus.PASS:
        if seen != {(m, n) for m in ("A008", "A009", "A010") for n in (1, 2)}:
            issue("Missing mandatory repeat observations")

    for check in pack.frozen_checks:
        refs(check.evidence_refs)
        if check.status == GateStatus.PASS and (
            check.observed is None or json_value(check.expected) != json_value(check.observed) or
            json.dumps(json_value(check.expected), sort_keys=True) !=
            json.dumps(json_value(check.observed), sort_keys=True)):
            issue("Frozen PASS contradicts observed identity")
        if check.status == GateStatus.FAIL and not pack.errors:
            issue("Frozen mismatch lacks failed gate")
    env = pack.physical_environment
    if not full and env is not None:
        issue("Portable scope has physical environment")
    if full and env is None and not any(
        g.status in (GateStatus.FAIL, GateStatus.BLOCKED) for g in pack.gates):
        issue("Missing physical environment without causal gate")
    if env is not None:
        refs(env.evidence_refs)
        if not env.evidence_refs:
            issue("Physical environment lacks raw evidence")
    return tuple(issues)


def artifact_issues(pack, root):
    """Artifact-aware validation is opt-in; decoding remains filesystem-independent."""
    from .artifacts import artifact_issues as check_artifacts
    return check_artifacts(pack, root)
