from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
import json

from flywire_asca.contracts import Cue, CueKind, RetrievalState, dumps_contract
from flywire_asca.contracts.validation import require_nonempty

from .exact import ExactFamiliarityIndex, ExhaustiveFamiliarityBaseline
from .models import FamiliarityResult, FamiliarityTrace


def _require_nonnegative_int(name: str, value: int) -> None:
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise ValueError(f"{name} must be a nonnegative integer")


def _canonical(values: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(sorted(set(values)))


@dataclass(frozen=True, slots=True)
class FamiliarityBenchmarkCase:
    case_id: str
    cue: Cue
    expected_state: RetrievalState
    expected_region_ids: tuple[str, ...]
    universe_region_count: int | None = None
    ambiguity_expected: bool = False

    def __post_init__(self) -> None:
        require_nonempty("case_id", self.case_id)
        if self.expected_state not in (
            RetrievalState.FAMILIAR,
            RetrievalState.UNFAMILIAR,
        ):
            raise ValueError(
                "expected_state must be FAMILIAR or UNFAMILIAR"
            )
        if self.expected_region_ids != _canonical(self.expected_region_ids):
            raise ValueError(
                "expected_region_ids must be unique and sorted canonically"
            )
        if self.expected_state is RetrievalState.FAMILIAR:
            if not self.expected_region_ids:
                raise ValueError(
                    "FAMILIAR expected_state requires expected_region_ids"
                )
        elif self.expected_region_ids:
            raise ValueError(
                "UNFAMILIAR expected_state requires empty expected_region_ids"
            )
        if self.universe_region_count is not None:
            if (
                not isinstance(self.universe_region_count, int)
                or isinstance(self.universe_region_count, bool)
                or self.universe_region_count <= 0
                or self.universe_region_count < len(self.expected_region_ids)
            ):
                raise ValueError(
                    "universe_region_count must be positive and cover expected regions"
                )
        if self.ambiguity_expected and len(self.expected_region_ids) < 2:
            raise ValueError(
                "ambiguity_expected requires at least two expected regions"
            )


@dataclass(frozen=True, slots=True)
class FamiliarityBenchmarkCaseResult:
    case_id: str
    expected_state: RetrievalState
    actual_state: RetrievalState
    expected_region_ids: tuple[str, ...]
    actual_region_ids: tuple[str, ...]
    classification_correct: bool
    regions_correct: bool
    ambiguity_preserved: bool
    candidate_region_count: int
    candidate_region_fraction: float | None
    matched_trace_count: int
    exact_logical_probes: int
    exhaustive_logical_probes: int
    semantic_equivalent: bool


@dataclass(frozen=True, slots=True)
class FamiliarityBenchmarkReport:
    scope: str
    total_trace_count: int
    case_results: tuple[FamiliarityBenchmarkCaseResult, ...]
    case_count: int
    correct_classification_count: int
    classification_accuracy: float
    false_familiarity_count: int
    false_unfamiliar_count: int
    ambiguity_failure_count: int
    semantic_mismatch_count: int
    exact_logical_probes: int
    exhaustive_logical_probes: int

    def __post_init__(self) -> None:
        require_nonempty("scope", self.scope)
        for name in (
            "total_trace_count",
            "case_count",
            "correct_classification_count",
            "false_familiarity_count",
            "false_unfamiliar_count",
            "ambiguity_failure_count",
            "semantic_mismatch_count",
            "exact_logical_probes",
            "exhaustive_logical_probes",
        ):
            _require_nonnegative_int(name, getattr(self, name))
        if self.case_count != len(self.case_results):
            raise ValueError("case_count must equal len(case_results)")
        if not 0.0 <= self.classification_accuracy <= 1.0:
            raise ValueError("classification_accuracy must be within [0, 1]")


def _semantic_tuple(result: FamiliarityResult) -> tuple[object, ...]:
    return (
        result.cue_id,
        result.retrieval_state,
        result.familiarity_score,
        result.candidate_region_ids,
        result.matched_trace_ids,
        result.cost.matched_trace_count,
        result.cost.total_trace_count,
    )


def run_familiarity_benchmark(
    traces: Iterable[FamiliarityTrace],
    cases: Iterable[FamiliarityBenchmarkCase],
) -> FamiliarityBenchmarkReport:
    trace_tuple = tuple(traces)
    case_tuple = tuple(cases)
    case_ids = tuple(case.case_id for case in case_tuple)
    if len(set(case_ids)) != len(case_ids):
        raise ValueError("duplicate case_id values are not allowed")

    exact = ExactFamiliarityIndex(trace_tuple)
    exhaustive = ExhaustiveFamiliarityBaseline(trace_tuple)

    results: list[FamiliarityBenchmarkCaseResult] = []
    correct_classification_count = 0
    false_familiarity_count = 0
    false_unfamiliar_count = 0
    ambiguity_failure_count = 0
    semantic_mismatch_count = 0
    exact_logical_probes = 0
    exhaustive_logical_probes = 0

    for case in case_tuple:
        exact_result = exact.assess(case.cue)
        exhaustive_result = exhaustive.assess(case.cue)
        classification_correct = (
            exact_result.retrieval_state is case.expected_state
        )
        regions_correct = (
            exact_result.candidate_region_ids == case.expected_region_ids
        )
        semantic_equivalent = (
            _semantic_tuple(exact_result) == _semantic_tuple(exhaustive_result)
        )

        if classification_correct:
            correct_classification_count += 1
        elif (
            case.expected_state is RetrievalState.UNFAMILIAR
            and exact_result.retrieval_state is RetrievalState.FAMILIAR
        ):
            false_familiarity_count += 1
        elif (
            case.expected_state is RetrievalState.FAMILIAR
            and exact_result.retrieval_state is RetrievalState.UNFAMILIAR
        ):
            false_unfamiliar_count += 1

        ambiguity_preserved = True
        if case.ambiguity_expected:
            ambiguity_preserved = (
                regions_correct
                and len(exact_result.candidate_region_ids) >= 2
                and not hasattr(exact_result, "identity_id")
                and not hasattr(exact_result, "winner_id")
                and not hasattr(exact_result, "same_person")
            )
            if not ambiguity_preserved:
                ambiguity_failure_count += 1

        if not semantic_equivalent:
            semantic_mismatch_count += 1

        candidate_count = len(exact_result.candidate_region_ids)
        candidate_fraction = (
            candidate_count / case.universe_region_count
            if case.universe_region_count is not None
            else None
        )
        exact_logical_probes += exact_result.cost.index_probes
        exhaustive_logical_probes += exhaustive_result.cost.index_probes

        results.append(
            FamiliarityBenchmarkCaseResult(
                case_id=case.case_id,
                expected_state=case.expected_state,
                actual_state=exact_result.retrieval_state,
                expected_region_ids=case.expected_region_ids,
                actual_region_ids=exact_result.candidate_region_ids,
                classification_correct=classification_correct,
                regions_correct=regions_correct,
                ambiguity_preserved=ambiguity_preserved,
                candidate_region_count=candidate_count,
                candidate_region_fraction=candidate_fraction,
                matched_trace_count=exact_result.cost.matched_trace_count,
                exact_logical_probes=exact_result.cost.index_probes,
                exhaustive_logical_probes=exhaustive_result.cost.index_probes,
                semantic_equivalent=semantic_equivalent,
            )
        )

    case_count = len(case_tuple)
    accuracy = (
        correct_classification_count / case_count
        if case_count
        else 0.0
    )
    return FamiliarityBenchmarkReport(
        scope="controlled_fixture_only",
        total_trace_count=len(trace_tuple),
        case_results=tuple(results),
        case_count=case_count,
        correct_classification_count=correct_classification_count,
        classification_accuracy=accuracy,
        false_familiarity_count=false_familiarity_count,
        false_unfamiliar_count=false_unfamiliar_count,
        ambiguity_failure_count=ambiguity_failure_count,
        semantic_mismatch_count=semantic_mismatch_count,
        exact_logical_probes=exact_logical_probes,
        exhaustive_logical_probes=exhaustive_logical_probes,
    )


def build_a003_qualification_fixture() -> tuple[
    tuple[FamiliarityTrace, ...],
    tuple[FamiliarityBenchmarkCase, ...],
]:
    traces: list[FamiliarityTrace] = [
        FamiliarityTrace(
            "trace-alice",
            CueKind.ENTITY,
            "Alice",
            "person-alice",
        ),
        FamiliarityTrace(
            "trace-a-primary",
            CueKind.ENTITY,
            "A",
            "person-a-primary",
        ),
        FamiliarityTrace(
            "trace-a-neighbor",
            CueKind.ENTITY,
            "a",
            "person-a-neighbor",
        ),
        FamiliarityTrace(
            "trace-beta-1",
            CueKind.ENTITY,
            "Beta",
            "person-beta",
        ),
        FamiliarityTrace(
            "trace-beta-2",
            CueKind.ENTITY,
            "ＢＥＴＡ",
            "person-beta",
        ),
        FamiliarityTrace(
            "trace-thai",
            CueKind.TEXT,
            "สวัสดี โลก",
            "text-thai-greeting",
        ),
        FamiliarityTrace(
            "trace-office",
            CueKind.CONTEXT,
            "Office",
            "context-office",
        ),
    ]
    for index in range(256):
        traces.append(
            FamiliarityTrace(
                f"trace-distractor-{index:03d}",
                CueKind.ENTITY,
                f"Distractor {index:03d}",
                f"region-distractor-{index:03d}",
            )
        )

    universe_region_count = len({trace.region_id for trace in traces})
    cases = (
        FamiliarityBenchmarkCase(
            "known-unique",
            Cue("cue-known", CueKind.ENTITY, "Alice", 1.0),
            RetrievalState.FAMILIAR,
            ("person-alice",),
            universe_region_count,
        ),
        FamiliarityBenchmarkCase(
            "unknown",
            Cue("cue-unknown", CueKind.ENTITY, "Completely Unknown", 1.0),
            RetrievalState.UNFAMILIAR,
            (),
            universe_region_count,
        ),
        FamiliarityBenchmarkCase(
            "normalization-equivalent",
            Cue("cue-normalized", CueKind.ENTITY, "  ＡＬＩＣＥ  ", 1.0),
            RetrievalState.FAMILIAR,
            ("person-alice",),
            universe_region_count,
        ),
        FamiliarityBenchmarkCase(
            "cross-kind-negative",
            Cue("cue-cross-kind", CueKind.TEXT, "Alice", 1.0),
            RetrievalState.UNFAMILIAR,
            (),
            universe_region_count,
        ),
        FamiliarityBenchmarkCase(
            "same-name-ambiguity",
            Cue("cue-ambiguous", CueKind.ENTITY, "A", 1.0),
            RetrievalState.FAMILIAR,
            ("person-a-neighbor", "person-a-primary"),
            universe_region_count,
            True,
        ),
        FamiliarityBenchmarkCase(
            "duplicate-traces-one-region",
            Cue("cue-beta", CueKind.ENTITY, "beta", 1.0),
            RetrievalState.FAMILIAR,
            ("person-beta",),
            universe_region_count,
        ),
        FamiliarityBenchmarkCase(
            "thai-unicode",
            Cue("cue-thai", CueKind.TEXT, "สวัสดี\u00a0  โลก", 1.0),
            RetrievalState.FAMILIAR,
            ("text-thai-greeting",),
            universe_region_count,
        ),
        FamiliarityBenchmarkCase(
            "synthetic-known",
            Cue("cue-distractor", CueKind.ENTITY, "distractor 042", 1.0),
            RetrievalState.FAMILIAR,
            ("region-distractor-042",),
            universe_region_count,
        ),
        FamiliarityBenchmarkCase(
            "synthetic-unknown",
            Cue("cue-distractor-missing", CueKind.ENTITY, "distractor 999", 1.0),
            RetrievalState.UNFAMILIAR,
            (),
            universe_region_count,
        ),
    )
    return tuple(traces), cases


def benchmark_report_payload(
    report: FamiliarityBenchmarkReport,
) -> dict[str, object]:
    return json.loads(dumps_contract(report))


def qualify_a003_report(report: FamiliarityBenchmarkReport) -> list[str]:
    errors: list[str] = []
    if report.scope != "controlled_fixture_only":
        errors.append('scope must be "controlled_fixture_only"')
    if report.case_count <= 0:
        errors.append("case_count must be > 0")
    if report.classification_accuracy != 1.0:
        errors.append("classification_accuracy must be 1.0")
    if report.false_familiarity_count != 0:
        errors.append("false_familiarity_count must be 0")
    if report.false_unfamiliar_count != 0:
        errors.append("false_unfamiliar_count must be 0")
    if report.ambiguity_failure_count != 0:
        errors.append("ambiguity_failure_count must be 0")
    if report.semantic_mismatch_count != 0:
        errors.append("semantic_mismatch_count must be 0")
    if report.exact_logical_probes != report.case_count:
        errors.append("exact_logical_probes must equal case_count")
    if (
        report.exhaustive_logical_probes
        != report.case_count * report.total_trace_count
    ):
        errors.append(
            "exhaustive_logical_probes must equal case_count * total_trace_count"
        )
    return errors
