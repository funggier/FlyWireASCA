from __future__ import annotations

import hashlib
import json

from flywire_asca.contracts import Observation
from flywire_asca.contracts.validation import require_nonempty

from .library import canonical_primitive_step_path
from .models import (
    SimulatedActionDefinition,
    SimulatedCompletionProbe,
    SimulatedFailureOverride,
    SimulatedWorldState,
)


def _event_id(
    execution_id: str,
    call_path: tuple[str, ...],
    step_or_procedure: str,
    event_type: str,
) -> str:
    require_nonempty("execution_id", execution_id)
    payload = json.dumps(
        {
            "execution_id": execution_id,
            "call_path": call_path,
            "subject": step_or_procedure,
            "event_type": event_type,
        },
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return f"a008-{hashlib.sha256(payload).hexdigest()[:24]}"


class DeterministicProcedureSimulator:
    def __init__(
        self,
        action_definitions: tuple[SimulatedActionDefinition, ...],
        completion_probes: tuple[SimulatedCompletionProbe, ...],
        initial_state: SimulatedWorldState,
        failure_overrides: tuple[SimulatedFailureOverride, ...] = (),
    ) -> None:
        if not isinstance(initial_state, SimulatedWorldState):
            raise ValueError("initial_state must be a SimulatedWorldState")
        actions = tuple(action_definitions)
        if any(not isinstance(item, SimulatedActionDefinition) for item in actions):
            raise ValueError("action_definitions must contain SimulatedActionDefinition values")
        action_ids = tuple(item.action_ref for item in actions)
        if len(action_ids) != len(set(action_ids)):
            raise ValueError("action_ref values must be unique")

        probes = tuple(completion_probes)
        if any(not isinstance(item, SimulatedCompletionProbe) for item in probes):
            raise ValueError("completion_probes must contain SimulatedCompletionProbe values")
        probe_ids = tuple(item.procedure_id for item in probes)
        if len(probe_ids) != len(set(probe_ids)):
            raise ValueError("completion probe procedure_id values must be unique")

        overrides = tuple(failure_overrides)
        if any(not isinstance(item, SimulatedFailureOverride) for item in overrides):
            raise ValueError("failure_overrides must contain SimulatedFailureOverride values")
        override_ids = tuple(item.primitive_step_path for item in overrides)
        if len(override_ids) != len(set(override_ids)):
            raise ValueError("failure override primitive_step_path values must be unique")

        self._actions = {item.action_ref: item for item in actions}
        self._probes = {item.procedure_id: item for item in probes}
        self._overrides = {item.primitive_step_path: item for item in overrides}
        self._state = dict(initial_state.values)
        self._executed_paths: list[str] = []

    def execute_action(
        self,
        *,
        action_ref: str,
        execution_id: str,
        call_path: tuple[str, ...],
        step_id: str,
    ) -> Observation:
        require_nonempty("action_ref", action_ref)
        definition = self._actions.get(action_ref)
        if definition is None:
            raise ValueError(f"unknown action_ref: {action_ref}")
        path = canonical_primitive_step_path(call_path, step_id)
        override = self._overrides.get(path)

        if override is None or not override.suppress_writes:
            for key, value in definition.writes:
                self._state[key] = value

        self._executed_paths.append(path)
        kind = override.observation_kind if override else definition.observation_kind
        payload = override.payload_ref if override else definition.success_payload_ref
        return Observation(
            observation_id=_event_id(execution_id, call_path, step_id, "action"),
            kind=kind,
            payload_ref=payload,
            expected_match=None,
            evidence_ids=(),
        )

    def observe_procedure_completion(
        self,
        *,
        procedure_id: str,
        execution_id: str,
        call_path: tuple[str, ...],
    ) -> Observation:
        require_nonempty("procedure_id", procedure_id)
        probe = self._probes.get(procedure_id)
        if probe is None:
            raise ValueError(f"missing completion probe for procedure_id: {procedure_id}")
        if probe.state_key not in self._state:
            raise ValueError(
                f"completion probe state key is missing: {probe.state_key}"
            )
        return Observation(
            observation_id=_event_id(
                execution_id,
                call_path,
                procedure_id,
                "completion",
            ),
            kind=probe.observation_kind,
            payload_ref=self._state[probe.state_key],
            expected_match=None,
            evidence_ids=(),
        )

    def world_state(self) -> SimulatedWorldState:
        return SimulatedWorldState(tuple(self._state.items()))

    def world_state_ref(self) -> str:
        payload = json.dumps(
            self.world_state().values,
            ensure_ascii=False,
            separators=(",", ":"),
        ).encode("utf-8")
        return hashlib.sha256(payload).hexdigest()

    def executed_primitive_step_paths(self) -> tuple[str, ...]:
        return tuple(self._executed_paths)
