from __future__ import annotations

from dataclasses import replace
import hashlib
import pytest

from flywire_asca.qualification.records import (
    ArtifactRecord, CLAIMS_BOUNDARY, EvidenceRole, EngineeringVerdict, FrozenCheck,
    Freshness, GateEvidence, GateStatus, PHYSICAL_GATE_IDS, PORTABLE_GATE_IDS,
    PhysicalEnvironment, ProfileIdentity, QualificationPack, Reason, ReplayIdentity,
    ReplayObservation, ResearchEvidence, ResearchObservation, ResearchOutcome,
    Scope, SourceIdentity, SourceSnapshot,
)
from flywire_asca.qualification.classifier import classify_full, classify_portable

COMMIT = "c" * 40
HASH = "a" * 64
TIME = "2026-10-10T10:00:00Z"
OUTCOMES = ("NOT_SUPPORTED", "SUPPORTED", "SUPPORTED", "SUPPORTED", "NOT_SUPPORTED")


def _make_pack(scope=Scope.FULL_SYSTEM):
    ids = PORTABLE_GATE_IDS + (PHYSICAL_GATE_IDS if scope == Scope.FULL_SYSTEM else ())
    gates = tuple(GateEvidence(g, Scope.PORTABLE_ONLY if g.startswith("P") else Scope.FULL_SYSTEM,
        GateStatus.PASS, ("a011-internal", g), TIME, TIME, 0,
        (f"raw/{g}.json",), (), ()) for g in ids)
    artifacts = tuple(ArtifactRecord(f"raw/{g}.json", "gate",
        hashlib.sha256(b"{}").hexdigest(), 2) for g in ids)
    snap = SourceSnapshot(COMMIT, True, HASH, HASH, TIME)
    research = []
    replay = []
    for index, outcome in enumerate(OUTCOMES, 6):
        milestone = f"A{index:03}"
        observations = []
        if index >= 8:
            gate_id = PORTABLE_GATE_IDS[index - 3]
            observations.append(ResearchObservation(ResearchOutcome(outcome),
                EvidenceRole.PORTABLE_PRIMARY, Freshness.FRESH_PORTABLE, f"raw/{gate_id}.json"))
            for run in (1, 2):
                replay.append(ReplayObservation(milestone, run, f"a{index:03}-deterministic-v1",
                    HASH, HASH, COMMIT, COMMIT, HASH,
                    f"raw/{gate_id if run == 1 else PORTABLE_GATE_IDS[8]}.json"))
        if scope == Scope.FULL_SYSTEM and index != 8:
            gate_id = PHYSICAL_GATE_IDS[index - 3 if index < 8 else index - 4]
            observations.append(ResearchObservation(ResearchOutcome(outcome),
                EvidenceRole.PHYSICAL_PRIMARY if index < 8 else EvidenceRole.PHYSICAL_SECONDARY,
                Freshness.FRESH_PHYSICAL, f"raw/{gate_id}.json"))
        research.append(ResearchEvidence(milestone, ResearchOutcome(outcome),
            tuple(observations), (f"historical/{milestone}",)))
    env = None if scope == Scope.PORTABLE_ONLY else PhysicalEnvironment(
        "test-host", "test-platform", "3.11", "test", "http://127.0.0.1:11434",
        {"model": "qwen3.5:4b", "digest": HASH, "dimension": None},
        {"model": "qwen3-embedding:0.6b", "digest": HASH, "dimension": 1024},
        (f"raw/{PHYSICAL_GATE_IDS[0]}.json",))
    return QualificationPack(1, ProfileIdentity("asca-v0x-a011-v1", 1, HASH, HASH,
        "qualification.profile.EXPECTED_PROFILE_SHA256"),
        SourceIdentity("funggier/FlyWireASCA", COMMIT, HASH, snap, snap), scope,
        scope == Scope.FULL_SYSTEM, GateStatus.PASS,
        EngineeringVerdict.ENGINEERING_QUALIFIED if scope == Scope.FULL_SYSTEM else None,
        gates, (FrozenCheck("test-profile", HASH, HASH, GateStatus.PASS,
                            (f"raw/{ids[0]}.json",)),),
        tuple(research), ReplayIdentity("test-pack", COMMIT, HASH, tuple(replay)), env,
        (), (), artifacts, CLAIMS_BOUNDARY)


def _replace_gate(pack, gate_id, status, reason=None):
    old = next(g for g in pack.gates if g.gate_id == gate_id)
    changed = replace(old, status=status, errors=() if reason is None else (reason,))
    gates = tuple(changed if g.gate_id == gate_id else g for g in pack.gates)
    errors = pack.errors + ((reason,) if reason and status == GateStatus.FAIL else ())
    blockers = pack.blockers + ((reason,) if reason and status == GateStatus.BLOCKED else ())
    return replace(pack, gates=gates, errors=errors, blockers=blockers,
        portable_status=classify_portable(gates, errors, blockers),
        engineering_verdict=classify_full(gates, errors, blockers)
            if pack.scope == Scope.FULL_SYSTEM else None)


@pytest.fixture(name="make_pack")
def make_pack_fixture():
    return _make_pack


@pytest.fixture(name="replace_gate")
def replace_gate_fixture():
    return _replace_gate
