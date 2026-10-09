from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json

from flywire_asca.contracts import Observation, ObservationKind
from flywire_asca.contracts.validation import require_nonempty, require_unique_nonempty
from flywire_asca.procedural_memory import (
    DeterministicProcedureSimulator,
    SimulatedActionDefinition,
    SimulatedCompletionProbe,
    SimulatedFailureOverride,
    SimulatedWorldState,
    canonical_primitive_step_path,
)


@dataclass(frozen=True, slots=True)
class ActionMemoryRequirement:
    action_ref: str
    required_memory_ids: tuple[str, ...]
    failure_observation_kind: ObservationKind
    failure_payload_ref: str

    def __post_init__(self) -> None:
        require_nonempty("action_ref", self.action_ref)
        if not self.required_memory_ids:
            raise ValueError("required_memory_ids must not be empty")
        require_unique_nonempty("required_memory_ids", self.required_memory_ids)
        if not isinstance(self.failure_observation_kind, ObservationKind):
            raise ValueError(
                "failure_observation_kind must be an ObservationKind"
            )
        require_nonempty("failure_payload_ref", self.failure_payload_ref)


def _missing_memory_event_id(
    execution_id: str,
    primitive_step_path: str,
) -> str:
    payload = json.dumps(
        {
            "execution_id": execution_id,
            "primitive_step_path": primitive_step_path,
            "event_type": "missing-memory",
        },
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return f"a009-{hashlib.sha256(payload).hexdigest()[:24]}"


class ContextBoundProcedureExecutor:
    def __init__(
        self,
        simulator: DeterministicProcedureSimulator,
        *,
        requirements: tuple[ActionMemoryRequirement, ...],
        available_memory_ids: tuple[str, ...],
        execution_id: str,
    ) -> None:
        if not isinstance(simulator, DeterministicProcedureSimulator):
            raise ValueError(
                "simulator must be a DeterministicProcedureSimulator"
            )
        require_unique_nonempty("available_memory_ids", available_memory_ids)
        require_nonempty("execution_id", execution_id)
        self._simulator = simulator
        self._requirements = {
            item.action_ref: item
            for item in requirements
        }
        self._available_memory_ids = frozenset(available_memory_ids)
        self._execution_id = execution_id
        self._executed_paths: list[str] = []
        self.initial_world_state_ref = simulator.world_state_ref()

    def execute_action(
        self,
        *,
        action_ref: str,
        execution_id: str,
        call_path: tuple[str, ...],
        step_id: str,
    ) -> Observation:
        require_nonempty("action_ref", action_ref)
        require_nonempty("execution_id", execution_id)
        if execution_id != self._execution_id:
            raise ValueError(
                "execution_id must match executor creation execution_id"
            )
        path = canonical_primitive_step_path(call_path, step_id)
        self._executed_paths.append(path)

        requirement = self._requirements.get(action_ref)
        if requirement is not None:
            missing = tuple(
                memory_id
                for memory_id in requirement.required_memory_ids
                if memory_id not in self._available_memory_ids
            )
            if missing:
                return Observation(
                    observation_id=_missing_memory_event_id(
                        execution_id,
                        path,
                    ),
                    kind=requirement.failure_observation_kind,
                    payload_ref=requirement.failure_payload_ref,
                    expected_match=None,
                    evidence_ids=(),
                )

        return self._simulator.execute_action(
            action_ref=action_ref,
            execution_id=execution_id,
            call_path=call_path,
            step_id=step_id,
        )

    def observe_procedure_completion(
        self,
        *,
        procedure_id: str,
        execution_id: str,
        call_path: tuple[str, ...],
    ) -> Observation:
        require_nonempty("execution_id", execution_id)
        if execution_id != self._execution_id:
            raise ValueError(
                "execution_id must match executor creation execution_id"
            )
        return self._simulator.observe_procedure_completion(
            procedure_id=procedure_id,
            execution_id=execution_id,
            call_path=call_path,
        )

    def world_state(self) -> SimulatedWorldState:
        return self._simulator.world_state()

    def world_state_ref(self) -> str:
        return self._simulator.world_state_ref()

    def executed_primitive_step_paths(self) -> tuple[str, ...]:
        return tuple(self._executed_paths)


class ContextBoundProcedureExecutorFactory:
    def __init__(
        self,
        action_definitions: tuple[SimulatedActionDefinition, ...],
        completion_probes: tuple[SimulatedCompletionProbe, ...],
        initial_state: SimulatedWorldState,
        requirements: tuple[ActionMemoryRequirement, ...],
        failure_overrides: tuple[SimulatedFailureOverride, ...] = (),
    ) -> None:
        if any(
            not isinstance(item, ActionMemoryRequirement)
            for item in requirements
        ):
            raise ValueError(
                "requirements must contain only ActionMemoryRequirement values"
            )
        requirement_action_refs = tuple(
            item.action_ref for item in requirements
        )
        if len(requirement_action_refs) != len(set(requirement_action_refs)):
            raise ValueError(
                "requirement action_ref values must be unique"
            )

        validation_simulator = DeterministicProcedureSimulator(
            action_definitions,
            completion_probes,
            initial_state,
            failure_overrides,
        )
        action_refs = {
            item.action_ref for item in action_definitions
        }
        unknown = tuple(
            action_ref
            for action_ref in requirement_action_refs
            if action_ref not in action_refs
        )
        if unknown:
            raise ValueError(
                f"unknown requirement action_ref: {unknown[0]}"
            )

        self._action_definitions = tuple(action_definitions)
        self._completion_probes = tuple(completion_probes)
        self._initial_state = initial_state
        self._requirements = tuple(requirements)
        self._failure_overrides = tuple(failure_overrides)
        self.initial_world_state_ref = validation_simulator.world_state_ref()

    def create(
        self,
        *,
        available_memory_ids: tuple[str, ...],
        execution_id: str,
    ) -> ContextBoundProcedureExecutor:
        require_unique_nonempty(
            "available_memory_ids",
            available_memory_ids,
        )
        require_nonempty("execution_id", execution_id)
        simulator = DeterministicProcedureSimulator(
            self._action_definitions,
            self._completion_probes,
            self._initial_state,
            self._failure_overrides,
        )
        executor = ContextBoundProcedureExecutor(
            simulator,
            requirements=self._requirements,
            available_memory_ids=available_memory_ids,
            execution_id=execution_id,
        )
        if executor.initial_world_state_ref != self.initial_world_state_ref:
            raise ValueError(
                "fresh executor initial world snapshot does not match factory"
            )
        return executor
