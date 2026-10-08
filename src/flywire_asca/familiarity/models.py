from __future__ import annotations

from dataclasses import dataclass

from flywire_asca.contracts import CueKind, RetrievalState
from flywire_asca.contracts.validation import require_nonempty, require_unique_nonempty

from .normalization import normalize_surface


def _require_nonnegative_int(name: str, value: int) -> None:
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise ValueError(f"{name} must be a nonnegative integer")


def _require_canonical_ids(name: str, values: tuple[str, ...]) -> None:
    require_unique_nonempty(name, values)
    if values != tuple(sorted(values)):
        raise ValueError(f"{name} must be sorted in canonical order")


@dataclass(frozen=True, slots=True)
class FamiliarityTrace:
    trace_id: str
    cue_kind: CueKind
    surface_value: str
    region_id: str
    evidence_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        require_nonempty("trace_id", self.trace_id)
        require_nonempty("region_id", self.region_id)
        try:
            normalize_surface(self.surface_value)
        except ValueError as exc:
            raise ValueError("surface_value must not be empty after normalization") from exc
        require_unique_nonempty("evidence_ids", self.evidence_ids)


@dataclass(frozen=True, slots=True)
class FamiliarityCost:
    index_probes: int
    matched_trace_count: int
    total_trace_count: int

    def __post_init__(self) -> None:
        _require_nonnegative_int("index_probes", self.index_probes)
        _require_nonnegative_int("matched_trace_count", self.matched_trace_count)
        _require_nonnegative_int("total_trace_count", self.total_trace_count)
        if self.matched_trace_count > self.total_trace_count:
            raise ValueError(
                "total_trace_count must be >= matched_trace_count"
            )


@dataclass(frozen=True, slots=True)
class FamiliarityResult:
    cue_id: str
    retrieval_state: RetrievalState
    familiarity_score: float
    candidate_region_ids: tuple[str, ...]
    matched_trace_ids: tuple[str, ...]
    cost: FamiliarityCost

    def __post_init__(self) -> None:
        require_nonempty("cue_id", self.cue_id)
        if self.retrieval_state not in (
            RetrievalState.FAMILIAR,
            RetrievalState.UNFAMILIAR,
        ):
            raise ValueError(
                "retrieval_state must be FAMILIAR or UNFAMILIAR"
            )
        _require_canonical_ids("candidate_region_ids", self.candidate_region_ids)
        _require_canonical_ids("matched_trace_ids", self.matched_trace_ids)
        if self.cost.matched_trace_count != len(self.matched_trace_ids):
            raise ValueError(
                "matched_trace_count must equal len(matched_trace_ids)"
            )

        if self.retrieval_state is RetrievalState.FAMILIAR:
            if self.familiarity_score != 1.0:
                raise ValueError("familiarity_score must be 1.0 for FAMILIAR")
            if not self.candidate_region_ids or not self.matched_trace_ids:
                raise ValueError(
                    "FAMILIAR result requires candidate regions and matched traces"
                )
        else:
            if self.familiarity_score != 0.0:
                raise ValueError(
                    "familiarity_score must be 0.0 for UNFAMILIAR"
                )
            if self.candidate_region_ids or self.matched_trace_ids:
                raise ValueError(
                    "UNFAMILIAR result requires empty candidate and trace tuples"
                )
