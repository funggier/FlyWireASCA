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

# Test-only evidence factories. These never claim physical hardware freshness.
from collections import deque
import importlib.util
from pathlib import Path
import sys
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]

POST_A011_COGNITIVE_PATHS = (
    "src/flywire_asca/relational_reasoning",
)


def _prepare_frozen_a011_candidate(root: Path) -> str:
    """Turn a post-A011 clone into the exact frozen A011 cognitive source universe.

    A011 intentionally rejects any additional non-qualification cognitive Python
    package. Later milestones therefore must not be treated as A011 candidates.
    Historical A011 tests use this synthetic commit inside their temporary clone
    instead of weakening the production provenance guard.
    """
    subprocess.run(
        ["git", "config", "user.email", "a011-tests@example.invalid"],
        cwd=root,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "A011 frozen fixture"],
        cwd=root,
        check=True,
        capture_output=True,
    )
    for relative in POST_A011_COGNITIVE_PATHS:
        subprocess.run(
            ["git", "rm", "-r", "-f", "--ignore-unmatch", "--", relative],
            cwd=root,
            check=True,
            capture_output=True,
        )
    staged = subprocess.run(
        ["git", "diff", "--cached", "--quiet"],
        cwd=root,
        check=False,
        capture_output=True,
    )
    if staged.returncode not in (0, 1):
        raise RuntimeError("cannot inspect frozen A011 fixture staging state")
    if staged.returncode == 1:
        subprocess.run(
            ["git", "commit", "-m", "Test fixture: frozen A011 cognitive source"],
            cwd=root,
            check=True,
            capture_output=True,
        )
    return subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=root,
        check=True,
        capture_output=True,
    ).stdout.decode("ascii").strip()


@pytest.fixture(name="prepare_frozen_a011_candidate")
def prepare_frozen_a011_candidate_fixture():
    return _prepare_frozen_a011_candidate


def legacy_module(filename):
    name = "_a011_test_" + filename.replace(".", "_")
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / filename)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _portable_payload(milestone):
    filename = {"A008": "qualify_procedural_memory_a008.py",
                "A009": "qualify_integrated_loop_a009.py",
                "A010": "qualify_baseline_comparison_a010.py"}[milestone]
    module = legacy_module(filename)
    payload = module.run_qualification()
    assert not module.validate_qualification_payload(payload)
    return payload


def _physical_payload(gate_id):
    from flywire_asca.qualification.profile import DEFAULT_PROFILE_PATH, load_frozen_profile
    values = load_frozen_profile((ROOT / DEFAULT_PROFILE_PATH).read_bytes()).values
    model = {"name": values["embedding"]["model"], "digest": values["embedding"]["digest"],
             "embedding_dimension": 1024}
    threshold = values["a005_threshold"]
    if gate_id == "H01_A004":
        return {"qualification_scope": "local_physical_qwen_a004",
            "qualified": True, "errors": [],
            "model": {"name": values["terminal"]["model"], "digest": values["terminal"]["digest"]},
            "generation_profile": {"thinking": False, "tools": False, "vision": False,
                                   "profile_name": "qwen3.5-4b-thinking-off-v1"},
            "baseline": {"case_count": 6, "passed_case_count": 6, "pass_rate": 1.0,
                         "case_results": [{"case_id":c.case_id,"passed":True} for c in
                             legacy_module("qualify_qwen_a004.py").build_qwen_a004_baseline_cases()]}}
    if gate_id == "H02_A005":
        # Synthetic accepted evidence from the unchanged eight physical cases;
        # no embedding execution and no claim of hardware freshness.
        from flywire_asca.vector_memory.benchmark import (
            VectorMemoryBenchmarkCaseResult, VectorMemoryBenchmarkReport,
            benchmark_report_payload,
        )
        module = legacy_module("qualify_vector_memory_a005.py")
        documents, cases = module.build_physical_qualification_fixture(threshold)
        results = tuple(VectorMemoryBenchmarkCaseResult(
            case.case_id, case.relevant_memory_ids, case.relevant_memory_ids,
            1.0 if case.relevant_memory_ids and case.require_recall_at_1 else None,
            1.0 if case.relevant_memory_ids else None,
            1.0 if case.relevant_memory_ids else None,
            True if not case.relevant_memory_ids else None,
            True if case.metadata_filter_expected else None,
            0, True, False, False, len(documents),
            1 if case.metadata_filter_expected else len(documents),
            1 if case.metadata_filter_expected else len(documents),
            len(case.relevant_memory_ids), len(case.relevant_memory_ids),
        ) for case in cases)
        report = VectorMemoryBenchmarkReport(
            "controlled_fixture_only", threshold, "physical_frozen_threshold_v1",
            results, len(results), 1.0, 1.0, 1.0, 1.0, 1.0,
            0, 0, 0, 0, len(documents),
            sum(case.scored_vector_count for case in results), len(cases)+1,
            len(documents)+len(cases), model["name"], model["digest"],
            module.PROFILE_NAME,
        )
        calibration = module.build_physical_calibration_fixture()[1]
        return {"qualification_scope": "local_physical_vector_memory_a005",
            "mode": "qualification", "experiment_valid": True, "retrieval_qualified": True,
            "errors": [], "model": model, "physical_threshold": threshold,
            "threshold_origin": "physical_frozen_threshold_v1",
            "benchmark": benchmark_report_payload(report),
            "qualification_case_ids": [case.case_id for case in cases],
            "calibration_case_ids": [case.case_id for case in calibration],
            "vector_health": {"dimension": 1024, "zero_vector_count": 0, "nonfinite_vector_count": 0}}
    if gate_id in ("H03_A006", "H04_A007"):
        milestone = "A006" if gate_id == "H03_A006" else "A007"
        filename = "qualify_selective_activation_a006.py" if milestone == "A006" else "qualify_uncertainty_expansion_a007.py"
        module = legacy_module(filename)
        payload = module._base_payload(descriptor=None, experiment_valid=True, errors=[])
        payload["model"] = model
        cases = module.build_physical_fixture()
        metrics = {"embedding_request_count": 2, "embedding_input_count": 3,
                   "prompt_tokens_total": 12, "prompt_tokens_observed_response_count": 2,
                   "total_duration_ns_total": 100, "total_duration_observed_response_count": 2,
                   "load_duration_ns_total": 20, "load_duration_observed_response_count": 2}
        if milestone == "A006":
            experiment = {"fixture_version": module.FIXTURE_VERSION,
                "fixture_fingerprint": values["fixture_fingerprints"][milestone],
                "case_ids": [case.case_id for case in cases], "required_memory_coverage": 1.0,
                "convergence_recovery_count": 0, "convergence_regression_count": 0,
                "ambiguity_failure_count": 0, "no_selection_failure_count": 0,
                "strict_budget_observation_count": sum(int(case.strict_budget_expected) for case in cases),
                "total_positive_candidates": 10, "total_selected_items": 5,
                "active_state_reduction_ratio": 0.5, "deterministic_repeat_match": True,
                "embedding_metrics": metrics, "cases": [],
                "hypothesis_outcome": "NOT_SUPPORTED", "experiment_valid": True}
        else:
            scopes = module.build_a007_primary_profile().scopes
            def metric(requests, inputs):
                return {**metrics, "embedding_request_count": requests, "embedding_input_count": inputs,
                        "prompt_tokens_observed_response_count": requests,
                        "total_duration_observed_response_count": requests,
                        "load_duration_observed_response_count": requests}
            experiment = {"fixture_version": module.FIXTURE_VERSION,
                "fixture_fingerprint": values["fixture_fingerprints"][milestone],
                "case_ids": [case.case_id for case in cases], "selector": "SINGLE_BEST",
                "threshold": threshold, "profile": [{"round_index": s.round_index,
                    "enabled_cue_tier_count": s.enabled_cue_tier_count, "top_k": s.top_k,
                    "max_memory_nodes": s.budget.max_memory_nodes,
                    "max_working_set_items": s.budget.max_working_set_items} for s in scopes],
                "required_memory_coverage": {"NO_EXPANSION": 0.5, "SIGNAL_DRIVEN": 1.0, "ALWAYS_EXPAND": 1.0},
                "signal_driven_recovery_count": 1, "signal_driven_regression_count": 0,
                "easy_unnecessary_expansion_count": 0, "persistent_insufficient_expected_count": 1,
                "persistent_insufficient_exhausted_count": 1, "ambiguity_failure_count": 0,
                "deterministic_repeat_match": True,
                "total_rounds": {"NO_EXPANSION": len(cases), "SIGNAL_DRIVEN": len(cases)+1,
                                 "ALWAYS_EXPAND": len(cases)*3},
                "setup_embedding_metrics": metric(8,24),
                "policy_embedding_metrics": {"NO_EXPANSION": metric(8,8),
                    "SIGNAL_DRIVEN": metric(9,9), "ALWAYS_EXPAND": metric(24,24)},
                "cases": [], "hypothesis_outcome": "SUPPORTED", "experiment_valid": True}
        assert not module.validate_physical_experiment(experiment)
        payload.update(experiment)
        return payload
    milestone = "A009" if gate_id == "H05_A009" else "A010"
    metadata = {"embedding_model": values["embedding"]["model"],
                "embedding_digest": values["embedding"]["digest"],
                "embedding_dimension": 1024, "minimum_similarity": threshold}
    if milestone == "A009":
        metadata.update({"terminal_model": values["terminal"]["model"],
            "terminal_model_digest": values["terminal"]["digest"],
            "terminal_model_invoked": True, "terminal_model_request_count": 1,
            "primary_selector": "SINGLE_BEST", "primary_procedure_mode": "CHUNKED"})
    details = {"physical_integration": {
        "success_case_completed": True, "success_case_attempt_count": 1,
        "success_case_scope_count": 1, "success_case_final_working_set_ids": ["mem-physical"],
        "fallback_case_exhausted": True, "fallback_case_attempt_count": 3,
        "fallback_case_scope_count": 3, "terminal_model_invoked": True,
        "terminal_model_request_count": 1, "terminal_model_response_nonempty": True,
        "terminal_model_prompt_tokens": 20, "terminal_model_generated_tokens": 10,
        "terminal_model_total_duration_ns": 100,
    }} if milestone == "A009" else {"physical_comparison": {
        variant: {"procedure_success": True, "final_state_correct": True,
            "query_count": 1 if variant == "asca" else 3, "scored_vector_count": 3,
            "cumulative_selected_count": 3, "peak_selected_count": 3,
            "procedure_attempt_count": 1, "final_selected_memory_ids": ["mem-000-target"],
            "runner_duration_ns": 100} for variant in ("asca", "dense")}}
    return {"qualification_scope": "physical_integrated_cognitive_loop_a009" if milestone == "A009"
            else "physical_dense_nonselective_baseline_a010", "fixture_version": milestone.lower()+"-physical-v1",
            "portable_primary_outcome": values["research_outcomes"][milestone],
            "physical_metadata": metadata, "physical_prerequisites_valid": True,
            "physical_integration_valid": True, "errors": [], **details}


class FakeRunner:
    def __init__(self, responses=()):
        self.responses = deque(responses)
        self.commands = []

    def run(self, command):
        self.commands.append(command)
        response = self.responses.popleft()
        return response(command) if callable(response) else replace(response, command=command)


@pytest.fixture(name="portable_payload")
def portable_payload_fixture():
    return _portable_payload


@pytest.fixture(name="physical_payload")
def physical_payload_fixture():
    return _physical_payload


@pytest.fixture(name="frozen_profile")
def frozen_profile_fixture():
    from flywire_asca.qualification.profile import DEFAULT_PROFILE_PATH, load_frozen_profile
    return load_frozen_profile((ROOT / DEFAULT_PROFILE_PATH).read_bytes())

# Shared clean local clone and injected child runner for Tasks 6-7.
import json
import subprocess
from collections import Counter


class SystemFakeRunner:
    def __init__(self):
        self.commands = []
        self.seen = Counter()
        self.mutations = {}
        self.hook = None
        self.responses = {}

    def run(self, command):
        from flywire_asca.qualification.process import ProcessEvidence
        self.commands.append(command)
        if command.gate_id in self.responses:
            response = self.responses[command.gate_id]
            return response(command) if callable(response) else replace(response,command=command)
        gate = command.gate_id
        self.seen[gate] += 1
        if gate == "P01_TESTS":
            stdout = b"884 passed in 0.1s\n"
        elif gate == "P02_ARCHITECTURE":
            stdout = b"architecture_contract_audit=PASS\n"
        elif gate == "P03_REPOSITORY":
            stdout = b"repository_qualification=PASS\n"
        else:
            if gate == "P04_A003":
                module = legacy_module("run_familiarity_benchmark_a003.py")
                traces,cases = module.build_a003_qualification_fixture()
                payload = module.benchmark_report_payload(module.run_familiarity_benchmark(traces,cases))
            elif gate.startswith("P"):
                payload = _portable_payload({"P05_A008":"A008","P06_A009":"A009","P07_A010":"A010"}[gate])
            else:
                payload = _physical_payload(gate)
            if (gate,self.seen[gate]) in self.mutations:
                self.mutations[(gate,self.seen[gate])](payload)
            stdout = json.dumps(payload,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()
            if command.output_path is not None:
                command.output_path.parent.mkdir(parents=True,exist_ok=True)
                command.output_path.write_bytes(stdout)
        if self.hook:
            self.hook(command)
        now = datetime.now(timezone.utc).isoformat()
        return ProcessEvidence(command,now,now,0,stdout,b"",None)


@pytest.fixture
def qualification_context(tmp_path):
    from flywire_asca.qualification.artifacts import ArtifactStore
    from flywire_asca.qualification.portable import RunContext
    from flywire_asca.qualification.profile import DEFAULT_PROFILE_PATH
    root = tmp_path/"candidate"
    result = subprocess.run(["git","-c","core.autocrlf=false","clone","--depth=1",
        "--no-tags",ROOT.as_uri(),str(root)],capture_output=True)
    assert result.returncode == 0, result.stderr
    commit = _prepare_frozen_a011_candidate(root)
    assert not (root/"src"/"flywire_asca"/"relational_reasoning").exists()
    runner = SystemFakeRunner()
    bridge = legacy_module("_a011_legacy_evidence.py")
    context = RunContext(root,commit,root/DEFAULT_PROFILE_PATH,
                         ArtifactStore.create(root,tmp_path/"pack"),runner,bridge.load_legacy_validators(root))
    return context
