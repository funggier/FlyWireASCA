from __future__ import annotations

from dataclasses import dataclass, field

from flywire_asca.contracts.validation import require_nonempty

from .models import (
    FlattenedPrimitiveStep,
    ProcedureDefinition,
    ProcedureStep,
    ProcedureStepKind,
)


def _completion_contract(outcome):
    return (
        outcome.observation_kind,
        outcome.expected_payload_ref,
        outcome.matcher,
    )


def canonical_primitive_step_path(
    call_path: tuple[str, ...],
    step_id: str,
) -> str:
    if not call_path:
        raise ValueError("call_path must not be empty")
    for procedure_id in call_path:
        require_nonempty("call_path", procedure_id)
    require_nonempty("step_id", step_id)
    return f"{'/'.join(call_path)}::{step_id}"


@dataclass(frozen=True, slots=True)
class ProcedureLibrary:
    procedures: tuple[ProcedureDefinition, ...]
    max_call_depth: int = 8
    _by_id: dict[str, ProcedureDefinition] = field(init=False, repr=False, compare=False)
    _depths: dict[str, int] = field(init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        if not self.procedures:
            raise ValueError("procedures must not be empty")
        if not isinstance(self.max_call_depth, int) or isinstance(self.max_call_depth, bool) or self.max_call_depth <= 0:
            raise ValueError("max_call_depth must be a positive integer")
        if any(not isinstance(item, ProcedureDefinition) for item in self.procedures):
            raise ValueError("procedures must contain ProcedureDefinition values")
        by_id = {item.procedure.procedure_id: item for item in self.procedures}
        if len(by_id) != len(self.procedures):
            raise ValueError("procedure_id values must be unique")

        for definition in self.procedures:
            for step in definition.steps:
                if step.kind is ProcedureStepKind.CALL_PROCEDURE:
                    callee = by_id.get(step.callee_procedure_id)
                    if callee is None:
                        raise ValueError(
                            f"callee procedure_id not found: {step.callee_procedure_id}"
                        )
                    if _completion_contract(step.expected_outcome) != _completion_contract(callee.completion_outcome):
                        raise ValueError(
                            "CALL_PROCEDURE expected outcome must match callee completion_outcome"
                        )

        depths: dict[str, int] = {}
        active: list[str] = []

        def depth(pid: str) -> int:
            if pid in depths:
                return depths[pid]
            if pid in active:
                cycle = " -> ".join(active + [pid])
                raise ValueError(f"procedure recursion is forbidden: {cycle}")
            active.append(pid)
            definition = by_id[pid]
            child_depths = [
                depth(step.callee_procedure_id)
                for step in definition.steps
                if step.kind is ProcedureStepKind.CALL_PROCEDURE
            ]
            active.pop()
            value = 1 + (max(child_depths) if child_depths else 0)
            if value > self.max_call_depth:
                raise ValueError(
                    f"static call depth {value} exceeds max_call_depth {self.max_call_depth}"
                )
            depths[pid] = value
            return value

        for pid in by_id:
            depth(pid)

        object.__setattr__(self, "_by_id", by_id)
        object.__setattr__(self, "_depths", depths)

    def get(self, procedure_id: str) -> ProcedureDefinition:
        require_nonempty("procedure_id", procedure_id)
        try:
            return self._by_id[procedure_id]
        except KeyError as exc:
            raise ValueError(f"unknown procedure_id: {procedure_id}") from exc

    def static_call_depth(self, procedure_id: str) -> int:
        self.get(procedure_id)
        return self._depths[procedure_id]


def _validate_call_path(
    library: ProcedureLibrary,
    call_path: tuple[str, ...],
) -> None:
    if not call_path:
        raise ValueError("call_path must not be empty")
    for index, pid in enumerate(call_path):
        library.get(pid)
        if index == 0:
            continue
        parent = library.get(call_path[index - 1])
        if not any(
            step.kind is ProcedureStepKind.CALL_PROCEDURE
            and step.callee_procedure_id == pid
            for step in parent.steps
        ):
            raise ValueError("call_path does not follow ProcedureLibrary CALL relationships")


def canonical_explanation_memory_ids(
    library: ProcedureLibrary,
    call_path: tuple[str, ...],
    step: ProcedureStep,
) -> tuple[str, ...]:
    _validate_call_path(library, call_path)
    current = library.get(call_path[-1])
    if step not in current.steps:
        raise ValueError("step does not belong to the current call_path procedure")
    ordered: list[str] = []
    seen: set[str] = set()
    for pid in call_path:
        for memory_id in library.get(pid).procedure.explanation_memory_ids:
            if memory_id not in seen:
                seen.add(memory_id)
                ordered.append(memory_id)
    for memory_id in step.explanation_memory_ids:
        if memory_id not in seen:
            seen.add(memory_id)
            ordered.append(memory_id)
    return tuple(ordered)


def flatten_procedure(
    library: ProcedureLibrary,
    root_procedure_id: str,
) -> tuple[FlattenedPrimitiveStep, ...]:
    library.get(root_procedure_id)
    output: list[FlattenedPrimitiveStep] = []

    def walk(pid: str, path: tuple[str, ...]) -> None:
        definition = library.get(pid)
        for step in definition.steps:
            if step.kind is ProcedureStepKind.ACTION:
                output.append(
                    FlattenedPrimitiveStep(
                        procedure_id=pid,
                        step_id=step.step_id,
                        call_path=path,
                        primitive_step_path=canonical_primitive_step_path(
                            path,
                            step.step_id,
                        ),
                        action_ref=step.action_ref,
                        expected_outcome=step.expected_outcome,
                        explanation_memory_ids=canonical_explanation_memory_ids(
                            library,
                            path,
                            step,
                        ),
                    )
                )
            else:
                walk(step.callee_procedure_id, path + (step.callee_procedure_id,))

    walk(root_procedure_id, (root_procedure_id,))
    return tuple(output)
