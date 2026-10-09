from __future__ import annotations

import importlib.util
import io
import json
from pathlib import Path

import pytest

from flywire_asca.contracts import MemoryKind, MemoryRecord
from flywire_asca.embedding import (
    EmbeddingDescriptor,
    EmbeddingResponse,
    normalize_embedding_values,
)
from flywire_asca.vector_memory import VectorMemoryDocument


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "qualify_uncertainty_expansion_a007.py"
DIGEST = "ac6da0dfba84a81fdbfbaf330198c33cd77c4cdfc53e8bc50eb581914a15621d"


def _load_module():
    assert SCRIPT.exists(), "A007 physical qualification script must exist"
    spec = importlib.util.spec_from_file_location(
        "qualify_uncertainty_expansion_a007",
        SCRIPT,
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _doc(memory_id, text):
    return VectorMemoryDocument(
        MemoryRecord(
            memory_id,
            MemoryKind.SEMANTIC,
            f"content:{memory_id}",
            0.8,
        ),
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
            normalize_embedding_values(
                self.vectors[text],
                expected_dimension=2,
            )
            for text in request.texts
        )
        count = len(vectors)
        return EmbeddingResponse(
            request_id=request.request_id,
            model_name=self.descriptor.model_name,
            model_digest=self.descriptor.model_digest,
            vectors=vectors,
            input_count=count,
            prompt_tokens=count * 2,
            total_duration_ns=count * 100,
            load_duration_ns=count * 10,
        )


def _valid_metrics(requests=1, inputs=1):
    return {
        "embedding_request_count": requests,
        "embedding_input_count": inputs,
        "prompt_tokens_total": inputs * 2,
        "prompt_tokens_observed_response_count": requests,
        "total_duration_ns_total": inputs * 100,
        "total_duration_observed_response_count": requests,
        "load_duration_ns_total": inputs * 10,
        "load_duration_observed_response_count": requests,
    }


def _valid_physical_payload(module):
    profile = module.build_a007_primary_profile()
    cases = module.build_physical_fixture()
    return {
        "fixture_version": module.FIXTURE_VERSION,
        "fixture_fingerprint": module.EXPECTED_FIXTURE_FINGERPRINT,
        "case_ids": [case.case_id for case in cases],
        "selector": "SINGLE_BEST",
        "threshold": module.A005_THRESHOLD,
        "profile": [
            {
                "round_index": scope.round_index,
                "enabled_cue_tier_count": scope.enabled_cue_tier_count,
                "top_k": scope.top_k,
                "max_memory_nodes": scope.budget.max_memory_nodes,
                "max_working_set_items": scope.budget.max_working_set_items,
            }
            for scope in profile.scopes
        ],
        "required_memory_coverage": {
            "NO_EXPANSION": 0.5,
            "SIGNAL_DRIVEN": 1.0,
            "ALWAYS_EXPAND": 1.0,
        },
        "signal_driven_recovery_count": 1,
        "signal_driven_regression_count": 0,
        "easy_unnecessary_expansion_count": 0,
        "persistent_insufficient_expected_count": 1,
        "persistent_insufficient_exhausted_count": 1,
        "ambiguity_failure_count": 0,
        "deterministic_repeat_match": True,
        "total_rounds": {
            "NO_EXPANSION": len(cases),
            "SIGNAL_DRIVEN": len(cases) + 1,
            "ALWAYS_EXPAND": len(cases) * 3,
        },
        "setup_embedding_metrics": _valid_metrics(8, 24),
        "policy_embedding_metrics": {
            "NO_EXPANSION": _valid_metrics(8, 8),
            "SIGNAL_DRIVEN": _valid_metrics(9, 9),
            "ALWAYS_EXPAND": _valid_metrics(24, 24),
        },
        "cases": [],
        "hypothesis_outcome": "SUPPORTED",
        "experiment_valid": True,
    }


def test_constants_pin_exact_physical_profile():
    module = _load_module()
    assert module.MODEL_NAME == "qwen3-embedding:0.6b"
    assert module.EXPECTED_DIGEST == DIGEST
    assert module.EXPECTED_DIMENSION == 1024
    assert module.A005_THRESHOLD == pytest.approx(0.5037018224299838)
    assert module.PRIMARY_SELECTOR == "SINGLE_BEST"
    assert module.PROFILE_NAME == "a007-structural-expansion-v1"
    profile = module.build_a007_primary_profile()
    assert [
        (
            scope.round_index,
            scope.enabled_cue_tier_count,
            scope.top_k,
            scope.budget.max_memory_nodes,
            scope.budget.max_working_set_items,
        )
        for scope in profile.scopes
    ] == [
        (0, 1, 12, 8, 4),
        (1, 2, 24, 12, 8),
        (2, 3, 32, 16, 12),
    ]


def test_physical_fixture_is_frozen_and_covers_declared_categories():
    module = _load_module()
    cases = module.build_physical_fixture()
    assert {case.case_id for case in cases} == {
        "physical-en-easy",
        "physical-th-easy",
        "physical-en-recovery",
        "physical-th-recovery",
        "physical-cross-lingual-recovery",
        "physical-budget-truncation",
        "physical-same-name-ambiguity",
        "physical-persistent-insufficient",
    }
    assert all(len(case.cue_tiers) == 3 for case in cases)
    assert module.FIXTURE_VERSION == "a007-physical-v1"
    assert module.EXPECTED_FIXTURE_FINGERPRINT == "59f95ef115534fe24e59570cb281c0564ab75aadf364f4c26feba0d4078213c9"
    assert len(module.EXPECTED_FIXTURE_FINGERPRINT) == 64
    int(module.EXPECTED_FIXTURE_FINGERPRINT, 16)
    assert (
        module._fixture_fingerprint(cases)
        == module.EXPECTED_FIXTURE_FINGERPRINT
    )

    for case in cases:
        source_ids = [
            cue.source_cue_id
            for tier in case.cue_tiers
            for cue in tier.cues
        ]
        query_ids = [
            cue.query_id
            for tier in case.cue_tiers
            for cue in tier.cues
        ]
        assert len(source_ids) == len(set(source_ids))
        assert len(query_ids) == len(set(query_ids))


def test_validate_physical_fixture_rejects_duplicate_cue_or_query_identity():
    module = _load_module()
    base = module.build_physical_fixture()[0]
    cue = base.cue_tiers[0].cues[0]
    duplicate_source = module.PhysicalExpansionCue(
        cue.source_cue_id,
        "other-query",
        "other text",
    )
    malformed = module.PhysicalExpansionCase(
        "malformed",
        base.documents,
        (
            base.cue_tiers[0],
            module.PhysicalExpansionCueTier(1, (duplicate_source,)),
            base.cue_tiers[2],
        ),
        base.required_memory_ids,
    )
    errors = module.validate_physical_fixture((malformed,))
    assert any("source_cue_id" in error for error in errors)

    duplicate_query = module.PhysicalExpansionCue(
        "other-source",
        cue.query_id,
        "other text",
    )
    malformed_query = module.PhysicalExpansionCase(
        "malformed-query",
        base.documents,
        (
            base.cue_tiers[0],
            module.PhysicalExpansionCueTier(1, (duplicate_query,)),
            base.cue_tiers[2],
        ),
        base.required_memory_ids,
    )
    errors = module.validate_physical_fixture((malformed_query,))
    assert any("query_id" in error for error in errors)


def test_fake_composition_recovers_at_later_tier_and_separates_costs():
    module = _load_module()
    case = module.PhysicalExpansionCase(
        case_id="fake-recovery",
        documents=(
            _doc("target", "target document"),
            _doc("noise", "noise document"),
        ),
        cue_tiers=(
            module.PhysicalExpansionCueTier(
                0,
                (module.PhysicalExpansionCue("cue-0", "q-0", "irrelevant query"),),
            ),
            module.PhysicalExpansionCueTier(
                1,
                (module.PhysicalExpansionCue("cue-1", "q-1", "target query"),),
            ),
            module.PhysicalExpansionCueTier(
                2,
                (module.PhysicalExpansionCue("cue-2", "q-2", "target query two"),),
            ),
        ),
        required_memory_ids=("target",),
    )
    adapter = FakeEmbeddingAdapter(
        {
            "target document": (1.0, 0.0),
            "noise document": (0.0, 1.0),
            "irrelevant query": (-1.0, 0.0),
            "target query": (1.0, 0.0),
            "target query two": (1.0, 0.0),
        }
    )

    result = module.run_physical_case(
        adapter,
        case,
        profile=module.build_a007_primary_profile(),
        threshold=0.5,
        embedding_profile="fake-profile",
    )

    assert result["setup_embedding_metrics"]["embedding_request_count"] == 1
    assert result["setup_embedding_metrics"]["embedding_input_count"] == 2

    no_expansion = result["policies"]["NO_EXPANSION"]
    signal = result["policies"]["SIGNAL_DRIVEN"]
    always = result["policies"]["ALWAYS_EXPAND"]

    assert no_expansion["selected_ids"] == []
    assert signal["selected_ids"] == ["target"]
    assert always["selected_ids"] == ["target"]
    assert result["signal_driven_recovered"] is True

    assert no_expansion["round_count"] == 1
    assert signal["round_count"] == 2
    assert always["round_count"] == 3

    assert no_expansion["embedding_metrics"]["embedding_request_count"] == 1
    assert signal["embedding_metrics"]["embedding_request_count"] == 3
    assert always["embedding_metrics"]["embedding_request_count"] == 6
    assert no_expansion["embedding_metrics"]["embedding_input_count"] == 1
    assert signal["embedding_metrics"]["embedding_input_count"] == 3
    assert always["embedding_metrics"]["embedding_input_count"] == 6

    assert no_expansion["retrieval_request_count"] == 1
    assert signal["retrieval_request_count"] == 3
    assert always["retrieval_request_count"] == 6
    assert result["deterministic_repeat_match"] is True


@pytest.mark.parametrize(
    "recovery,regression,signal_cov,always_cov,easy,persist_ok,signal_rounds,always_rounds,expected",
    [
        (1, 0, 1.0, 1.0, 0, True, 10, 24, "SUPPORTED"),
        (1, 1, 1.0, 1.0, 0, True, 10, 24, "MIXED"),
        (1, 0, 0.8, 1.0, 0, True, 10, 24, "MIXED"),
        (1, 0, 1.0, 1.0, 1, True, 10, 24, "MIXED"),
        (1, 0, 1.0, 1.0, 0, True, 24, 24, "MIXED"),
        (0, 0, 1.0, 1.0, 0, True, 10, 24, "NOT_SUPPORTED"),
    ],
)
def test_hypothesis_outcome_rules_are_frozen(
    recovery,
    regression,
    signal_cov,
    always_cov,
    easy,
    persist_ok,
    signal_rounds,
    always_rounds,
    expected,
):
    module = _load_module()
    assert module.classify_hypothesis_outcome(
        recovery_count=recovery,
        regression_count=regression,
        signal_coverage=signal_cov,
        always_coverage=always_cov,
        easy_unnecessary_expansion_count=easy,
        persistent_exhaustion_complete=persist_ok,
        signal_rounds=signal_rounds,
        always_rounds=always_rounds,
    ) == expected


@pytest.mark.parametrize(
    "mutator, match",
    [
        (lambda p: p.update(fixture_version="wrong"), "fixture_version"),
        (lambda p: p.update(fixture_fingerprint="0" * 64), "fixture_fingerprint"),
        (lambda p: p.update(case_ids=["wrong"]), "case_ids"),
        (lambda p: p.update(selector="SELECTIVE_CONVERGENCE"), "selector"),
        (lambda p: p.update(threshold=0.4), "threshold"),
        (lambda p: p.update(ambiguity_failure_count=1), "ambiguity"),
        (
            lambda p: p.update(
                persistent_insufficient_exhausted_count=0,
            ),
            "persistent",
        ),
        (
            lambda p: p.update(deterministic_repeat_match=False),
            "deterministic",
        ),
        (
            lambda p: p["setup_embedding_metrics"].update(
                embedding_request_count=-1,
            ),
            "embedding_request_count",
        ),
    ],
)
def test_physical_engineering_validation_fails_closed(mutator, match):
    module = _load_module()
    payload = _valid_physical_payload(module)
    mutator(payload)
    errors = module.validate_physical_experiment(payload)
    assert any(match in error for error in errors)


def test_valid_negative_research_outcome_is_not_execution_failure(monkeypatch, tmp_path, capsys):
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
                parameter_size="595.78M",
                quantization="Q8_0",
                context_length=32768,
                embedding_dimension=1024,
                capabilities=("embedding",),
            )

    payload = _valid_physical_payload(module)
    payload["signal_driven_recovery_count"] = 0
    payload["hypothesis_outcome"] = "NOT_SUPPORTED"

    monkeypatch.setattr(module, "OllamaEmbeddingAdapter", FakePhysicalAdapter)
    monkeypatch.setattr(module, "run_physical_experiment", lambda adapter: payload)

    output = tmp_path / "a007.json"
    rc = module.main(["--output", str(output)])
    captured = capsys.readouterr()

    assert rc == 0
    assert output.read_bytes() == captured.out.encode("utf-8")
    decoded = json.loads(captured.out)
    assert decoded["experiment_valid"] is True
    assert decoded["hypothesis_outcome"] == "NOT_SUPPORTED"
    lower = captured.out.lower()
    assert "qwen3.5:4b" not in lower
    assert "flop" not in lower
    assert "energy" not in lower


def test_emit_handles_windows_cp1252_console_with_thai(monkeypatch):
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