from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

from flywire_asca.model import (
    ModelDescriptor,
    ModelRequest,
    ModelResponse,
)


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "qualify_qwen_a004.py"
TARGET_DIGEST = "2a654d98e6fba55d452b7043684e9b57a947e393bbffa62485a7aac05ee4eefd"


def _load_module():
    assert SCRIPT.exists(), "qualification script must exist"
    spec = importlib.util.spec_from_file_location("qualify_qwen_a004", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _descriptor(*, digest: str = TARGET_DIGEST):
    return ModelDescriptor(
        backend_name="ollama",
        backend_version="0.32.15",
        model_name="qwen3.5:4b",
        model_digest=digest,
        architecture="qwen35",
        parameter_count=4659865088,
        parameter_size="4.7B",
        quantization="Q4_K_M",
        context_length=262144,
        embedding_length=2560,
        capabilities=("completion", "thinking", "tools", "vision"),
    )


class FakeAdapter:
    outputs = {
        "a004-english-exact": "BLUE",
        "a004-thai-exact": "แมว",
        "a004-context-selection": "29",
        "a004-context-middle": "green",
        "a004-insufficient-context": "INSUFFICIENT_CONTEXT",
        "a004-boolean-allowed": "yes",
    }
    descriptor = _descriptor()

    def __init__(self, model_name, **kwargs):
        self.model_name = model_name
        self.kwargs = kwargs
        self.requests: list[ModelRequest] = []

    def inspect(self):
        return self.descriptor

    def generate(self, request):
        self.requests.append(request)
        return ModelResponse(
            request_id=request.request_id,
            model_name=self.descriptor.model_name,
            model_digest=self.descriptor.model_digest,
            content=self.outputs[request.request_id],
            finish_reason="stop",
            prompt_tokens=10,
            generated_tokens=2,
            total_duration_ns=100,
            load_duration_ns=10,
            prompt_eval_duration_ns=20,
            eval_duration_ns=70,
        )


def test_payload_contains_identity_generation_profile_and_backend_metrics():
    module = _load_module()
    adapter = FakeAdapter("qwen3.5:4b")
    report = module.run_model_baseline(
        adapter,
        module.build_qwen_a004_baseline_cases(),
        profile_name=module.PROFILE_NAME,
    )
    payload = module.build_qualification_payload(adapter.inspect(), report)

    assert payload["qualification_scope"] == "local_physical_qwen_a004"
    assert payload["qualified"] is True
    assert payload["errors"] == []
    assert payload["runtime"]["backend_name"] == "ollama"
    assert payload["runtime"]["backend_version"] == "0.32.15"
    assert payload["model"] == {
        "name": "qwen3.5:4b",
        "digest": TARGET_DIGEST,
        "architecture": "qwen35",
        "parameter_count": 4659865088,
        "parameter_size": "4.7B",
        "quantization": "Q4_K_M",
        "context_length": 262144,
        "embedding_length": 2560,
        "capabilities": ["completion", "thinking", "tools", "vision"],
    }
    assert payload["generation_profile"] == {
        "profile_name": "qwen3.5-4b-thinking-off-v1",
        "thinking": False,
        "tools": False,
        "vision": False,
        "context_limit": 8192,
        "max_output_tokens": 256,
        "temperature": 0.0,
        "seed": 0,
    }
    baseline = payload["baseline"]
    assert baseline["case_count"] == 6
    assert baseline["passed_case_count"] == 6
    assert baseline["pass_rate"] == 1.0
    assert baseline["prompt_tokens_total"] == 60
    assert baseline["generated_tokens_total"] == 12
    assert baseline["total_duration_ns"] == 600
    assert baseline["load_duration_ns"] == 60
    assert baseline["prompt_eval_duration_ns"] == 120
    assert baseline["eval_duration_ns"] == 420
    assert len(baseline["case_results"]) == 6

    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True).lower()
    assert "flop" not in encoded
    assert "energy" not in encoded
    assert "hardware_compute_reduction" not in encoded


def test_main_success_writes_byte_identical_stdout_and_output(monkeypatch, tmp_path, capsys):
    module = _load_module()
    monkeypatch.setattr(module, "OllamaModelAdapter", FakeAdapter)
    output = tmp_path / "evidence.json"

    rc = module.main(["--output", str(output)])
    captured = capsys.readouterr()

    assert rc == 0
    assert captured.err == ""
    assert output.read_text(encoding="utf-8") == captured.out
    payload = json.loads(captured.out)
    assert payload["qualified"] is True
    assert payload["generation_profile"]["thinking"] is False


def test_main_fails_closed_for_digest_mismatch(monkeypatch, capsys):
    module = _load_module()

    class WrongDigestAdapter(FakeAdapter):
        descriptor = _descriptor(digest="wrong-digest")

    monkeypatch.setattr(module, "OllamaModelAdapter", WrongDigestAdapter)
    rc = module.main([])
    payload = json.loads(capsys.readouterr().out)

    assert rc == 1
    assert payload["qualified"] is False
    assert any("digest" in error for error in payload["errors"])


def test_main_fails_closed_for_baseline_failure(monkeypatch, capsys):
    module = _load_module()

    class FailingBaselineAdapter(FakeAdapter):
        outputs = dict(FakeAdapter.outputs, **{"a004-english-exact": "RED"})

    monkeypatch.setattr(module, "OllamaModelAdapter", FailingBaselineAdapter)
    rc = module.main([])
    payload = json.loads(capsys.readouterr().out)

    assert rc == 1
    assert payload["qualified"] is False
    assert "pass_rate must be 1.0" in payload["errors"]


def test_descriptor_validation_pins_exact_qwen_runtime_identity():
    module = _load_module()
    good = _descriptor()
    assert module.validate_descriptor(good) == []

    variants = [
        ("model_name", "other", "model name"),
        ("model_digest", "wrong", "digest"),
        ("architecture", "other", "architecture"),
        ("parameter_count", 1, "parameter_count"),
        ("parameter_size", "4B", "parameter_size"),
        ("quantization", "Q8_0", "quantization"),
        ("context_length", 4096, "context_length"),
        ("embedding_length", 1, "embedding_length"),
        ("capabilities", ("completion",), "capabilities"),
    ]
    for field, value, needle in variants:
        kwargs = {
            "backend_name": good.backend_name,
            "backend_version": good.backend_version,
            "model_name": good.model_name,
            "model_digest": good.model_digest,
            "architecture": good.architecture,
            "parameter_count": good.parameter_count,
            "parameter_size": good.parameter_size,
            "quantization": good.quantization,
            "context_length": good.context_length,
            "embedding_length": good.embedding_length,
            "capabilities": good.capabilities,
        }
        kwargs[field] = value
        errors = module.validate_descriptor(ModelDescriptor(**kwargs))
        assert any(needle in error for error in errors), (field, errors)
