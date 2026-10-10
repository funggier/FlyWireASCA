from __future__ import annotations

from dataclasses import dataclass

import pytest

from flywire_asca.baseline_comparison import ComparisonVariant
from flywire_asca.baseline_comparison.dense import (
    evaluate_dense_exhaustive,
    run_dense_exhaustive,
)
from flywire_asca.contracts import (
    MemoryKind,
    MemoryRecord,
    ObservationKind,
    ProcedureRef,
)
from flywire_asca.embedding import (
    EmbeddingDescriptor,
    EmbeddingResponse,
    normalize_embedding_values,
)
from flywire_asca.integrated_loop import (
    ActionMemoryRequirement,
    ContextBoundProcedureExecutorFactory,
    IntegratedRetrievalContext,
    IntegratedRetrievalCue,
    IntegratedRetrievalCueTier,
)
from flywire_asca.procedural_memory import (
    ExpectedOutcome,
    ProcedureDefinition,
    ProcedureLibrary,
    ProcedureStep,
    ProcedureStepKind,
    SimulatedActionDefinition,
    SimulatedWorldState,
)
from flywire_asca.vector_memory import (
    ExactVectorMemoryIndex,
    VectorMemoryDocument,
)


class FakeEmbeddingAdapter:
    def __init__(self, vectors: dict[str, tuple[float, ...]]) -> None:
        self.vectors = vectors
        dimensions = {len(item) for item in vectors.values()}
        self.dimension = next(iter(dimensions)) if dimensions else 2

    def inspect(self) -> EmbeddingDescriptor:
        return EmbeddingDescriptor(
            backend_name="fixture",
            backend_version="1",
            model_name="fixture-embed",
            model_digest="fixture-digest",
            architecture="fixture",
            parameter_count=0,
            parameter_size=None,
            quantization=None,
            context_length=1024,
            embedding_dimension=self.dimension,
            capabilities=("embedding",),
        )

    def embed(self, request) -> EmbeddingResponse:
        values = tuple(
            normalize_embedding_values(
                self.vectors[text],
                expected_dimension=self.dimension,
            )
            for text in request.texts
        )
        return EmbeddingResponse(
            request_id=request.request_id,
            model_name="fixture-embed",
            model_digest="fixture-digest",
            vectors=values,
            input_count=len(values),
            prompt_tokens=0,
            total_duration_ns=0,
            load_duration_ns=0,
        )


class TrackingIndex(ExactVectorMemoryIndex):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.queries = []

    def search(self, query):
        self.queries.append(query)
        return super().search(query)


def _context(
    *,
    document_count: int,
    tier_count: int = 3,
    same_name: bool = False,
) -> IntegratedRetrievalContext:
    vectors: dict[str, tuple[float, ...]] = {}
    documents = []
    for index in range(document_count):
        memory_id = f"mem-{index:02d}"
        text = "Alex" if same_name and index < 2 else f"doc-{index:02d}"
        vectors[text] = (1.0, 0.0)
        documents.append(
            VectorMemoryDocument(
                MemoryRecord(
                    memory_id,
                    MemoryKind.SEMANTIC,
                    f"content:{memory_id}",
                    1.0,
                ),
                text,
            )
        )
    for index in range(tier_count):
        vectors[f"cue-{index}"] = (1.0, 0.0)
    index = TrackingIndex(
        tuple(documents),
        FakeEmbeddingAdapter(vectors),
        embedding_profile="a010-test",
    )
    tiers = tuple(
        IntegratedRetrievalCueTier(
            index_,
            (
                IntegratedRetrievalCue(
                    f"source-{index_}",
                    f"query-{index_}",
                    f"cue-{index_}",
                ),
            ),
        )
        for index_ in range(tier_count)
    )
    return IntegratedRetrievalContext(index, tiers, 0.9)


def _library() -> ProcedureLibrary:
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


def _factory(required_memory_id: str) -> ContextBoundProcedureExecutorFactory:
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
                (required_memory_id,),
                ObservationKind.RESULT,
                "missing-memory",
            ),
        ),
    )


def test_dense_retrieval_uses_all_tiers_full_index_top_k_and_keeps_40_candidates():
    context = _context(document_count=40)
    result = evaluate_dense_exhaustive(context)

    assert len(result.retrieval_results) == 3
    assert [query.top_k for query in context.index.queries] == [40, 40, 40]
    assert [query.minimum_similarity for query in context.index.queries] == [
        0.9,
        0.9,
        0.9,
    ]
    assert all(item.returned_count == 40 for item in result.retrieval_results)
    assert result.working_set_result.selected_count == 40
    assert len(result.working_set_result.working_set.entries) == 40


def test_dense_retrieval_empty_index_uses_positive_top_k_and_valid_empty_working_set():
    context = _context(document_count=0)
    result = evaluate_dense_exhaustive(context)

    assert [query.top_k for query in context.index.queries] == [1, 1, 1]
    assert all(item.returned_count == 0 for item in result.retrieval_results)
    assert result.working_set_result.selected_count == 0
    assert result.working_set_result.working_set.entries == ()


def test_dense_retrieval_preserves_distinct_same_name_memory_ids():
    context = _context(document_count=2, same_name=True)
    result = evaluate_dense_exhaustive(context)

    assert {
        entry.ref_id for entry in result.working_set_result.working_set.entries
    } == {"mem-00", "mem-01"}


def test_dense_runner_executes_one_chunked_attempt_without_recovery():
    context = _context(document_count=3)
    result = run_dense_exhaustive(
        case_id="dense-success",
        root_procedure_id="root",
        retrieval_context=context,
        procedure_library=_library(),
        procedure_executor_factory=_factory("mem-00"),
    )

    assert result.variant is ComparisonVariant.DENSE_EXHAUSTIVE
    assert result.procedure_success is True
    assert result.final_state_correct is True
    assert result.evaluated_scope_indices == (2,)
    assert result.procedure_attempt_count == 1
    assert result.execution_ids == (
        "a010:dense-success:dense:procedure-attempt:0",
    )
    assert result.procedure_states == ("COMPLETED",)
    assert result.mismatch_count == 0
    assert result.forced_recovery_scope_count == 0
    assert {"mem-00", "mem-01", "mem-02"}.issubset(
        result.final_selected_memory_ids
    )


def test_dense_runner_records_interruption_without_replay():
    context = _context(document_count=2)
    result = run_dense_exhaustive(
        case_id="dense-fail",
        root_procedure_id="root",
        retrieval_context=context,
        procedure_library=_library(),
        procedure_executor_factory=_factory("mem-never"),
    )

    assert result.procedure_success is False
    assert result.final_state_correct is False
    assert result.procedure_attempt_count == 1
    assert result.procedure_states == ("INTERRUPTED",)
    assert result.mismatch_count == 1
    assert result.forced_recovery_scope_count == 0


def test_dense_runner_fails_closed_on_unknown_root_and_malformed_context():
    context = _context(document_count=1)
    with pytest.raises(ValueError, match="unknown procedure_id"):
        run_dense_exhaustive(
            case_id="bad-root",
            root_procedure_id="missing",
            retrieval_context=context,
            procedure_library=_library(),
            procedure_executor_factory=_factory("mem-00"),
        )
    with pytest.raises(ValueError, match="retrieval_context"):
        run_dense_exhaustive(
            case_id="bad-context",
            root_procedure_id="root",
            retrieval_context=object(),
            procedure_library=_library(),
            procedure_executor_factory=_factory("mem-00"),
        )
