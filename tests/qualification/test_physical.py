from dataclasses import replace
from collections import deque
import json
import urllib.error
import urllib.request
import pytest
from flywire_asca.qualification.artifacts import artifact_issues, publish_pack
from flywire_asca.qualification.classifier import pack_exit_code
from flywire_asca.qualification.manifest import decode_pack, manifest_issues
from flywire_asca.qualification.physical import (
    RuntimeSnapshot, OllamaRuntimeProbe, runtime_issues, run_full,
)
from flywire_asca.qualification.process import ProcessEvidence
from flywire_asca.qualification.records import (
    EngineeringVerdict, EvidenceRole, GateStatus, PHYSICAL_GATE_IDS,
    PORTABLE_GATE_IDS, Reason,
)

class Probe:
    def __init__(self, *snapshots):
        self.snapshots = deque(snapshots)
        self.last = snapshots[-1]
        self.calls = 0
    def inspect(self):
        self.calls += 1
        return self.snapshots.popleft() if self.snapshots else self.last

def snapshot(profile, **changes):
    value = RuntimeSnapshot(True, "test-host", "test-platform", "3.14",
        "http://127.0.0.1:11434", "0.32.15", {**profile.values["terminal"],"dimension":None},
        dict(profile.values["embedding"]), (), {"test_only": True})
    return replace(value, **changes)

def absent(profile):
    return snapshot(profile, available=False, terminal=None, embedding=None,
        ollama_version=None, reasons=(Reason("PREREQUISITE_UNAVAILABLE",
        "H00_PREREQUISITES", "Confirmed refusal", ()),))

def gate(pack, name):
    return next(g for g in pack.gates if g.gate_id == name)

def diagnostic(command, payload=None, execution_error=None):
    if payload is None:
        payload = {"qualification_scope":"local_physical_qwen_a004",
            "qualified":False, "errors":["connection / model unavailable"],
            "generation_profile":{"thinking":False,"tools":False,"vision":False}}
    data = json.dumps(payload, sort_keys=True).encode()
    if command.output_path:
        command.output_path.write_bytes(data)
    return ProcessEvidence(command, "2026-10-10T10:00:00Z", "2026-10-10T10:00:01Z",
        1 if execution_error is None else None, data, b"", execution_error)

@pytest.mark.parametrize("missing", ["runtime", "terminal", "embedding"])
def test_runtime_missing_or_model_absent_is_confirmed_blocker(qualification_context, frozen_profile, missing):
    state = absent(frozen_profile) if missing == "runtime" else snapshot(frozen_profile, **{missing:None})
    context = qualification_context
    pack = run_full(context, Probe(state))
    assert gate(pack,"H00_PREREQUISITES").status is GateStatus.BLOCKED
    assert not any(c.gate_id.startswith("H") for c in context.runner.commands)
    assert all(gate(pack,g).status is GateStatus.NOT_RUN and
        gate(pack,g).cause_ids == ("H00_PREREQUISITES",) for g in PHYSICAL_GATE_IDS[1:7])
    assert pack.engineering_verdict is EngineeringVerdict.QUALIFICATION_BLOCKED
    assert pack_exit_code(pack) == 2
    assert manifest_issues(pack) == () and artifact_issues(pack,context.store.root) == ()
    path,_ = publish_pack(context.store,pack)
    assert decode_pack(path.read_bytes()) == pack

@pytest.mark.parametrize("identity", ["terminal_digest", "embedding_digest", "dimension"])
def test_installed_wrong_digest_dimension_is_failure(qualification_context, frozen_profile, identity):
    state = snapshot(frozen_profile)
    if identity == "dimension":
        state = replace(state,embedding={**state.embedding,"dimension":768})
    else:
        field = identity.split("_")[0]
        state = replace(state, **{field:{**getattr(state,field),"digest":"b"*64}})
    pack = run_full(qualification_context, Probe(state))
    assert gate(pack,"H00_PREREQUISITES").status is GateStatus.FAIL
    assert any(r.code == "IDENTITY_DRIFT" for r in pack.errors)
    assert pack.engineering_verdict is EngineeringVerdict.ENGINEERING_NOT_QUALIFIED
    assert pack_exit_code(pack) == 1

def test_missing_terminal_and_wrong_embedding_digest_is_failure(qualification_context, frozen_profile):
    state = snapshot(frozen_profile,terminal=None)
    state = replace(state,embedding={**state.embedding,"digest":"b"*64})
    pack = run_full(qualification_context,Probe(state))
    assert {r.code for r in gate(pack,"H00_PREREQUISITES").errors} >= {"MODEL_MISSING","IDENTITY_DRIFT"}
    assert pack.engineering_verdict is EngineeringVerdict.ENGINEERING_NOT_QUALIFIED

def test_full_runs_fresh_local_portable_then_six_physical_qualifiers(qualification_context, frozen_profile):
    context = qualification_context
    probe = Probe(snapshot(frozen_profile))
    pack = run_full(context,probe)
    assert tuple(g.gate_id for g in pack.gates) == PORTABLE_GATE_IDS + PHYSICAL_GATE_IDS
    assert pack.engineering_verdict is EngineeringVerdict.ENGINEERING_QUALIFIED
    assert pack_exit_code(pack) == 0
    assert pack.source.before.commit == pack.source.after.commit == context.expected_commit
    commands = context.runner.commands
    physical = [c for c in commands if c.gate_id.startswith("H")]
    assert [c.gate_id for c in physical] == list(PHYSICAL_GATE_IDS[1:7])
    assert commands.index(physical[0]) > max(i for i,c in enumerate(commands) if c.gate_id.startswith("P"))
    a005_command = physical[1]
    assert a005_command.argv[a005_command.argv.index("--threshold")+1] == "0.5037018224299838"
    assert "--calibrate" not in a005_command.argv and a005_command.timeout_seconds is None
    for command,outcome in zip(physical[-2:],("SUPPORTED","NOT_SUPPORTED")):
        assert command.argv[command.argv.index("--portable-primary-outcome")+1] == outcome
    assert probe.calls == 2
    assert manifest_issues(pack) == () and artifact_issues(pack,context.store.root) == ()
    path,_ = publish_pack(context.store,pack)
    assert decode_pack(path.read_bytes()) == pack

def test_physical_secondary_never_overwrites_portable_primary(qualification_context, frozen_profile):
    pack = run_full(qualification_context,Probe(snapshot(frozen_profile)))
    for evidence in pack.research_evidence:
        if evidence.milestone in ("A009","A010"):
            assert tuple(o.role for o in evidence.observations) == (
                EvidenceRole.PORTABLE_PRIMARY,EvidenceRole.PHYSICAL_SECONDARY)
        if evidence.milestone in ("A006","A007"):
            assert tuple(o.role for o in evidence.observations) == (EvidenceRole.PHYSICAL_PRIMARY,)
        assert all(o.outcome == evidence.expected_outcome for o in evidence.observations)

def test_confirmed_runtime_disappearance_after_h00_is_blocked(qualification_context, frozen_profile):
    context = qualification_context
    context.runner.responses["H01_A004"] = diagnostic
    pack = run_full(context,Probe(snapshot(frozen_profile),absent(frozen_profile)))
    assert gate(pack,"H01_A004").status is GateStatus.BLOCKED
    assert any("after-failure" in ref for r in pack.blockers for ref in r.evidence_refs)
    assert pack.engineering_verdict is EngineeringVerdict.QUALIFICATION_BLOCKED
    assert pack_exit_code(pack) == 2
    assert len([c for c in context.runner.commands if c.gate_id.startswith("H")]) == 1

@pytest.mark.parametrize("error", [None,"TimeoutError: connection to missing model"])
def test_unknown_timeout_or_nonzero_is_failure_not_keyword_blocker(qualification_context, frozen_profile, error):
    context = qualification_context
    context.runner.responses["H01_A004"] = lambda c: diagnostic(c,execution_error=error)
    pack = run_full(context,Probe(snapshot(frozen_profile)))
    assert gate(pack,"H01_A004").status is GateStatus.FAIL
    assert pack.engineering_verdict is EngineeringVerdict.ENGINEERING_NOT_QUALIFIED
    assert pack_exit_code(pack) == 1

def test_verified_child_identity_drift_dominates_later_runtime_loss(qualification_context, frozen_profile, physical_payload):
    context = qualification_context
    def wrong(command):
        payload = physical_payload(command.gate_id)
        payload["model"]["digest"] = "b"*64
        payload["qualified"] = False
        payload["errors"] = ["connection lost later"]
        return diagnostic(command,payload)
    context.runner.responses["H01_A004"] = wrong
    pack = run_full(context,Probe(snapshot(frozen_profile),absent(frozen_profile)))
    assert any(r.code == "IDENTITY_DRIFT" for r in pack.errors)
    assert pack.engineering_verdict is EngineeringVerdict.ENGINEERING_NOT_QUALIFIED
    assert pack_exit_code(pack) == 1

def test_completion_probe_detects_mid_run_identity_drift(qualification_context, frozen_profile):
    state = snapshot(frozen_profile)
    drift = replace(state,embedding={**state.embedding,"dimension":768})
    pack = run_full(qualification_context,Probe(state,drift))
    assert gate(pack,"H07_FULL_VALIDATION").status is GateStatus.FAIL
    assert any(r.code == "IDENTITY_DRIFT" for r in pack.errors)
    assert pack.engineering_verdict is EngineeringVerdict.ENGINEERING_NOT_QUALIFIED

def test_no_auto_retry_pull_calibration_restart_or_new_deadline(qualification_context, frozen_profile, monkeypatch):
    calls = []
    class Response:
        def __init__(self,value): self.value=value
        def __enter__(self): return self
        def __exit__(self,*args): pass
        def read(self): return json.dumps(self.value).encode()
    def open_metadata(request, timeout):
        calls.append((request.method,request.full_url,timeout,request.data))
        if request.full_url.endswith("/api/version"):
            return Response({"version":"0.32.15"})
        if request.full_url.endswith("/api/tags"):
            return Response({"models":[{"name":v["model"],"digest":v["digest"]} for v in (
                frozen_profile.values["terminal"],frozen_profile.values["embedding"])]})
        assert request.full_url.endswith("/api/show") and request.method == "POST"
        return Response({"model_info":{"general.architecture":"qwen3","qwen3.embedding_length":1024}})
    monkeypatch.setattr(urllib.request,"urlopen",open_metadata)
    probe = OllamaRuntimeProbe()
    state = probe.inspect()
    assert runtime_issues(state,frozen_profile) == ()
    pack = run_full(qualification_context,probe)
    assert pack_exit_code(pack) == 0
    assert all(c.timeout_seconds is None for c in qualification_context.runner.commands)
    assert all("/api/" in u and u.rsplit("/",1)[-1] in ("version","tags","show") and t == 5
        for m,u,t,d in calls)
    assert all(len([x for x in qualification_context.runner.commands if x.gate_id == g]) == 1
        for g in PHYSICAL_GATE_IDS[1:7])

def test_reachable_malformed_metadata_is_failure_not_absence(frozen_profile, monkeypatch):
    class Response:
        def __enter__(self): return self
        def __exit__(self,*args): pass
        def read(self): return b'{"models":[],"models":[]}'
    monkeypatch.setattr(urllib.request,"urlopen",lambda *a,**k:Response())
    reasons = runtime_issues(OllamaRuntimeProbe().inspect(),frozen_profile)
    assert any(r.code == "EVIDENCE_INVALID" for r in reasons)
    assert not any(r.code == "PREREQUISITE_UNAVAILABLE" for r in reasons)

def test_portable_failure_prevents_all_physical_work(qualification_context, frozen_profile):
    context = qualification_context
    context.runner.mutations[("P05_A008",1)] = lambda p:p.update(primary_hypothesis_outcome="NOT_SUPPORTED")
    probe = Probe(snapshot(frozen_profile))
    pack = run_full(context,probe)
    assert probe.calls == 0
    assert not any(c.gate_id.startswith("H") for c in context.runner.commands)
    assert all(gate(pack,g).status is GateStatus.NOT_RUN for g in PHYSICAL_GATE_IDS[:-1])
    assert pack.engineering_verdict is EngineeringVerdict.ENGINEERING_NOT_QUALIFIED

def test_flattened_legacy_a006_a007_emission_is_accepted(qualification_context, frozen_profile, physical_payload):
    context = qualification_context
    for g in ("H03_A006","H04_A007"):
        def flatten(p):
            assert "experiment" not in p
            assert "fixture_fingerprint" in p
        context.runner.mutations[(g,1)] = flatten
    pack = run_full(context,Probe(snapshot(frozen_profile)))
    assert pack.engineering_verdict is EngineeringVerdict.ENGINEERING_QUALIFIED
