"""Pinned local metadata inspection and fresh full-system qualification."""
from __future__ import annotations
from dataclasses import dataclass, replace
import json
import platform
import re
import socket
from typing import Protocol
import urllib.error
import urllib.request

from .manifest import json_value, strict_json_object, validate_completed_evidence
from .portable import RunContext, _run_portable_builder, now, not_run, write_json
from .profile import FrozenProfile
from .records import (
    BLOCKER_CODES, FrozenCheck, GateEvidence, GateStatus, JsonObject,
    PHYSICAL_GATE_IDS, PhysicalEnvironment, QualificationError, QualificationPack,
    Reason, Scope, freeze_json,
)

ENDPOINT = "http://127.0.0.1:11434"
TERMINAL_MODEL = "qwen3.5:4b"
EMBEDDING_MODEL = "qwen3-embedding:0.6b"


@dataclass(frozen=True)
class RuntimeSnapshot:
    available: bool
    hostname: str
    platform: str
    python_version: str
    endpoint: str
    ollama_version: str | None
    terminal: JsonObject | None
    embedding: JsonObject | None
    reasons: tuple[Reason, ...]
    raw: JsonObject

    def __post_init__(self):
        if type(self.available) is not bool:
            raise QualificationError("EVIDENCE_INVALID", "Runtime availability must be boolean")
        for name in ("terminal", "embedding", "raw"):
            value = getattr(self, name)
            if value is not None:
                object.__setattr__(self, name, freeze_json(value))
        object.__setattr__(self, "reasons", tuple(self.reasons))


class RuntimeProbe(Protocol):
    def inspect(self) -> RuntimeSnapshot: ...


class OllamaRuntimeProbe:
    """One bounded request per metadata endpoint/model; no inference or retry."""
    def __init__(self, endpoint=ENDPOINT):
        if endpoint != ENDPOINT:
            raise QualificationError("IDENTITY_DRIFT", "Physical endpoint is fixed by the declared profile")
        self.endpoint = endpoint

    def inspect(self):
        raw, reasons = [], []
        def reason(code, message):
            reasons.append(Reason(code, "H00_PREREQUISITES", message, ()))
        def request(method, path, payload=None):
            body = None if payload is None else json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(self.endpoint+path, data=body, method=method,
                                         headers={"Content-Type": "application/json"})
            record = {"method":method, "path":path, "request":payload}
            try:
                with urllib.request.urlopen(req, timeout=5) as response:
                    data = response.read()
                record["response_hex"] = data.hex()
                record["response_text"] = data.decode("utf-8", errors="replace")
                value = strict_json_object(data)
                record["response"] = value
                return value
            except urllib.error.HTTPError as exc:
                record["error"] = str(exc)
                record["http_status"] = exc.code
                reason("EVIDENCE_INVALID", "Reachable metadata endpoint returned HTTP error: "+path)
            except (urllib.error.URLError, socket.timeout, TimeoutError, ConnectionError) as exc:
                record["error"] = str(exc)
                record["error_code"] = "PREREQUISITE_UNAVAILABLE"
                reason("PREREQUISITE_UNAVAILABLE", "Metadata endpoint independently unreachable: "+path)
            except (QualificationError, UnicodeError, ValueError) as exc:
                record["error"] = str(exc)
                reason("EVIDENCE_INVALID", "Malformed reachable metadata: "+path)
            finally:
                raw.append(record)
            return None

        version = request("GET", "/api/version")
        ollama_version = version.get("version") if version is not None else None
        if version is not None and (type(ollama_version) is not str or not ollama_version):
            reason("EVIDENCE_INVALID", "Runtime version is missing or malformed")
            ollama_version = None
        tags = request("GET", "/api/tags")
        models = tags.get("models") if tags is not None else None
        if tags is not None and (type(models) is not list or any(type(m) is not dict for m in models)):
            reason("EVIDENCE_INVALID", "Runtime model inventory is malformed")
            models = None
        descriptors = {}
        if models is not None:
            for name, kind in ((TERMINAL_MODEL,"terminal"), (EMBEDDING_MODEL,"embedding")):
                matches = [m for m in models if m.get("name") == name]
                if not matches:
                    reason("MODEL_MISSING", "Required model tag absent: "+name)
                    descriptors[kind] = None
                    continue
                if len(matches) != 1:
                    reason("EVIDENCE_INVALID", "Duplicate required model tag: "+name)
                selected = matches[0]
                digest = selected.get("digest")
                if type(digest) is not str or re.fullmatch("[0-9a-f]{64}",digest) is None:
                    reason("EVIDENCE_INVALID", "Model digest is malformed: "+name)
                show = request("POST", "/api/show", {"model":name})
                dimension = None
                if show is not None:
                    info = show.get("model_info")
                    if type(info) is not dict:
                        reason("EVIDENCE_INVALID", "Model metadata is malformed: "+name)
                    elif kind == "embedding":
                        architecture = info.get("general.architecture")
                        dimension = info.get(str(architecture)+".embedding_length")
                        if type(architecture) is not str or type(dimension) is not int or dimension <= 0:
                            reason("EVIDENCE_INVALID", "Embedding dimension metadata is malformed")
                descriptors[kind] = {"model":name, "digest":digest, "dimension":dimension}
        available = tags is not None and models is not None
        return RuntimeSnapshot(available, socket.gethostname(), platform.platform(),
            platform.python_version(), self.endpoint, ollama_version,
            descriptors.get("terminal"), descriptors.get("embedding"), tuple(reasons),
            {"requests":raw})


def runtime_issues(snapshot: RuntimeSnapshot, profile: FrozenProfile) -> tuple[Reason, ...]:
    issues = list(snapshot.reasons)
    def add(code, message):
        issues.append(Reason(code, "H00_PREREQUISITES", message, ()))
    if snapshot.endpoint != ENDPOINT:
        add("IDENTITY_DRIFT", "Runtime endpoint differs from the declared fixed endpoint")
    if not snapshot.available:
        if not issues:
            add("PREREQUISITE_UNAVAILABLE", "Runtime inspection confirms unavailability")
        return tuple(issues)
    for kind in ("terminal","embedding"):
        descriptor = getattr(snapshot,kind)
        if descriptor is None:
            if not any(r.code == "MODEL_MISSING" and profile.values[kind]["model"] in r.message for r in issues):
                add("MODEL_MISSING", "Required model absent: "+profile.values[kind]["model"])
            continue
        expected = {**profile.values[kind], "dimension":None} if kind == "terminal" else profile.values[kind]
        for key in ("model","digest","dimension"):
            value = descriptor.get(key)
            # A failed /show request did not measure a dimension. Keep checking
            # tag/digest observations: verified drift still dominates absence.
            dimension_unobserved = (kind == "embedding" and key == "dimension" and value is None and
                any(record.get("path") == "/api/show" and
                    record.get("request", {}).get("model") == profile.values[kind]["model"] and
                    record.get("error_code") == "PREREQUISITE_UNAVAILABLE"
                    for record in snapshot.raw.get("requests", ())))
            if dimension_unobserved:
                continue
            if json.dumps(json_value(value),sort_keys=True) != json.dumps(json_value(expected[key]),sort_keys=True):
                add("IDENTITY_DRIFT", "Runtime "+kind+"."+key+" differs from frozen identity")
    return tuple(issues)


def _reasons(snapshot, profile, gate_id, ref):
    return tuple(replace(r, gate_id=gate_id, evidence_refs=(ref,))
                 for r in runtime_issues(snapshot,profile))


def _status(issues):
    if any(r.code not in BLOCKER_CODES for r in issues):
        return GateStatus.FAIL
    return GateStatus.BLOCKED if issues else GateStatus.PASS


def _environment(snapshot, ref):
    def descriptor(value, terminal=False):
        if value is None or set(value) != {"model","digest","dimension"}:
            return None
        if type(value["model"]) is not str or not value["model"] or type(value["digest"]) is not str or re.fullmatch("[0-9a-f]{64}",value["digest"]) is None:
            return None
        dim = value["dimension"]
        if (terminal and dim is not None) or (not terminal and (type(dim) is not int or dim <= 0)):
            return None
        return value
    return PhysicalEnvironment(snapshot.hostname,snapshot.platform,snapshot.python_version,
        snapshot.ollama_version,snapshot.endpoint,descriptor(snapshot.terminal,True),
        descriptor(snapshot.embedding),(ref,))


def _inspect(builder, probe, gate_id, ref):
    snapshot = probe.inspect()
    issues = _reasons(snapshot,builder.profile,gate_id,ref)
    write_json(builder.context.store,ref,{"snapshot": {
        "available":snapshot.available,"hostname":snapshot.hostname,"platform":snapshot.platform,
        "python_version":snapshot.python_version,"endpoint":snapshot.endpoint,
        "ollama_version":snapshot.ollama_version,"terminal":snapshot.terminal,
        "embedding":snapshot.embedding,"reasons":snapshot.reasons,"raw":snapshot.raw},
        "issues":issues},"runtime")
    for kind in ("terminal","embedding"):
        descriptor = getattr(snapshot,kind)
        if descriptor is None:
            continue  # Absence is a blocker, not a fabricated mismatch measurement.
        expected = {**builder.profile.values[kind],"dimension":None} if kind == "terminal" else builder.profile.values[kind]
        for key in ("model","digest","dimension"):
            # Terminal dimension is intentionally null, so its other two fields are checked.
            if kind == "terminal" and key == "dimension":
                continue
            observed = descriptor.get(key)
            if observed is not None:
                builder.frozen("runtime."+kind+"."+key,expected[key],observed,(ref,))
    return snapshot, issues


def _transport_diagnostic(result, evidence):
    """Only structured incomplete known diagnostic variants can be blocked."""
    if evidence.execution_error is not None or evidence.exit_code == 0 or result.payload is None:
        return False
    if not result.errors or any(r.code != "QUALIFIER_FAILED" for r in result.errors):
        return False
    payload = result.payload
    if not isinstance(payload.get("errors"),tuple) or not payload["errors"] or any(type(e) is not str for e in payload["errors"]):
        return False
    gate_id = evidence.command.gate_id
    if gate_id == "H01_A004":
        return payload.get("qualified") is False and "baseline" not in payload
    if gate_id == "H02_A005":
        return payload.get("experiment_valid") is False and "vector_health" not in payload
    if gate_id in ("H03_A006","H04_A007"):
        return payload.get("experiment_valid") is False and "fixture_version" not in payload
    return payload.get("physical_prerequisites_valid") is False and "physical_metadata" not in payload


def _full_validation(builder, probe, inspect_completion):
    start = now()
    gate_id = "H07_FULL_VALIDATION"
    refs, issues = [], []
    if inspect_completion:
        ref = "runtime/completion.json"
        _, observed = _inspect(builder,probe,gate_id,ref)
        refs.append(ref)
        issues.extend(observed)
        if builder.environment:
            builder.environment = replace(builder.environment,
                evidence_refs=builder.environment.evidence_refs+(ref,))
    builder.finish_source("source/after-physical.json")
    issues.extend(validate_completed_evidence(builder.pack(Scope.FULL_SYSTEM,gate_id),
                                              gate_id,builder.context.store.root))
    ref = "raw/"+gate_id+"/audit.json"
    refs.append(ref)
    # Validator findings refer to this indexed independent audit.
    issues = tuple(replace(r,gate_id=gate_id,evidence_refs=r.evidence_refs or (ref,)) for r in issues)
    status = _status(issues)
    write_json(builder.context.store,ref,{"status":status,"validation_phase":gate_id,
        "completed_gate_ids":tuple(g.gate_id for g in builder.gates),"errors":issues},"audit")
    builder.gates.append(GateEvidence(gate_id,Scope.FULL_SYSTEM,status,
        ("a011-internal","completed-full-evidence-v1"),start,now(),
        0 if status == GateStatus.PASS else 2 if status == GateStatus.BLOCKED else 1,
        tuple(refs),issues,()))


def run_full(context: RunContext, probe: RuntimeProbe) -> QualificationPack:
    # This is always a new local portable execution, never a loaded prior pack.
    builder = _run_portable_builder(context)
    cause = next((g.gate_id for g in builder.gates if g.status in (
        GateStatus.FAIL,GateStatus.BLOCKED)),None)
    inspect_completion = cause is None
    if cause:
        builder.gates.extend(not_run(g,cause) for g in PHYSICAL_GATE_IDS[:-1])
    else:
        start = now()
        ref = "runtime/preflight.json"
        snapshot, issues = _inspect(builder,probe,"H00_PREREQUISITES",ref)
        builder.environment = _environment(snapshot,ref)
        status = _status(issues)
        builder.gates.append(GateEvidence("H00_PREREQUISITES",Scope.FULL_SYSTEM,status,
            ("a011-internal","ollama-metadata-preflight-v1"),start,now(),
            0 if status == GateStatus.PASS else 2 if status == GateStatus.BLOCKED else 1,
            (ref,),issues,()))
        cause = "H00_PREREQUISITES" if status != GateStatus.PASS else None
        for gate_id in PHYSICAL_GATE_IDS[1:7]:
            if cause:
                builder.gates.append(not_run(gate_id,cause))
                continue
            gate, result, evidence = builder.execute_child(gate_id)
            if gate.status != GateStatus.PASS:
                ref = "runtime/after-failure-"+gate_id+".json"
                _, issues = _inspect(builder,probe,gate_id,ref)
                if _transport_diagnostic(result,evidence) and issues and _status(issues) == GateStatus.BLOCKED:
                    gate = replace(gate,status=GateStatus.BLOCKED,errors=issues)
                else:
                    gate = replace(gate,errors=gate.errors+issues)
                gate = replace(gate,artifacts=gate.artifacts+(ref,))
                builder.environment = replace(builder.environment,
                    evidence_refs=builder.environment.evidence_refs+(ref,))
                cause = gate_id
            builder.gates.append(gate)
    _full_validation(builder,probe,inspect_completion)
    return builder.validate_pack(Scope.FULL_SYSTEM)
