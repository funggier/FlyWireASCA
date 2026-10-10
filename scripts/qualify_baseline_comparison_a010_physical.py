import argparse
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from flywire_asca.baseline_comparison import (
    run_asca_primary,
    run_dense_exhaustive,
)
from flywire_asca.contracts import (
    Cue,
    CueKind,
    MemoryKind,
    MemoryRecord,
    ObservationKind,
    ProcedureRef,
)
from flywire_asca.embedding import (
    EmbeddingDescriptor,
    OllamaEmbeddingAdapter,
)
from flywire_asca.familiarity import ExactFamiliarityIndex, FamiliarityTrace
from flywire_asca.integrated_loop import (
    ActionMemoryRequirement,
    CognitiveLoopRequest,
    ContextBoundProcedureExecutorFactory,
    IntegratedRetrievalContext,
    IntegratedRetrievalCue,
    IntegratedRetrievalCueTier,
    LoopPolicy,
    ModelUsePolicy,
)
from flywire_asca.procedural_memory import (
    DeterministicProcedureSimulator,
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

EMBEDDING_MODEL = "qwen3-embedding:0.6b"
EMBEDDING_DIGEST = "ac6da0dfba84a81fdbfbaf330198c33cd77c4cdfc53e8bc50eb581914a15621d"
EMBEDDING_DIMENSION = 1024
MINIMUM_SIMILARITY = 0.5037018224299838
PHYSICAL_FIXTURE_VERSION = "a010-physical-v1"

_TARGET = "FlyWireASCA A010 physical target memory"
_DISTRACTOR_1 = "FlyWireASCA A010 physical distractor memory one"
_DISTRACTOR_2 = "FlyWireASCA A010 physical distractor memory two"


def validate_embedding_descriptor(descriptor):
    errors = []
    if not isinstance(descriptor, EmbeddingDescriptor):
        return ["embedding descriptor must be an EmbeddingDescriptor"]
    if descriptor.model_name != EMBEDDING_MODEL:
        errors.append("embedding model_name mismatch")
    if descriptor.model_digest != EMBEDDING_DIGEST:
        errors.append("embedding model_digest mismatch")
    if descriptor.embedding_dimension != EMBEDDING_DIMENSION:
        errors.append("embedding dimension mismatch")
    return errors


def _context(adapter):
    documents = (
        VectorMemoryDocument(
            MemoryRecord(
                "mem-000-target",
                MemoryKind.SEMANTIC,
                "content:physical-target",
                1.0,
            ),
            _TARGET,
        ),
        VectorMemoryDocument(
            MemoryRecord(
                "mem-001-distractor",
                MemoryKind.SEMANTIC,
                "content:physical-distractor-1",
                1.0,
            ),
            _DISTRACTOR_1,
        ),
        VectorMemoryDocument(
            MemoryRecord(
                "mem-002-distractor",
                MemoryKind.SEMANTIC,
                "content:physical-distractor-2",
                1.0,
            ),
            _DISTRACTOR_2,
        ),
    )
    index = ExactVectorMemoryIndex(
        documents,
        adapter,
        embedding_profile=PHYSICAL_FIXTURE_VERSION,
    )
    query_texts = (_TARGET, _DISTRACTOR_1, _DISTRACTOR_2)
    tiers = tuple(
        IntegratedRetrievalCueTier(
            index_,
            (
                IntegratedRetrievalCue(
                    f"physical-source-{index_}",
                    f"physical-query-{index_}",
                    text,
                ),
            ),
        )
        for index_, text in enumerate(query_texts)
    )
    return IntegratedRetrievalContext(
        index,
        tiers,
        MINIMUM_SIMILARITY,
    )


def _library():
    return ProcedureLibrary(
        (
            ProcedureDefinition(
                ProcedureRef("root", "root", "1"),
                (
                    ProcedureStep(
                        "act",
                        ProcedureStepKind.ACTION,
                        ExpectedOutcome(
                            "act-ok",
                            ObservationKind.RESULT,
                            "done",
                        ),
                        action_ref="act",
                    ),
                ),
                ExpectedOutcome(
                    "root-done",
                    ObservationKind.RESULT,
                    "done",
                ),
            ),
        )
    )


def _factory():
    return ContextBoundProcedureExecutorFactory(
        (
            SimulatedActionDefinition(
                "act",
                (("done", "yes"),),
                ObservationKind.RESULT,
                "done",
            ),
        ),
        (),
        SimulatedWorldState((("done", "no"),)),
        (
            ActionMemoryRequirement(
                "act",
                ("mem-000-target",),
                ObservationKind.RESULT,
                "missing-memory",
            ),
        ),
    )


def _expected_final_world_state_ref():
    return DeterministicProcedureSimulator(
        (),
        (),
        SimulatedWorldState((("done", "yes"),)),
    ).world_state_ref()


def _request():
    return CognitiveLoopRequest(
        "a009:a010-physical:MISMATCH_DRIVEN_RECOVERY",
        "A010 physical comparison goal",
        Cue(
            "a010-physical-cue",
            CueKind.TEXT,
            "physical goal",
            1.0,
        ),
        "root",
        LoopPolicy.MISMATCH_DRIVEN_RECOVERY,
        ModelUsePolicy.DISABLED,
    )


def _familiarity():
    return ExactFamiliarityIndex(
        (
            FamiliarityTrace(
                "a010-physical-trace",
                CueKind.TEXT,
                "physical goal",
                "physical-region",
            ),
        )
    )


def _run_payload(run, duration_ns):
    return {
        "procedure_success": run.procedure_success,
        "final_state_correct": run.final_state_correct,
        "query_count": run.query_count,
        "scored_vector_count": run.scored_vector_count_sum,
        "cumulative_selected_count": run.cumulative_selected_count,
        "peak_selected_count": run.peak_selected_count,
        "procedure_attempt_count": run.procedure_attempt_count,
        "final_selected_memory_ids": list(run.final_selected_memory_ids),
        "runner_duration_ns": duration_ns,
    }


def run_physical_qualification(
    *,
    embedding_adapter,
    portable_primary_outcome,
):
    if portable_primary_outcome not in {"SUPPORTED", "MIXED", "NOT_SUPPORTED"}:
        raise ValueError("portable_primary_outcome has invalid vocabulary")

    descriptor = embedding_adapter.inspect()
    errors = validate_embedding_descriptor(descriptor)
    payload = {
        "qualification_scope": "physical_dense_nonselective_baseline_a010",
        "fixture_version": PHYSICAL_FIXTURE_VERSION,
        "portable_primary_outcome": portable_primary_outcome,
        "physical_metadata": {
            "embedding_model": descriptor.model_name,
            "embedding_digest": descriptor.model_digest,
            "embedding_dimension": descriptor.embedding_dimension,
            "minimum_similarity": MINIMUM_SIMILARITY,
        },
        "physical_prerequisites_valid": not errors,
        "errors": errors,
        "claims_boundary": (
            "physical comparison/timing is secondary descriptive evidence "
            "and cannot change the frozen portable A010 primary outcome"
        ),
    }
    if errors:
        payload["physical_integration_valid"] = False
        return payload

    context = _context(embedding_adapter)
    library = _library()
    factory = _factory()
    common = dict(
        request=_request(),
        familiarity_index=_familiarity(),
        retrieval_context=context,
        expansion_profile=build_a007_primary_profile(),
        procedure_library=library,
        procedure_executor_factory=factory,
        model_adapter=None,
        memory_context_provider=None,
        expected_final_world_state_ref=_expected_final_world_state_ref(),
        same_name_expected_ids=(),
    )

    start = time.perf_counter_ns()
    asca = run_asca_primary(**common)
    asca_duration = time.perf_counter_ns() - start

    start = time.perf_counter_ns()
    dense = run_dense_exhaustive(
        case_id="a010-physical",
        root_procedure_id="root",
        retrieval_context=context,
        procedure_library=library,
        procedure_executor_factory=factory,
        expected_final_world_state_ref=_expected_final_world_state_ref(),
    )
    dense_duration = time.perf_counter_ns() - start

    comparison = {
        "asca": _run_payload(asca, asca_duration),
        "dense": _run_payload(dense, dense_duration),
    }
    payload["physical_comparison"] = comparison
    valid = (
        asca.procedure_success
        and dense.procedure_success
        and "mem-000-target" in asca.final_selected_memory_ids
        and "mem-000-target" in dense.final_selected_memory_ids
        and dense.query_count == 3
        and asca.query_count >= 1
    )
    if not valid:
        payload["errors"].append(
            "physical comparison did not satisfy frozen integration checks"
        )
    payload["physical_integration_valid"] = valid
    return payload


def inspect_live_prerequisites(*, portable_primary_outcome):
    adapter = OllamaEmbeddingAdapter(
        EMBEDDING_MODEL,
        expected_digest=EMBEDDING_DIGEST,
        expected_dimension=EMBEDDING_DIMENSION,
        keep_alive="6h",
    )
    return run_physical_qualification(
        embedding_adapter=adapter,
        portable_primary_outcome=portable_primary_outcome,
    )


def _emit(payload, output_path):
    data = (
        json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
    ).encode("utf-8")
    stream = getattr(sys.stdout, "buffer", None)
    if stream is not None:
        stream.write(data)
        stream.flush()
    else:
        sys.stdout.write(data.decode("utf-8"))
    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(data)


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument(
        "--portable-primary-outcome",
        default="NOT_SUPPORTED",
        choices=("SUPPORTED", "MIXED", "NOT_SUPPORTED"),
    )
    args = parser.parse_args(argv)
    try:
        payload = inspect_live_prerequisites(
            portable_primary_outcome=args.portable_primary_outcome,
        )
    except Exception as exc:
        payload = {
            "qualification_scope": "physical_dense_nonselective_baseline_a010",
            "fixture_version": PHYSICAL_FIXTURE_VERSION,
            "portable_primary_outcome": args.portable_primary_outcome,
            "physical_prerequisites_valid": False,
            "physical_integration_valid": False,
            "errors": [f"{type(exc).__name__}: {exc}"],
            "claims_boundary": (
                "physical prerequisites/integration were not accepted; "
                "portable A010 outcome is unchanged"
            ),
        }
    _emit(payload, args.output)
    return 0 if (
        payload.get("physical_prerequisites_valid")
        and payload.get("physical_integration_valid")
    ) else 1


if __name__ == "__main__":
    raise SystemExit(main())
