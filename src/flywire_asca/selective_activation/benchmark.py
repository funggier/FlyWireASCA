from __future__ import annotations

from dataclasses import dataclass
from collections.abc import Iterable

from flywire_asca.contracts import ActivationBudget, MemoryKind
from flywire_asca.vector_memory import VectorMemoryHit, VectorMemoryResult

from .baselines import select_exhaustive, select_single_best
from .models import SelectiveRetrievalEvidence
from .selector import select_working_set


@dataclass(frozen=True, slots=True)
class SelectiveActivationBenchmarkCase:
    case_id: str
    evidence: tuple[SelectiveRetrievalEvidence, ...]
    budget: ActivationBudget
    required_memory_ids: tuple[str, ...] = ()
    allowed_selected_memory_ids: tuple[str, ...] = ()
    expected_no_selection: bool = False
    expected_validation_error: str | None = None
    convergence_recovery_expected: bool = False
    ambiguity_expected: bool = False
    confidence_independence_expected: bool = False


@dataclass(frozen=True, slots=True)
class SelectiveActivationCaseResult:
    case_id: str
    required_memory_ids: tuple[str, ...]
    selective_selected_ids: tuple[str, ...]
    single_best_selected_ids: tuple[str, ...]
    exhaustive_selected_ids: tuple[str, ...]
    convergence_recovered: bool
    convergence_regressed: bool
    ambiguity_preserved: bool
    confidence_separated: bool
    expected_no_selection: bool
    no_selection_correct: bool
    expected_validation_error: str | None
    validation_error_observed: bool
    input_hit_count: int
    unique_candidate_count: int
    positive_candidate_count: int
    activated_candidate_count: int
    selected_count: int
    memory_budget_drop_count: int
    working_set_budget_drop_count: int
    boundary_tie_count: int
    active_state_reduction_ratio: float
    selected_precision: float
    required_selected_count: int
    active_required_count: int
    single_best_required_count: int
    exhaustive_required_count: int
    deterministic_repeat_match: bool
    budget_valid: bool
    count_invariants_valid: bool


@dataclass(frozen=True, slots=True)
class SelectiveActivationBenchmarkReport:
    case_results: tuple[SelectiveActivationCaseResult, ...]
    case_count: int
    required_memory_coverage: float
    active_memory_required_coverage: float
    single_best_required_memory_coverage: float
    exhaustive_required_memory_coverage: float
    selected_set_precision: float
    convergence_recovery_count: int
    convergence_regression_count: int
    ambiguity_failure_count: int
    confidence_separation_failure_count: int
    budget_violation_count: int
    count_invariant_failure_count: int
    validation_failure_count: int
    total_input_hits: int
    total_unique_candidates: int
    total_positive_candidates: int
    total_activated_candidates: int
    total_selected_items: int
    total_memory_budget_drops: int
    total_working_set_budget_drops: int
    boundary_tie_count: int
    aggregate_active_state_reduction_ratio: float
    deterministic_repeat_match: bool


def _hit(
    memory_id: str,
    similarity: float,
    *,
    confidence: float = 0.5,
    entity_ids: tuple[str, ...] = (),
) -> VectorMemoryHit:
    return VectorMemoryHit(
        memory_id=memory_id,
        similarity=similarity,
        memory_kind=MemoryKind.SEMANTIC,
        proposition_confidence=confidence,
        evidence_ids=(),
        entity_ids=entity_ids,
        context_tags=(),
        source_tags=(),
    )


def _result(
    query_id: str,
    hits: tuple[VectorMemoryHit, ...],
    *,
    profile: str = "portable-a006-v1",
) -> VectorMemoryResult:
    count = len(hits)
    return VectorMemoryResult(
        query_id=query_id,
        hits=hits,
        stored_count=max(1, count),
        metadata_eligible_count=count,
        scored_vector_count=count,
        above_threshold_count=count,
        returned_count=count,
        embedding_model_name="portable-embedder",
        embedding_model_digest="portable-digest",
        embedding_profile=profile,
    )


def _ev(
    cue: str,
    query: str,
    *hits: VectorMemoryHit,
    profile: str = "portable-a006-v1",
) -> SelectiveRetrievalEvidence:
    return SelectiveRetrievalEvidence(
        cue,
        _result(query, tuple(hits), profile=profile),
    )


def _budget(memory: int, working: int) -> ActivationBudget:
    return ActivationBudget(memory, 0, working, 0, 0)


def build_a006_portable_fixture() -> tuple[SelectiveActivationBenchmarkCase, ...]:
    distractors = tuple(
        _hit(f"distractor-{index:03d}", 0.70 - index * 0.0005)
        for index in range(256)
    )
    return (
        SelectiveActivationBenchmarkCase(
            "single-query",
            (_ev("cue", "q-single", _hit("target-single", 0.9), _hit("d", 0.2)),),
            _budget(2, 1),
            ("target-single",),
        ),
        SelectiveActivationBenchmarkCase(
            "convergence-recovery",
            (
                _ev("cue-a", "q-conv-a", _hit("target", 0.6), _hit("one-off", 0.8)),
                _ev("cue-b", "q-conv-b", _hit("target", 0.6)),
            ),
            _budget(2, 1),
            ("target",),
            convergence_recovery_expected=True,
        ),
        SelectiveActivationBenchmarkCase(
            "convergence-parity",
            (_ev("cue", "q-parity", _hit("parity-target", 0.8), _hit("parity-d", 0.7)),),
            _budget(2, 1),
            ("parity-target",),
        ),
        SelectiveActivationBenchmarkCase(
            "memory-budget",
            (_ev("cue", "q-memory-budget", _hit("mb-a", 0.9), _hit("mb-b", 0.8), _hit("mb-c", 0.7)),),
            _budget(2, 2),
            ("mb-a", "mb-b"),
        ),
        SelectiveActivationBenchmarkCase(
            "working-set-budget",
            (_ev("cue", "q-working-budget", _hit("wb-a", 0.9), _hit("wb-b", 0.8), _hit("wb-c", 0.7)),),
            _budget(3, 1),
            ("wb-a",),
        ),
        SelectiveActivationBenchmarkCase(
            "memory-boundary-tie",
            (_ev("cue", "q-mem-tie", _hit("tie-a", 0.8), _hit("tie-b", 0.8)),),
            _budget(1, 1),
            ("tie-a",),
        ),
        SelectiveActivationBenchmarkCase(
            "working-set-boundary-tie",
            (_ev("cue", "q-ws-tie", _hit("ws-a", 0.8), _hit("ws-b", 0.8)),),
            _budget(2, 1),
            ("ws-a",),
        ),
        SelectiveActivationBenchmarkCase(
            "same-name-ambiguity",
            (
                _ev(
                    "cue",
                    "q-ambiguity",
                    _hit("somchai-a", 0.8, entity_ids=("person-a",)),
                    _hit("somchai-b", 0.8, entity_ids=("person-b",)),
                ),
            ),
            _budget(2, 2),
            ("somchai-a", "somchai-b"),
            allowed_selected_memory_ids=("somchai-a", "somchai-b"),
            ambiguity_expected=True,
        ),
        SelectiveActivationBenchmarkCase(
            "confidence-independence",
            (
                _ev(
                    "cue",
                    "q-confidence",
                    _hit("low-confidence", 0.9, confidence=0.1),
                    _hit("high-confidence", 0.8, confidence=0.99),
                ),
            ),
            _budget(2, 1),
            ("low-confidence",),
            confidence_independence_expected=True,
        ),
        SelectiveActivationBenchmarkCase(
            "insufficient-evidence",
            (_ev("cue", "q-none", _hit("zero", 0.0), _hit("negative", -0.2)),),
            _budget(2, 1),
            (),
            expected_no_selection=True,
        ),
        SelectiveActivationBenchmarkCase(
            "duplicate-cue-validation",
            (
                _ev("dup-cue", "q-dup-a", _hit("dup-a", 0.8)),
                _ev("dup-cue", "q-dup-b", _hit("dup-b", 0.7)),
            ),
            _budget(2, 1),
            (),
            expected_validation_error="source_cue_id",
        ),
        SelectiveActivationBenchmarkCase(
            "profile-mismatch-validation",
            (
                _ev("cue-a", "q-prof-a", _hit("prof-a", 0.8), profile="profile-a"),
                _ev("cue-b", "q-prof-b", _hit("prof-b", 0.7), profile="profile-b"),
            ),
            _budget(2, 1),
            (),
            expected_validation_error="embedding_profile",
        ),
        SelectiveActivationBenchmarkCase(
            "deterministic-repeat",
            (_ev("cue", "q-repeat", _hit("repeat-target", 0.85), _hit("repeat-d", 0.4)),),
            _budget(2, 1),
            ("repeat-target",),
        ),
        SelectiveActivationBenchmarkCase(
            "distractor-heavy",
            (
                _ev(
                    "cue",
                    "q-heavy",
                    _hit("heavy-target", 0.95),
                    *distractors,
                ),
            ),
            _budget(8, 4),
            ("heavy-target",),
        ),
    )


def _ids(result) -> tuple[str, ...]:
    return tuple(entry.ref_id for entry in result.working_set.entries)


def _active_ids(result) -> tuple[str, ...]:
    return tuple(state.node_id for state in result.activation_states)


def _count_invariants(result) -> bool:
    return (
        result.input_hit_count >= result.unique_candidate_count
        >= result.positive_candidate_count
        >= result.activated_candidate_count
        >= result.selected_count
        and result.dropped_by_memory_budget_count
        == result.positive_candidate_count - result.activated_candidate_count
        and result.dropped_by_working_set_budget_count
        == result.activated_candidate_count - result.selected_count
    )


def _run_validation_case(
    case: SelectiveActivationBenchmarkCase,
) -> SelectiveActivationCaseResult:
    expected = case.expected_validation_error
    assert expected is not None
    observed: list[bool] = []
    for call in (
        lambda: select_working_set(case.evidence, budget=case.budget),
        lambda: select_single_best(case.evidence, budget=case.budget),
        lambda: select_exhaustive(case.evidence),
    ):
        try:
            call()
        except ValueError as exc:
            observed.append(expected in str(exc))
        else:
            observed.append(False)
    passed = all(observed)
    return SelectiveActivationCaseResult(
        case_id=case.case_id,
        required_memory_ids=case.required_memory_ids,
        selective_selected_ids=(),
        single_best_selected_ids=(),
        exhaustive_selected_ids=(),
        convergence_recovered=False,
        convergence_regressed=False,
        ambiguity_preserved=True,
        confidence_separated=True,
        expected_no_selection=case.expected_no_selection,
        no_selection_correct=True,
        expected_validation_error=expected,
        validation_error_observed=passed,
        input_hit_count=0,
        unique_candidate_count=0,
        positive_candidate_count=0,
        activated_candidate_count=0,
        selected_count=0,
        memory_budget_drop_count=0,
        working_set_budget_drop_count=0,
        boundary_tie_count=0,
        active_state_reduction_ratio=0.0,
        selected_precision=1.0,
        required_selected_count=0,
        active_required_count=0,
        single_best_required_count=0,
        exhaustive_required_count=0,
        deterministic_repeat_match=passed,
        budget_valid=True,
        count_invariants_valid=True,
    )


def _run_case(case: SelectiveActivationBenchmarkCase) -> SelectiveActivationCaseResult:
    if case.expected_validation_error is not None:
        return _run_validation_case(case)

    selective = select_working_set(case.evidence, budget=case.budget)
    single = select_single_best(case.evidence, budget=case.budget)
    exhaustive = select_exhaustive(case.evidence)

    selective_repeat = select_working_set(case.evidence, budget=case.budget)
    single_repeat = select_single_best(case.evidence, budget=case.budget)
    exhaustive_repeat = select_exhaustive(case.evidence)
    deterministic = (
        selective == selective_repeat
        and single == single_repeat
        and exhaustive == exhaustive_repeat
    )

    selected = _ids(selective)
    single_ids = _ids(single)
    exhaustive_ids = _ids(exhaustive)
    active_ids = _active_ids(selective)
    required = set(case.required_memory_ids)
    selected_set = set(selected)
    single_set = set(single_ids)
    exhaustive_set = set(exhaustive_ids)
    active_set = set(active_ids)

    required_selected = len(required & selected_set)
    active_required = len(required & active_set)
    single_required = len(required & single_set)
    exhaustive_required = len(required & exhaustive_set)

    selective_covers = required.issubset(selected_set)
    single_covers = required.issubset(single_set)
    convergence_recovered = (
        case.convergence_recovery_expected
        and selective_covers
        and not single_covers
    )
    convergence_regressed = bool(required) and single_covers and not selective_covers

    allowed = set(
        case.allowed_selected_memory_ids
        if case.allowed_selected_memory_ids
        else case.required_memory_ids
    )
    if selected:
        precision = sum(1 for memory_id in selected if memory_id in allowed) / len(selected)
    else:
        precision = 1.0

    ambiguity_preserved = True
    if case.ambiguity_expected:
        ambiguity_preserved = selected_set == allowed

    confidence_separated = True
    if case.confidence_independence_expected:
        confidence_separated = selective_covers

    no_selection_correct = (
        (not selected)
        if case.expected_no_selection
        else True
    )
    budget_valid = (
        selective.activated_candidate_count <= case.budget.max_memory_nodes
        and selective.selected_count <= case.budget.max_working_set_items
    )
    count_valid = _count_invariants(selective)

    positive = selective.positive_candidate_count
    reduction = (
        (positive - selective.selected_count) / positive
        if positive
        else 0.0
    )

    return SelectiveActivationCaseResult(
        case_id=case.case_id,
        required_memory_ids=case.required_memory_ids,
        selective_selected_ids=selected,
        single_best_selected_ids=single_ids,
        exhaustive_selected_ids=exhaustive_ids,
        convergence_recovered=convergence_recovered,
        convergence_regressed=convergence_regressed,
        ambiguity_preserved=ambiguity_preserved,
        confidence_separated=confidence_separated,
        expected_no_selection=case.expected_no_selection,
        no_selection_correct=no_selection_correct,
        expected_validation_error=None,
        validation_error_observed=False,
        input_hit_count=selective.input_hit_count,
        unique_candidate_count=selective.unique_candidate_count,
        positive_candidate_count=positive,
        activated_candidate_count=selective.activated_candidate_count,
        selected_count=selective.selected_count,
        memory_budget_drop_count=selective.dropped_by_memory_budget_count,
        working_set_budget_drop_count=selective.dropped_by_working_set_budget_count,
        boundary_tie_count=(
            int(selective.memory_budget_boundary_tie)
            + int(selective.working_set_boundary_tie)
        ),
        active_state_reduction_ratio=reduction,
        selected_precision=precision,
        required_selected_count=required_selected,
        active_required_count=active_required,
        single_best_required_count=single_required,
        exhaustive_required_count=exhaustive_required,
        deterministic_repeat_match=deterministic,
        budget_valid=budget_valid,
        count_invariants_valid=count_valid,
    )


def run_a006_benchmark(
    cases: Iterable[SelectiveActivationBenchmarkCase],
) -> SelectiveActivationBenchmarkReport:
    case_tuple = tuple(cases)
    results = tuple(_run_case(case) for case in case_tuple)

    normal = tuple(
        result
        for result in results
        if result.expected_validation_error is None
    )
    total_required = sum(len(result.required_memory_ids) for result in normal)
    required_selected = sum(result.required_selected_count for result in normal)
    active_required = sum(result.active_required_count for result in normal)
    single_required = sum(result.single_best_required_count for result in normal)
    exhaustive_required = sum(result.exhaustive_required_count for result in normal)

    total_selected_for_precision = sum(result.selected_count for result in normal)
    acceptable_selected = sum(
        result.selected_precision * result.selected_count
        for result in normal
    )

    total_input_hits = sum(result.input_hit_count for result in normal)
    total_unique = sum(result.unique_candidate_count for result in normal)
    total_positive = sum(result.positive_candidate_count for result in normal)
    total_activated = sum(result.activated_candidate_count for result in normal)
    total_selected = sum(result.selected_count for result in normal)
    total_memory_drops = sum(result.memory_budget_drop_count for result in normal)
    total_working_drops = sum(result.working_set_budget_drop_count for result in normal)

    return SelectiveActivationBenchmarkReport(
        case_results=results,
        case_count=len(results),
        required_memory_coverage=(
            required_selected / total_required if total_required else 1.0
        ),
        active_memory_required_coverage=(
            active_required / total_required if total_required else 1.0
        ),
        single_best_required_memory_coverage=(
            single_required / total_required if total_required else 1.0
        ),
        exhaustive_required_memory_coverage=(
            exhaustive_required / total_required if total_required else 1.0
        ),
        selected_set_precision=(
            acceptable_selected / total_selected_for_precision
            if total_selected_for_precision
            else 1.0
        ),
        convergence_recovery_count=sum(
            int(result.convergence_recovered) for result in normal
        ),
        convergence_regression_count=sum(
            int(result.convergence_regressed) for result in normal
        ),
        ambiguity_failure_count=sum(
            int(not result.ambiguity_preserved) for result in normal
        ),
        confidence_separation_failure_count=sum(
            int(not result.confidence_separated) for result in normal
        ),
        budget_violation_count=sum(
            int(not result.budget_valid) for result in normal
        ),
        count_invariant_failure_count=sum(
            int(not result.count_invariants_valid) for result in normal
        ),
        validation_failure_count=sum(
            int(
                result.expected_validation_error is not None
                and not result.validation_error_observed
            )
            for result in results
        ),
        total_input_hits=total_input_hits,
        total_unique_candidates=total_unique,
        total_positive_candidates=total_positive,
        total_activated_candidates=total_activated,
        total_selected_items=total_selected,
        total_memory_budget_drops=total_memory_drops,
        total_working_set_budget_drops=total_working_drops,
        boundary_tie_count=sum(result.boundary_tie_count for result in normal),
        aggregate_active_state_reduction_ratio=(
            (total_positive - total_selected) / total_positive
            if total_positive
            else 0.0
        ),
        deterministic_repeat_match=all(
            result.deterministic_repeat_match for result in results
        ),
    )


def qualify_a006_report(
    report: SelectiveActivationBenchmarkReport,
) -> list[str]:
    errors: list[str] = []
    if report.required_memory_coverage != 1.0:
        errors.append("required-memory coverage must be 1.0")
    if report.active_memory_required_coverage != 1.0:
        errors.append("active-memory required coverage must be 1.0")
    if report.convergence_recovery_count < 1:
        errors.append("at least one convergence recovery is required")
    if report.convergence_regression_count != 0:
        errors.append("convergence regression count must be 0")
    if report.ambiguity_failure_count != 0:
        errors.append("ambiguity failure count must be 0")
    if report.confidence_separation_failure_count != 0:
        errors.append("confidence separation failure count must be 0")
    if report.budget_violation_count != 0:
        errors.append("budget violation count must be 0")
    if report.count_invariant_failure_count != 0:
        errors.append("count invariant failure count must be 0")
    if report.validation_failure_count != 0:
        errors.append("validation failure count must be 0")
    if not report.deterministic_repeat_match:
        errors.append("deterministic repeated execution must match")
    return errors
