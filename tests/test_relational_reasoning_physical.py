from __future__ import annotations

import importlib.util
import io
import json
from pathlib import Path

from flywire_asca.embedding import (
    EmbeddingDescriptor,
    EmbeddingResponse,
    normalize_embedding_values,
)


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "qualify_relational_reasoning_a012_physical.py"


def load():
    assert SCRIPT.exists()
    spec = importlib.util.spec_from_file_location("a012physical", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class FixturePhysicalAdapter:
    def __init__(self, module):
        self.module = module
        cases = module.build_a012_deterministic_fixture()
        self.vectors = {}
        for case in cases:
            for memory in case.memories:
                self.vectors[memory.retrieval_text] = memory.vector
            self.vectors[case.query_text] = case.query_vector
        self.descriptor = EmbeddingDescriptor(
            backend_name="ollama",
            backend_version="0.32.15",
            model_name=module.MODEL_NAME,
            model_digest=module.EXPECTED_DIGEST,
            architecture="qwen3",
            parameter_count=595776512,
            parameter_size="639 MB",
            quantization="Q8_0",
            context_length=32768,
            embedding_dimension=module.EXPECTED_DIMENSION,
            capabilities=("embedding",),
        )

    def inspect(self):
        return self.descriptor

    def embed(self, request):
        vectors = tuple(
            normalize_embedding_values(
                tuple(self.vectors[text]) + (0.0,) * (
                    self.descriptor.embedding_dimension - len(self.vectors[text])
                ),
                expected_dimension=self.descriptor.embedding_dimension,
            )
            for text in request.texts
        )
        return EmbeddingResponse(
            request.request_id,
            self.descriptor.model_name,
            self.descriptor.model_digest,
            vectors,
            len(vectors),
            0,
            0,
            0,
        )


def test_physical_payload_pins_runtime_identity_and_preserves_portable_authority(monkeypatch):
    m = load()
    fake = FixturePhysicalAdapter(m)
    monkeypatch.setattr(m, "OllamaEmbeddingAdapter", lambda *args, **kwargs: fake)

    payload = m.run_physical_qualification()

    assert payload["experiment_valid"] is True
    assert payload["portable_primary_architecture_decision"] == (
        "EXPLICIT_RELATION_TRAVERSAL_JUSTIFIED"
    )
    assert payload["physical_observed_architecture_decision"] == (
        "EXPLICIT_RELATION_TRAVERSAL_JUSTIFIED"
    )
    assert payload["physical_agrees_with_portable_decision"] is True
    assert payload["physical_threshold"] == m.FROZEN_PHYSICAL_THRESHOLD
    assert payload["model"]["name"] == m.MODEL_NAME
    assert payload["model"]["digest"] == m.EXPECTED_DIGEST
    assert payload["model"]["embedding_dimension"] == m.EXPECTED_DIMENSION
    assert payload["benchmark"]["aggregate_metrics"]["relation_only_recovery_count"] == 6
    assert payload["errors"] == []


def test_physical_result_divergence_is_valid_secondary_evidence(monkeypatch):
    m = load()
    fake = FixturePhysicalAdapter(m)
    monkeypatch.setattr(m, "OllamaEmbeddingAdapter", lambda *args, **kwargs: fake)
    monkeypatch.setattr(
        m,
        "classify_a012_architecture",
        lambda report: m.ArchitectureDecision.MIXED,
    )

    payload = m.run_physical_qualification()

    assert payload["experiment_valid"] is True
    assert payload["physical_observed_architecture_decision"] == "MIXED"
    assert payload["physical_agrees_with_portable_decision"] is False
    assert payload["portable_primary_architecture_decision"] == (
        "EXPLICIT_RELATION_TRAVERSAL_JUSTIFIED"
    )


def test_wrong_runtime_identity_fails_closed(monkeypatch):
    m = load()
    fake = FixturePhysicalAdapter(m)
    fake.descriptor = EmbeddingDescriptor(
        backend_name="ollama",
        backend_version="0.32.15",
        model_name=m.MODEL_NAME,
        model_digest="0" * 64,
        architecture="qwen3",
        parameter_count=None,
        parameter_size=None,
        quantization=None,
        context_length=32768,
        embedding_dimension=m.EXPECTED_DIMENSION,
        capabilities=("embedding",),
    )
    monkeypatch.setattr(m, "OllamaEmbeddingAdapter", lambda *args, **kwargs: fake)

    payload = m.run_physical_qualification()

    assert payload["experiment_valid"] is False
    assert any("digest" in item.lower() for item in payload["errors"])


def test_stdout_and_output_bytes_match_utf8(monkeypatch, tmp_path):
    m = load()
    fake = FixturePhysicalAdapter(m)
    monkeypatch.setattr(m, "OllamaEmbeddingAdapter", lambda *args, **kwargs: fake)
    raw = io.BytesIO()
    stdout = io.TextIOWrapper(raw, encoding="cp1252", errors="strict")
    monkeypatch.setattr(m.sys, "stdout", stdout)
    out = tmp_path / "a012-physical.json"

    rc = m.main(["--output", str(out), "--note", "ภาษาไทย"])
    stdout.flush()

    assert rc == 0
    assert raw.getvalue() == out.read_bytes()
    payload = json.loads(raw.getvalue().decode("utf-8"))
    assert payload["note"] == "ภาษาไทย"
    assert payload["experiment_valid"] is True


def test_cli_exits_nonzero_for_invalid_runtime(monkeypatch, capsys):
    m = load()
    monkeypatch.setattr(
        m,
        "run_physical_qualification",
        lambda **kwargs: {
            "experiment_valid": False,
            "errors": ["runtime invalid"],
        },
    )
    rc = m.main([])
    assert rc == 1
    payload = json.loads(capsys.readouterr().out)
    assert payload["experiment_valid"] is False
