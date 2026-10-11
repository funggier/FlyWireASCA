from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import shutil
import subprocess

from flywire_asca.model import ModelDescriptor, ModelResponse
from flywire_asca.structural_routing.benchmark_fixture import build_a014_frozen_fixture


ROOT = Path(__file__).resolve().parents[1]
PHYSICAL_SCRIPT = ROOT / "scripts" / "qualify_structural_routing_a014_physical.py"
VERIFY_SCRIPT = ROOT / "scripts" / "verify_a014_physical_evidence.py"


def _load(path: Path, name: str):
    assert path.exists()
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class _FakePhysicalAdapter:
    def __init__(self, physical_module, *, digest=None, name=None):
        self.m = physical_module
        self.digest = digest or physical_module.EXPECTED_DIGEST
        self.name = name or physical_module.MODEL_NAME
        self.inspect_calls = 0
        self.generate_calls = []
        self.mapping = {}
        for case in build_a014_frozen_fixture():
            need = case.expected_structural_need
            self.mapping[case.query_text] = json.dumps(
                {
                    "requires_relation": need.active,
                    "required_relations": [r.value for r in need.required_relations],
                    "requires_path_provenance": need.requires_path_provenance,
                },
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            )

    def inspect(self):
        self.inspect_calls += 1
        return ModelDescriptor(
            backend_name="ollama",
            backend_version="fixture-1",
            model_name=self.name,
            model_digest=self.digest,
            architecture="qwen35",
            parameter_count=4_659_865_088,
            parameter_size="4.7B",
            quantization="Q4_K_M",
            context_length=32768,
            embedding_length=2560,
            capabilities=("completion", "thinking"),
        )

    def generate(self, request):
        self.generate_calls.append(request)
        query = request.messages[-1].content
        return ModelResponse(
            request_id=request.request_id,
            model_name=self.name,
            model_digest=self.digest,
            content=self.mapping[query],
            finish_reason="stop",
            prompt_tokens=10,
            generated_tokens=5,
            total_duration_ns=100,
            load_duration_ns=1,
            prompt_eval_duration_ns=2,
            eval_duration_ns=3,
        )


def _run_git(root: Path, *args: str) -> str:
    result = subprocess.run(["git", *args], cwd=root, capture_output=True, text=True, check=True)
    return result.stdout.strip()


def _source_repo(tmp_path: Path) -> tuple[Path, str]:
    root = tmp_path / "repo"
    (root / "src" / "flywire_asca").mkdir(parents=True)
    shutil.copytree(
        ROOT / "src" / "flywire_asca" / "structural_routing",
        root / "src" / "flywire_asca" / "structural_routing",
    )
    (root / "scripts").mkdir()
    shutil.copy2(ROOT / "scripts" / "qualify_structural_routing_a014.py", root / "scripts")
    shutil.copy2(PHYSICAL_SCRIPT, root / "scripts")
    _run_git(root, "init")
    _run_git(root, "config", "user.email", "a014@example.invalid")
    _run_git(root, "config", "user.name", "A014 Test")
    _run_git(root, "add", ".")
    _run_git(root, "commit", "-m", "fixture")
    return root, _run_git(root, "rev-parse", "HEAD")


def test_source_manifest_is_git_bound_and_fingerprinted(tmp_path):
    m = _load(PHYSICAL_SCRIPT, "a014physical_manifest")
    root, head = _source_repo(tmp_path)
    manifest = m.a014_source_manifest(root=root, ref=head)
    paths = tuple(item[1] for item in manifest)
    assert paths == tuple(sorted(paths))
    assert "scripts/qualify_structural_routing_a014.py" in paths
    assert "scripts/qualify_structural_routing_a014_physical.py" in paths
    assert any(path.startswith("src/flywire_asca/structural_routing/") for path in paths)
    fingerprint = m.a014_source_manifest_fingerprint(root=root, ref=head)
    assert len(fingerprint) == 64
    assert int(fingerprint, 16) >= 0


def test_physical_runner_rejects_expected_source_sha_mismatch_before_model_scoring(tmp_path):
    m = _load(PHYSICAL_SCRIPT, "a014physical_sha")
    root, head = _source_repo(tmp_path)
    adapter = _FakePhysicalAdapter(m)
    payload = m.run_physical_qualification(
        adapter=adapter, expected_source_sha="0" * 40, root=root
    )
    assert payload["experiment_valid"] is False
    assert any("source SHA" in error for error in payload["errors"])
    assert adapter.inspect_calls == 0
    assert adapter.generate_calls == []
    assert head != "0" * 40


def test_physical_runner_rejects_pinned_model_mismatch_before_generation(tmp_path):
    m = _load(PHYSICAL_SCRIPT, "a014physical_identity")
    root, head = _source_repo(tmp_path)
    adapter = _FakePhysicalAdapter(m, digest="wrong-digest")
    payload = m.run_physical_qualification(adapter=adapter, expected_source_sha=head, root=root)
    assert payload["experiment_valid"] is False
    assert any("digest" in error.lower() for error in payload["errors"])
    assert adapter.inspect_calls == 1
    assert adapter.generate_calls == []


def test_fake_physical_run_preserves_raw_outputs_and_derives_bound_decision(tmp_path):
    m = _load(PHYSICAL_SCRIPT, "a014physical_valid")
    root, head = _source_repo(tmp_path)
    adapter = _FakePhysicalAdapter(m)
    payload = m.run_physical_qualification(adapter=adapter, expected_source_sha=head, root=root)
    assert payload["experiment_valid"] is True
    assert payload["source"]["git_sha"] == head
    assert payload["source"]["manifest_fingerprint"] == m.a014_source_manifest_fingerprint(root=root, ref=head)
    assert payload["fixture_fingerprint"] == "c100f828265063c369d535f85db8166cbeaaba26943fbb6d276a24dc46018eca"
    assert payload["model"]["name"] == m.MODEL_NAME
    assert payload["model"]["digest"] == m.EXPECTED_DIGEST
    assert payload["benchmark"]["physical_evidence_bound"] is True
    assert payload["physical_architecture_decision"] == "HYBRID_STRUCTURAL_ROUTING_JUSTIFIED"
    assert adapter.inspect_calls == 1
    assert len(adapter.generate_calls) == 41
    raw_outputs = [
        item["raw_model_output"]
        for item in payload["benchmark"]["cases"]
        if item["model_invoked"]
    ]
    assert len(raw_outputs) == 41
    assert all(output and output.startswith("{") for output in raw_outputs)


def test_verifier_accepts_valid_fake_physical_payload_and_rejects_tampering(tmp_path):
    p = _load(PHYSICAL_SCRIPT, "a014physical_for_verify")
    v = _load(VERIFY_SCRIPT, "a014verify")
    root, head = _source_repo(tmp_path)
    payload = p.run_physical_qualification(
        adapter=_FakePhysicalAdapter(p), expected_source_sha=head, root=root
    )
    assert v.verify_payload(payload, root=root) == []

    tampered = json.loads(json.dumps(payload))
    tampered["benchmark"]["policy_metrics"][0]["downstream_success_count"] += 1
    assert v.verify_payload(tampered, root=root)

    tampered = json.loads(json.dumps(payload))
    tampered["physical_architecture_decision"] = "MODEL_ROUTING_PREFERRED"
    assert v.verify_payload(tampered, root=root)

    tampered = json.loads(json.dumps(payload))
    tampered["fixture_fingerprint"] = "0" * 64
    assert v.verify_payload(tampered, root=root)

    tampered = json.loads(json.dumps(payload))
    tampered["prompt_fingerprint"] = "0" * 64
    assert v.verify_payload(tampered, root=root)

    tampered = json.loads(json.dumps(payload))
    tampered["source"]["manifest_fingerprint"] = "0" * 64
    assert v.verify_payload(tampered, root=root)


def test_verifier_missing_evidence_file_exits_nonzero(tmp_path):
    v = _load(VERIFY_SCRIPT, "a014verify_missing")
    missing = tmp_path / "missing.json"
    assert v.main([str(missing)]) == 1

def _rehash_physical_payload(physical_module, payload):
    payload.pop("physical_evidence_sha256", None)
    payload["physical_evidence_sha256"] = physical_module._canonical_sha(payload)
    return payload


def test_verifier_reconstructs_raw_case_semantics_and_checks_evidence_sha(tmp_path):
    p = _load(PHYSICAL_SCRIPT, "a014physical_semantic_verify")
    v = _load(VERIFY_SCRIPT, "a014verify_semantic")
    root, head = _source_repo(tmp_path)
    payload = p.run_physical_qualification(
        adapter=_FakePhysicalAdapter(p), expected_source_sha=head, root=root
    )
    assert v.verify_payload(payload, root=root) == []

    stale_hash = json.loads(json.dumps(payload))
    stale_hash["physical_evidence_sha256"] = "0" * 64
    assert v.verify_payload(stale_hash, root=root)

    raw_mismatch = json.loads(json.dumps(payload))
    raw_case = next(
        item
        for item in raw_mismatch["benchmark"]["cases"]
        if item["model_invoked"] and item["inferred_structural_need"]["required_relations"]
    )
    raw_case["raw_model_output"] = json.dumps(
        {
            "requires_relation": False,
            "required_relations": [],
            "requires_path_provenance": False,
        },
        separators=(",", ":"),
    )
    _rehash_physical_payload(p, raw_mismatch)
    assert v.verify_payload(raw_mismatch, root=root)

    outcome_mismatch = json.loads(json.dumps(payload))
    outcome_case = next(
        item
        for item in outcome_mismatch["benchmark"]["cases"]
        if item["policy"] == "MODEL_ONLY"
        and item["task_success"]
        and item["found_expected_ids"]
    )
    outcome_case["final_selected_ids"] = []
    _rehash_physical_payload(p, outcome_mismatch)
    assert v.verify_payload(outcome_mismatch, root=root)
