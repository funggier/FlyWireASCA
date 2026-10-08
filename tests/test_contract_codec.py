from __future__ import annotations

import pytest

from flywire_asca.contracts import (
    ActivationBudget,
    Cue,
    CueKind,
    Observation,
    ObservationKind,
    RetrievalState,
    WorkingSet,
    WorkingSetEntry,
    WorkingSetKind,
    dumps_contract,
    loads_contract,
)


def test_nested_working_set_round_trips_with_exact_types_and_deterministic_json():
    budget = ActivationBudget(32, 2, 3, 1024, 2)
    record = WorkingSet(
        entries=(
            WorkingSetEntry("mem-1", WorkingSetKind.MEMORY, 0.9, "cue match"),
            WorkingSetEntry("proc-1", WorkingSetKind.PROCEDURE, 0.7, "routine"),
        ),
        retrieval_state=RetrievalState.PARTIAL_RECALL,
        budget=budget,
    )
    first = dumps_contract(record)
    second = dumps_contract(record)
    assert first == second
    assert '"retrieval_state":"PARTIAL_RECALL"' in first

    restored = loads_contract(WorkingSet, first)
    assert restored == record
    assert isinstance(restored.entries, tuple)
    assert isinstance(restored.entries[0], WorkingSetEntry)
    assert isinstance(restored.entries[0].kind, WorkingSetKind)
    assert isinstance(restored.budget, ActivationBudget)
    assert isinstance(restored.retrieval_state, RetrievalState)


def test_optional_and_tuple_fields_round_trip_without_loss():
    observation = Observation(
        "obs-1",
        ObservationKind.STATE,
        "fixture://state",
        None,
        ("ev-1",),
    )
    restored_observation = loads_contract(
        Observation,
        dumps_contract(observation),
    )
    assert restored_observation == observation
    assert restored_observation.expected_match is None

    cue = Cue(
        "cue-1",
        CueKind.CONTEXT,
        "office",
        0.8,
        evidence_ids=("ev-1",),
        context_tags=("work", "day"),
    )
    restored_cue = loads_contract(Cue, dumps_contract(cue))
    assert restored_cue == cue
    assert isinstance(restored_cue.context_tags, tuple)


def test_codec_rejects_non_dataclass_top_level_values():
    with pytest.raises(TypeError, match="dataclass"):
        dumps_contract({"not": "a contract"})
