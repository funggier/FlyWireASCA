from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from collections.abc import Iterable

from flywire_asca.contracts import ObservationKind, ProcedureRef

from .models import (
    ProcedureDefinition,
    ProcedureExecutionMetrics,
    ProcedureExecutionMode,
    ProcedureExecutionState,
    ProcedureStep,
    ProcedureStepKind,
    SimulatedActionDefinition,
    SimulatedCompletionProbe,
    SimulatedFailureOverride,
    SimulatedWorldState,
    ExpectedOutcome,
)
from .library import ProcedureLibrary
from .runner import run_procedure
from .simulator import DeterministicProcedureSimulator


@dataclass(frozen=True, slots=True)
class ProceduralBenchmarkCase:
    case_id: str
    procedures: tuple[ProcedureDefinition, ...]
    root_procedure_id: str
    action_definitions: tuple[SimulatedActionDefinition, ...]
    completion_probes: tuple[SimulatedCompletionProbe, ...]
    initial_state: SimulatedWorldState
    failure_overrides: tuple[SimulatedFailureOverride, ...] = ()
    expected_final_state: SimulatedWorldState | None = None
    expected_validation_error: str | None = None
    expected_failure: tuple[str, str, tuple[str, ...]] | None = None
    expected_blind_failure: tuple[str, str, tuple[str, ...]] | None = None
    expected_checked_explanations: tuple[str, ...] = ()
    expected_blind_explanations: tuple[str, ...] = ()
    forbidden_post_failure_paths: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class ProceduralModeCaseResult:
    mode: ProcedureExecutionMode
    state: ProcedureExecutionState
    primitive_action_refs: tuple[str, ...]
    executed_primitive_step_paths: tuple[str, ...]
    final_world_state_ref: str | None
    final_state_correct: bool | None
    metrics: ProcedureExecutionMetrics
    interruption_procedure_id: str | None
    interruption_step_id: str | None
    interruption_call_path: tuple[str, ...]
    interruption_explanation_memory_ids: tuple[str, ...]
    deterministic_repeat_match: bool


@dataclass(frozen=True, slots=True)
class ProceduralBenchmarkCaseResult:
    case_id: str
    expected_validation_error: str | None
    validation_error_observed: bool
    mode_results: tuple[ProceduralModeCaseResult, ...]


@dataclass(frozen=True, slots=True)
class ProceduralBenchmarkReport:
    case_results: tuple[ProceduralBenchmarkCaseResult, ...]
    case_count: int
    valid_case_count: int
    invalid_case_count: int
    success_case_count: int
    flat_success_count: int
    chunked_success_count: int
    blind_success_count: int
    primitive_sequence_equivalence_count: int
    flat_final_state_correct_count: int
    chunked_final_state_correct_count: int
    blind_final_state_correct_count: int
    aggregate_flat_root_visible_dispatches: int
    aggregate_chunked_root_visible_dispatches: int
    max_deliberative_compression_ratio: float
    chunk_reuse_counts: tuple[tuple[str, int], ...]
    reused_procedure_ids: tuple[str, ...]
    chunk_reuse_count: int
    checked_failure_case_count: int
    flat_exact_failure_localization_count: int
    chunked_exact_failure_localization_count: int
    blind_boundary_localization_count: int
    explanation_provenance_correct_count: int
    no_post_interruption_failure_count: int
    invalid_validation_failure_count: int
    deterministic_repeat_match: bool


def _exp(eid: str, payload: str, kind: ObservationKind = ObservationKind.RESULT) -> ExpectedOutcome:
    return ExpectedOutcome(eid, kind, payload)


def _action(step_id: str, action_ref: str, payload: str, explanations: tuple[str, ...] = ()) -> ProcedureStep:
    return ProcedureStep(step_id, ProcedureStepKind.ACTION, _exp(f"exp-{step_id}", payload), explanations, action_ref=action_ref)


def _call(step_id: str, callee: str, payload: str, explanations: tuple[str, ...] = ()) -> ProcedureStep:
    return ProcedureStep(step_id, ProcedureStepKind.CALL_PROCEDURE, _exp(f"exp-{step_id}", payload, ObservationKind.STATE), explanations, callee_procedure_id=callee)


def _proc(pid: str, steps: tuple[ProcedureStep, ...], completion_payload: str, *, explanations: tuple[str, ...] = ()) -> ProcedureDefinition:
    return ProcedureDefinition(ProcedureRef(pid, pid, "1", explanations), steps, _exp(f"completion-{pid}", completion_payload, ObservationKind.STATE))


def _beverage_definitions() -> tuple[ProcedureDefinition, ...]:
    heat = _proc("heat-water", (_action("fill", "fill-kettle", "kettle-filled"), _action("heat", "heat-water-action", "water-heated", ("mem-heat-step",))), "hot", explanations=("mem-heat",))
    tea = _proc("tea", (_call("heat-call", "heat-water", "hot", ("mem-heat-call",)), _action("brew", "brew-tea", "tea-brewed")), "tea-ready", explanations=("mem-tea",))
    coffee = _proc("coffee", (_call("heat-call", "heat-water", "hot"), _action("brew", "brew-coffee", "coffee-brewed")), "coffee-ready", explanations=("mem-coffee",))
    return tea, coffee, heat


def _beverage_actions() -> tuple[SimulatedActionDefinition, ...]:
    return (
        SimulatedActionDefinition("fill-kettle", (("kettle", "filled"),), ObservationKind.RESULT, "kettle-filled"),
        SimulatedActionDefinition("heat-water-action", (("water", "hot"),), ObservationKind.RESULT, "water-heated"),
        SimulatedActionDefinition("brew-tea", (("drink", "tea-ready"),), ObservationKind.RESULT, "tea-brewed"),
        SimulatedActionDefinition("brew-coffee", (("drink", "coffee-ready"),), ObservationKind.RESULT, "coffee-brewed"),
    )


def _beverage_probes() -> tuple[SimulatedCompletionProbe, ...]:
    return (SimulatedCompletionProbe("heat-water", "water", ObservationKind.STATE),)

def _document_backup_case() -> ProceduralBenchmarkCase:
    snapshot = _proc("snapshot", (_action("prepare", "snapshot-prepare", "snapshot-prepared"), _action("checksum", "snapshot-checksum", "checksum-ok")), "ok", explanations=("mem-snapshot",))
    backup = _proc("backup", (_call("snapshot-call", "snapshot", "ok"), _action("copy", "backup-copy", "backup-copied")), "copied", explanations=("mem-backup",))
    root = _proc("document-backup", (_call("backup-call", "backup", "copied"), _action("audit", "backup-audit", "audit-recorded")), "audit-done", explanations=("mem-document-backup",))
    actions = (
        SimulatedActionDefinition("snapshot-prepare", (("snapshot", "prepared"),), ObservationKind.RESULT, "snapshot-prepared"),
        SimulatedActionDefinition("snapshot-checksum", (("checksum", "ok"),), ObservationKind.RESULT, "checksum-ok"),
        SimulatedActionDefinition("backup-copy", (("backup", "copied"),), ObservationKind.RESULT, "backup-copied"),
        SimulatedActionDefinition("backup-audit", (("audit", "audit-done"),), ObservationKind.RESULT, "audit-recorded"),
    )
    probes = (SimulatedCompletionProbe("snapshot", "checksum", ObservationKind.STATE), SimulatedCompletionProbe("backup", "backup", ObservationKind.STATE))
    final = SimulatedWorldState((("snapshot", "prepared"), ("checksum", "ok"), ("backup", "copied"), ("audit", "audit-done")))
    return ProceduralBenchmarkCase("document-backup-success", (root, backup, snapshot), "document-backup", actions, probes, SimulatedWorldState(()), expected_final_state=final)


def _package_case() -> ProceduralBenchmarkCase:
    prep = _proc("prepare-package", (_action("label", "package-label", "labeled"), _action("seal", "package-seal", "sealed")), "sealed", explanations=("mem-package-prep",))
    root = _proc("package-dispatch", (_call("prep-call", "prepare-package", "sealed"), _action("dispatch", "package-dispatch-action", "dispatched")), "dispatched")
    actions = (
        SimulatedActionDefinition("package-label", (("label", "labeled"),), ObservationKind.RESULT, "labeled"),
        SimulatedActionDefinition("package-seal", (("package", "sealed"),), ObservationKind.RESULT, "sealed"),
        SimulatedActionDefinition("package-dispatch-action", (("dispatch", "dispatched"),), ObservationKind.RESULT, "dispatched"),
    )
    probes = (SimulatedCompletionProbe("prepare-package", "package", ObservationKind.STATE),)
    final = SimulatedWorldState((("label", "labeled"), ("package", "sealed"), ("dispatch", "dispatched")))
    return ProceduralBenchmarkCase("package-preparation-success", (root, prep), "package-dispatch", actions, probes, SimulatedWorldState(()), expected_final_state=final)


def _invalid_cases() -> tuple[ProceduralBenchmarkCase, ...]:
    direct = _proc("direct", (_call("self", "direct", "done"),), "done")
    a = _proc("a", (_call("ab", "b", "b-done"),), "a-done")
    b = _proc("b", (_call("ba", "a", "a-done"),), "b-done")
    missing = _proc("missing-root", (_call("m", "missing-child", "x"),), "done")

    deep: list[ProcedureDefinition] = []
    for index in range(9, 0, -1):
        pid = f"depth-{index}"
        steps = (_action("end", "depth-end", "end"),) if index == 9 else (_call("next", f"depth-{index+1}", f"done-{index+1}"),)
        deep.append(_proc(pid, steps, f"done-{index}"))

    empty = SimulatedWorldState(())
    return (
        ProceduralBenchmarkCase("direct-recursion-invalid", (direct,), "direct", (), (), empty, expected_validation_error="recursion"),
        ProceduralBenchmarkCase("indirect-recursion-invalid", (a, b), "a", (), (), empty, expected_validation_error="recursion"),
        ProceduralBenchmarkCase("missing-callee-invalid", (missing,), "missing-root", (), (), empty, expected_validation_error="callee"),
        ProceduralBenchmarkCase("depth-nine-invalid", tuple(reversed(deep)), "depth-1", (), (), empty, expected_validation_error="max_call_depth"),
    )


def build_a008_fixture() -> tuple[ProceduralBenchmarkCase, ...]:
    tea, coffee, heat = _beverage_definitions()
    actions = _beverage_actions()
    probes = _beverage_probes()
    base = SimulatedWorldState((("water", "cold"),))
    tea_final = SimulatedWorldState((("water", "hot"), ("kettle", "filled"), ("drink", "tea-ready")))
    coffee_final = SimulatedWorldState((("water", "hot"), ("kettle", "filled"), ("drink", "coffee-ready")))

    tea_case = ProceduralBenchmarkCase("tea-success", (tea, coffee, heat), "tea", actions, probes, base, expected_final_state=tea_final)
    coffee_case = ProceduralBenchmarkCase("coffee-success", (tea, coffee, heat), "coffee", actions, probes, base, expected_final_state=coffee_final)
    failure = ProceduralBenchmarkCase(
        "heat-water-failure",
        (tea, coffee, heat),
        "tea",
        actions,
        probes,
        base,
        failure_overrides=(SimulatedFailureOverride("tea/heat-water::heat", ObservationKind.ERROR, "heater-failed", True),),
        expected_failure=("heat-water", "heat", ("tea", "heat-water")),
        expected_blind_failure=("tea", "heat-call", ("tea",)),
        expected_checked_explanations=("mem-tea", "mem-heat", "mem-heat-step"),
        expected_blind_explanations=("mem-tea", "mem-heat-call"),
        forbidden_post_failure_paths=("tea::brew",),
    )
    return (tea_case, coffee_case, _document_backup_case(), _package_case(), failure, *_invalid_cases())


def _mode_result(case: ProceduralBenchmarkCase, library: ProcedureLibrary, mode: ProcedureExecutionMode) -> ProceduralModeCaseResult:
    def execute_once():
        sim = DeterministicProcedureSimulator(case.action_definitions, case.completion_probes, case.initial_state, case.failure_overrides)
        result = run_procedure(library, root_procedure_id=case.root_procedure_id, mode=mode, executor=sim, execution_id=f"{case.case_id}:{mode.value}")
        refs = tuple(step.action_ref for step in result.step_results if step.primitive_action_executed)
        final_correct = None if case.expected_final_state is None else sim.world_state() == case.expected_final_state
        return result, sim.world_state(), sim.executed_primitive_step_paths(), refs, final_correct, result.interruption

    first = execute_once()
    second = execute_once()
    deterministic = first == second
    result, _state, paths, refs, final_correct, interruption = first
    return ProceduralModeCaseResult(
        mode=mode,
        state=result.state,
        primitive_action_refs=refs,
        executed_primitive_step_paths=paths,
        final_world_state_ref=result.final_world_state_ref,
        final_state_correct=final_correct,
        metrics=result.metrics,
        interruption_procedure_id=interruption.failing_procedure_id if interruption else None,
        interruption_step_id=interruption.failing_step_id if interruption else None,
        interruption_call_path=interruption.call_path if interruption else (),
        interruption_explanation_memory_ids=interruption.explanation_memory_ids if interruption else (),
        deterministic_repeat_match=deterministic,
    )


def _case_result(case: ProceduralBenchmarkCase) -> ProceduralBenchmarkCaseResult:
    try:
        library = ProcedureLibrary(case.procedures, max_call_depth=8)
    except ValueError as exc:
        observed = case.expected_validation_error is not None and case.expected_validation_error in str(exc)
        return ProceduralBenchmarkCaseResult(case.case_id, case.expected_validation_error, observed, ())
    if case.expected_validation_error is not None:
        return ProceduralBenchmarkCaseResult(case.case_id, case.expected_validation_error, False, ())
    return ProceduralBenchmarkCaseResult(case.case_id, None, False, tuple(_mode_result(case, library, mode) for mode in ProcedureExecutionMode))


def _mode_map(result: ProceduralBenchmarkCaseResult) -> dict[ProcedureExecutionMode, ProceduralModeCaseResult]:
    return {item.mode: item for item in result.mode_results}


def _reuse_counts(cases: tuple[ProceduralBenchmarkCase, ...]) -> tuple[tuple[str, int], ...]:
    parent_pairs: set[tuple[str, str]] = set()
    seen_defs: dict[str, ProcedureDefinition] = {}
    for case in cases:
        for definition in case.procedures:
            pid = definition.procedure.procedure_id
            previous = seen_defs.get(pid)
            if previous is not None and previous != definition:
                continue
            seen_defs[pid] = definition
            for step in definition.steps:
                if step.kind is ProcedureStepKind.CALL_PROCEDURE:
                    parent_pairs.add((pid, step.callee_procedure_id))
    counts: dict[str, int] = {}
    for _parent, callee in parent_pairs:
        counts[callee] = counts.get(callee, 0) + 1
    return tuple(sorted(counts.items()))

def run_a008_benchmark(cases: Iterable[ProceduralBenchmarkCase]) -> ProceduralBenchmarkReport:
    case_tuple = tuple(cases)
    results = tuple(_case_result(case) for case in case_tuple)
    valid_pairs = tuple((case, result) for case, result in zip(case_tuple, results) if case.expected_validation_error is None)
    success_pairs = tuple((case, result) for case, result in valid_pairs if case.expected_final_state is not None)
    failure_pairs = tuple((case, result) for case, result in valid_pairs if case.expected_failure is not None)

    flat_success = chunk_success = blind_success = 0
    seq_equal = flat_final = chunk_final = blind_final = 0
    flat_dispatch = chunk_dispatch = 0
    ratios: list[float] = []
    flat_failure = chunk_failure = blind_failure = 0
    provenance_correct = 0
    no_post_failures = 0

    for case, result in success_pairs:
        by = _mode_map(result)
        flat = by[ProcedureExecutionMode.FLAT]
        chunk = by[ProcedureExecutionMode.CHUNKED]
        blind = by[ProcedureExecutionMode.BLIND_CHUNKED]
        flat_success += int(flat.state is ProcedureExecutionState.COMPLETED)
        chunk_success += int(chunk.state is ProcedureExecutionState.COMPLETED)
        blind_success += int(blind.state is ProcedureExecutionState.COMPLETED)
        seq_equal += int(flat.primitive_action_refs == chunk.primitive_action_refs)
        flat_final += int(flat.final_state_correct is True)
        chunk_final += int(chunk.final_state_correct is True)
        blind_final += int(blind.final_state_correct is True)
        flat_dispatch += flat.metrics.root_visible_dispatch_count
        chunk_dispatch += chunk.metrics.root_visible_dispatch_count
        if chunk.metrics.root_visible_dispatch_count > 0:
            ratios.append(flat.metrics.root_visible_dispatch_count / chunk.metrics.root_visible_dispatch_count)

    for case, result in failure_pairs:
        by = _mode_map(result)
        flat = by[ProcedureExecutionMode.FLAT]
        chunk = by[ProcedureExecutionMode.CHUNKED]
        blind = by[ProcedureExecutionMode.BLIND_CHUNKED]
        expected_proc, expected_step, expected_path = case.expected_failure
        blind_proc, blind_step, blind_path = case.expected_blind_failure
        flat_failure += int((flat.interruption_procedure_id, flat.interruption_step_id, flat.interruption_call_path) == (expected_proc, expected_step, expected_path))
        chunk_failure += int((chunk.interruption_procedure_id, chunk.interruption_step_id, chunk.interruption_call_path) == (expected_proc, expected_step, expected_path))
        blind_failure += int((blind.interruption_procedure_id, blind.interruption_step_id, blind.interruption_call_path) == (blind_proc, blind_step, blind_path))
        provenance_correct += int(flat.interruption_explanation_memory_ids == case.expected_checked_explanations)
        provenance_correct += int(chunk.interruption_explanation_memory_ids == case.expected_checked_explanations)
        provenance_correct += int(blind.interruption_explanation_memory_ids == case.expected_blind_explanations)
        for mode_result in (flat, chunk, blind):
            if any(forbidden in mode_result.executed_primitive_step_paths for forbidden in case.forbidden_post_failure_paths):
                no_post_failures += 1

    reuse_counts = _reuse_counts(tuple(case for case, _result in valid_pairs))
    reused = tuple(pid for pid, count in reuse_counts if count >= 2)
    reuse_count = sum(count for _pid, count in reuse_counts if count >= 2)
    invalid_results = tuple(result for result in results if result.expected_validation_error is not None)
    deterministic = all(item.deterministic_repeat_match for result in results for item in result.mode_results)

    return ProceduralBenchmarkReport(
        case_results=results,
        case_count=len(results),
        valid_case_count=len(valid_pairs),
        invalid_case_count=len(invalid_results),
        success_case_count=len(success_pairs),
        flat_success_count=flat_success,
        chunked_success_count=chunk_success,
        blind_success_count=blind_success,
        primitive_sequence_equivalence_count=seq_equal,
        flat_final_state_correct_count=flat_final,
        chunked_final_state_correct_count=chunk_final,
        blind_final_state_correct_count=blind_final,
        aggregate_flat_root_visible_dispatches=flat_dispatch,
        aggregate_chunked_root_visible_dispatches=chunk_dispatch,
        max_deliberative_compression_ratio=max(ratios, default=0.0),
        chunk_reuse_counts=reuse_counts,
        reused_procedure_ids=reused,
        chunk_reuse_count=reuse_count,
        checked_failure_case_count=len(failure_pairs),
        flat_exact_failure_localization_count=flat_failure,
        chunked_exact_failure_localization_count=chunk_failure,
        blind_boundary_localization_count=blind_failure,
        explanation_provenance_correct_count=provenance_correct,
        no_post_interruption_failure_count=no_post_failures,
        invalid_validation_failure_count=sum(int(not result.validation_error_observed) for result in invalid_results),
        deterministic_repeat_match=deterministic,
    )


def classify_a008_hypothesis(report: ProceduralBenchmarkReport) -> str:
    has_reuse = report.chunk_reuse_count >= 2 and bool(report.reused_procedure_ids)
    has_reduction = (
        report.aggregate_chunked_root_visible_dispatches < report.aggregate_flat_root_visible_dispatches
        and report.max_deliberative_compression_ratio > 1.0
    )
    if not has_reuse or not has_reduction:
        return "NOT_SUPPORTED"
    supported = (
        report.flat_success_count == report.success_case_count
        and report.chunked_success_count == report.success_case_count
        and report.primitive_sequence_equivalence_count == report.success_case_count
        and report.flat_final_state_correct_count == report.success_case_count
        and report.chunked_final_state_correct_count == report.success_case_count
        and report.flat_exact_failure_localization_count == report.checked_failure_case_count
        and report.chunked_exact_failure_localization_count == report.checked_failure_case_count
        and report.blind_boundary_localization_count == report.checked_failure_case_count
        and report.explanation_provenance_correct_count == report.checked_failure_case_count * 3
        and report.no_post_interruption_failure_count == 0
        and report.deterministic_repeat_match
    )
    return "SUPPORTED" if supported else "MIXED"


def qualify_a008_report(report: ProceduralBenchmarkReport) -> list[str]:
    errors: list[str] = []
    if report.invalid_validation_failure_count != 0:
        errors.append("expected invalid-library cases must fail closed")
    if not report.deterministic_repeat_match:
        errors.append("deterministic replay must match")
    if report.blind_boundary_localization_count != report.checked_failure_case_count:
        errors.append("BLIND_CHUNKED negative-control boundary localization failed")
    if report.no_post_interruption_failure_count != 0:
        errors.append("a primitive executed after an interruption boundary")
    return errors


def _expected_payload(outcome: ExpectedOutcome) -> dict[str, object]:
    return {
        "expectation_id": outcome.expectation_id,
        "observation_kind": outcome.observation_kind.value,
        "expected_payload_ref": outcome.expected_payload_ref,
        "matcher": outcome.matcher.value,
    }


def fixture_fingerprint(cases: Iterable[ProceduralBenchmarkCase]) -> str:
    payload = []
    for case in cases:
        payload.append({
            "case_id": case.case_id,
            "root_procedure_id": case.root_procedure_id,
            "procedures": [
                {
                    "procedure_id": d.procedure.procedure_id,
                    "name": d.procedure.name,
                    "version": d.procedure.version,
                    "explanation_memory_ids": list(d.procedure.explanation_memory_ids),
                    "steps": [
                        {
                            "step_id": s.step_id,
                            "kind": s.kind.value,
                            "expected": _expected_payload(s.expected_outcome),
                            "explanation_memory_ids": list(s.explanation_memory_ids),
                            "action_ref": s.action_ref,
                            "callee_procedure_id": s.callee_procedure_id,
                        }
                        for s in d.steps
                    ],
                    "completion_outcome": _expected_payload(d.completion_outcome),
                }
                for d in case.procedures
            ],
            "actions": [
                {
                    "action_ref": a.action_ref,
                    "writes": list(a.writes),
                    "observation_kind": a.observation_kind.value,
                    "success_payload_ref": a.success_payload_ref,
                }
                for a in case.action_definitions
            ],
            "probes": [
                {
                    "procedure_id": p.procedure_id,
                    "state_key": p.state_key,
                    "observation_kind": p.observation_kind.value,
                }
                for p in case.completion_probes
            ],
            "initial_state": list(case.initial_state.values),
            "failure_overrides": [
                {
                    "primitive_step_path": f.primitive_step_path,
                    "observation_kind": f.observation_kind.value,
                    "payload_ref": f.payload_ref,
                    "suppress_writes": f.suppress_writes,
                }
                for f in case.failure_overrides
            ],
            "expected_final_state": list(case.expected_final_state.values) if case.expected_final_state is not None else None,
            "expected_validation_error": case.expected_validation_error,
            "expected_failure": case.expected_failure,
            "expected_blind_failure": case.expected_blind_failure,
            "expected_checked_explanations": case.expected_checked_explanations,
            "expected_blind_explanations": case.expected_blind_explanations,
            "forbidden_post_failure_paths": case.forbidden_post_failure_paths,
        })
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()