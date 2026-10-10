from dataclasses import replace
import json
from pathlib import Path
import subprocess
import pytest
from flywire_asca.qualification.artifacts import artifact_issues, publish_pack
from flywire_asca.qualification.classifier import pack_exit_code
from flywire_asca.qualification.evidence import semantic_payload_sha256
from flywire_asca.qualification.manifest import decode_pack, manifest_issues, validate_completed_evidence
from flywire_asca.qualification.portable import run_portable
from flywire_asca.qualification.records import GateStatus, PORTABLE_GATE_IDS, QualificationError, Scope


def test_portable_runs_all_ten_gates_without_ollama(qualification_context):
    context = qualification_context
    pack = run_portable(context)
    assert tuple(g.gate_id for g in pack.gates) == PORTABLE_GATE_IDS
    assert pack.scope is Scope.PORTABLE_ONLY and pack.is_final is False
    assert pack.engineering_verdict is None and pack.portable_status is GateStatus.PASS
    assert pack_exit_code(pack) == 0
    assert pack.source.commit == context.expected_commit
    assert manifest_issues(pack) == () and artifact_issues(pack,context.store.root) == ()
    commands = context.runner.commands
    assert [c.gate_id for c in commands].count("P01_TESTS") == 1
    for gate in ("P05_A008","P06_A009","P07_A010"):
        assert [c.gate_id for c in commands].count(gate) == 2
    command = next(c for c in commands if c.gate_id == "P04_A003")
    assert "--qualify" in command.argv and "--output" not in command.argv
    assert not any(c.gate_id.startswith("H") for c in commands)
    assert all(not r.observations for r in pack.research_evidence if r.milestone in ("A006","A007"))
    manifest,_ = publish_pack(context.store,pack)
    assert decode_pack(manifest.read_bytes()) == pack


@pytest.mark.parametrize("mutation", ["execution_id","case_order","sentinel","unknown"])
def test_repeat_changes_execution_id_case_order_sentinel_or_unknown_field_fail(qualification_context, mutation):
    context = qualification_context
    def mutate(payload):
        if mutation == "execution_id":
            payload["cases"][0]["runs"][0]["execution_ids"].append("new-execution-identity")
        elif mutation == "case_order":
            payload["cases"].reverse()
        elif mutation == "sentinel":
            payload["cases"][:] = [c for c in payload["cases"] if c["case_id"] != "selective-routing-miss-sentinel"]
        else:
            payload["unreviewed_control"] = True
    context.runner.mutations[("P07_A010",2)] = mutate
    pack = run_portable(context)
    gate = next(g for g in pack.gates if g.gate_id == "P08_FROZEN_AUDIT")
    assert gate.status is GateStatus.FAIL and pack.portable_status is GateStatus.FAIL
    assert any(r.code in ("REPLAY_DRIFT","EVIDENCE_INVALID") for r in gate.errors)
    assert manifest_issues(pack) == ()
    assert pack_exit_code(pack) == 1


def test_only_optional_top_level_note_is_ignored(portable_payload,frozen_profile):
    payload = portable_payload("A010")
    expected = semantic_payload_sha256(payload,"A010",frozen_profile)
    payload["note"] = "Different descriptive note only"
    assert semantic_payload_sha256(payload,"A010",frozen_profile) == expected
    payload["another_note"] = "Not allowlisted"
    with pytest.raises(QualificationError):
        semantic_payload_sha256(payload,"A010",frozen_profile)


def test_a010_primary_nine_is_distinct_from_total_twelve(portable_payload,frozen_profile):
    payload = portable_payload("A010")
    assert payload["aggregate_metrics"]["case_count"] == 12
    assert payload["aggregate_metrics"]["primary_case_count"] == 9
    for key,value in frozen_profile.values["a010_primary_counts"].items():
        assert type(payload["aggregate_metrics"][key]) is int
        assert payload["aggregate_metrics"][key] == value
    sentinel = next(c for c in payload["cases"] if c["case_id"] == frozen_profile.values["a010_dense_only_sentinel"])
    results = {r["variant"]:r["procedure_success"] for r in sentinel["runs"]}
    assert results["ASCA_PRIMARY"] is False and results["DENSE_EXHAUSTIVE"] is True


@pytest.mark.parametrize("mutation", ["dirty","wrong_source","profile","missing_profile"])
def test_p00_rejects_dirty_wrong_source_or_profile_before_child_calls(qualification_context, mutation):
    context = qualification_context
    if mutation == "dirty":
        (context.repo_root/"untracked-drift.txt").write_text("drift",encoding="utf-8")
    elif mutation == "wrong_source":
        context = replace(context,expected_commit="d"*40)
    elif mutation == "profile":
        context.profile_path.write_bytes(b"{}")
    else:
        context.profile_path.unlink()
    pack = run_portable(context)
    assert context.runner.commands == []
    assert pack.gates[0].status is GateStatus.FAIL and pack.portable_status is GateStatus.FAIL
    assert all(g.status is GateStatus.NOT_RUN and g.cause_ids == ("P00_PROFILE_SOURCE",)
               for g in pack.gates[1:-1])
    assert manifest_issues(pack) == ()
    assert pack_exit_code(pack) == 1
    manifest,_ = publish_pack(context.store,pack)
    assert decode_pack(manifest.read_bytes()) == pack


def test_mid_run_source_drift_cannot_publish_pass(qualification_context):
    context = qualification_context
    def drift(command):
        if command.gate_id == "P07_A010":
            (context.repo_root/"mid-run-drift.txt").write_text("drift",encoding="utf-8")
    context.runner.hook = drift
    pack = run_portable(context)
    assert pack.portable_status is GateStatus.FAIL and pack_exit_code(pack) == 1
    assert any(r.code == "SOURCE_MISMATCH" for r in pack.errors)


@pytest.mark.parametrize("mutation", ["missing_raw","coverage"])
def test_missing_raw_or_bad_gate_coverage_fails_p09(qualification_context, mutation):
    context = qualification_context
    pack = run_portable(context)
    prefix = replace(pack,gates=pack.gates[:-1])
    if mutation == "missing_raw":
        (context.store.root/"raw/P01_TESTS/stdout.log").unlink()
    else:
        prefix = replace(prefix,gates=prefix.gates[1:])
    assert validate_completed_evidence(prefix,"P09_PACK_VALIDATION",context.store.root)


def test_final_validator_checks_completed_prefix_and_then_requires_itself_once(qualification_context):
    context = qualification_context
    pack = run_portable(context)
    assert validate_completed_evidence(replace(pack,gates=pack.gates[:-1]),
        "P09_PACK_VALIDATION",context.store.root) == ()
    assert validate_completed_evidence(pack,"P09_PACK_VALIDATION",context.store.root)
    assert manifest_issues(replace(pack,gates=pack.gates[:-1]))
    with pytest.raises(QualificationError):
        validate_completed_evidence(pack,"P00_PROFILE_SOURCE",context.store.root)


def test_pytest_tests_never_spawn_real_nested_pytest(qualification_context,monkeypatch):
    context = qualification_context
    actual = subprocess.run
    def guarded(argv,*args,**kwargs):
        assert not ("-m" in argv and "pytest" in argv), "real nested pytest"
        return actual(argv,*args,**kwargs)
    monkeypatch.setattr(subprocess,"run",guarded)
    assert run_portable(context).portable_status is GateStatus.PASS


def test_p00_rejects_package_version_drift_before_child_calls(qualification_context):
    context = qualification_context
    path = context.repo_root/"pyproject.toml"
    data = path.read_text(encoding="utf-8")
    assert 'version = "0.1.0.dev0"' in data
    path.write_text(data.replace('version = "0.1.0.dev0"','version = "0.1.0"'),encoding="utf-8")
    subprocess.run(["git","-c","user.name=A011 tests","-c","user.email=a011@example.invalid",
        "commit","-am","Test committed metadata drift"],cwd=context.repo_root,capture_output=True,check=True)
    commit = subprocess.run(["git","rev-parse","HEAD"],cwd=context.repo_root,capture_output=True,check=True).stdout.decode().strip()
    context = replace(context,expected_commit=commit)
    pack = run_portable(context)
    assert context.runner.commands == []
    assert pack.portable_status is GateStatus.FAIL
    assert any(r.code == "IDENTITY_DRIFT" for r in pack.errors)


def test_cli_requires_exact_source_and_exposes_no_retuning_controls(tmp_path):
    import importlib.util
    script = Path(__file__).resolve().parents[2]/"scripts/qualify_asca_v0x_a011.py"
    spec = importlib.util.spec_from_file_location("a011_portable_cli_test",script)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert module.main(["--expected-source-sha","abbreviated"]) == 1
    assert module.main(["--expected-source-sha","c"*40,"--repo-root",str(tmp_path)]) == 1
    for option in ("--threshold","--model","--calibrate","--accept-current"):
        with pytest.raises(SystemExit) as exc:
            module.main(["--expected-source-sha","c"*40,option,"override"])
        assert exc.value.code == 1
