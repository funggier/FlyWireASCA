from __future__ import annotations

from collections.abc import Iterable

from flywire_asca.contracts import Cue, RetrievalState

from .models import FamiliarityCost, FamiliarityResult, FamiliarityTrace
from .normalization import familiarity_key


def _materialize_traces(
    traces: Iterable[FamiliarityTrace],
) -> tuple[FamiliarityTrace, ...]:
    materialized = tuple(traces)
    trace_ids = tuple(trace.trace_id for trace in materialized)
    if len(set(trace_ids)) != len(trace_ids):
        raise ValueError("duplicate trace_id values are not allowed")
    return materialized


def _build_result(
    cue: Cue,
    matches: tuple[FamiliarityTrace, ...],
    *,
    index_probes: int,
    total_trace_count: int,
) -> FamiliarityResult:
    matched_trace_ids = tuple(sorted(trace.trace_id for trace in matches))
    candidate_region_ids = tuple(sorted({trace.region_id for trace in matches}))
    familiar = bool(matches)
    return FamiliarityResult(
        cue_id=cue.cue_id,
        retrieval_state=(
            RetrievalState.FAMILIAR
            if familiar
            else RetrievalState.UNFAMILIAR
        ),
        familiarity_score=1.0 if familiar else 0.0,
        candidate_region_ids=candidate_region_ids,
        matched_trace_ids=matched_trace_ids,
        cost=FamiliarityCost(
            index_probes=index_probes,
            matched_trace_count=len(matched_trace_ids),
            total_trace_count=total_trace_count,
        ),
    )


class ExactFamiliarityIndex:
    def __init__(self, traces: Iterable[FamiliarityTrace]) -> None:
        self._traces = _materialize_traces(traces)
        buckets: dict[tuple[object, str], list[FamiliarityTrace]] = {}
        for trace in self._traces:
            key = familiarity_key(trace.cue_kind, trace.surface_value)
            buckets.setdefault(key, []).append(trace)
        self._buckets = {
            key: tuple(values)
            for key, values in buckets.items()
        }

    def assess(self, cue: Cue) -> FamiliarityResult:
        key = familiarity_key(cue.kind, cue.value)
        matches = self._buckets.get(key, ())
        return _build_result(
            cue,
            matches,
            index_probes=1,
            total_trace_count=len(self._traces),
        )


class ExhaustiveFamiliarityBaseline:
    def __init__(self, traces: Iterable[FamiliarityTrace]) -> None:
        self._traces = _materialize_traces(traces)

    def assess(self, cue: Cue) -> FamiliarityResult:
        key = familiarity_key(cue.kind, cue.value)
        matches = tuple(
            trace
            for trace in self._traces
            if familiarity_key(trace.cue_kind, trace.surface_value) == key
        )
        return _build_result(
            cue,
            matches,
            index_probes=len(self._traces),
            total_trace_count=len(self._traces),
        )
