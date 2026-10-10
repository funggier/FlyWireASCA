from dataclasses import replace
from flywire_asca.qualification.records import GateStatus, Reason, Scope, PHYSICAL_GATE_IDS, PORTABLE_GATE_IDS
from flywire_asca.qualification.classifier import classify_full, classify_portable, pack_exit_code


def test_negative_research_outcomes_do_not_fail_engineering(make_pack):
    pack = make_pack()
    assert [r.expected_outcome.value for r in pack.research_evidence] == [
        "NOT_SUPPORTED", "SUPPORTED", "SUPPORTED", "SUPPORTED", "NOT_SUPPORTED"]
    assert classify_full(pack.gates, pack.errors, pack.blockers).value == "ENGINEERING_QUALIFIED"


def test_portable_pass_never_has_final_verdict(make_pack):
    pack = make_pack(Scope.PORTABLE_ONLY)
    assert pack.is_final is False and pack.engineering_verdict is None
    assert classify_portable(pack.gates, pack.errors, pack.blockers).value == "PASS"
    assert pack_exit_code(pack) == 0


def test_all_pass_full_is_qualified(make_pack):
    pack = make_pack()
    assert classify_full(pack.gates, (), ()).value == "ENGINEERING_QUALIFIED"
    assert pack_exit_code(pack) == 0


def test_verified_failure_dominates_simultaneous_blocker(make_pack, replace_gate):
    pack = replace_gate(make_pack(), "H00_PREREQUISITES", GateStatus.BLOCKED,
        Reason("PREREQUISITE_UNAVAILABLE", "H00_PREREQUISITES", "independent probe", ("raw/H00_PREREQUISITES.json",)))
    pack = replace_gate(pack, "H03_A006", GateStatus.FAIL,
        Reason("IDENTITY_DRIFT", "H03_A006", "wrong identity", ("raw/H03_A006.json",)))
    assert classify_full(pack.gates, pack.errors, pack.blockers).value == "ENGINEERING_NOT_QUALIFIED"
    assert pack_exit_code(pack) == 1


def test_confirmed_blocker_with_caused_not_run_is_blocked(make_pack, replace_gate):
    pack = replace_gate(make_pack(), "H00_PREREQUISITES", GateStatus.BLOCKED,
        Reason("MODEL_MISSING", "H00_PREREQUISITES", "independent absent model", ("raw/H00_PREREQUISITES.json",)))
    gates = tuple(replace(g, status=GateStatus.NOT_RUN, command=None, started_at=None,
        finished_at=None, exit_code=None, artifacts=(), errors=(),
        cause_ids=("H00_PREREQUISITES",)) if g.gate_id in PHYSICAL_GATE_IDS[1:] else g
        for g in pack.gates)
    pack = replace(pack, gates=gates, physical_environment=None, research_evidence=tuple(
        replace(r, observations=tuple(o for o in r.observations if o.freshness.value == "FRESH_PORTABLE"))
        for r in pack.research_evidence))
    assert classify_full(pack.gates, pack.errors, pack.blockers).value == "QUALIFICATION_BLOCKED"
    assert pack_exit_code(pack) == 2


def test_unexplained_not_run_is_failure(make_pack):
    pack = make_pack()
    gates = (replace(pack.gates[0], status=GateStatus.NOT_RUN, command=None,
        started_at=None, finished_at=None, exit_code=None),) + pack.gates[1:]
    assert classify_full(gates, (), ()).value == "ENGINEERING_NOT_QUALIFIED"


def test_unproved_blocker_is_failure(make_pack):
    pack = make_pack()
    gates = (replace(pack.gates[0], status=GateStatus.BLOCKED, errors=()),) + pack.gates[1:]
    assert classify_full(gates, (), ()).value == "ENGINEERING_NOT_QUALIFIED"


def test_portable_classifier_does_not_inherit_physical_failure(make_pack, replace_gate):
    pack = replace_gate(make_pack(), "H01_A004", GateStatus.FAIL,
        Reason("QUALIFIER_FAILED", "H01_A004", "physical failure", ("raw/H01_A004.json",)))
    assert classify_portable(pack.gates, pack.errors, pack.blockers) == GateStatus.PASS
