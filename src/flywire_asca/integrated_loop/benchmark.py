from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from collections.abc import Iterable

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
    EmbeddingResponse,
    normalize_embedding_values,
)
from flywire_asca.familiarity import ExactFamiliarityIndex, FamiliarityTrace
from flywire_asca.model import ModelResponse
from flywire_asca.procedural_memory import (
    ExpectedOutcome,
    ProcedureDefinition,
    ProcedureExecutionMode,
    ProcedureExecutionState,
    ProcedureLibrary,
    ProcedureStep,
    ProcedureStepKind,
    SimulatedActionDefinition,
    SimulatedWorldState,
    run_procedure,
)
from flywire_asca.uncertainty_expansion import build_a007_primary_profile
from flywire_asca.vector_memory import ExactVectorMemoryIndex, VectorMemoryDocument

from .controller import run_cognitive_loop
from .models import (
    CognitiveLoopRequest,
    CognitiveTerminationReason,
    LoopPolicy,
    ModelUsePolicy,
)
from .procedure import ActionMemoryRequirement, ContextBoundProcedureExecutorFactory
from .retrieval import (
    IntegratedRetrievalContext,
    IntegratedRetrievalCue,
    IntegratedRetrievalCueTier,
)


@dataclass(frozen=True, slots=True)
class BenchmarkMemorySpec:
    memory_id: str
    retrieval_text: str
    vector: tuple[float, ...]
    content_ref: str
    display_text: str


@dataclass(frozen=True, slots=True)
class IntegratedLoopBenchmarkCase:
    case_id: str
    familiar: bool
    cue_targets: tuple[str, str, str]
    memories: tuple[BenchmarkMemorySpec, ...]
    required_memory_ids: tuple[str, ...]
    expected_recoverable: bool = False
    same_name_expected_ids: tuple[str, ...] = ()
    terminal_model: bool = False
    invalid_root: bool = False


@dataclass(frozen=True, slots=True)
class IntegratedLoopPolicyCaseResult:
    policy: LoopPolicy
    termination_reason: CognitiveTerminationReason
    evaluated_scope_indices: tuple[int, ...]
    forced_recovery_scope_count: int
    procedure_attempt_count: int
    execution_ids: tuple[str, ...]
    procedure_states: tuple[str, ...]
    final_working_set_ids: tuple[str, ...]
    final_world_state_ref: str | None
    procedure_success: bool
    final_state_correct: bool
    same_name_ambiguity_preserved: bool
    model_fallback_called: bool
    trace_signature: tuple[tuple[str, tuple[str, ...]], ...]


@dataclass(frozen=True, slots=True)
class IntegratedLoopBenchmarkCaseResult:
    case_id: str
    recoverable: bool
    validation_error_observed: bool
    validation_error: str | None
    policy_results: tuple[IntegratedLoopPolicyCaseResult, ...]
    chunked_flat_equivalent: bool | None
    model_control_isolated: bool | None


@dataclass(frozen=True, slots=True)
class IntegratedLoopBenchmarkReport:
    case_results: tuple[IntegratedLoopBenchmarkCaseResult, ...]
    case_count: int
    valid_case_count: int
    invalid_case_count: int
    recoverable_case_count: int
    genuine_recovery_count: int
    regression_count: int
    primary_recoverable_success_count: int
    always_recoverable_success_count: int
    primary_total_scope_evaluations: int
    always_total_scope_evaluations: int
    primary_success_count: int
    always_success_count: int
    primary_final_state_correct_count: int
    primary_same_name_ambiguity_failure_count: int
    chunked_flat_diagnostic_case_count: int
    chunked_flat_equivalence_count: int
    max_procedure_attempt_count: int
    max_scope_index: int
    duplicate_execution_id_failure_count: int
    model_fallback_call_count: int
    model_control_leakage_failure_count: int
    deterministic_repeat_match: bool


class _FixtureEmbeddingAdapter:
    def __init__(self, vectors: dict[str, tuple[float, ...]]) -> None:
        self._vectors = vectors
        dimensions = {len(value) for value in vectors.values()}
        if len(dimensions) != 1:
            raise ValueError("fixture vectors must have one dimension")
        self._dimension = next(iter(dimensions))

    def inspect(self) -> EmbeddingDescriptor:
        return EmbeddingDescriptor(
            backend_name="deterministic-fixture",
            backend_version="1",
            model_name="a009-deterministic-embedder",
            model_digest="a009-deterministic-embedder-v1",
            architecture="fixture",
            parameter_count=0,
            parameter_size=None,
            quantization=None,
            context_length=1024,
            embedding_dimension=self._dimension,
            capabilities=("embedding",),
        )

    def embed(self, request) -> EmbeddingResponse:
        vectors = tuple(
            normalize_embedding_values(
                self._vectors[text],
                expected_dimension=self._dimension,
            )
            for text in request.texts
        )
        return EmbeddingResponse(
            request_id=request.request_id,
            model_name="a009-deterministic-embedder",
            model_digest="a009-deterministic-embedder-v1",
            vectors=vectors,
            input_count=len(vectors),
            prompt_tokens=0,
            total_duration_ns=0,
            load_duration_ns=0,
        )


class _FixtureModelAdapter:
    def __init__(self, content: str = "deterministic terminal diagnostic") -> None:
        self.call_count = 0
        self.content = content

    def generate(self, request):
        self.call_count += 1
        return ModelResponse(
            request_id=request.request_id,
            model_name="a009-deterministic-terminal-model",
            model_digest="a009-deterministic-terminal-model-v1",
            content=self.content,
            finish_reason="stop",
            prompt_tokens=0,
            generated_tokens=0,
            total_duration_ns=0,
            load_duration_ns=0,
            prompt_eval_duration_ns=0,
            eval_duration_ns=0,
        )


class _FixtureMemoryContext:
    def __init__(self, case: IntegratedLoopBenchmarkCase) -> None:
        self._texts = {item.memory_id: item.display_text for item in case.memories}

    def resolve(self, memory_id: str) -> str | None:
        return self._texts.get(memory_id)


def _memory(
    memory_id: str,
    retrieval_text: str,
    vector: tuple[float, ...],
    *,
    display_text: str | None = None,
) -> BenchmarkMemorySpec:
    return BenchmarkMemorySpec(
        memory_id=memory_id,
        retrieval_text=retrieval_text,
        vector=vector,
        content_ref=f"content:{memory_id}",
        display_text=display_text or memory_id,
    )


_BASE = (1.0, 0.0, 0.0)
_MIDDLE = (0.0, 1.0, 0.0)
_FINISH = (0.0, 0.0, 1.0)
_NONE = (-1.0, -1.0, -1.0)


def _standard_memories() -> tuple[BenchmarkMemorySpec, ...]:
    return (
        _memory("mem-base", "doc-base", _BASE),
        _memory("mem-middle", "doc-middle", _MIDDLE),
        _memory("mem-finish", "doc-finish", _FINISH),
    )


def build_a009_deterministic_fixture() -> tuple[IntegratedLoopBenchmarkCase, ...]:
    standard = _standard_memories()
    same_name = (
        _memory("mem-alex-a", "alex-a", _BASE, display_text="Alex"),
        _memory("mem-alex-b", "alex-b", _BASE, display_text="Alex"),
        _memory("mem-middle", "doc-middle", _MIDDLE),
        _memory("mem-finish", "doc-finish", _FINISH),
    )
    return (
        IntegratedLoopBenchmarkCase(
            "easy-familiar-success",
            True,
            ("base", "base", "base"),
            standard,
            ("mem-base",),
        ),
        IntegratedLoopBenchmarkCase(
            "unfamiliar-semantic-success",
            False,
            ("base", "base", "base"),
            standard,
            ("mem-base",),
        ),
        IntegratedLoopBenchmarkCase(
            "structural-expansion-success",
            True,
            ("none", "finish", "finish"),
            standard,
            ("mem-finish",),
        ),
        IntegratedLoopBenchmarkCase(
            "procedure-recovery-round-one",
            True,
            ("base", "finish", "finish"),
            standard,
            ("mem-finish",),
            expected_recoverable=True,
        ),
        IntegratedLoopBenchmarkCase(
            "procedure-recovery-round-two",
            True,
            ("base", "middle", "finish"),
            standard,
            ("mem-finish",),
            expected_recoverable=True,
        ),
        IntegratedLoopBenchmarkCase(
            "persistent-procedure-mismatch",
            True,
            ("base", "middle", "finish"),
            standard,
            ("mem-never",),
        ),
        IntegratedLoopBenchmarkCase(
            "max-scope-mismatch",
            True,
            ("none", "none", "none"),
            standard,
            ("mem-never",),
        ),
        IntegratedLoopBenchmarkCase(
            "same-name-ambiguity-preserved",
            True,
            ("base", "base", "base"),
            same_name,
            ("mem-alex-a",),
            same_name_expected_ids=("mem-alex-a", "mem-alex-b"),
        ),
        IntegratedLoopBenchmarkCase(
            "model-terminal-fallback",
            True,
            ("base", "middle", "finish"),
            standard,
            ("mem-never",),
            terminal_model=True,
        ),
        IntegratedLoopBenchmarkCase(
            "invalid-contract",
            True,
            ("base", "base", "base"),
            standard,
            ("mem-base",),
            invalid_root=True,
        ),
    )


def _canonical_fixture_payload(
    cases: tuple[IntegratedLoopBenchmarkCase, ...],
) -> list[dict[str, object]]:
    return [
        {
            "case_id": case.case_id,
            "familiar": case.familiar,
            "cue_targets": case.cue_targets,
            "memories": [
                {
                    "memory_id": memory.memory_id,
                    "retrieval_text": memory.retrieval_text,
                    "vector": memory.vector,
                    "content_ref": memory.content_ref,
                    "display_text": memory.display_text,
                }
                for memory in case.memories
            ],
            "required_memory_ids": case.required_memory_ids,
            "expected_recoverable": case.expected_recoverable,
            "same_name_expected_ids": case.same_name_expected_ids,
            "terminal_model": case.terminal_model,
            "invalid_root": case.invalid_root,
        }
        for case in cases
    ]


def fixture_fingerprint(cases: Iterable[IntegratedLoopBenchmarkCase]) -> str:
    materialized = tuple(cases)
    payload = json.dumps(
        _canonical_fixture_payload(materialized),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _procedure_library() -> ProcedureLibrary:
    return ProcedureLibrary(
        (
            ProcedureDefinition(
                procedure=ProcedureRef("root", "root", "1"),
                steps=(
                    ProcedureStep(
                        step_id="act",
                        kind=ProcedureStepKind.ACTION,
                        expected_outcome=ExpectedOutcome(
                            "act-ok",
                            ObservationKind.RESULT,
                            "done",
                        ),
                        action_ref="act",
                    ),
                ),
                completion_outcome=ExpectedOutcome(
                    "root-done",
                    ObservationKind.RESULT,
                    "done",
                ),
            ),
        )
    )


def _factory(case: IntegratedLoopBenchmarkCase) -> ContextBoundProcedureExecutorFactory:
    return ContextBoundProcedureExecutorFactory(
        action_definitions=(
            SimulatedActionDefinition(
                action_ref="act",
                writes=(("done", "yes"),),
                observation_kind=ObservationKind.RESULT,
                success_payload_ref="done",
            ),
        ),
        completion_probes=(),
        initial_state=SimulatedWorldState((("done", "no"),)),
        requirements=(
            ActionMemoryRequirement(
                action_ref="act",
                required_memory_ids=case.required_memory_ids,
                failure_observation_kind=ObservationKind.RESULT,
                failure_payload_ref="missing-memory",
            ),
        ),
    )


def _retrieval_context(case: IntegratedLoopBenchmarkCase) -> IntegratedRetrievalContext:
    targets = {
        "base": _BASE,
        "middle": _MIDDLE,
        "finish": _FINISH,
        "none": _NONE,
    }
    vectors: dict[str, tuple[float, ...]] = {
        memory.retrieval_text: memory.vector for memory in case.memories
    }
    vectors.update(
        {
            f"cue-{index}": targets[target]
            for index, target in enumerate(case.cue_targets)
        }
    )
    documents = tuple(
        VectorMemoryDocument(
            memory=MemoryRecord(
                memory_id=memory.memory_id,
                kind=MemoryKind.SEMANTIC,
                content_ref=memory.content_ref,
                proposition_confidence=1.0,
            ),
            retrieval_text=memory.retrieval_text,
        )
        for memory in case.memories
    )
    index = ExactVectorMemoryIndex(
        documents,
        _FixtureEmbeddingAdapter(vectors),
        embedding_profile="a009-deterministic-v1",
    )
    return IntegratedRetrievalContext(
        index=index,
        cue_tiers=tuple(
            IntegratedRetrievalCueTier(
                tier_index=index_,
                cues=(
                    IntegratedRetrievalCue(
                        source_cue_id=f"source-{index_}",
                        query_id=f"query-{index_}",
                        query_text=f"cue-{index_}",
                    ),
                ),
            )
            for index_ in range(3)
        ),
        minimum_similarity=0.9,
    )


def _familiarity_index(case: IntegratedLoopBenchmarkCase) -> ExactFamiliarityIndex:
    traces = (
        (
            FamiliarityTrace(
                trace_id=f"trace:{case.case_id}",
                cue_kind=CueKind.TEXT,
                surface_value="goal",
                region_id="region:goal",
            ),
        )
        if case.familiar
        else ()
    )
    return ExactFamiliarityIndex(traces)


def _request(case: IntegratedLoopBenchmarkCase, policy: LoopPolicy) -> CognitiveLoopRequest:
    return CognitiveLoopRequest(
        loop_id=f"a009:{case.case_id}:{policy.value}",
        goal_text=f"goal for {case.case_id}",
        familiarity_cue=Cue(
            cue_id=f"cue:{case.case_id}",
            kind=CueKind.TEXT,
            value="goal",
            confidence=1.0,
        ),
        root_procedure_id="missing-root" if case.invalid_root else "root",
        policy=policy,
        model_use_policy=(
            ModelUsePolicy.TERMINAL_ONLY
            if case.terminal_model
            else ModelUsePolicy.DISABLED
        ),
    )


def _trace_signature(result) -> tuple[tuple[str, tuple[str, ...]], ...]:
    return tuple((event.kind.value, event.refs) for event in result.trace)


def _result_for_policy(
    case: IntegratedLoopBenchmarkCase,
    policy: LoopPolicy,
    *,
    model_content: str = "deterministic terminal diagnostic",
) -> IntegratedLoopPolicyCaseResult:
    model = _FixtureModelAdapter(model_content) if case.terminal_model else None
    result = run_cognitive_loop(
        _request(case, policy),
        familiarity_index=_familiarity_index(case),
        retrieval_context=_retrieval_context(case),
        expansion_profile=build_a007_primary_profile(),
        procedure_library=_procedure_library(),
        procedure_executor_factory=_factory(case),
        model_adapter=model,
        memory_context_provider=_FixtureMemoryContext(case),
    )
    attempt = result.procedure_attempts[-1]
    success = attempt.execution.state is ProcedureExecutionState.COMPLETED
    success_state_ref = _factory(case).create(
        available_memory_ids=case.required_memory_ids,
        execution_id="expected-success",
    )
    run_procedure(
        _procedure_library(),
        root_procedure_id="root",
        mode=ProcedureExecutionMode.CHUNKED,
        executor=success_state_ref,
        execution_id="expected-success",
    )
    expected_success_ref = success_state_ref.world_state_ref()
    final_ids = tuple(entry.ref_id for entry in result.final_working_set.entries)
    same_name_ok = set(case.same_name_expected_ids).issubset(final_ids)
    return IntegratedLoopPolicyCaseResult(
        policy=policy,
        termination_reason=result.termination_reason,
        evaluated_scope_indices=tuple(
            evaluation.scope.round_index
            for evaluation in result.scope_evaluations
        ),
        forced_recovery_scope_count=sum(
            event.kind.value == "RECOVERY_SCOPE_FORCED"
            for event in result.trace
        ),
        procedure_attempt_count=len(result.procedure_attempts),
        execution_ids=tuple(item.execution_id for item in result.procedure_attempts),
        procedure_states=tuple(
            item.execution.state.value for item in result.procedure_attempts
        ),
        final_working_set_ids=final_ids,
        final_world_state_ref=result.final_world_state_ref,
        procedure_success=success,
        final_state_correct=(success and result.final_world_state_ref == expected_success_ref)
        or not success,
        same_name_ambiguity_preserved=(
            same_name_ok if case.same_name_expected_ids else True
        ),
        model_fallback_called=(model.call_count == 1 if model is not None else False),
        trace_signature=_trace_signature(result),
    )


def _primitive_refs(execution) -> tuple[str, ...]:
    return tuple(
        item.action_ref
        for item in execution.step_results
        if item.action_ref is not None
    )


def _chunked_flat_equivalent(
    case: IntegratedLoopBenchmarkCase,
    primary: IntegratedLoopPolicyCaseResult,
) -> bool | None:
    if not primary.procedure_success:
        return None
    factory = _factory(case)
    chunked_executor = factory.create(
        available_memory_ids=primary.final_working_set_ids,
        execution_id="diag-chunked",
    )
    flat_executor = factory.create(
        available_memory_ids=primary.final_working_set_ids,
        execution_id="diag-flat",
    )
    chunked = run_procedure(
        _procedure_library(),
        root_procedure_id="root",
        mode=ProcedureExecutionMode.CHUNKED,
        executor=chunked_executor,
        execution_id="diag-chunked",
    )
    flat = run_procedure(
        _procedure_library(),
        root_procedure_id="root",
        mode=ProcedureExecutionMode.FLAT,
        executor=flat_executor,
        execution_id="diag-flat",
    )
    return (
        chunked.state is flat.state
        and chunked.final_world_state_ref == flat.final_world_state_ref
        and _primitive_refs(chunked) == _primitive_refs(flat)
    )


def _run_case(case: IntegratedLoopBenchmarkCase) -> IntegratedLoopBenchmarkCaseResult:
    if case.invalid_root:
        try:
            _result_for_policy(case, LoopPolicy.MISMATCH_DRIVEN_RECOVERY)
        except ValueError as exc:
            return IntegratedLoopBenchmarkCaseResult(
                case_id=case.case_id,
                recoverable=case.expected_recoverable,
                validation_error_observed=True,
                validation_error=str(exc),
                policy_results=(),
                chunked_flat_equivalent=None,
                model_control_isolated=None,
            )
        return IntegratedLoopBenchmarkCaseResult(
            case_id=case.case_id,
            recoverable=case.expected_recoverable,
            validation_error_observed=False,
            validation_error=None,
            policy_results=(),
            chunked_flat_equivalent=None,
            model_control_isolated=None,
        )

    policy_results = tuple(
        _result_for_policy(case, policy)
        for policy in (
            LoopPolicy.NO_PROCEDURE_RECOVERY,
            LoopPolicy.MISMATCH_DRIVEN_RECOVERY,
            LoopPolicy.ALWAYS_MAX_SCOPE,
        )
    )
    primary = policy_results[1]
    model_control_isolated: bool | None = None
    if case.terminal_model:
        alternate = _result_for_policy(
            case,
            LoopPolicy.MISMATCH_DRIVEN_RECOVERY,
            model_content="different deterministic terminal diagnostic",
        )
        model_control_isolated = alternate == primary
    return IntegratedLoopBenchmarkCaseResult(
        case_id=case.case_id,
        recoverable=case.expected_recoverable,
        validation_error_observed=False,
        validation_error=None,
        policy_results=policy_results,
        chunked_flat_equivalent=_chunked_flat_equivalent(case, primary),
        model_control_isolated=model_control_isolated,
    )


def _policy_result(
    case: IntegratedLoopBenchmarkCaseResult,
    policy: LoopPolicy,
) -> IntegratedLoopPolicyCaseResult:
    return next(item for item in case.policy_results if item.policy is policy)


def run_a009_benchmark(
    cases: Iterable[IntegratedLoopBenchmarkCase],
) -> IntegratedLoopBenchmarkReport:
    materialized = tuple(cases)
    ids = tuple(case.case_id for case in materialized)
    if len(ids) != len(set(ids)):
        raise ValueError("case_id values must be unique")
    first = tuple(_run_case(case) for case in materialized)
    second = tuple(_run_case(case) for case in materialized)
    deterministic = first == second

    valid = tuple(item for item in first if not item.validation_error_observed)
    invalid = tuple(item for item in first if item.validation_error_observed)
    recoverable = tuple(item for item in valid if item.recoverable)

    genuine_recovery = 0
    regression = 0
    primary_recoverable_success = 0
    always_recoverable_success = 0
    primary_scope_total = 0
    always_scope_total = 0
    primary_success = 0
    always_success = 0
    final_state_correct = 0
    ambiguity_failures = 0
    diag_cases = 0
    diag_equal = 0
    max_attempts = 0
    max_scope = 0
    duplicate_ids = 0
    model_calls = 0
    model_control_leakage_failures = 0

    for case in valid:
        no = _policy_result(case, LoopPolicy.NO_PROCEDURE_RECOVERY)
        primary = _policy_result(case, LoopPolicy.MISMATCH_DRIVEN_RECOVERY)
        always = _policy_result(case, LoopPolicy.ALWAYS_MAX_SCOPE)
        primary_scope_total += len(primary.evaluated_scope_indices)
        always_scope_total += len(always.evaluated_scope_indices)
        primary_success += int(primary.procedure_success)
        always_success += int(always.procedure_success)
        final_state_correct += int(
            primary.procedure_success and primary.final_state_correct
        )
        ambiguity_failures += int(not primary.same_name_ambiguity_preserved)
        max_attempts = max(max_attempts, primary.procedure_attempt_count)
        max_scope = max(max_scope, *primary.evaluated_scope_indices)
        duplicate_ids += int(
            len(primary.execution_ids) != len(set(primary.execution_ids))
        )
        model_calls += int(primary.model_fallback_called)
        model_control_leakage_failures += int(
            case.model_control_isolated is False
        )
        if no.procedure_success and not primary.procedure_success:
            regression += 1
        if (
            not no.procedure_success
            and primary.procedure_success
            and primary.forced_recovery_scope_count > 0
            and len(primary.execution_ids) == len(set(primary.execution_ids))
        ):
            genuine_recovery += 1
        if case.recoverable:
            primary_recoverable_success += int(primary.procedure_success)
            always_recoverable_success += int(always.procedure_success)
        if case.chunked_flat_equivalent is not None:
            diag_cases += 1
            diag_equal += int(case.chunked_flat_equivalent)

    return IntegratedLoopBenchmarkReport(
        case_results=first,
        case_count=len(first),
        valid_case_count=len(valid),
        invalid_case_count=len(invalid),
        recoverable_case_count=len(recoverable),
        genuine_recovery_count=genuine_recovery,
        regression_count=regression,
        primary_recoverable_success_count=primary_recoverable_success,
        always_recoverable_success_count=always_recoverable_success,
        primary_total_scope_evaluations=primary_scope_total,
        always_total_scope_evaluations=always_scope_total,
        primary_success_count=primary_success,
        always_success_count=always_success,
        primary_final_state_correct_count=final_state_correct,
        primary_same_name_ambiguity_failure_count=ambiguity_failures,
        chunked_flat_diagnostic_case_count=diag_cases,
        chunked_flat_equivalence_count=diag_equal,
        max_procedure_attempt_count=max_attempts,
        max_scope_index=max_scope,
        duplicate_execution_id_failure_count=duplicate_ids,
        model_fallback_call_count=model_calls,
        model_control_leakage_failure_count=model_control_leakage_failures,
        deterministic_repeat_match=deterministic,
    )


def classify_a009_hypothesis(report: IntegratedLoopBenchmarkReport) -> str:
    if report.genuine_recovery_count <= 0:
        return "NOT_SUPPORTED"
    supported = (
        report.regression_count == 0
        and report.primary_recoverable_success_count
        == report.always_recoverable_success_count
        and report.primary_recoverable_success_count == report.recoverable_case_count
        and report.primary_total_scope_evaluations
        < report.always_total_scope_evaluations
        and report.duplicate_execution_id_failure_count == 0
        and report.max_procedure_attempt_count <= 3
        and report.max_scope_index <= 2
        and report.primary_final_state_correct_count == report.primary_success_count
        and report.primary_same_name_ambiguity_failure_count == 0
        and report.model_control_leakage_failure_count == 0
        and report.chunked_flat_equivalence_count
        == report.chunked_flat_diagnostic_case_count
        and report.deterministic_repeat_match is True
    )
    return "SUPPORTED" if supported else "MIXED"


def qualify_a009_report(report: IntegratedLoopBenchmarkReport) -> list[str]:
    errors: list[str] = []
    int_fields = (
        "case_count",
        "valid_case_count",
        "invalid_case_count",
        "recoverable_case_count",
        "genuine_recovery_count",
        "regression_count",
        "primary_recoverable_success_count",
        "always_recoverable_success_count",
        "primary_total_scope_evaluations",
        "always_total_scope_evaluations",
        "primary_success_count",
        "always_success_count",
        "primary_final_state_correct_count",
        "primary_same_name_ambiguity_failure_count",
        "chunked_flat_diagnostic_case_count",
        "chunked_flat_equivalence_count",
        "max_procedure_attempt_count",
        "max_scope_index",
        "duplicate_execution_id_failure_count",
        "model_fallback_call_count",
        "model_control_leakage_failure_count",
    )
    for name in int_fields:
        value = getattr(report, name)
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            errors.append(f"{name} must be a nonnegative integer")
    if report.case_count != report.valid_case_count + report.invalid_case_count:
        errors.append("case_count must equal valid_case_count + invalid_case_count")
    if report.recoverable_case_count > report.valid_case_count:
        errors.append("recoverable_case_count cannot exceed valid_case_count")
    if report.primary_recoverable_success_count > report.recoverable_case_count:
        errors.append(
            "primary_recoverable_success_count cannot exceed recoverable_case_count"
        )
    if report.always_recoverable_success_count > report.recoverable_case_count:
        errors.append(
            "always_recoverable_success_count cannot exceed recoverable_case_count"
        )
    if report.genuine_recovery_count > report.valid_case_count:
        errors.append("genuine_recovery_count cannot exceed valid_case_count")
    if report.regression_count > report.valid_case_count:
        errors.append("regression_count cannot exceed valid_case_count")
    if report.primary_success_count > report.valid_case_count:
        errors.append("primary_success_count cannot exceed valid_case_count")
    if report.always_success_count > report.valid_case_count:
        errors.append("always_success_count cannot exceed valid_case_count")
    if report.primary_final_state_correct_count > report.primary_success_count:
        errors.append(
            "primary_final_state_correct_count cannot exceed primary_success_count"
        )
    if (
        report.chunked_flat_equivalence_count
        > report.chunked_flat_diagnostic_case_count
    ):
        errors.append(
            "chunked_flat_equivalence_count cannot exceed diagnostic case count"
        )
    if report.max_procedure_attempt_count > 3:
        errors.append("max_procedure_attempt_count must be <= 3")
    if report.max_scope_index > 2:
        errors.append("max_scope_index must be <= 2")
    if report.model_control_leakage_failure_count != 0:
        errors.append("model_control_leakage_failure_count must be 0")
    if not isinstance(report.deterministic_repeat_match, bool):
        errors.append("deterministic_repeat_match must be bool")
    return errors
