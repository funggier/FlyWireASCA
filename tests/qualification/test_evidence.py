from dataclasses import replace
import ast
import importlib.util
import json
from pathlib import Path
import sys
import pytest
from flywire_asca.qualification.process import CommandSpec, ProcessEvidence
from flywire_asca.qualification.evidence import normalize_child, semantic_payload_sha256
from flywire_asca.qualification.records import GateStatus, QualificationError

ROOT = Path(__file__).resolve().parents[2]


def raw(payload):
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()


def child(tmp_path, gate_id, payload, exit_code=0, output=True):
    command = CommandSpec(gate_id, ("python", "child") + (("--qualify",) if gate_id=="P04_A003" else ()),
        tmp_path, tmp_path/"output.json" if output else None, None)
    data = raw(payload) if isinstance(payload, dict) else payload
    return ProcessEvidence(command, "2026-10-10T10:00:00Z", "2026-10-10T10:00:01Z",
                           exit_code, data, b"", None)


@pytest.fixture
def validators():
    path = ROOT/"scripts/_a011_legacy_evidence.py"
    spec = importlib.util.spec_from_file_location("_a011_bridge_test", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.load_legacy_validators(ROOT)


@pytest.mark.parametrize("milestone,gate,outcome", [
    ("A008","P05_A008","SUPPORTED"),("A009","P06_A009","SUPPORTED"),("A010","P07_A010","NOT_SUPPORTED")])
def test_real_portable_payloads_retain_frozen_outcomes(tmp_path, portable_payload, frozen_profile, validators, milestone, gate, outcome):
    payload = portable_payload(milestone)
    result = normalize_child(gate, child(tmp_path,gate,payload), raw(payload), frozen_profile, validators[milestone])
    assert result.status is GateStatus.PASS
    assert result.observation.outcome.value == outcome
    assert result.payload["aggregate_metrics"] == payload["aggregate_metrics"]
    assert result.semantic_sha256 == frozen_profile.values["portable_payloads"][milestone]["semantic_sha256"]


@pytest.mark.parametrize("invalid", [b'{"x":', b'{"experiment_valid":true,"experiment_valid":false}', None])
def test_zero_exit_truncated_duplicate_key_or_missing_output_fails(tmp_path, frozen_profile, invalid):
    evidence = child(tmp_path,"P05_A008",b'{}')
    result = normalize_child("P05_A008",evidence,invalid,frozen_profile,lambda p: ())
    assert result.status is GateStatus.FAIL
    assert any(e.code == "EVIDENCE_INVALID" for e in result.errors)


@pytest.mark.parametrize("mutation", ["exit", "flag", "errors", "validator"])
def test_exit_success_flag_and_validator_must_all_agree(tmp_path, portable_payload, frozen_profile, mutation):
    payload = portable_payload("A008")
    if mutation == "flag":
        payload["experiment_valid"] = False
    if mutation == "errors":
        payload["errors"] = ["rejected"]
    evidence = child(tmp_path,"P05_A008",payload,exit_code=1 if mutation=="exit" else 0)
    validator = lambda p: ("validator rejected",) if mutation=="validator" else ()
    assert normalize_child("P05_A008",evidence,raw(payload),frozen_profile,validator).status is GateStatus.FAIL


def test_stdout_and_json_artifact_must_agree(tmp_path, portable_payload, frozen_profile):
    payload = portable_payload("A008")
    evidence = child(tmp_path,"P05_A008",payload)
    payload["note"] = "changed stdout/file"
    assert normalize_child("P05_A008",evidence,raw(payload),frozen_profile,lambda p: ()).status is GateStatus.FAIL


def test_a003_uses_json_exit_contract_without_invented_marker(tmp_path, frozen_profile):
    from flywire_asca.familiarity import build_a003_qualification_fixture, run_familiarity_benchmark
    from flywire_asca.familiarity import benchmark_report_payload
    traces,cases = build_a003_qualification_fixture()
    payload = benchmark_report_payload(run_familiarity_benchmark(traces,cases))
    evidence = child(tmp_path,"P04_A003",payload,output=False)
    assert "--qualify" in evidence.command.argv and "--output" not in evidence.command.argv
    assert normalize_child("P04_A003",evidence,None,frozen_profile,None).status is GateStatus.PASS
    assert normalize_child("P04_A003",replace(evidence,exit_code=1),None,frozen_profile,None).status is GateStatus.FAIL
    for invalid in (b'[]', b'{} junk'):
        assert normalize_child("P04_A003",replace(evidence,stdout=invalid),None,frozen_profile,None).status is GateStatus.FAIL


def test_a005_checks_observed_vector_health_dimension(tmp_path, physical_payload, frozen_profile):
    payload = physical_payload("H02_A005")
    assert normalize_child("H02_A005",child(tmp_path,"H02_A005",payload),raw(payload),frozen_profile,None).status is GateStatus.PASS
    payload["vector_health"]["dimension"] = 768
    result = normalize_child("H02_A005",child(tmp_path,"H02_A005",payload),raw(payload),frozen_profile,None)
    assert result.status is GateStatus.FAIL
    assert any(e.code == "IDENTITY_DRIFT" for e in result.errors)


@pytest.mark.parametrize("gate", ["H05_A009","H06_A010"])
@pytest.mark.parametrize("flag", ["physical_prerequisites_valid","physical_integration_valid"])
@pytest.mark.parametrize("value", [False,None])
def test_a009_a010_require_both_physical_validity_flags(tmp_path, physical_payload, frozen_profile, gate, flag, value):
    payload = physical_payload(gate)
    if value is None:
        del payload[flag]
    else:
        payload[flag] = value
    assert normalize_child(gate,child(tmp_path,gate,payload),raw(payload),frozen_profile,None).status is GateStatus.FAIL


@pytest.mark.parametrize("gate", ["H01_A004","H03_A006","H04_A007","H05_A009","H06_A010"])
def test_valid_physical_fixture_uses_pure_legacy_validator(tmp_path, physical_payload, frozen_profile, validators, gate):
    payload = physical_payload(gate)
    validator = validators.get({"H03_A006":"A006","H04_A007":"A007"}.get(gate))
    assert normalize_child(gate,child(tmp_path,gate,payload),raw(payload),frozen_profile,validator).status is GateStatus.PASS


def test_qualification_package_does_not_load_scripts_or_cognitive_modules():
    allowed = {"contracts", "qualification"}
    for path in (ROOT/"src/flywire_asca/qualification").glob("*.py"):
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            imports = [a.name for a in node.names] if isinstance(node,ast.Import) else [node.module or ""] if isinstance(node,ast.ImportFrom) else []
            for name in imports:
                assert not name.startswith("scripts")
                assert not name.startswith("importlib")
                if name.startswith("flywire_asca."):
                    assert name.split(".")[1] in allowed


def test_stdout_file_agreement_preserves_exact_json_primitive_types(tmp_path, portable_payload, frozen_profile, validators):
    payload = portable_payload("A008")
    evidence = child(tmp_path,"P05_A008",payload)
    payload["experiment_valid"] = 1
    result = normalize_child("P05_A008",evidence,raw(payload),frozen_profile,validators["A008"])
    assert result.status is GateStatus.FAIL


def test_a003_case_claims_must_agree_with_success_summary(tmp_path, frozen_profile):
    from flywire_asca.familiarity import benchmark_report_payload, build_a003_qualification_fixture, run_familiarity_benchmark
    traces,cases = build_a003_qualification_fixture()
    payload = benchmark_report_payload(run_familiarity_benchmark(traces,cases))
    payload["case_results"][0]["classification_correct"] = False
    evidence = child(tmp_path,"P04_A003",payload,output=False)
    assert normalize_child("P04_A003",evidence,None,frozen_profile,None).status is GateStatus.FAIL


def test_missing_output_references_retained_stdout_diagnostics(tmp_path, frozen_profile):
    evidence = child(tmp_path,"H01_A004",b"",exit_code=1)
    result = normalize_child("H01_A004",evidence,None,frozen_profile,None)
    assert all("stdout.log" in ref for reason in result.errors for ref in reason.evidence_refs)


def test_nonzero_diagnostic_variant_never_passes_or_invents_identity_drift(tmp_path, frozen_profile):
    payload = {"qualification_scope":"physical_integrated_cognitive_loop_a009",
        "fixture_version":"a009-physical-v1", "portable_primary_outcome":"SUPPORTED",
        "physical_prerequisites_valid":False, "errors":["transport diagnostic"]}
    evidence = child(tmp_path,"H05_A009",payload,exit_code=1)
    result = normalize_child("H05_A009",evidence,raw(payload),frozen_profile,None)
    assert result.status is GateStatus.FAIL
    assert result.observation is None
    assert all(r.code == "QUALIFIER_FAILED" for r in result.errors)

@pytest.mark.parametrize("gate,milestone", [("H03_A006","A006"),("H04_A007","A007")])
def test_actual_flattened_physical_cli_contract(tmp_path,physical_payload,frozen_profile,validators,gate,milestone):
    payload = physical_payload(gate)
    if "experiment" in payload:
        payload.update(payload.pop("experiment"))
    result = normalize_child(gate,child(tmp_path,gate,payload),raw(payload),frozen_profile,validators[milestone])
    assert result.status is GateStatus.PASS
    assert result.observation.outcome.value == frozen_profile.values["research_outcomes"][milestone]

@pytest.mark.parametrize("contradiction", ["case_count","passed_count","pass_rate","per_case"])
def test_a004_baseline_success_requires_actual_legacy_acceptance(tmp_path,physical_payload,frozen_profile,contradiction):
    payload = physical_payload("H01_A004")
    baseline = payload["baseline"]
    if contradiction == "case_count": baseline["case_count"] = 1
    if contradiction == "passed_count": baseline["passed_case_count"] = 0
    if contradiction == "pass_rate": baseline["pass_rate"] = 0.0
    if contradiction == "per_case": baseline["case_results"] = [{"case_id":"bad","passed":False}]
    result = normalize_child("H01_A004",child(tmp_path,"H01_A004",payload),raw(payload),frozen_profile,None)
    assert result.status is GateStatus.FAIL
