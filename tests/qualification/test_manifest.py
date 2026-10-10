from dataclasses import replace
import json
import pytest
from flywire_asca.qualification.records import EvidenceRole, Freshness, GateStatus, QualificationError, Reason, Scope
from flywire_asca.qualification.manifest import decode_pack, encode_pack, manifest_issues, strict_json_object


def test_complete_pack_round_trips(make_pack):
    pack = make_pack()
    assert manifest_issues(pack) == ()
    assert decode_pack(encode_pack(pack)) == pack


@pytest.mark.parametrize("mutation", ["missing", "duplicate", "unknown"])
def test_missing_duplicate_unknown_gate_is_rejected(make_pack, mutation):
    pack = make_pack()
    gates = pack.gates[1:] if mutation == "missing" else pack.gates + (
        pack.gates[0] if mutation == "duplicate" else replace(pack.gates[0], gate_id="P99_UNKNOWN"),)
    assert manifest_issues(replace(pack, gates=gates))


def test_pass_with_errors_and_bad_cause_is_rejected(make_pack):
    pack = make_pack()
    gate = replace(pack.gates[0], errors=(Reason("EVIDENCE_INVALID", pack.gates[0].gate_id, "contradiction", ()),),
                   cause_ids=("H07_FULL_VALIDATION",))
    assert manifest_issues(replace(pack, gates=(gate,) + pack.gates[1:]))


@pytest.mark.parametrize("path", ["profile", "source.before", "gates.0", "research_evidence.0.observations.0",
                                 "replay_identity.observations.0", "physical_environment.terminal"])
def test_unknown_nested_field_is_rejected(make_pack, path):
    value = json.loads(encode_pack(make_pack()))
    node = value
    for key in path.split("."):
        node = node[int(key)] if isinstance(node, list) else node[key]
    node["unreviewed"] = True
    with pytest.raises(QualificationError):
        decode_pack(json.dumps(value).encode())


@pytest.mark.parametrize("raw", [b'{"x":1,"x":2}', b'{"x":NaN}', b'{"x":Infinity}',
    b'[]', b'{} trailing', b'\xff', b'{"nested":{"x":1,"x":2}}'])
def test_bool_counts_duplicate_keys_nonfinite_and_bad_hash_are_rejected(make_pack, raw):
    with pytest.raises(QualificationError):
        strict_json_object(raw)
    value = json.loads(encode_pack(make_pack()))
    value["artifact_index"][0]["byte_length"] = True
    with pytest.raises(QualificationError):
        decode_pack(json.dumps(value).encode())
    value["artifact_index"][0]["byte_length"] = 2
    value["profile"]["sha256"] = "bad"
    with pytest.raises(QualificationError):
        decode_pack(json.dumps(value).encode())


def test_scope_finality_and_physical_freshness_cannot_contradict(make_pack):
    pack = make_pack(Scope.PORTABLE_ONLY)
    assert manifest_issues(pack) == ()
    assert manifest_issues(replace(pack, is_final=True))
    research = list(pack.research_evidence)
    observed = research[2].observations[0]
    research[2] = replace(research[2], observations=(replace(observed,
        role=EvidenceRole.PHYSICAL_SECONDARY, freshness=Freshness.FRESH_PHYSICAL),))
    assert manifest_issues(replace(pack, research_evidence=tuple(research)))


def test_cause_cycle_and_forward_cause_fail_closed(make_pack):
    pack = make_pack()
    gates = list(pack.gates)
    for index in (0, 1):
        gates[index] = replace(gates[index], status=GateStatus.NOT_RUN, command=None,
            started_at=None, finished_at=None, exit_code=None, artifacts=(),
            cause_ids=(gates[1-index].gate_id,))
    assert manifest_issues(replace(pack, gates=tuple(gates)))


def test_duplicate_milestone_and_missing_evidence_reference_fail(make_pack):
    pack = make_pack()
    assert manifest_issues(replace(pack, research_evidence=pack.research_evidence + (pack.research_evidence[0],)))
    assert manifest_issues(replace(pack, artifact_index=pack.artifact_index[1:]))


def test_utc_intervals_and_one_candidate_are_required(make_pack):
    pack = make_pack()
    assert manifest_issues(replace(pack, source=replace(pack.source,
        after=replace(pack.source.after, commit="d"*40))))
    assert manifest_issues(replace(pack, gates=(replace(pack.gates[0],
        finished_at="2026-10-09T00:00:00Z"),) + pack.gates[1:]))
    assert manifest_issues(replace(pack, claims_boundary=("too broad",)))


def test_coherent_failure_pack_remains_schema_valid(make_pack, replace_gate):
    pack = replace_gate(make_pack(), "H03_A006", GateStatus.FAIL,
        Reason("IDENTITY_DRIFT", "H03_A006", "independently verified wrong digest", ("raw/H03_A006.json",)))
    pack = replace(pack, research_evidence=tuple(
        replace(r, observations=()) if r.milestone == "A006" else r for r in pack.research_evidence))
    assert manifest_issues(pack) == ()
    assert decode_pack(encode_pack(pack)) == pack


def test_schema_rejects_wrong_primitive_and_missing_top_level(make_pack):
    value = json.loads(encode_pack(make_pack()))
    value["is_final"] = "true"
    with pytest.raises(QualificationError):
        decode_pack(json.dumps(value).encode())
    value = json.loads(encode_pack(make_pack()))
    del value["blockers"]
    with pytest.raises(QualificationError):
        decode_pack(json.dumps(value).encode())
