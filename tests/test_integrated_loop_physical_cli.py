import importlib.util
from pathlib import Path

import pytest

from flywire_asca.embedding import EmbeddingDescriptor
from flywire_asca.model import ModelDescriptor

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/"scripts"/"qualify_integrated_loop_a009_physical.py"


def load():
    assert SCRIPT.exists()
    spec=importlib.util.spec_from_file_location("a009physical",SCRIPT)
    module=importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def embedding_descriptor(*,digest=None,dimension=1024,model="qwen3-embedding:0.6b"):
    return EmbeddingDescriptor(
        "ollama","test",model,digest,
        "qwen3",600_000_000,None,None,4096,dimension,("embedding",),
    )


def model_descriptor(*,model="qwen3.5:4b"):
    return ModelDescriptor(
        "ollama","test",model,"model-digest","qwen3",4_000_000_000,
        None,None,8192,None,("completion",),
    )


def test_physical_constants_pin_a005_and_a004_boundaries():
    m=load()
    assert m.EMBEDDING_MODEL=="qwen3-embedding:0.6b"
    assert m.EMBEDDING_DIGEST=="ac6da0dfba84a81fdbfbaf330198c33cd77c4cdfc53e8bc50eb581914a15621d"
    assert m.EMBEDDING_DIMENSION==1024
    assert m.MINIMUM_SIMILARITY==0.5037018224299838
    assert m.TERMINAL_MODEL=="qwen3.5:4b"
    assert m.PRIMARY_SELECTOR=="SINGLE_BEST"
    assert m.PRIMARY_PROCEDURE_MODE=="CHUNKED"


def test_embedding_identity_validation_requires_exact_model_digest_dimension():
    m=load()
    good=embedding_descriptor(digest=m.EMBEDDING_DIGEST)
    assert m.validate_embedding_descriptor(good)==[]
    assert m.validate_embedding_descriptor(
        embedding_descriptor(digest="wrong")
    )
    assert m.validate_embedding_descriptor(
        embedding_descriptor(digest=m.EMBEDDING_DIGEST,dimension=768)
    )
    assert m.validate_embedding_descriptor(
        embedding_descriptor(digest=m.EMBEDDING_DIGEST,model="other")
    )


def test_terminal_model_validation_requires_qwen35_4b_only():
    m=load()
    assert m.validate_terminal_model_descriptor(model_descriptor())==[]
    assert m.validate_terminal_model_descriptor(
        model_descriptor(model="other")
    )


def test_physical_payload_keeps_primary_portable_outcome_separate():
    m=load()
    payload=m.build_physical_metadata_payload(
        embedding_descriptor=embedding_descriptor(digest=m.EMBEDDING_DIGEST),
        model_descriptor=model_descriptor(),
        portable_primary_outcome="SUPPORTED",
        terminal_model_invoked=True,
        terminal_model_request_count=1,
    )
    assert payload["portable_primary_outcome"]=="SUPPORTED"
    assert payload["physical_metadata"]["embedding_model"]==m.EMBEDDING_MODEL
    assert payload["physical_metadata"]["terminal_model"]==m.TERMINAL_MODEL
    assert payload["physical_metadata"]["terminal_model_invoked"] is True
    assert payload["physical_metadata"]["terminal_model_request_count"]==1
    assert "physical_primary_outcome" not in payload

class FakePhysicalEmbeddingAdapter:
    def __init__(self):
        self.vector=tuple([1.0]+[0.0]*1023)
    def inspect(self):
        return embedding_descriptor(
            digest="ac6da0dfba84a81fdbfbaf330198c33cd77c4cdfc53e8bc50eb581914a15621d",
            dimension=1024,
        )
    def embed(self,request):
        from flywire_asca.embedding import EmbeddingResponse, normalize_embedding_values
        vectors=tuple(
            normalize_embedding_values(self.vector,expected_dimension=1024)
            for _ in request.texts
        )
        return EmbeddingResponse(
            request.request_id,
            "qwen3-embedding:0.6b",
            "ac6da0dfba84a81fdbfbaf330198c33cd77c4cdfc53e8bc50eb581914a15621d",
            vectors,len(vectors),0,0,0,
        )


class FakePhysicalModelAdapter:
    def __init__(self):
        self.calls=0
    def inspect(self):
        return model_descriptor()
    def generate(self,request):
        from flywire_asca.model import ModelResponse
        self.calls+=1
        return ModelResponse(
            request.request_id,"qwen3.5:4b","model-digest",
            "physical diagnostic","stop",1,1,1,0,0,0,
        )


def test_physical_qualification_runs_retrieval_success_and_terminal_fallback_with_fakes():
    m=load()
    embedding=FakePhysicalEmbeddingAdapter()
    model=FakePhysicalModelAdapter()
    payload=m.run_physical_qualification(
        embedding_adapter=embedding,
        model_adapter=model,
        portable_primary_outcome="SUPPORTED",
    )
    assert payload["physical_prerequisites_valid"] is True
    assert payload["physical_integration"]["success_case_completed"] is True
    assert payload["physical_integration"]["success_case_attempt_count"]==1
    assert payload["physical_integration"]["fallback_case_exhausted"] is True
    assert payload["physical_integration"]["fallback_case_attempt_count"]==3
    assert payload["physical_integration"]["terminal_model_invoked"] is True
    assert payload["physical_integration"]["terminal_model_request_count"]==1
    assert model.calls==1
    assert payload["portable_primary_outcome"]=="SUPPORTED"
