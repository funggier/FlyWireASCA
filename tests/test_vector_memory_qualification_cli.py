from __future__ import annotations

import importlib.util
import io
import json
import math
from pathlib import Path

import pytest

from flywire_asca.embedding import (
    EmbeddingDescriptor,
    EmbeddingRequest,
    EmbeddingResponse,
    normalize_embedding_values,
)


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "qualify_vector_memory_a005.py"
MODEL = "qwen3-embedding:0.6b"
DIGEST = "test-embedding-digest"
DIMENSION = 1024


def _load_module():
    assert SCRIPT.exists(), "qualification script must exist"
    spec = importlib.util.spec_from_file_location("qualify_vector_memory_a005", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _basis(index: int):
    return tuple(1.0 if i == index else 0.0 for i in range(DIMENSION))


def _negative_all():
    value = -1.0 / math.sqrt(DIMENSION)
    return tuple(value for _ in range(DIMENSION))


def _descriptor(digest=DIGEST):
    return EmbeddingDescriptor(
        backend_name="ollama",
        backend_version="0.32.15",
        model_name=MODEL,
        model_digest=digest,
        architecture="qwen3",
        parameter_count=595776512,
        parameter_size="639M",
        quantization="Q8_0",
        context_length=32768,
        embedding_dimension=DIMENSION,
        capabilities=("embedding",),
    )


def _vector_map(module):
    mapping = {
        "The bicycle is stored in the garage.": _basis(0),
        "Where is the bike kept?": _basis(0),
        "แมวสีดำชอบนอนบนเก้าอี้ไม้": _basis(1),
        "แมวสีดำชอบนอนที่ไหน": _basis(1),
        "The company meeting starts at 9 AM.": _basis(2),
        "ร้านอาหารปิดเวลา 21:00 น.": _basis(3),
        "I parked the red scooter beside the library.": _basis(4),
        "Where did I park the red scooter?": _basis(4),
        "นกแก้วสีเขียวชอบกินเมล็ดทานตะวัน": _basis(5),
        "นกแก้วสีเขียวชอบกินอะไร": _basis(5),
        "The backup drive is stored in the blue cabinet.": _basis(6),
        "ไดรฟ์สำรองเก็บไว้ที่ไหน": _basis(6),
        "ห้องประชุมอยู่ชั้นสามของอาคาร": _basis(7),
        "Which floor is the meeting room on?": _basis(7),
        "Somchai works at company A.": _basis(8),
        "Somchai works at company B.": _basis(8),
        "Somchai works where?": _basis(8),
        "Which Somchai works at company B?": _basis(8),
        "health probe english": _basis(9),
        "ทดสอบเวกเตอร์สุขภาพ": _basis(10),
    }
    return mapping


def _fake_adapter_class(module, *, digest=DIGEST):
    mapping = _vector_map(module)

    class FakeAdapter:
        def __init__(self, model_name, **kwargs):
            self.model_name = model_name
            self.kwargs = kwargs
            self.descriptor = _descriptor(digest)
            self.requests: list[EmbeddingRequest] = []

        def inspect(self):
            return self.descriptor

        def embed(self, request):
            self.requests.append(request)
            vectors = tuple(
                normalize_embedding_values(
                    mapping.get(text, _negative_all()),
                    expected_dimension=DIMENSION,
                )
                for text in request.texts
            )
            return EmbeddingResponse(
                request.request_id,
                self.descriptor.model_name,
                self.descriptor.model_digest,
                vectors,
                len(vectors),
                len(request.texts) * 5,
                100,
                10,
            )

    return FakeAdapter


def test_physical_calibration_and_qualification_fixtures_are_disjoint():
    module = _load_module()
    cal = module.build_physical_calibration_fixture()
    qual = module.build_physical_qualification_fixture(0.5)
    assert {case.case_id for case in cal[1]}.isdisjoint(
        {case.case_id for case in qual[1]}
    )
    assert len(cal[0]) == 4
    assert len(qual[0]) == 6


def test_descriptor_and_health_validation_pin_embedding_identity_and_vectors():
    module = _load_module()
    assert module.validate_descriptor(_descriptor(), DIGEST) == []
    assert any(
        "digest" in error
        for error in module.validate_descriptor(_descriptor("wrong"), DIGEST)
    )
    bad_dim = EmbeddingDescriptor(
        "ollama", "0.32.15", MODEL, DIGEST, "qwen3",
        595776512, "639M", "Q8_0", 32768, 2, ("embedding",)
    )
    assert any(
        "dimension" in error
        for error in module.validate_descriptor(bad_dim, DIGEST)
    )

    adapter = _fake_adapter_class(module)(MODEL)
    health = module.run_vector_health(adapter, repeats=3)
    assert health["probe_count"] == 6
    assert health["dimension"] == DIMENSION
    assert health["zero_vector_count"] == 0
    assert health["nonfinite_vector_count"] == 0
    assert health["norm_min"] == pytest.approx(1.0)
    assert health["norm_max"] == pytest.approx(1.0)


def test_calibration_mode_emits_real_fixture_threshold_with_fake_adapter(monkeypatch, capsys):
    module = _load_module()
    monkeypatch.setattr(module, "OllamaEmbeddingAdapter", _fake_adapter_class(module))
    rc = module.main(["--calibrate", "--expected-digest", DIGEST])
    payload = json.loads(capsys.readouterr().out)
    assert rc == 0
    assert payload["mode"] == "calibration"
    assert payload["experiment_valid"] is True
    assert payload["model"]["digest"] == DIGEST
    assert payload["physical_threshold"] == pytest.approx(0.5)
    assert payload["calibration_case_ids"] == [
        "physical-cal-bike",
        "physical-cal-cat",
    ]


def test_qualification_mode_uses_pinned_digest_and_threshold_defaults(monkeypatch, capsys):
    module = _load_module()
    assert module.EXPECTED_DIGEST == "ac6da0dfba84a81fdbfbaf330198c33cd77c4cdfc53e8bc50eb581914a15621d"
    assert module.FROZEN_PHYSICAL_THRESHOLD == pytest.approx(0.5037018224299838)
    monkeypatch.setattr(
        module,
        "OllamaEmbeddingAdapter",
        _fake_adapter_class(module, digest=module.EXPECTED_DIGEST),
    )

    rc = module.main([])
    payload = json.loads(capsys.readouterr().out)
    assert rc == 0
    assert payload["mode"] == "qualification"
    assert payload["experiment_valid"] is True
    assert payload["retrieval_qualified"] is True
    assert payload["physical_threshold"] == pytest.approx(module.FROZEN_PHYSICAL_THRESHOLD)
    assert payload["graph_decision"] == "VECTOR_SUFFICIENT"
    assert payload["qualification_case_ids"] == [
        "physical-en-paraphrase",
        "physical-th-paraphrase",
        "physical-th-to-en",
        "physical-en-to-th",
        "physical-same-name",
        "physical-entity-filter",
    ]
    assert payload["calibration_case_ids"] == [
        "physical-cal-bike",
        "physical-cal-cat",
    ]
    assert set(payload["calibration_case_ids"]).isdisjoint(
        payload["qualification_case_ids"]
    )


def test_utf8_stdout_and_output_are_byte_identical_under_cp1252(monkeypatch, tmp_path):
    module = _load_module()
    monkeypatch.setattr(module, "OllamaEmbeddingAdapter", _fake_adapter_class(module))
    raw = io.BytesIO()
    stdout = io.TextIOWrapper(raw, encoding="cp1252", errors="strict")
    monkeypatch.setattr(module.sys, "stdout", stdout)
    output = tmp_path / "evidence.json"

    rc = module.main([
        "--expected-digest", DIGEST,
        "--threshold", "0.5",
        "--output", str(output),
    ])
    stdout.flush()
    assert rc == 0
    assert raw.getvalue() == output.read_bytes()
    assert "นกแก้ว" in raw.getvalue().decode("utf-8")


def test_payload_does_not_claim_flops_energy_or_generative_qwen(monkeypatch, capsys):
    module = _load_module()
    monkeypatch.setattr(module, "OllamaEmbeddingAdapter", _fake_adapter_class(module))
    rc = module.main([
        "--expected-digest", DIGEST,
        "--threshold", "0.5",
    ])
    assert rc == 0
    encoded = capsys.readouterr().out.lower()
    assert "qwen3.5:4b" not in encoded
    assert "flop" not in encoded
    assert "energy" not in encoded
    assert "tools" not in encoded
    assert "vision" not in encoded

def test_pinned_digest_mismatch_fails_closed(monkeypatch, capsys):
    module = _load_module()
    monkeypatch.setattr(
        module,
        "OllamaEmbeddingAdapter",
        _fake_adapter_class(module, digest="wrong-digest"),
    )
    rc = module.main([])
    payload = json.loads(capsys.readouterr().out)
    assert rc == 1
    assert payload["experiment_valid"] is False
    assert any("digest" in error for error in payload["errors"])
