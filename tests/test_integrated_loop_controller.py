from __future__ import annotations

from flywire_asca.contracts import Cue, CueKind, MemoryKind, MemoryRecord, ObservationKind, ProcedureRef
from flywire_asca.embedding import (
    EmbeddingDescriptor,
    EmbeddingResponse,
    normalize_embedding_values,
)
from flywire_asca.familiarity import ExactFamiliarityIndex, FamiliarityTrace
from flywire_asca.integrated_loop import (
    ActionMemoryRequirement,
    CognitiveTerminationReason,
    CognitiveTraceEventKind,
    ContextBoundProcedureExecutorFactory,
    IntegratedRetrievalContext,
    IntegratedRetrievalCue,
    IntegratedRetrievalCueTier,
    LoopPolicy,
    ModelUsePolicy,
    run_cognitive_loop,
)
from flywire_asca.model import ModelResponse
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


class FakeEmbeddingAdapter:
    def __init__(self, vectors):
        self.vectors = vectors

    def inspect(self):
        return EmbeddingDescriptor(
            "fake",
            "1",
            "a009-controller-embedder",
            "controller-digest",
            "fixture",
            0,
            None,
            None,
            1024,
            3,
            ("embedding",),
        )

    def embed(self, request):
        vectors = tuple(
            normalize_embedding_values(self.vectors[text], expected_dimension=3)
            for text in request.texts
        )
        return EmbeddingResponse(
            request.request_id,
            "a009-controller-embedder",
            "controller-digest",
            vectors,
            len(vectors),
            0,
            0,
            0,
        )


class CountingFamiliarityIndex(ExactFamiliarityIndex):
    def __init__(self, traces):
        super().__init__(traces)
        self.calls = 0

    def assess(self, cue):
        self.calls += 1
        return super().assess(cue)


class FakeModelAdapter:
    def __init__(self, content: str):
        self.content = content
        self.requests = []

    def generate(self, request):
        self.requests.append(request)
        return ModelResponse(
            request.request_id,
            "fake-terminal-model",
            "terminal-digest",
            self.content,
            "stop",
            10,
            3,
            1,
            0,
            0,
            0,
        )


class MemoryTextProvider:
    def resolve(self, memory_id: str) -> str | None:
        return {
            "mem-base": "base memory",
            "mem-middle": "middle memory",
            "mem-finish": "finish memory",
        }.get(memory_id)


def _basis(name: str):
    return {
        "base": (1.0, 0.0, 0.0),
        "middle": (0.0, 1.0, 0.0),
        "finish": (0.0, 0.0, 1.0),
        "none": (-1.0, -1.0, -1.0),
    }[name]


def _document(memory_id: str, text: str) -> VectorMemoryDocument:
    return VectorMemoryDocument(
        MemoryRecord(memory_id, MemoryKind.SEMANTIC, f"content:{memory_id}", 1.0),
        text,
    )


def _retrieval_context(
    targets: tuple[str, str, str] = ("base", "finish", "finish"),
) -> IntegratedRetrievalContext:
    vectors = {
        "doc-base": _basis("base"),
        "doc-middle": _basis("middle"),
        "doc-finish": _basis("finish"),
        "cue-0": _basis(targets[0]),
        "cue-1": _basis(targets[1]),
        "cue-2": _basis(targets[2]),
    }
    index = ExactVectorMemoryIndex(
        (
            _document("mem-base", "doc-base"),
            _document("mem-middle", "doc-middle"),
            _document("mem-finish", "doc-finish"),
        ),
        FakeEmbeddingAdapter(vectors),
        embedding_profile="a009-controller",
    )
    return IntegratedRetrievalContext(
        index,
        (
            IntegratedRetrievalCueTier(
                0, (IntegratedRetrievalCue("source-0", "query-0", "cue-0"),)
            ),
            IntegratedRetrievalCueTier(
                1, (IntegratedRetrievalCue("source-1", "query-1", "cue-1"),)
            ),
            IntegratedRetrievalCueTier(
                2, (IntegratedRetrievalCue("source-2", "query-2", "cue-2"),)
            ),
        ),
        0.9,
    )


def _familiarity(*, familiar: bool = True) -> CountingFamiliarityIndex:
    traces = (
        (
            FamiliarityTrace(
                "trace-goal",
                CueKind.TEXT,
                "goal",
                "region-goal",
            ),
        )
        if familiar
        else ()
    )
    return CountingFamiliarityIndex(traces)


def _procedure_library() -> ProcedureLibrary:
    outcome = ExpectedOutcome("act-ok", ObservationKind.RESULT, "done")
    return ProcedureLibrary(
        (
            ProcedureDefinition(
                ProcedureRef("root", "root", "1"),
                (
                    ProcedureStep(
                        "act",
                        ProcedureStepKind.ACTION,
                        outcome,
                        action_ref="act",
                    ),
                ),
                ExpectedOutcome("root-done", ObservationKind.RESULT, "done"),
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


def _request(
    policy: LoopPolicy,
    *,
    model_use_policy: ModelUsePolicy = ModelUsePolicy.DISABLED,
):
    from flywire_asca.integrated_loop import CognitiveLoopRequest

    return CognitiveLoopRequest(
        "loop",
        "prepare goal",
        Cue("goal-cue", CueKind.TEXT, "goal", 1.0),
        "root",
        policy,
        model_use_policy,
    )


def _run(
    *,
    policy: LoopPolicy = LoopPolicy.MISMATCH_DRIVEN_RECOVERY,
    required_memory_id: str = "mem-base",
    targets: tuple[str, str, str] = ("base", "finish", "finish"),
    familiar: bool = True,
    model_use_policy: ModelUsePolicy = ModelUsePolicy.DISABLED,
    model_adapter=None,
):
    familiarity = _familiarity(familiar=familiar)
    result = run_cognitive_loop(
        _request(policy, model_use_policy=model_use_policy),
        familiarity_index=familiarity,
        retrieval_context=_retrieval_context(targets),
        expansion_profile=build_a007_primary_profile(),
        procedure_library=_procedure_library(),
        procedure_executor_factory=_factory(required_memory_id),
        model_adapter=model_adapter,
        memory_context_provider=MemoryTextProvider(),
    )
    return result, familiarity


def _kinds(result):
    return tuple(event.kind for event in result.trace)


def test_easy_success_assesses_familiarity_once_and_uses_one_chunked_attempt():
    result, familiarity = _run(required_memory_id="mem-base")
    assert familiarity.calls == 1
    assert len(result.scope_evaluations) == 1
    assert len(result.procedure_attempts) == 1
    assert result.procedure_attempts[0].execution_id == "loop:procedure-attempt:0"
    assert result.termination_reason is CognitiveTerminationReason.PROCEDURE_COMPLETED
    assert result.model_response is None
    assert _kinds(result) == (
        CognitiveTraceEventKind.FAMILIARITY_ASSESSED,
        CognitiveTraceEventKind.INITIAL_EXPANSION_SCOPE_EVALUATED,
        CognitiveTraceEventKind.INITIAL_EXPANSION_TERMINATED,
        CognitiveTraceEventKind.ROOT_PROCEDURE_SELECTED,
        CognitiveTraceEventKind.PROCEDURE_ATTEMPT_STARTED,
        CognitiveTraceEventKind.PROCEDURE_COMPLETED,
        CognitiveTraceEventKind.TERMINAL_STATE_REACHED,
    )


def test_unfamiliar_input_still_runs_semantic_retrieval_and_succeeds():
    result, familiarity = _run(required_memory_id="mem-base", familiar=False)
    assert familiarity.calls == 1
    assert result.familiarity.retrieval_state.value == "UNFAMILIAR"
    assert result.scope_evaluations[0].retrieval_results
    assert result.termination_reason is CognitiveTerminationReason.PROCEDURE_COMPLETED


def test_mismatch_driven_recovery_advances_one_scope_then_stops_on_success():
    result, _ = _run(
        required_memory_id="mem-finish",
        targets=("base", "finish", "finish"),
    )
    assert tuple(item.scope.round_index for item in result.scope_evaluations) == (0, 1)
    assert tuple(item.attempt_index for item in result.procedure_attempts) == (0, 1)
    assert tuple(item.execution_id for item in result.procedure_attempts) == (
        "loop:procedure-attempt:0",
        "loop:procedure-attempt:1",
    )
    assert result.procedure_attempts[0].execution.state.value == "INTERRUPTED"
    assert result.procedure_attempts[1].execution.state.value == "COMPLETED"
    assert result.termination_reason is CognitiveTerminationReason.RECOVERED_AFTER_MISMATCH
    assert CognitiveTraceEventKind.RECOVERY_SCOPE_FORCED in _kinds(result)


def test_mismatch_driven_recovery_can_use_second_and_final_recovery_scope():
    result, _ = _run(
        required_memory_id="mem-finish",
        targets=("base", "middle", "finish"),
    )
    assert tuple(item.scope.round_index for item in result.scope_evaluations) == (0, 1, 2)
    assert tuple(item.attempt_index for item in result.procedure_attempts) == (0, 1, 2)
    assert len({item.execution_id for item in result.procedure_attempts}) == 3
    assert result.termination_reason is CognitiveTerminationReason.RECOVERED_AFTER_MISMATCH


def test_persistent_mismatch_is_bounded_to_three_attempts_and_scope_two():
    result, _ = _run(
        required_memory_id="mem-never",
        targets=("base", "middle", "finish"),
    )
    assert tuple(item.scope.round_index for item in result.scope_evaluations) == (0, 1, 2)
    assert len(result.procedure_attempts) == 3
    assert max(item.scope.round_index for item in result.procedure_attempts) == 2
    assert all(item.execution.state.value == "INTERRUPTED" for item in result.procedure_attempts)
    assert result.termination_reason is CognitiveTerminationReason.PROCEDURE_MISMATCH_EXHAUSTED


def test_initial_max_scope_mismatch_does_not_replay():
    result, _ = _run(
        required_memory_id="mem-never",
        targets=("none", "none", "none"),
    )
    assert tuple(item.scope.round_index for item in result.scope_evaluations) == (0, 1, 2)
    assert len(result.procedure_attempts) == 1
    assert result.procedure_attempts[0].scope.round_index == 2
    assert result.termination_reason is CognitiveTerminationReason.PROCEDURE_MISMATCH_EXHAUSTED


def test_no_recovery_control_terminates_after_first_mismatch():
    result, _ = _run(
        policy=LoopPolicy.NO_PROCEDURE_RECOVERY,
        required_memory_id="mem-finish",
        targets=("base", "finish", "finish"),
    )
    assert tuple(item.scope.round_index for item in result.scope_evaluations) == (0,)
    assert len(result.procedure_attempts) == 1
    assert result.termination_reason is CognitiveTerminationReason.PROCEDURE_MISMATCH_EXHAUSTED


def test_always_max_scope_control_evaluates_all_scopes_then_attempts_once():
    result, _ = _run(
        policy=LoopPolicy.ALWAYS_MAX_SCOPE,
        required_memory_id="mem-finish",
        targets=("base", "middle", "finish"),
    )
    assert tuple(item.scope.round_index for item in result.scope_evaluations) == (0, 1, 2)
    assert len(result.procedure_attempts) == 1
    assert result.procedure_attempts[0].scope.round_index == 2
    assert result.termination_reason is CognitiveTerminationReason.PROCEDURE_COMPLETED


def test_terminal_model_fallback_is_called_once_and_cannot_change_control_result():
    first_model = FakeModelAdapter("first diagnostic")
    second_model = FakeModelAdapter("different diagnostic")

    first, _ = _run(
        required_memory_id="mem-never",
        targets=("base", "middle", "finish"),
        model_use_policy=ModelUsePolicy.TERMINAL_ONLY,
        model_adapter=first_model,
    )
    second, _ = _run(
        required_memory_id="mem-never",
        targets=("base", "middle", "finish"),
        model_use_policy=ModelUsePolicy.TERMINAL_ONLY,
        model_adapter=second_model,
    )

    assert len(first_model.requests) == 1
    assert len(second_model.requests) == 1
    assert first_model.requests[0].request_id == "loop:terminal-model"
    prompt = "\n".join(message.content for message in first_model.requests[0].messages)
    for expected in (
        "prepare goal",
        "FAMILIAR",
        "mem-base",
        "mem-middle",
        "mem-finish",
        "root",
        "act",
        "done",
        "missing-memory",
    ):
        assert expected in prompt
    assert first.termination_reason is CognitiveTerminationReason.PROCEDURE_MISMATCH_EXHAUSTED
    assert second.termination_reason is first.termination_reason
    assert first.scope_evaluations == second.scope_evaluations
    assert first.procedure_attempts == second.procedure_attempts
    assert first.trace == second.trace
    assert first.model_response is not None
    assert second.model_response is not None
    assert first.model_response.content != second.model_response.content
    assert _kinds(first).count(CognitiveTraceEventKind.MODEL_FALLBACK_INVOKED) == 1


def test_success_path_never_calls_terminal_model_even_when_policy_allows_it():
    model = FakeModelAdapter("must not be used")
    result, _ = _run(
        required_memory_id="mem-base",
        model_use_policy=ModelUsePolicy.TERMINAL_ONLY,
        model_adapter=model,
    )
    assert model.requests == []
    assert result.model_response is None

class WrongRequestIdModel(FakeModelAdapter):
    def generate(self, request):
        self.requests.append(request)
        return ModelResponse(
            "wrong-request-id",
            "fake-terminal-model",
            "terminal-digest",
            self.content,
            "stop",
            10,
            3,
            1,
            0,
            0,
            0,
        )


def test_terminal_model_response_request_id_mismatch_fails_closed():
    import pytest

    with pytest.raises(ValueError, match="request_id"):
        _run(
            required_memory_id="mem-never",
            targets=("base", "middle", "finish"),
            model_use_policy=ModelUsePolicy.TERMINAL_ONLY,
            model_adapter=WrongRequestIdModel("diagnostic"),
        )
