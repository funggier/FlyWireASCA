import argparse
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/"src"
if str(SRC) not in sys.path:
    sys.path.insert(0,str(SRC))

from flywire_asca.contracts import (
    Cue, CueKind, MemoryKind, MemoryRecord, ObservationKind, ProcedureRef,
)
from flywire_asca.embedding import (
    EmbeddingDescriptor, OllamaEmbeddingAdapter,
)
from flywire_asca.familiarity import ExactFamiliarityIndex, FamiliarityTrace
from flywire_asca.integrated_loop import (
    ActionMemoryRequirement,
    CognitiveLoopRequest,
    CognitiveTerminationReason,
    ContextBoundProcedureExecutorFactory,
    IntegratedRetrievalContext,
    IntegratedRetrievalCue,
    IntegratedRetrievalCueTier,
    LoopPolicy,
    ModelUsePolicy,
    run_cognitive_loop,
)
from flywire_asca.model import ModelDescriptor, OllamaModelAdapter
from flywire_asca.procedural_memory import (
    ExpectedOutcome,
    ProcedureDefinition,
    ProcedureLibrary,
    ProcedureStep,
    ProcedureStepKind,
    SimulatedActionDefinition,
    SimulatedWorldState,
)
from flywire_asca.uncertainty_expansion import build_a007_primary_profile
from flywire_asca.vector_memory import ExactVectorMemoryIndex, VectorMemoryDocument

EMBEDDING_MODEL="qwen3-embedding:0.6b"
EMBEDDING_DIGEST="ac6da0dfba84a81fdbfbaf330198c33cd77c4cdfc53e8bc50eb581914a15621d"
EMBEDDING_DIMENSION=1024
MINIMUM_SIMILARITY=0.5037018224299838
TERMINAL_MODEL="qwen3.5:4b"
PRIMARY_SELECTOR="SINGLE_BEST"
PRIMARY_PROCEDURE_MODE="CHUNKED"
PHYSICAL_FIXTURE_VERSION="a009-physical-v1"
PHYSICAL_ANCHOR_TEXT="FlyWireASCA A009 physical integration anchor memory"


def validate_embedding_descriptor(descriptor):
    errors=[]
    if not isinstance(descriptor,EmbeddingDescriptor):
        return ["embedding descriptor must be an EmbeddingDescriptor"]
    if descriptor.model_name!=EMBEDDING_MODEL:
        errors.append("embedding model_name mismatch")
    if descriptor.model_digest!=EMBEDDING_DIGEST:
        errors.append("embedding model_digest mismatch")
    if descriptor.embedding_dimension!=EMBEDDING_DIMENSION:
        errors.append("embedding dimension mismatch")
    return errors


def validate_terminal_model_descriptor(descriptor):
    errors=[]
    if not isinstance(descriptor,ModelDescriptor):
        return ["terminal model descriptor must be a ModelDescriptor"]
    if descriptor.model_name!=TERMINAL_MODEL:
        errors.append("terminal model_name mismatch")
    return errors


def build_physical_metadata_payload(
    *,
    embedding_descriptor,
    model_descriptor,
    portable_primary_outcome,
    terminal_model_invoked,
    terminal_model_request_count,
):
    if portable_primary_outcome not in {"SUPPORTED","MIXED","NOT_SUPPORTED"}:
        raise ValueError("portable_primary_outcome has invalid vocabulary")
    if not isinstance(terminal_model_request_count,int) or isinstance(terminal_model_request_count,bool) or terminal_model_request_count<0:
        raise ValueError("terminal_model_request_count must be nonnegative")
    errors=validate_embedding_descriptor(embedding_descriptor)
    errors.extend(validate_terminal_model_descriptor(model_descriptor))
    return {
        "qualification_scope":"physical_integrated_cognitive_loop_a009",
        "fixture_version":PHYSICAL_FIXTURE_VERSION,
        "portable_primary_outcome":portable_primary_outcome,
        "physical_metadata":{
            "embedding_model":embedding_descriptor.model_name,
            "embedding_digest":embedding_descriptor.model_digest,
            "embedding_dimension":embedding_descriptor.embedding_dimension,
            "minimum_similarity":MINIMUM_SIMILARITY,
            "terminal_model":model_descriptor.model_name,
            "terminal_model_digest":model_descriptor.model_digest,
            "terminal_model_invoked":bool(terminal_model_invoked),
            "terminal_model_request_count":terminal_model_request_count,
            "primary_selector":PRIMARY_SELECTOR,
            "primary_procedure_mode":PRIMARY_PROCEDURE_MODE,
        },
        "physical_prerequisites_valid":not errors,
        "errors":errors,
        "claims_boundary":"physical integration/model metadata is secondary evidence and cannot change the portable A009 primary outcome",
    }


class _MemoryTextProvider:
    def resolve(self,memory_id):
        return PHYSICAL_ANCHOR_TEXT if memory_id=="mem-physical" else None


def _library():
    return ProcedureLibrary((
        ProcedureDefinition(
            ProcedureRef("physical-root","physical-root","1"),
            (
                ProcedureStep(
                    "act",
                    ProcedureStepKind.ACTION,
                    ExpectedOutcome("act-ok",ObservationKind.RESULT,"done"),
                    action_ref="physical-action",
                ),
            ),
            ExpectedOutcome("root-done",ObservationKind.RESULT,"done"),
        ),
    ))


def _factory(required_memory_id):
    return ContextBoundProcedureExecutorFactory(
        (
            SimulatedActionDefinition(
                "physical-action",
                (("done","yes"),),
                ObservationKind.RESULT,
                "done",
            ),
        ),
        (),
        SimulatedWorldState((("done","no"),)),
        (
            ActionMemoryRequirement(
                "physical-action",
                (required_memory_id,),
                ObservationKind.RESULT,
                "missing-memory",
            ),
        ),
    )


def _retrieval_context(embedding_adapter):
    index=ExactVectorMemoryIndex(
        (
            VectorMemoryDocument(
                MemoryRecord(
                    "mem-physical",
                    MemoryKind.SEMANTIC,
                    "content:physical-anchor",
                    1.0,
                ),
                PHYSICAL_ANCHOR_TEXT,
            ),
        ),
        embedding_adapter,
        embedding_profile=PHYSICAL_FIXTURE_VERSION,
    )
    tiers=tuple(
        IntegratedRetrievalCueTier(
            i,
            (
                IntegratedRetrievalCue(
                    f"physical-source-{i}",
                    f"physical-query-{i}",
                    PHYSICAL_ANCHOR_TEXT,
                ),
            ),
        )
        for i in range(3)
    )
    return IntegratedRetrievalContext(
        index,
        tiers,
        MINIMUM_SIMILARITY,
    )


def _familiarity_index():
    return ExactFamiliarityIndex((
        FamiliarityTrace(
            "physical-trace",
            CueKind.TEXT,
            "physical goal",
            "physical-region",
        ),
    ))


def _request(loop_id,model_policy):
    return CognitiveLoopRequest(
        loop_id,
        "physical integration goal",
        Cue("physical-cue",CueKind.TEXT,"physical goal",1.0),
        "physical-root",
        LoopPolicy.MISMATCH_DRIVEN_RECOVERY,
        model_policy,
    )


def run_physical_qualification(
    *,
    embedding_adapter,
    model_adapter,
    portable_primary_outcome,
):
    embedding_descriptor=embedding_adapter.inspect()
    model_descriptor=model_adapter.inspect()
    payload=build_physical_metadata_payload(
        embedding_descriptor=embedding_descriptor,
        model_descriptor=model_descriptor,
        portable_primary_outcome=portable_primary_outcome,
        terminal_model_invoked=False,
        terminal_model_request_count=0,
    )
    if not payload["physical_prerequisites_valid"]:
        return payload

    context=_retrieval_context(embedding_adapter)
    common=dict(
        familiarity_index=_familiarity_index(),
        retrieval_context=context,
        expansion_profile=build_a007_primary_profile(),
        procedure_library=_library(),
        memory_context_provider=_MemoryTextProvider(),
    )
    success=run_cognitive_loop(
        _request("a009-physical-success",ModelUsePolicy.DISABLED),
        procedure_executor_factory=_factory("mem-physical"),
        model_adapter=None,
        **common,
    )
    fallback=run_cognitive_loop(
        _request("a009-physical-fallback",ModelUsePolicy.TERMINAL_ONLY),
        procedure_executor_factory=_factory("mem-never"),
        model_adapter=model_adapter,
        **common,
    )
    integration={
        "success_case_completed":success.termination_reason is CognitiveTerminationReason.PROCEDURE_COMPLETED,
        "success_case_attempt_count":len(success.procedure_attempts),
        "success_case_scope_count":len(success.scope_evaluations),
        "success_case_final_working_set_ids":[entry.ref_id for entry in success.final_working_set.entries],
        "fallback_case_exhausted":fallback.termination_reason is CognitiveTerminationReason.PROCEDURE_MISMATCH_EXHAUSTED,
        "fallback_case_attempt_count":len(fallback.procedure_attempts),
        "fallback_case_scope_count":len(fallback.scope_evaluations),
        "terminal_model_invoked":fallback.model_response is not None,
        "terminal_model_request_count":1 if fallback.model_response is not None else 0,
        "terminal_model_response_nonempty":bool(fallback.model_response and fallback.model_response.content.strip()),
        "terminal_model_prompt_tokens":fallback.model_response.prompt_tokens if fallback.model_response else None,
        "terminal_model_generated_tokens":fallback.model_response.generated_tokens if fallback.model_response else None,
        "terminal_model_total_duration_ns":fallback.model_response.total_duration_ns if fallback.model_response else None,
    }
    payload["physical_integration"]=integration
    payload["physical_metadata"]["terminal_model_invoked"]=integration["terminal_model_invoked"]
    payload["physical_metadata"]["terminal_model_request_count"]=integration["terminal_model_request_count"]
    evidence_ok=(
        integration["success_case_completed"]
        and integration["success_case_attempt_count"]==1
        and "mem-physical" in integration["success_case_final_working_set_ids"]
        and integration["fallback_case_exhausted"]
        and integration["fallback_case_attempt_count"]==3
        and integration["terminal_model_invoked"]
        and integration["terminal_model_request_count"]==1
        and integration["terminal_model_response_nonempty"]
    )
    if not evidence_ok:
        payload["errors"].append("physical integrated-loop evidence did not satisfy frozen secondary checks")
    payload["physical_integration_valid"]=evidence_ok
    return payload


def inspect_live_prerequisites(*,portable_primary_outcome):
    embedding=OllamaEmbeddingAdapter(
        EMBEDDING_MODEL,
        expected_digest=EMBEDDING_DIGEST,
        expected_dimension=EMBEDDING_DIMENSION,
        keep_alive="6h",
    )
    model=OllamaModelAdapter(
        TERMINAL_MODEL,
        keep_alive="6h",
    )
    return run_physical_qualification(
        embedding_adapter=embedding,
        model_adapter=model,
        portable_primary_outcome=portable_primary_outcome,
    )


def _emit(payload,output_path):
    data=(json.dumps(payload,ensure_ascii=False,sort_keys=True,separators=(",",":"))+"\n").encode("utf-8")
    stream=getattr(sys.stdout,"buffer",None)
    if stream is not None:
        stream.write(data); stream.flush()
    else:
        sys.stdout.write(data.decode("utf-8"))
    if output_path is not None:
        output_path.parent.mkdir(parents=True,exist_ok=True)
        output_path.write_bytes(data)


def main(argv=None):
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",type=Path)
    parser.add_argument("--portable-primary-outcome",default="SUPPORTED",choices=("SUPPORTED","MIXED","NOT_SUPPORTED"))
    args=parser.parse_args(argv)
    try:
        payload=inspect_live_prerequisites(
            portable_primary_outcome=args.portable_primary_outcome
        )
    except Exception as exc:
        payload={
            "qualification_scope":"physical_integrated_cognitive_loop_a009",
            "fixture_version":PHYSICAL_FIXTURE_VERSION,
            "portable_primary_outcome":args.portable_primary_outcome,
            "physical_prerequisites_valid":False,
            "errors":[f"{type(exc).__name__}: {exc}"],
            "claims_boundary":"physical prerequisites/integration were not accepted; portable primary outcome is unchanged",
        }
    _emit(payload,args.output)
    return 0 if payload.get("physical_prerequisites_valid") and payload.get("physical_integration_valid") else 1


if __name__=="__main__":
    raise SystemExit(main())
