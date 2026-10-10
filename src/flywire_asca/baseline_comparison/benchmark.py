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

from .ablations import (
    run_asca_always_max_scope,
    run_asca_primary,
    run_familiarity_disabled_ablation,
    run_no_structural_expansion_ablation,
)
from .dense import run_dense_exhaustive
from .models import (
    BaselineComparisonReport,
    ComparisonCaseResult,
    ComparisonRunResult,
    ComparisonVariant,
)


@dataclass(frozen=True, slots=True)
class BenchmarkMemorySpec:
    memory_id: str
    retrieval_text: str
    vector: tuple[float, ...]
    content_ref: str
    display_text: str


@dataclass(frozen=True, slots=True)
class BaselineComparisonCase:
    case_id: str
    familiar: bool
    corpus_size: int
    cue_vectors: tuple[tuple[float, ...], tuple[float, ...], tuple[float, ...]]
    memories: tuple[BenchmarkMemorySpec, ...]
    required_memory_ids: tuple[str, ...]
    minimum_similarity: float = 0.9
    root_procedure_id: str = "root"
    same_name_expected_ids: tuple[str, ...] = ()
    expected_primary_case: bool = True
    run_structural_ablation: bool = False
    run_familiarity_ablation: bool = False
    invalid_root: bool = False
    designated_parity_reduction: bool = False
    initial_state_items: tuple[tuple[str, str], ...] = (("done", "no"),)
    expected_final_state_items: tuple[tuple[str, str], ...] = (("done", "yes"),)


_A = (1.0, 0.0, 0.0)
_B = (0.0, 1.0, 0.0)
_C = (0.0, 0.0, 1.0)
_NONE = (-1.0, -1.0, -1.0)


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
            model_name="a010-deterministic-embedder",
            model_digest="a010-deterministic-embedder-v1",
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
            model_name="a010-deterministic-embedder",
            model_digest="a010-deterministic-embedder-v1",
            vectors=vectors,
            input_count=len(vectors),
            prompt_tokens=0,
            total_duration_ns=0,
            load_duration_ns=0,
        )


def _memory(
    memory_id: str,
    vector: tuple[float, ...],
    *,
    retrieval_text: str | None = None,
    display_text: str | None = None,
) -> BenchmarkMemorySpec:
    text = retrieval_text or f"doc:{memory_id}"
    return BenchmarkMemorySpec(
        memory_id=memory_id,
        retrieval_text=text,
        vector=vector,
        content_ref=f"content:{memory_id}",
        display_text=display_text or memory_id,
    )


def _easy_memories(size: int) -> tuple[BenchmarkMemorySpec, ...]:
    return (
        _memory("mem-000-target", _A),
        *tuple(
            _memory(f"mem-{index:03d}-distractor", _B)
            for index in range(1, size)
        ),
    )


def _structural_memories(size: int) -> tuple[BenchmarkMemorySpec, ...]:
    return (
        _memory("mem-000-target", _A),
        *tuple(
            _memory(f"mem-{index:03d}-distractor", _B)
            for index in range(1, size)
        ),
    )


def _recovery_one_memories(size: int) -> tuple[BenchmarkMemorySpec, ...]:
    return (
        _memory("mem-000-base", _A),
        _memory("mem-001-target", _B),
        *tuple(
            _memory(f"mem-{index:03d}-distractor", _C)
            for index in range(2, size)
        ),
    )


def _recovery_two_memories(size: int) -> tuple[BenchmarkMemorySpec, ...]:
    return (
        _memory("mem-000-base", _A),
        _memory("mem-001-middle", _B),
        _memory("mem-002-target", _C),
        *tuple(
            _memory(f"mem-{index:03d}-distractor", _C)
            for index in range(3, size)
        ),
    )


def _persistent_memories(size: int) -> tuple[BenchmarkMemorySpec, ...]:
    return (
        _memory("mem-000-base", _A),
        _memory("mem-001-middle", _B),
        _memory("mem-002-finish", _C),
        *tuple(
            _memory(f"mem-{index:03d}-distractor", _C)
            for index in range(3, size)
        ),
    )


def _sentinel_memories(size: int) -> tuple[BenchmarkMemorySpec, ...]:
    return (
        *tuple(
            _memory(f"mem-{index:03d}-distractor", _B)
            for index in range(size - 1)
        ),
        _memory("mem-999-target", _B),
    )


def _same_name_memories(size: int) -> tuple[BenchmarkMemorySpec, ...]:
    return (
        _memory(
            "mem-000-alex-a",
            _A,
            retrieval_text="Alex",
            display_text="Alex",
        ),
        _memory(
            "mem-001-alex-b",
            _A,
            retrieval_text="Alex",
            display_text="Alex",
        ),
        *tuple(
            _memory(f"mem-{index:03d}-distractor", _B)
            for index in range(2, size)
        ),
    )


def _tie_memories(size: int) -> tuple[BenchmarkMemorySpec, ...]:
    return (
        _memory("mem-000-target", _A),
        _memory("mem-001-tie", _A),
        _memory("mem-002-tie", _A),
        _memory("mem-003-tie", _A),
        *tuple(
            _memory(f"mem-{index:03d}-distractor", _B)
            for index in range(4, size)
        ),
    )


def build_a010_deterministic_fixture() -> tuple[BaselineComparisonCase, ...]:
    return (
        BaselineComparisonCase(
            "easy-local-many-distractors",
            True,
            64,
            (_A, _B, _B),
            _easy_memories(64),
            ("mem-000-target",),
            designated_parity_reduction=True,
        ),
        BaselineComparisonCase(
            "unfamiliar-semantic-many-distractors",
            False,
            64,
            (_A, _B, _B),
            _easy_memories(64),
            ("mem-000-target",),
            designated_parity_reduction=True,
        ),
        BaselineComparisonCase(
            "structural-expansion-required",
            True,
            16,
            (_NONE, _A, _B),
            _structural_memories(16),
            ("mem-000-target",),
            designated_parity_reduction=True,
        ),
        BaselineComparisonCase(
            "procedure-recovery-one-scope",
            True,
            16,
            (_A, _B, _C),
            _recovery_one_memories(16),
            ("mem-001-target",),
            designated_parity_reduction=True,
        ),
        BaselineComparisonCase(
            "procedure-recovery-two-scopes",
            True,
            16,
            (_A, _B, _C),
            _recovery_two_memories(16),
            ("mem-002-target",),
            designated_parity_reduction=True,
        ),
        BaselineComparisonCase(
            "persistent-missing-memory",
            True,
            16,
            (_A, _B, _C),
            _persistent_memories(16),
            ("mem-never",),
        ),
        BaselineComparisonCase(
            "selective-routing-miss-sentinel",
            True,
            256,
            (_B, _B, _B),
            _sentinel_memories(256),
            ("mem-999-target",),
        ),
        BaselineComparisonCase(
            "same-name-identity",
            True,
            16,
            (_A, _B, _B),
            _same_name_memories(16),
            ("mem-000-alex-a",),
            same_name_expected_ids=("mem-000-alex-a", "mem-001-alex-b"),
            designated_parity_reduction=True,
        ),
        BaselineComparisonCase(
            "tie-heavy-distractors",
            True,
            16,
            (_A, _B, _B),
            _tie_memories(16),
            ("mem-000-target",),
            designated_parity_reduction=True,
        ),
        BaselineComparisonCase(
            "structural-expansion-ablation",
            True,
            16,
            (_NONE, _A, _B),
            _structural_memories(16),
            ("mem-000-target",),
            expected_primary_case=False,
            run_structural_ablation=True,
        ),
        BaselineComparisonCase(
            "familiarity-disabled-equivalence",
            True,
            16,
            (_A, _B, _B),
            _easy_memories(16),
            ("mem-000-target",),
            expected_primary_case=False,
            run_familiarity_ablation=True,
        ),
        BaselineComparisonCase(
            "invalid-contract",
            True,
            16,
            (_A, _B, _B),
            _easy_memories(16),
            ("mem-000-target",),
            root_procedure_id="missing-root",
            expected_primary_case=False,
            invalid_root=True,
        ),
    )


def _shared_payload(case: BaselineComparisonCase) -> dict[str, object]:
    return {
        "case_id": case.case_id,
        "familiar": case.familiar,
        "corpus_size": case.corpus_size,
        "cue_vectors": case.cue_vectors,
        "memories": [
            {
                "memory_id": item.memory_id,
                "retrieval_text": item.retrieval_text,
                "vector": item.vector,
                "content_ref": item.content_ref,
                "display_text": item.display_text,
            }
            for item in case.memories
        ],
        "required_memory_ids": case.required_memory_ids,
        "minimum_similarity": case.minimum_similarity,
        "root_procedure_id": case.root_procedure_id,
        "same_name_expected_ids": case.same_name_expected_ids,
        "initial_state_items": case.initial_state_items,
        "expected_final_state_items": case.expected_final_state_items,
        "execution_contract": _execution_contract_payload(),
    }


def shared_input_fingerprint(case: BaselineComparisonCase) -> str:
    payload = json.dumps(
        _shared_payload(case),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _canonical_fixture_payload(
    cases: tuple[BaselineComparisonCase, ...],
) -> list[dict[str, object]]:
    return [
        _shared_payload(case)
        | {
            "expected_primary_case": case.expected_primary_case,
            "run_structural_ablation": case.run_structural_ablation,
            "run_familiarity_ablation": case.run_familiarity_ablation,
            "invalid_root": case.invalid_root,
            "designated_parity_reduction": case.designated_parity_reduction,
        }
        for case in cases
    ]


def a010_fixture_fingerprint(
    cases: Iterable[BaselineComparisonCase],
) -> str:
    materialized = tuple(cases)
    payload = json.dumps(
        _canonical_fixture_payload(materialized),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _retrieval_context(case: BaselineComparisonCase) -> IntegratedRetrievalContext:
    vectors = {
        item.retrieval_text: item.vector
        for item in case.memories
    }
    vectors.update(
        {f"cue-{index}": vector for index, vector in enumerate(case.cue_vectors)}
    )
    documents = tuple(
        VectorMemoryDocument(
            MemoryRecord(
                item.memory_id,
                MemoryKind.SEMANTIC,
                item.content_ref,
                1.0,
            ),
            item.retrieval_text,
        )
        for item in case.memories
    )
    index = ExactVectorMemoryIndex(
        documents,
        _FixtureEmbeddingAdapter(vectors),
        embedding_profile="a010-deterministic-v1",
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
        for index_ in range(3)
    )
    return IntegratedRetrievalContext(
        index,
        tiers,
        case.minimum_similarity,
    )


def _familiarity_index(case: BaselineComparisonCase) -> ExactFamiliarityIndex:
    traces = (
        (
            FamiliarityTrace(
                f"trace:{case.case_id}",
                CueKind.TEXT,
                "goal",
                "region:goal",
            ),
        )
        if case.familiar
        else ()
    )
    return ExactFamiliarityIndex(traces)


def _request(case: BaselineComparisonCase) -> CognitiveLoopRequest:
    return CognitiveLoopRequest(
        f"a009:{case.case_id}:{LoopPolicy.MISMATCH_DRIVEN_RECOVERY.value}",
        f"goal for {case.case_id}",
        Cue(
            f"cue:{case.case_id}",
            CueKind.TEXT,
            "goal",
            1.0,
        ),
        case.root_procedure_id,
        LoopPolicy.MISMATCH_DRIVEN_RECOVERY,
        ModelUsePolicy.DISABLED,
    )


def _procedure_library() -> ProcedureLibrary:
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


def _action_definitions() -> tuple[SimulatedActionDefinition, ...]:
    return (
        SimulatedActionDefinition(
            "act",
            (("done", "yes"),),
            ObservationKind.RESULT,
            "done",
        ),
    )


def _execution_contract_payload() -> dict[str, object]:
    library = _procedure_library()
    profile = build_a007_primary_profile()
    return {
        "query_texts": tuple(f"cue-{index}" for index in range(3)),
        "procedures": tuple(
            {
                "procedure_id": definition.procedure.procedure_id,
                "name": definition.procedure.name,
                "version": definition.procedure.version,
                "steps": tuple(
                    {
                        "step_id": step.step_id,
                        "kind": step.kind.value,
                        "action_ref": step.action_ref,
                        "callee_procedure_id": step.callee_procedure_id,
                        "expected_kind": step.expected_outcome.observation_kind.value,
                        "expected_payload_ref": step.expected_outcome.expected_payload_ref,
                        "matcher": step.expected_outcome.matcher.value,
                    }
                    for step in definition.steps
                ),
                "completion_kind": definition.completion_outcome.observation_kind.value,
                "completion_payload_ref": definition.completion_outcome.expected_payload_ref,
                "completion_matcher": definition.completion_outcome.matcher.value,
            }
            for definition in library.procedures
        ),
        "actions": tuple(
            {
                "action_ref": action.action_ref,
                "writes": action.writes,
                "observation_kind": action.observation_kind.value,
                "success_payload_ref": action.success_payload_ref,
            }
            for action in _action_definitions()
        ),
        "expansion_profile": {
            "profile_name": profile.profile_name,
            "scopes": tuple(
                {
                    "round_index": scope.round_index,
                    "enabled_cue_tier_count": scope.enabled_cue_tier_count,
                    "top_k": scope.top_k,
                    "max_memory_nodes": scope.budget.max_memory_nodes,
                    "max_working_set_items": scope.budget.max_working_set_items,
                }
                for scope in profile.scopes
            ),
        },
    }


def _expected_world_state_ref(case: BaselineComparisonCase) -> str:
    simulator = DeterministicProcedureSimulator(
        (),
        (),
        SimulatedWorldState(case.expected_final_state_items),
    )
    return simulator.world_state_ref()


def _factory(
    case: BaselineComparisonCase,
) -> ContextBoundProcedureExecutorFactory:
    return ContextBoundProcedureExecutorFactory(
        _action_definitions(),
        (),
        SimulatedWorldState(case.initial_state_items),
        (
            ActionMemoryRequirement(
                "act",
                case.required_memory_ids,
                ObservationKind.RESULT,
                "missing-memory",
            ),
        ),
    )


def _inputs(case: BaselineComparisonCase) -> dict[str, object]:
    return {
        "request": _request(case),
        "familiarity_index": _familiarity_index(case),
        "retrieval_context": _retrieval_context(case),
        "expansion_profile": build_a007_primary_profile(),
        "procedure_library": _procedure_library(),
        "procedure_executor_factory": _factory(case),
        "model_adapter": None,
        "memory_context_provider": None,
        "same_name_expected_ids": case.same_name_expected_ids,
        "expected_final_world_state_ref": _expected_world_state_ref(case),
    }


def _post_completion_failure(run: ComparisonRunResult) -> bool:
    return "COMPLETED" in run.procedure_states[:-1]


def _derive_aggregate(
    case_results: tuple[ComparisonCaseResult, ...],
    *,
    case_specs: dict[str, BaselineComparisonCase],
) -> dict[str, int]:
    valid = tuple(
        item for item in case_results if not item.validation_error_observed
    )
    primary = tuple(
        item
        for item in valid
        if item.expected_primary_case
    )
    asca_runs: list[ComparisonRunResult] = []
    dense_runs: list[ComparisonRunResult] = []
    designated = 0
    identity_failures = 0
    duplicate_failures = 0
    post_completion_failures = 0

    for item in primary:
        by_variant = {run.variant: run for run in item.runs}
        asca = by_variant.get(ComparisonVariant.ASCA_PRIMARY)
        dense = by_variant.get(ComparisonVariant.DENSE_EXHAUSTIVE)
        if asca is None or dense is None:
            continue
        asca_runs.append(asca)
        dense_runs.append(dense)
        if not asca.same_name_identity_preserved or not dense.same_name_identity_preserved:
            identity_failures += 1
        duplicate_failures += int(
            len(asca.execution_ids) != len(set(asca.execution_ids))
        )
        duplicate_failures += int(
            len(dense.execution_ids) != len(set(dense.execution_ids))
        )
        post_completion_failures += int(_post_completion_failure(asca))
        post_completion_failures += int(_post_completion_failure(dense))
        spec = case_specs[item.case_id]
        if (
            spec.designated_parity_reduction
            and asca.procedure_success
            and dense.procedure_success
            and len(asca.final_selected_memory_ids)
            < len(dense.final_selected_memory_ids)
        ):
            designated += 1

    asca_success = sum(item.procedure_success for item in asca_runs)
    dense_success = sum(item.procedure_success for item in dense_runs)
    shared_success = sum(
        a.procedure_success and d.procedure_success
        for a, d in zip(asca_runs, dense_runs)
    )
    dense_only = sum(
        (not a.procedure_success) and d.procedure_success
        for a, d in zip(asca_runs, dense_runs)
    )
    asca_only = sum(
        a.procedure_success and (not d.procedure_success)
        for a, d in zip(asca_runs, dense_runs)
    )
    return {
        "case_count": len(case_results),
        "valid_case_count": len(valid),
        "invalid_case_count": len(case_results) - len(valid),
        "primary_case_count": len(primary),
        "asca_success_count": asca_success,
        "dense_success_count": dense_success,
        "shared_success_count": shared_success,
        "dense_only_success_count": dense_only,
        "asca_only_success_count": asca_only,
        "asca_final_state_correct_count": sum(
            item.final_state_correct for item in asca_runs
        ),
        "dense_final_state_correct_count": sum(
            item.final_state_correct for item in dense_runs
        ),
        "asca_query_count": sum(item.query_count for item in asca_runs),
        "dense_query_count": sum(item.query_count for item in dense_runs),
        "asca_scored_vector_count": sum(
            item.scored_vector_count_sum for item in asca_runs
        ),
        "dense_scored_vector_count": sum(
            item.scored_vector_count_sum for item in dense_runs
        ),
        "asca_cumulative_selected_count": sum(
            item.cumulative_selected_count for item in asca_runs
        ),
        "dense_cumulative_selected_count": sum(
            item.cumulative_selected_count for item in dense_runs
        ),
        "asca_peak_selected_count": max(
            (item.peak_selected_count for item in asca_runs),
            default=0,
        ),
        "dense_peak_selected_count": max(
            (item.peak_selected_count for item in dense_runs),
            default=0,
        ),
        "asca_procedure_attempt_count": sum(
            item.procedure_attempt_count for item in asca_runs
        ),
        "dense_procedure_attempt_count": sum(
            item.procedure_attempt_count for item in dense_runs
        ),
        "identity_failure_count": identity_failures,
        "duplicate_execution_id_failure_count": duplicate_failures,
        "post_completion_extra_attempt_failure_count": post_completion_failures,
        "designated_parity_reduction_count": designated,
    }


def run_a010_benchmark(
    cases: Iterable[BaselineComparisonCase],
) -> BaselineComparisonReport:
    materialized = tuple(cases)
    if not materialized:
        raise ValueError("cases must not be empty")
    case_ids = tuple(case.case_id for case in materialized)
    if len(case_ids) != len(set(case_ids)):
        raise ValueError("case_id values must be unique")

    case_results: list[ComparisonCaseResult] = []
    asca_repeat_ok = True
    dense_repeat_ok = True

    for case in materialized:
        fingerprint = shared_input_fingerprint(case)
        try:
            kwargs = _inputs(case)
            primary = run_asca_primary(**kwargs)
            primary_repeat = run_asca_primary(**kwargs)
            dense = run_dense_exhaustive(
                case_id=case.case_id,
                root_procedure_id=case.root_procedure_id,
                retrieval_context=kwargs["retrieval_context"],
                procedure_library=kwargs["procedure_library"],
                procedure_executor_factory=kwargs["procedure_executor_factory"],
                expected_final_world_state_ref=kwargs["expected_final_world_state_ref"],
                same_name_expected_ids=case.same_name_expected_ids,
            )
            dense_repeat = run_dense_exhaustive(
                case_id=case.case_id,
                root_procedure_id=case.root_procedure_id,
                retrieval_context=kwargs["retrieval_context"],
                procedure_library=kwargs["procedure_library"],
                procedure_executor_factory=kwargs["procedure_executor_factory"],
                expected_final_world_state_ref=kwargs["expected_final_world_state_ref"],
                same_name_expected_ids=case.same_name_expected_ids,
            )
            asca_repeat_ok = asca_repeat_ok and primary == primary_repeat
            dense_repeat_ok = dense_repeat_ok and dense == dense_repeat

            runs: list[ComparisonRunResult] = [
                primary,
                dense,
                run_asca_always_max_scope(**kwargs),
            ]
            if case.run_structural_ablation:
                runs.append(run_no_structural_expansion_ablation(**kwargs))
            if case.run_familiarity_ablation:
                runs.append(run_familiarity_disabled_ablation(**kwargs))
            case_results.append(
                ComparisonCaseResult(
                    case_id=case.case_id,
                    shared_input_fingerprint=fingerprint,
                    validation_error_observed=False,
                    validation_error=None,
                    runs=tuple(runs),
                    expected_primary_case=case.expected_primary_case,
                )
            )
        except ValueError as exc:
            if not case.invalid_root:
                raise
            case_results.append(
                ComparisonCaseResult(
                    case_id=case.case_id,
                    shared_input_fingerprint=fingerprint,
                    validation_error_observed=True,
                    validation_error=str(exc),
                    runs=(),
                    expected_primary_case=case.expected_primary_case,
                )
            )

    result_tuple = tuple(case_results)
    specs = {case.case_id: case for case in materialized}
    aggregate = _derive_aggregate(result_tuple, case_specs=specs)
    return BaselineComparisonReport(
        case_results=result_tuple,
        asca_deterministic_repeat_match=asca_repeat_ok,
        dense_deterministic_repeat_match=dense_repeat_ok,
        **aggregate,
    )


def _bounded_primary_evidence(report: BaselineComparisonReport) -> bool:
    for case in report.case_results:
        if case.validation_error_observed or not case.expected_primary_case:
            continue
        by_variant = {run.variant: run for run in case.runs}
        asca = by_variant.get(ComparisonVariant.ASCA_PRIMARY)
        dense = by_variant.get(ComparisonVariant.DENSE_EXHAUSTIVE)
        if asca is None or dense is None:
            return False
        if asca.procedure_attempt_count > 3:
            return False
        if max(asca.evaluated_scope_indices) > 2:
            return False
        if dense.procedure_attempt_count != 1:
            return False
    return True


def classify_a010_hypothesis(report: BaselineComparisonReport) -> str:
    if not isinstance(report, BaselineComparisonReport):
        raise ValueError("report must be a BaselineComparisonReport")

    has_declared_reduction = (
        report.asca_query_count < report.dense_query_count
        and report.asca_scored_vector_count < report.dense_scored_vector_count
        and report.asca_cumulative_selected_count
        < report.dense_cumulative_selected_count
        and report.designated_parity_reduction_count >= 1
    )
    if not has_declared_reduction:
        return "NOT_SUPPORTED"

    supported = (
        report.dense_only_success_count == 0
        and report.asca_success_count == report.dense_success_count
        and report.shared_success_count == report.dense_success_count
        and report.asca_final_state_correct_count == report.asca_success_count
        and report.dense_final_state_correct_count == report.dense_success_count
        and report.identity_failure_count == 0
        and report.duplicate_execution_id_failure_count == 0
        and report.post_completion_extra_attempt_failure_count == 0
        and report.asca_deterministic_repeat_match
        and report.dense_deterministic_repeat_match
        and _bounded_primary_evidence(report)
    )
    return "SUPPORTED" if supported else "MIXED"


_REPORT_INT_FIELDS = (
    "case_count",
    "valid_case_count",
    "invalid_case_count",
    "primary_case_count",
    "asca_success_count",
    "dense_success_count",
    "shared_success_count",
    "dense_only_success_count",
    "asca_only_success_count",
    "asca_final_state_correct_count",
    "dense_final_state_correct_count",
    "asca_query_count",
    "dense_query_count",
    "asca_scored_vector_count",
    "dense_scored_vector_count",
    "asca_cumulative_selected_count",
    "dense_cumulative_selected_count",
    "asca_peak_selected_count",
    "dense_peak_selected_count",
    "asca_procedure_attempt_count",
    "dense_procedure_attempt_count",
    "identity_failure_count",
    "duplicate_execution_id_failure_count",
    "post_completion_extra_attempt_failure_count",
    "designated_parity_reduction_count",
)


def qualify_a010_report(report: BaselineComparisonReport) -> list[str]:
    if not isinstance(report, BaselineComparisonReport):
        return ["report must be a BaselineComparisonReport"]

    errors: list[str] = []
    frozen_cases = build_a010_deterministic_fixture()
    frozen_by_id = {case.case_id: case for case in frozen_cases}
    observed_ids = tuple(item.case_id for item in report.case_results)
    expected_ids = tuple(case.case_id for case in frozen_cases)
    if observed_ids != expected_ids:
        errors.append("case order/identity does not match frozen A010 fixture")

    for item in report.case_results:
        expected_case = frozen_by_id.get(item.case_id)
        if expected_case is None:
            continue
        expected_fingerprint = shared_input_fingerprint(expected_case)
        if item.shared_input_fingerprint != expected_fingerprint:
            errors.append(
                f"shared input fingerprint mismatch for {item.case_id}"
            )
        if item.expected_primary_case != expected_case.expected_primary_case:
            errors.append(
                f"expected_primary_case mismatch for {item.case_id}"
            )
        if item.validation_error_observed:
            if not expected_case.invalid_root:
                errors.append(
                    f"unexpected validation error for {item.case_id}"
                )
            if item.runs:
                errors.append(
                    f"invalid case must not contain runs for {item.case_id}"
                )
            continue
        if expected_case.invalid_root:
            errors.append(
                f"invalid-contract case did not fail closed: {item.case_id}"
            )
        expected_variants = [
            ComparisonVariant.ASCA_PRIMARY,
            ComparisonVariant.DENSE_EXHAUSTIVE,
            ComparisonVariant.ASCA_ALWAYS_MAX_SCOPE,
        ]
        if expected_case.run_structural_ablation:
            expected_variants.append(
                ComparisonVariant.ASCA_NO_STRUCTURAL_EXPANSION
            )
        if expected_case.run_familiarity_ablation:
            expected_variants.append(
                ComparisonVariant.ASCA_FAMILIARITY_DISABLED
            )
        variants = tuple(run.variant for run in item.runs)
        if variants != tuple(expected_variants):
            errors.append(
                f"variant set/order mismatch for {item.case_id}"
            )

    aggregate = _derive_aggregate(
        report.case_results,
        case_specs=frozen_by_id,
    )
    for name in _REPORT_INT_FIELDS:
        if getattr(report, name) != aggregate[name]:
            errors.append(f"{name} does not match raw case evidence")

    if not report.asca_deterministic_repeat_match:
        errors.append("ASCA_PRIMARY deterministic repeat mismatch")
    if not report.dense_deterministic_repeat_match:
        errors.append("DENSE_EXHAUSTIVE deterministic repeat mismatch")
    if not _bounded_primary_evidence(report):
        errors.append("primary boundedness evidence failed")
    return errors
