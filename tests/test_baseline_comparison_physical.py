import importlib.util
from pathlib import Path

from flywire_asca.embedding import (
    EmbeddingDescriptor,
    EmbeddingResponse,
    normalize_embedding_values,
)

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "qualify_baseline_comparison_a010_physical.py"


def load():
    assert SCRIPT.exists()
    spec = importlib.util.spec_from_file_location("a010p", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


class FakePhysicalEmbeddingAdapter:
    def __init__(self, *, digest: str) -> None:
        self.digest = digest
        raw = (1.0,) + (0.0,) * 1023
        self.vector = normalize_embedding_values(raw, expected_dimension=1024)

    def inspect(self):
        m = load()
        return EmbeddingDescriptor(
            backend_name="fake-ollama",
            backend_version="test",
            model_name=m.EMBEDDING_MODEL,
            model_digest=self.digest,
            architecture="qwen",
            parameter_count=0,
            parameter_size=None,
            quantization=None,
            context_length=1024,
            embedding_dimension=1024,
            capabilities=("embedding",),
        )

    def embed(self, request):
        return EmbeddingResponse(
            request_id=request.request_id,
            model_name=self.inspect().model_name,
            model_digest=self.inspect().model_digest,
            vectors=tuple(self.vector for _ in request.texts),
            input_count=len(request.texts),
            prompt_tokens=0,
            total_duration_ns=0,
            load_duration_ns=0,
        )


def test_physical_constants_pin_existing_a005_identity():
    m = load()
    assert m.EMBEDDING_MODEL == "qwen3-embedding:0.6b"
    assert m.EMBEDDING_DIGEST == "ac6da0dfba84a81fdbfbaf330198c33cd77c4cdfc53e8bc50eb581914a15621d"
    assert m.EMBEDDING_DIMENSION == 1024
    assert m.MINIMUM_SIMILARITY == 0.5037018224299838
    assert m.PHYSICAL_FIXTURE_VERSION == "a010-physical-v1"


def test_physical_fake_adapter_runs_same_inputs_and_keeps_portable_outcome_secondary():
    m = load()
    adapter = FakePhysicalEmbeddingAdapter(digest=m.EMBEDDING_DIGEST)
    payload = m.run_physical_qualification(
        embedding_adapter=adapter,
        portable_primary_outcome="NOT_SUPPORTED",
    )

    assert payload["physical_prerequisites_valid"] is True
    assert payload["physical_integration_valid"] is True
    assert payload["portable_primary_outcome"] == "NOT_SUPPORTED"
    comparison = payload["physical_comparison"]
    assert comparison["asca"]["procedure_success"] is True
    assert comparison["dense"]["procedure_success"] is True
    assert comparison["asca"]["query_count"] == 1
    assert comparison["dense"]["query_count"] == 3
    assert comparison["dense"]["scored_vector_count"] > comparison["asca"]["scored_vector_count"]


def test_physical_descriptor_mismatch_fails_closed():
    m = load()
    adapter = FakePhysicalEmbeddingAdapter(digest="wrong-digest")
    payload = m.run_physical_qualification(
        embedding_adapter=adapter,
        portable_primary_outcome="NOT_SUPPORTED",
    )

    assert payload["physical_prerequisites_valid"] is False
    assert any("digest" in item for item in payload["errors"])
