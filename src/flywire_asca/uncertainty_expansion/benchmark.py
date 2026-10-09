from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from flywire_asca.contracts import (
    ActivationBudget,
    ActivationState,
    MemoryKind,
    RetrievalState,
    WorkingSet,
    WorkingSetEntry,
    WorkingSetKind,
)
from flywire_asca.selective_activation import (
    MemoryActivationSupport,
    SelectiveWorkingSetResult,
)

from .models import (
    ExpansionPolicy,
    ExpansionTerminationReason,
    build_a007_primary_profile,
)
from .runner import run_expansion_policy


@dataclass(frozen=True, slots=True)
class UncertaintyExpansionBenchmarkCase:
    case_id: str
    round_results: tuple[SelectiveWorkingSetResult, ...]
    required_memory_ids: tuple[str, ...] = ()
    initially_sufficient: bool = False
    ambiguity_expected: bool = False
    persistent_insufficient: bool = False
    expected_validation_error: str | None = None


@dataclass(frozen=True, slots=True)
class UncertaintyExpansionCaseResult:
    case_id: str
    required_memory_ids: tuple[str, ...]
    initially_sufficient: bool
    persistent_insufficient: bool
    expected_validation_error: str | None
    validation_error_observed: bool
    no_expansion_selected_ids: tuple[str, ...]
    signal_driven_selected_ids: tuple[str, ...]
    always_expand_selected_ids: tuple[str, ...]
    signal_driven_recovered: bool
    signal_driven_regressed: bool
    signal_driven_unnecessary_expansion: bool
    ambiguity_preserved: bool
    persistent_exhausted: bool
    no_expansion_round_count: int
    signal_driven_round_count: int
    always_expand_round_count: int
    no_expansion_termination_reason: ExpansionTerminationReason | None
    signal_driven_termination_reason: ExpansionTerminationReason | None
    always_expand_termination_reason: ExpansionTerminationReason | None
    no_expansion_required_count: int
    signal_driven_required_count: int
    always_expand_required_count: int
    deterministic_repeat_match: bool


@dataclass(frozen=True, slots=True)
class UncertaintyExpansionBenchmarkReport:
    case_results: tuple[UncertaintyExpansionCaseResult, ...]
    case_count: int
    total_required_memory_ids: int
    no_expansion_required_memory_coverage: float
    signal_driven_required_memory_coverage: float
    always_expand_required_memory_coverage: float
    signal_driven_recovery_count: int
    signal_driven_regression_count: int
    easy_unnecessary_expansion_count: int
    persistent_insufficient_expected_count: int
    persistent_insufficient_exhausted_count: int
    ambiguity_failure_count: int
    structural_validation_failure_count: int
    max_signal_driven_rounds: int
    total_no_expansion_rounds: int
    total_signal_driven_rounds: int
    total_always_expand_rounds: int
    no_expansion_policy_termination_count: int
    always_expand_policy_termination_count: int
    signal_driven_controller_stop_count: int
    signal_driven_controller_exhausted_count: int
    deterministic_repeat_match: bool


def _support(memory_id: str, similarity: float) -> MemoryActivationSupport:
    return MemoryActivationSupport(
        memory_id=memory_id,
        source_cue_ids=("portable-cue",),
        similarities=(similarity,),
        support_count=1,
        max_similarity=similarity,
        activation=similarity,
        memory_kind=MemoryKind.SEMANTIC,
        proposition_confidence=0.5,
        evidence_ids=(),
        entity_ids=(),
        context_tags=(),
        source_tags=(),
    )


def _make_result(
    state: RetrievalState,
    *,
    selected_ids: tuple[str, ...] = (),
    memory_drop_ids: tuple[str, ...] = (),
    working_drop_ids: tuple[str, ...] = (),
    memory_tie: bool = False,
    working_tie: bool = False,
) -> SelectiveWorkingSetResult:
    if state is RetrievalState.INSUFFICIENT_EVIDENCE:
        selected_ids = ()
        memory_drop_ids = ()
        working_drop_ids = ()

    activated_ids = selected_ids + working_drop_ids
    positive_ids = activated_ids + memory_drop_ids
    supports = tuple(
        _support(memory_id, 0.95 - index * 0.01)
        for index, memory_id in enumerate(positive_ids)
    )
    support_by_id = {support.memory_id: support for support in supports}

    activation_states = tuple(
        ActivationState(
            node_id=memory_id,
            activation=support_by_id[memory_id].activation,
            hop=0,
            source_cue_ids=("portable-cue",),
        )
        for memory_id in activated_ids
    )
    entries = tuple(
        WorkingSetEntry(
            ref_id=memory_id,
            kind=WorkingSetKind.MEMORY,
            activation=support_by_id[memory_id].activation,
            reason="single_cue_support",
        )
        for memory_id in selected_ids
    )
    budget = ActivationBudget(
        max_memory_nodes=max(len(activated_ids), 1),
        max_relation_hops=0,
        max_working_set_items=max(len(selected_ids), 1),
        max_model_input_tokens=0,
        max_expansions=0,
    )
    return SelectiveWorkingSetResult(
        working_set=WorkingSet(entries, state, budget),
        activation_states=activation_states,
        supports=supports,
        input_result_count=1,
        input_hit_count=len(positive_ids),
        unique_candidate_count=len(positive_ids),
        positive_candidate_count=len(positive_ids),
        activated_candidate_count=len(activated_ids),
        selected_count=len(selected_ids),
        dropped_by_memory_budget_count=len(memory_drop_ids),
        dropped_by_working_set_budget_count=len(working_drop_ids),
        memory_budget_boundary_tie=memory_tie,
        working_set_boundary_tie=working_tie,
        embedding_model_name="portable-embedder",
        embedding_model_digest="portable-digest",
        embedding_profile="a007-portable-v1",
    )


def build_a007_portable_fixture() -> tuple[UncertaintyExpansionBenchmarkCase, ...]:
    recalled_easy = _make_result(
        RetrievalState.RECALLED,
        selected_ids=("easy-target",),
    )
    recovered_r1 = _make_result(
        RetrievalState.RECALLED,
        selected_ids=("target-r1",),
    )
    recovered_r2 = _make_result(
        RetrievalState.RECALLED,
        selected_ids=("target-r2",),
    )
    insufficient = _make_result(RetrievalState.INSUFFICIENT_EVIDENCE)

    return (
        UncertaintyExpansionBenchmarkCase(
            case_id="easy-stop",
            round_results=(recalled_easy, recalled_easy, recalled_easy),
            required_memory_ids=("easy-target",),
            initially_sufficient=True,
        ),
        UncertaintyExpansionBenchmarkCase(
            case_id="recover-round-1",
            round_results=(insufficient, recovered_r1, recovered_r1),
            required_memory_ids=("target-r1",),
        ),
        UncertaintyExpansionBenchmarkCase(
            case_id="recover-round-2",
            round_results=(insufficient, insufficient, recovered_r2),
            required_memory_ids=("target-r2",),
        ),
        UncertaintyExpansionBenchmarkCase(
            case_id="memory-budget-truncation",
            round_results=(
                _make_result(
                    RetrievalState.PARTIAL_RECALL,
                    selected_ids=("mb-a", "mb-b"),
                    memory_drop_ids=("mb-c",),
                ),
                _make_result(RetrievalState.RECALLED, selected_ids=("mb-a",)),
                _make_result(RetrievalState.RECALLED, selected_ids=("mb-a",)),
            ),
        ),
        UncertaintyExpansionBenchmarkCase(
            case_id="working-set-truncation",
            round_results=(
                _make_result(
                    RetrievalState.PARTIAL_RECALL,
                    selected_ids=("ws-a", "ws-b"),
                    working_drop_ids=("ws-c",),
                ),
                _make_result(RetrievalState.RECALLED, selected_ids=("ws-a",)),
                _make_result(RetrievalState.RECALLED, selected_ids=("ws-a",)),
            ),
        ),
        UncertaintyExpansionBenchmarkCase(
            case_id="memory-boundary-tie",
            round_results=(
                _make_result(
                    RetrievalState.PARTIAL_RECALL,
                    selected_ids=("mt-a", "mt-b"),
                    memory_drop_ids=("mt-c",),
                    memory_tie=True,
                ),
                _make_result(RetrievalState.RECALLED, selected_ids=("mt-a",)),
                _make_result(RetrievalState.RECALLED, selected_ids=("mt-a",)),
            ),
        ),
        UncertaintyExpansionBenchmarkCase(
            case_id="working-set-boundary-tie",
            round_results=(
                _make_result(
                    RetrievalState.PARTIAL_RECALL,
                    selected_ids=("wt-a", "wt-b"),
                    working_drop_ids=("wt-c",),
                    working_tie=True,
                ),
                _make_result(RetrievalState.RECALLED, selected_ids=("wt-a",)),
                _make_result(RetrievalState.RECALLED, selected_ids=("wt-a",)),
            ),
        ),
        UncertaintyExpansionBenchmarkCase(
            case_id="persistent-insufficient",
            round_results=(insufficient, insufficient, insufficient),
            persistent_insufficient=True,
        ),
        UncertaintyExpansionBenchmarkCase(
            case_id="same-name-ambiguity",
            round_results=(
                _make_result(
                    RetrievalState.RECALLED,
                    selected_ids=("somchai-a", "somchai-b"),
                ),
                _make_result(
                    RetrievalState.RECALLED,
                    selected_ids=("somchai-a", "somchai-b"),
                ),
                _make_result(
                    RetrievalState.RECALLED,
                    selected_ids=("somchai-a", "somchai-b"),
                ),
            ),
            required_memory_ids=("somchai-a", "somchai-b"),
            initially_sufficient=True,
            ambiguity_expected=True,
        ),
        UncertaintyExpansionBenchmarkCase(
            case_id="initially-sufficient-no-regression",
            round_results=(
                _make_result(
                    RetrievalState.RECALLED,
                    selected_ids=("stable-target",),
                ),
                _make_result(
                    RetrievalState.RECALLED,
                    selected_ids=("stable-target",),
                ),
                _make_result(
                    RetrievalState.RECALLED,
                    selected_ids=("stable-target",),
                ),
            ),
            required_memory_ids=("stable-target",),
            initially_sufficient=True,
        ),
        UncertaintyExpansionBenchmarkCase(
            case_id="unsupported-state-validation",
            round_results=(
                _make_result(RetrievalState.CONFLICTING_RECALL),
                insufficient,
                insufficient,
            ),
            expected_validation_error="retrieval_state",
        ),
        UncertaintyExpansionBenchmarkCase(
            case_id="inconsistent-state-validation",
            round_results=(
                _make_result(
                    RetrievalState.RECALLED,
                    selected_ids=("bad-a",),
                    memory_drop_ids=("bad-b",),
                ),
                insufficient,
                insufficient,
            ),
            expected_validation_error="RECALLED",
        ),
        UncertaintyExpansionBenchmarkCase(
            case_id="deterministic-repeat",
            round_results=(
                _make_result(
                    RetrievalState.PARTIAL_RECALL,
                    selected_ids=("repeat-a",),
                    working_drop_ids=("repeat-b",),
                ),
                _make_result(
                    RetrievalState.RECALLED,
                    selected_ids=("repeat-a",),
                ),
                _make_result(
                    RetrievalState.RECALLED,
                    selected_ids=("repeat-a",),
                ),
            ),
        ),
    )


def _selected_ids(run) -> tuple[str, ...]:
    return tuple(entry.ref_id for entry in run.final_result.working_set.entries)


def _run_case(
    case: UncertaintyExpansionBenchmarkCase,
) -> UncertaintyExpansionCaseResult:
    profile = build_a007_primary_profile()

    def evaluate(scope):
        return case.round_results[scope.round_index]

    if case.expected_validation_error is not None:
        observed = False
        try:
            run_expansion_policy(
                profile,
                policy=ExpansionPolicy.SIGNAL_DRIVEN,
                evaluate_scope=evaluate,
            )
        except ValueError as exc:
            observed = case.expected_validation_error in str(exc)
        return UncertaintyExpansionCaseResult(
            case_id=case.case_id,
            required_memory_ids=case.required_memory_ids,
            initially_sufficient=case.initially_sufficient,
            persistent_insufficient=case.persistent_insufficient,
            expected_validation_error=case.expected_validation_error,
            validation_error_observed=observed,
            no_expansion_selected_ids=(),
            signal_driven_selected_ids=(),
            always_expand_selected_ids=(),
            signal_driven_recovered=False,
            signal_driven_regressed=False,
            signal_driven_unnecessary_expansion=False,
            ambiguity_preserved=True,
            persistent_exhausted=False,
            no_expansion_round_count=0,
            signal_driven_round_count=0,
            always_expand_round_count=0,
            no_expansion_termination_reason=None,
            signal_driven_termination_reason=None,
            always_expand_termination_reason=None,
            no_expansion_required_count=0,
            signal_driven_required_count=0,
            always_expand_required_count=0,
            deterministic_repeat_match=observed,
        )

    no_expansion = run_expansion_policy(
        profile,
        policy=ExpansionPolicy.NO_EXPANSION,
        evaluate_scope=evaluate,
    )
    signal = run_expansion_policy(
        profile,
        policy=ExpansionPolicy.SIGNAL_DRIVEN,
        evaluate_scope=evaluate,
    )
    always = run_expansion_policy(
        profile,
        policy=ExpansionPolicy.ALWAYS_EXPAND,
        evaluate_scope=evaluate,
    )

    signal_repeat = run_expansion_policy(
        profile,
        policy=ExpansionPolicy.SIGNAL_DRIVEN,
        evaluate_scope=evaluate,
    )
    no_repeat = run_expansion_policy(
        profile,
        policy=ExpansionPolicy.NO_EXPANSION,
        evaluate_scope=evaluate,
    )
    always_repeat = run_expansion_policy(
        profile,
        policy=ExpansionPolicy.ALWAYS_EXPAND,
        evaluate_scope=evaluate,
    )
    deterministic = (
        signal == signal_repeat
        and no_expansion == no_repeat
        and always == always_repeat
    )

    no_ids = _selected_ids(no_expansion)
    signal_ids = _selected_ids(signal)
    always_ids = _selected_ids(always)
    required = set(case.required_memory_ids)
    no_set = set(no_ids)
    signal_set = set(signal_ids)
    always_set = set(always_ids)

    no_covers = required.issubset(no_set)
    signal_covers = required.issubset(signal_set)
    recovered = bool(required) and (not no_covers) and signal_covers
    regressed = bool(required) and no_covers and not signal_covers
    ambiguity_preserved = (
        not case.ambiguity_expected
        or signal_set == required
    )
    unnecessary = (
        case.initially_sufficient
        and len(signal.rounds) > 1
    )
    persistent_exhausted = (
        case.persistent_insufficient
        and signal.termination_reason
        is ExpansionTerminationReason.CONTROLLER_EXHAUSTED
    )

    return UncertaintyExpansionCaseResult(
        case_id=case.case_id,
        required_memory_ids=case.required_memory_ids,
        initially_sufficient=case.initially_sufficient,
        persistent_insufficient=case.persistent_insufficient,
        expected_validation_error=None,
        validation_error_observed=False,
        no_expansion_selected_ids=no_ids,
        signal_driven_selected_ids=signal_ids,
        always_expand_selected_ids=always_ids,
        signal_driven_recovered=recovered,
        signal_driven_regressed=regressed,
        signal_driven_unnecessary_expansion=unnecessary,
        ambiguity_preserved=ambiguity_preserved,
        persistent_exhausted=persistent_exhausted,
        no_expansion_round_count=len(no_expansion.rounds),
        signal_driven_round_count=len(signal.rounds),
        always_expand_round_count=len(always.rounds),
        no_expansion_termination_reason=no_expansion.termination_reason,
        signal_driven_termination_reason=signal.termination_reason,
        always_expand_termination_reason=always.termination_reason,
        no_expansion_required_count=len(required & no_set),
        signal_driven_required_count=len(required & signal_set),
        always_expand_required_count=len(required & always_set),
        deterministic_repeat_match=deterministic,
    )


def run_a007_benchmark(
    cases: Iterable[UncertaintyExpansionBenchmarkCase],
) -> UncertaintyExpansionBenchmarkReport:
    case_tuple = tuple(cases)
    results = tuple(_run_case(case) for case in case_tuple)
    valid = tuple(
        result for result in results
        if result.expected_validation_error is None
    )

    total_required = sum(len(result.required_memory_ids) for result in valid)
    no_required = sum(result.no_expansion_required_count for result in valid)
    signal_required = sum(result.signal_driven_required_count for result in valid)
    always_required = sum(result.always_expand_required_count for result in valid)

    return UncertaintyExpansionBenchmarkReport(
        case_results=results,
        case_count=len(results),
        total_required_memory_ids=total_required,
        no_expansion_required_memory_coverage=(
            no_required / total_required if total_required else 1.0
        ),
        signal_driven_required_memory_coverage=(
            signal_required / total_required if total_required else 1.0
        ),
        always_expand_required_memory_coverage=(
            always_required / total_required if total_required else 1.0
        ),
        signal_driven_recovery_count=sum(
            int(result.signal_driven_recovered) for result in valid
        ),
        signal_driven_regression_count=sum(
            int(result.signal_driven_regressed) for result in valid
        ),
        easy_unnecessary_expansion_count=sum(
            int(result.signal_driven_unnecessary_expansion)
            for result in valid
        ),
        persistent_insufficient_expected_count=sum(
            int(result.persistent_insufficient) for result in valid
        ),
        persistent_insufficient_exhausted_count=sum(
            int(result.persistent_exhausted) for result in valid
        ),
        ambiguity_failure_count=sum(
            int(not result.ambiguity_preserved) for result in valid
        ),
        structural_validation_failure_count=sum(
            int(
                result.expected_validation_error is not None
                and not result.validation_error_observed
            )
            for result in results
        ),
        max_signal_driven_rounds=max(
            (result.signal_driven_round_count for result in valid),
            default=0,
        ),
        total_no_expansion_rounds=sum(
            result.no_expansion_round_count for result in valid
        ),
        total_signal_driven_rounds=sum(
            result.signal_driven_round_count for result in valid
        ),
        total_always_expand_rounds=sum(
            result.always_expand_round_count for result in valid
        ),
        no_expansion_policy_termination_count=sum(
            int(
                result.no_expansion_termination_reason
                is ExpansionTerminationReason.POLICY_NO_EXPANSION
            )
            for result in valid
        ),
        always_expand_policy_termination_count=sum(
            int(
                result.always_expand_termination_reason
                is ExpansionTerminationReason.POLICY_MAX_SCOPE
            )
            for result in valid
        ),
        signal_driven_controller_stop_count=sum(
            int(
                result.signal_driven_termination_reason
                is ExpansionTerminationReason.CONTROLLER_STOP
            )
            for result in valid
        ),
        signal_driven_controller_exhausted_count=sum(
            int(
                result.signal_driven_termination_reason
                is ExpansionTerminationReason.CONTROLLER_EXHAUSTED
            )
            for result in valid
        ),
        deterministic_repeat_match=all(
            result.deterministic_repeat_match for result in results
        ),
    )


def qualify_a007_report(
    report: UncertaintyExpansionBenchmarkReport,
) -> list[str]:
    errors: list[str] = []
    if report.signal_driven_recovery_count < 2:
        errors.append("portable fixture requires at least two signal-driven recoveries")
    if report.signal_driven_regression_count != 0:
        errors.append("signal-driven regression count must be 0")
    if report.signal_driven_required_memory_coverage != 1.0:
        errors.append("signal-driven required-memory coverage must be 1.0")
    if report.always_expand_required_memory_coverage != 1.0:
        errors.append("always-expand required-memory coverage must be 1.0")
    if report.easy_unnecessary_expansion_count != 0:
        errors.append("easy unnecessary expansion count must be 0")
    if (
        report.persistent_insufficient_exhausted_count
        != report.persistent_insufficient_expected_count
    ):
        errors.append("persistent-insufficient cases must end exhausted")
    if report.ambiguity_failure_count != 0:
        errors.append("ambiguity failure count must be 0")
    if report.structural_validation_failure_count != 0:
        errors.append("structural validation failure count must be 0")
    if report.max_signal_driven_rounds > 3:
        errors.append("signal-driven policy exceeded three rounds")
    if (
        report.total_signal_driven_rounds
        >= report.total_always_expand_rounds
    ):
        errors.append("signal-driven total rounds must be less than always-expand")
    if not report.deterministic_repeat_match:
        errors.append("portable policy execution must be deterministic")
    return errors
