from __future__ import annotations

import importlib.util
import io
import json
from pathlib import Path

import pytest

from flywire_asca.contracts import ActivationBudget, MemoryKind, MemoryRecord
from flywire_asca.embedding import (
    EmbeddingDescriptor,
    EmbeddingInputKind,
    EmbeddingRequest,
    EmbeddingResponse,
    normalize_embedding_values,
)
from flywire_asca.vector_memory import VectorMemoryDocument


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "qualify_selective_activation_a006.py"
DIGEST = "ac6da0dfba84a81fdbfbaf330198c33cd77c4cdfc53e8bc50eb581914a15621d"


def _load_module():
    assert SCRIPT.exists(), "A006 physical qualification script must exist"
    spec = importlib.util.spec_from_file_location("qualify_selective_activation_a006", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _doc(memory_id, text):
    return VectorMemoryDocument(
        MemoryRecord(memory_id, MemoryKind.SEMANTIC, f"content:{memory_id}", 0.8),
        text,
    )


class FakeEmbeddingAdapter:
    def __init__(self, vectors):
        self.vectors = vectors
        self.descriptor = EmbeddingDescriptor(
            backend_name="fake",
            backend_version="1",
            model_name="fake-embedder",
            model_digest="fake-digest",
            architecture="fake",
            parameter_count=None,
            parameter_size=None,
            quantization=None,
            context_length=8192,
            embedding_dimension=2,
            capabilities=("embedding",),
        )

    def inspect(self):
        return self.descriptor

    def embed(self, request):
        vectors = tuple(
            normalize_embedding_values(self.vectors[text], expected_dimension=2)
            for text in request.texts
        )
        return EmbeddingResponse(
            request_id=request.request_id,
            model_name=self.descriptor.model_name,
            model_digest=self.descriptor.model_digest,
            vectors=vectors,
            input_count=len(vectors),
            prompt_tokens=None,
            total_duration_ns=None,
            load_duration_ns=None,
        )


def test_constants_pin_exact_physical_profile():
    module = _load_module()
    assert module.MODEL_NAME == "qwen3-embedding:0.6b"
    assert module.EXPECTED_DIGEST == DIGEST
    assert module.EXPECTED_DIMENSION == 1024
    assert module.A005_THRESHOLD == pytest.approx(0.5037018224299838)
    assert module.A005_TOP_K == 12
    assert module.A006_MAX_MEMORY_NODES == 8
    assert module.A006_MAX_WORKING_SET_ITEMS == 4
    assert module.SELECTOR_PROFILE == "a006-selective-convergence-v1"


def test_physical_fixture_is_frozen_and_covers_declared_case_classes():
    module = _load_module()
    cases = module.build_physical_fixture()
    ids = {case.case_id for case in cases}
    assert ids == {
        "physical-en-convergence",
        "physical-th-convergence",
        "physical-cross-lingual-convergence",
        "physical-same-name-ambiguity",
        "physical-budget-truncation",
        "physical-no-hit",
        "physical-convergence-recovery-challenge",
    }
    assert any(case.convergence_recovery_challenge for case in cases)
    assert any(case.ambiguity_expected for case in cases)
    assert any(case.strict_budget_expected for case in cases)
    assert any(case.expected_no_selection for case in cases)
    assert all(case.documents for case in cases)
    assert all(case.cues for case in cases)
    assert module.FIXTURE_VERSION == "a006-physical-v1"


def test_run_physical_case_composes_a005_retrieval_with_all_three_a006_modes():
    module = _load_module()
    case = module.PhysicalSelectiveCase(
        case_id="fake-convergence",
        documents=(
            _doc("target", "target doc"),
            _doc("one-a", "one a doc"),
            _doc("one-b", "one b doc"),
        ),
        cues=(
            module.PhysicalCue("cue-a", "q-a", "query a"),
            module.PhysicalCue("cue-b", "q-b", "query b"),
        ),
        required_memory_ids=("target",),
        convergence_recovery_challenge=True,
    )
    adapter = FakeEmbeddingAdapter(
        {
            "target doc": (0.8, 0.6),
            "one a doc": (0.9, -0.4358898944),
            "one b doc": (-0.083084, 0.996542),
            "query a": (1.0, 0.0),
            "query b": (0.28, 0.96),
        }
    )

    result = module.run_physical_case(
        adapter,
        case,
        threshold=0.5,
        top_k=12,
        budget=ActivationBudget(3, 0, 1, 0, 0),
        embedding_profile="fake-profile",
    )

    assert result["selective"]["selected_ids"] == ["target"]
    assert result["single_best"]["selected_ids"] != ["target"]
    assert "target" in result["exhaustive"]["selected_ids"]
    assert result["convergence_recovered"] is True
    assert result["convergence_regressed"] is False
    assert result["deterministic_repeat_match"] is True
    assert result["retrieval_hit_counts"] == [2, 2]


@pytest.mark.parametrize(
    "coverage, recovery, regression, expected",
    [
        (1.0, 1, 0, "SUPPORTED"),
        (0.8, 1, 0, "MIXED"),
        (1.0, 1, 1, "MIXED"),
        (1.0, 0, 0, "NOT_SUPPORTED"),
        (0.5, 0, 2, "NOT_SUPPORTED"),
    ],
)
def test_hypothesis_outcome_rules_are_frozen(coverage, recovery, regression, expected):
    module = _load_module()
    assert module.classify_hypothesis_outcome(
        required_memory_coverage=coverage,
        convergence_recovery_count=recovery,
        convergence_regression_count=regression,
    ) == expected


def test_main_valid_negative_result_exits_zero_and_writes_byte_identical_utf8(monkeypatch, tmp_path, capsys):
    module = _load_module()

    class FakePhysicalAdapter:
        def __init__(self, *args, **kwargs):
            pass

        def inspect(self):
            return EmbeddingDescriptor(
                backend_name="ollama",
                backend_version="0.32.15",
                model_name=module.MODEL_NAME,
                model_digest=module.EXPECTED_DIGEST,
                architecture="qwen3",
                parameter_count=595776512,
                parameter_size="639M",
                quantization="Q8_0",
                context_length=32768,
                embedding_dimension=1024,
                capabilities=("embedding",),
            )

    monkeypatch.setattr(module, "OllamaEmbeddingAdapter", FakePhysicalAdapter)
    payload = _valid_physical_payload(module)
    payload["cases"] = [{"case_id": "physical-th-convergence", "note": "ภาษาไทย"}]
    monkeypatch.setattr(
        module,
        "run_physical_experiment",
        lambda adapter: payload,
    )
    output = tmp_path / "evidence.json"
    rc = module.main(["--output", str(output)])
    captured = capsys.readouterr()

    assert rc == 0
    assert captured.err == ""
    assert output.read_bytes() == captured.out.encode("utf-8")
    payload = json.loads(captured.out)
    assert payload["experiment_valid"] is True
    assert payload["hypothesis_outcome"] == "NOT_SUPPORTED"
    encoded = captured.out.lower()
    assert "qwen3.5:4b" not in encoded
    assert "flop" not in encoded
    assert "energy" not in encoded


def test_emit_handles_windows_cp1252_console_with_thai_payload(monkeypatch):
    module = _load_module()
    raw = io.BytesIO()
    stdout = io.TextIOWrapper(raw, encoding="cp1252", errors="strict")
    monkeypatch.setattr(module.sys, "stdout", stdout)

    module._emit({"note": "ภาษาไทย"}, None)
    stdout.flush()

    assert raw.getvalue().decode("utf-8") == '{"note":"ภาษาไทย"}\n'


def test_main_identity_failure_exits_nonzero(monkeypatch, capsys):
    module = _load_module()

    class WrongIdentityAdapter:
        def __init__(self, *args, **kwargs):
            pass

        def inspect(self):
            return EmbeddingDescriptor(
                backend_name="ollama",
                backend_version="0.32.15",
                model_name=module.MODEL_NAME,
                model_digest="wrong",
                architecture="qwen3",
                parameter_count=None,
                parameter_size=None,
                quantization=None,
                context_length=32768,
                embedding_dimension=1024,
                capabilities=("embedding",),
            )

    monkeypatch.setattr(module, "OllamaEmbeddingAdapter", WrongIdentityAdapter)
    rc = module.main([])
    payload = json.loads(capsys.readouterr().out)

    assert rc == 1
    assert payload["experiment_valid"] is False
    assert any("digest" in error for error in payload["errors"])

def test_budget_truncation_case_does_not_label_an_arbitrary_equal_status_note_as_required():
    module = _load_module()
    case = next(
        case for case in module.build_physical_fixture()
        if case.case_id == "physical-budget-truncation"
    )
    assert case.strict_budget_expected is True
    assert case.required_memory_ids == ()


def _valid_physical_payload(module):
    cases = module.build_physical_fixture()
    return {
        "fixture_version": module.FIXTURE_VERSION,
        "fixture_fingerprint": module._fixture_fingerprint(cases),
        "case_ids": [case.case_id for case in cases],
        "required_memory_coverage": 1.0,
        "convergence_recovery_count": 0,
        "convergence_regression_count": 0,
        "ambiguity_failure_count": 0,
        "no_selection_failure_count": 0,
        "strict_budget_observation_count": sum(
            int(case.strict_budget_expected) for case in cases
        ),
        "total_positive_candidates": 10,
        "total_selected_items": 5,
        "active_state_reduction_ratio": 0.5,
        "deterministic_repeat_match": True,
        "embedding_metrics": {
            "embedding_request_count": 2,
            "embedding_input_count": 3,
            "prompt_tokens_total": 12,
            "prompt_tokens_observed_response_count": 2,
            "total_duration_ns_total": 100,
            "total_duration_observed_response_count": 2,
            "load_duration_ns_total": 20,
            "load_duration_observed_response_count": 2,
        },
        "cases": [{"case_id": "physical-th-convergence", "note": "ภาษาไทย"}],
        "hypothesis_outcome": "NOT_SUPPORTED",
        "experiment_valid": True,
    }


def test_final_physical_fixture_fingerprint_is_pinned():
    module = _load_module()
    assert module._fixture_fingerprint(module.build_physical_fixture()) == (
        "e51fea2e58186e94d7affc964509e96d96fc656759677d7dcc073e5b36b91035"
    )


@pytest.mark.parametrize(
    "field, bad_value, error_text",
    [
        ("fixture_version", "drifted", "fixture_version"),
        ("fixture_fingerprint", "wrong", "fixture_fingerprint"),
        ("case_ids", ["wrong-case"], "case_ids"),
        ("ambiguity_failure_count", 1, "ambiguity"),
        ("no_selection_failure_count", 1, "no-selection"),
        ("strict_budget_observation_count", 0, "strict-budget"),
        ("deterministic_repeat_match", False, "deterministic"),
    ],
)
def test_main_fails_closed_for_invalid_physical_engineering_evidence(
    monkeypatch,
    capsys,
    field,
    bad_value,
    error_text,
):
    module = _load_module()

    class FakePhysicalAdapter:
        def __init__(self, *args, **kwargs):
            pass

        def inspect(self):
            return EmbeddingDescriptor(
                backend_name="ollama",
                backend_version="0.32.15",
                model_name=module.MODEL_NAME,
                model_digest=module.EXPECTED_DIGEST,
                architecture="qwen3",
                parameter_count=595776512,
                parameter_size="639M",
                quantization="Q8_0",
                context_length=32768,
                embedding_dimension=1024,
                capabilities=("embedding",),
            )

    payload = _valid_physical_payload(module)
    payload[field] = bad_value
    monkeypatch.setattr(module, "OllamaEmbeddingAdapter", FakePhysicalAdapter)
    monkeypatch.setattr(module, "run_physical_experiment", lambda adapter: payload)

    rc = module.main([])
    emitted = json.loads(capsys.readouterr().out)

    assert rc == 1
    assert emitted["experiment_valid"] is False
    assert any(error_text in error for error in emitted["errors"])


def test_recording_embedding_adapter_preserves_response_and_records_available_metrics():
    module = _load_module()

    class Delegate:
        def inspect(self):
            return EmbeddingDescriptor(
                backend_name="fake",
                backend_version="1",
                model_name="fake",
                model_digest="digest",
                architecture="fake",
                parameter_count=None,
                parameter_size=None,
                quantization=None,
                context_length=100,
                embedding_dimension=2,
                capabilities=("embedding",),
            )

        def embed(self, request):
            vectors = tuple(
                normalize_embedding_values((1.0, 0.0))
                for _ in request.texts
            )
            return EmbeddingResponse(
                request_id=request.request_id,
                model_name="fake",
                model_digest="digest",
                vectors=vectors,
                input_count=len(vectors),
                prompt_tokens=7,
                total_duration_ns=50,
                load_duration_ns=10,
            )

    recorder = module._RecordingEmbeddingAdapter(Delegate())
    request = EmbeddingRequest(
        "metrics",
        EmbeddingInputKind.DOCUMENT,
        ("one", "two"),
    )
    response = recorder.embed(request)

    assert response.request_id == "metrics"
    assert recorder.metrics() == {
        "embedding_request_count": 1,
        "embedding_input_count": 2,
        "prompt_tokens_total": 7,
        "prompt_tokens_observed_response_count": 1,
        "total_duration_ns_total": 50,
        "total_duration_observed_response_count": 1,
        "load_duration_ns_total": 10,
        "load_duration_observed_response_count": 1,
    }