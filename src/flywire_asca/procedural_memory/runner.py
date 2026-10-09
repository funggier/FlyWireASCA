from __future__ import annotations

from typing import Protocol, runtime_checkable

from flywire_asca.contracts import Observation
from flywire_asca.contracts.validation import require_nonempty

from .library import (
    ProcedureLibrary,
    canonical_explanation_memory_ids,
    flatten_procedure,
)
from .models import (
    ProcedureExecutionMetrics,
    ProcedureExecutionMode,
    ProcedureExecutionResult,
    ProcedureExecutionState,
    ProcedureInterruption,
    ProcedureStep,
    ProcedureStepKind,
    StepExecutionResult,
)
from .verifier import verify_outcome


@runtime_checkable
class ProcedureExecutor(Protocol):
    def execute_action(
        self,
        *,
        action_ref: str,
        execution_id: str,
        call_path: tuple[str, ...],
        step_id: str,
    ) -> Observation: ...

    def observe_procedure_completion(
        self,
        *,
        procedure_id: str,
        execution_id: str,
        call_path: tuple[str, ...],
    ) -> Observation: ...


class _Counters:
    def __init__(self) -> None:
        self.primitive = 0
        self.calls = 0
        self.root_dispatch = 0
        self.checks = 0
        self.suppressed = 0
        self.max_depth = 0

    def metrics(self, step_count: int) -> ProcedureExecutionMetrics:
        return ProcedureExecutionMetrics(
            primitive_action_count=self.primitive,
            procedure_call_count=self.calls,
            root_visible_dispatch_count=self.root_dispatch,
            total_step_event_count=step_count,
            expected_outcome_check_count=self.checks,
            suppressed_internal_check_count=self.suppressed,
            max_runtime_call_depth=self.max_depth,
        )


def _final_world_ref(executor) -> str | None:
    getter = getattr(executor, "world_state_ref", None)
    if callable(getter):
        value = getter()
        if value is not None and not isinstance(value, str):
            raise ValueError("executor world_state_ref must return str or None")
        return value
    return None


def _executed_paths(executor) -> tuple[str, ...]:
    getter = getattr(executor, "executed_primitive_step_paths", None)
    if callable(getter):
        value = tuple(getter())
        if any(not isinstance(item, str) or not item for item in value):
            raise ValueError("executor primitive path log must contain nonblank strings")
        return value
    return ()


def _interruption(
    *,
    library: ProcedureLibrary,
    root_id: str,
    procedure_id: str,
    step: ProcedureStep,
    call_path: tuple[str, ...],
    observed: Observation,
    executor,
) -> ProcedureInterruption:
    return ProcedureInterruption(
        root_procedure_id=root_id,
        failing_procedure_id=procedure_id,
        failing_step_id=step.step_id,
        call_path=call_path,
        expected_outcome=step.expected_outcome,
        observed=observed,
        explanation_memory_ids=canonical_explanation_memory_ids(
            library,
            call_path,
            step,
        ),
        completed_primitive_step_paths=_executed_paths(executor),
    )


def run_procedure(
    library: ProcedureLibrary,
    *,
    root_procedure_id: str,
    mode: ProcedureExecutionMode,
    executor: ProcedureExecutor,
    execution_id: str,
) -> ProcedureExecutionResult:
    if not isinstance(library, ProcedureLibrary):
        raise ValueError("library must be a ProcedureLibrary")
    require_nonempty("execution_id", execution_id)
    library.get(root_procedure_id)
    if not isinstance(mode, ProcedureExecutionMode):
        raise ValueError("mode must be a ProcedureExecutionMode")
    if not callable(getattr(executor, "execute_action", None)) or not callable(
        getattr(executor, "observe_procedure_completion", None)
    ):
        raise ValueError("executor must implement action and completion observation methods")

    counters = _Counters()
    results: list[StepExecutionResult] = []
    interruption: ProcedureInterruption | None = None

    if mode is ProcedureExecutionMode.FLAT:
        flat = flatten_procedure(library, root_procedure_id)
        for item in flat:
            counters.max_depth = max(counters.max_depth, len(item.call_path))
            counters.root_dispatch += 1
            observed = executor.execute_action(
                action_ref=item.action_ref,
                execution_id=execution_id,
                call_path=item.call_path,
                step_id=item.step_id,
            )
            counters.primitive += 1
            verification = verify_outcome(item.expected_outcome, observed)
            counters.checks += 1
            step_result = StepExecutionResult(
                procedure_id=item.procedure_id,
                step_id=item.step_id,
                call_path=item.call_path,
                kind=ProcedureStepKind.ACTION,
                observation=observed,
                expected_outcome=item.expected_outcome,
                verification=verification,
                primitive_action_executed=True,
                action_ref=item.action_ref,
            )
            results.append(step_result)
            if not verification.matched:
                definition = library.get(item.procedure_id)
                step = next(x for x in definition.steps if x.step_id == item.step_id)
                interruption = _interruption(
                    library=library,
                    root_id=root_procedure_id,
                    procedure_id=item.procedure_id,
                    step=step,
                    call_path=item.call_path,
                    observed=observed,
                    executor=executor,
                )
                break
    else:
        def walk(procedure_id: str, call_path: tuple[str, ...]) -> bool:
            nonlocal interruption
            definition = library.get(procedure_id)
            counters.max_depth = max(counters.max_depth, len(call_path))
            for step in definition.steps:
                at_root = len(call_path) == 1
                if at_root:
                    counters.root_dispatch += 1

                if step.kind is ProcedureStepKind.ACTION:
                    observed = executor.execute_action(
                        action_ref=step.action_ref,
                        execution_id=execution_id,
                        call_path=call_path,
                        step_id=step.step_id,
                    )
                    counters.primitive += 1
                    should_check = (
                        mode is ProcedureExecutionMode.CHUNKED
                        or at_root
                    )
                    verification = None
                    if should_check:
                        verification = verify_outcome(step.expected_outcome, observed)
                        counters.checks += 1
                    else:
                        counters.suppressed += 1

                    results.append(
                        StepExecutionResult(
                            procedure_id=procedure_id,
                            step_id=step.step_id,
                            call_path=call_path,
                            kind=ProcedureStepKind.ACTION,
                            observation=observed,
                            expected_outcome=step.expected_outcome,
                            verification=verification,
                            primitive_action_executed=True,
                            action_ref=step.action_ref,
                        )
                    )
                    if verification is not None and not verification.matched:
                        interruption = _interruption(
                            library=library,
                            root_id=root_procedure_id,
                            procedure_id=procedure_id,
                            step=step,
                            call_path=call_path,
                            observed=observed,
                            executor=executor,
                        )
                        return False
                    continue

                counters.calls += 1
                child_id = step.callee_procedure_id
                child_path = call_path + (child_id,)
                if not walk(child_id, child_path):
                    return False

                observed = executor.observe_procedure_completion(
                    procedure_id=child_id,
                    execution_id=execution_id,
                    call_path=child_path,
                )
                verification = verify_outcome(step.expected_outcome, observed)
                counters.checks += 1
                results.append(
                    StepExecutionResult(
                        procedure_id=procedure_id,
                        step_id=step.step_id,
                        call_path=call_path,
                        kind=ProcedureStepKind.CALL_PROCEDURE,
                        observation=observed,
                        expected_outcome=step.expected_outcome,
                        verification=verification,
                        primitive_action_executed=False,
                        action_ref=None,
                    )
                )
                if not verification.matched:
                    interruption = _interruption(
                        library=library,
                        root_id=root_procedure_id,
                        procedure_id=procedure_id,
                        step=step,
                        call_path=call_path,
                        observed=observed,
                        executor=executor,
                    )
                    return False
            return True

        walk(root_procedure_id, (root_procedure_id,))

    state = (
        ProcedureExecutionState.INTERRUPTED
        if interruption is not None
        else ProcedureExecutionState.COMPLETED
    )
    return ProcedureExecutionResult(
        execution_id=execution_id,
        root_procedure_id=root_procedure_id,
        mode=mode,
        state=state,
        step_results=tuple(results),
        interruption=interruption,
        final_world_state_ref=_final_world_ref(executor),
        metrics=counters.metrics(len(results)),
    )
