from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from flywire_asca.contracts.validation import require_nonempty, require_unique_nonempty


class ComparisonVariant(str, Enum):
    ASCA_PRIMARY = "ASCA_PRIMARY"
    DENSE_EXHAUSTIVE = "DENSE_EXHAUSTIVE"
    ASCA_ALWAYS_MAX_SCOPE = "ASCA_ALWAYS_MAX_SCOPE"
    ASCA_NO_STRUCTURAL_EXPANSION = "ASCA_NO_STRUCTURAL_EXPANSION"
    ASCA_FAMILIARITY_DISABLED = "ASCA_FAMILIARITY_DISABLED"


def _require_nonnegative_int(name: str, value: int) -> None:
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise ValueError(f"{name} must be a nonnegative integer")


def _require_bool(name: str, value: bool) -> None:
    if not isinstance(value, bool):
        raise ValueError(f"{name} must be bool")


def _require_optional_nonempty(name: str, value: str | None) -> None:
    if value is not None:
        require_nonempty(name, value)


@dataclass(frozen=True, slots=True)
class ComparisonRunResult:
    variant: ComparisonVariant
    case_id: str
    procedure_success: bool
    final_state_correct: bool
    final_world_state_ref: str | None
    evaluated_scope_indices: tuple[int, ...]
    query_count: int
    stored_count_sum: int
    metadata_eligible_count_sum: int
    scored_vector_count_sum: int
    above_threshold_count_sum: int
    returned_count_sum: int
    cumulative_unique_candidate_count: int
    cumulative_activated_candidate_count: int
    cumulative_selected_count: int
    peak_selected_count: int
    final_selected_memory_ids: tuple[str, ...]
    procedure_attempt_count: int
    execution_ids: tuple[str, ...]
    procedure_states: tuple[str, ...]
    mismatch_count: int
    forced_recovery_scope_count: int
    same_name_identity_preserved: bool
    trace_signature: tuple[tuple[str, tuple[str, ...]], ...]

    def __post_init__(self) -> None:
        if not isinstance(self.variant, ComparisonVariant):
            raise ValueError("variant must be a ComparisonVariant")
        require_nonempty("case_id", self.case_id)
        _require_bool("procedure_success", self.procedure_success)
        _require_bool("final_state_correct", self.final_state_correct)
        if self.final_state_correct and not self.procedure_success:
            raise ValueError("final_state_correct requires procedure_success")
        _require_optional_nonempty("final_world_state_ref", self.final_world_state_ref)

        if not self.evaluated_scope_indices:
            raise ValueError("evaluated_scope_indices must not be empty")
        for value in self.evaluated_scope_indices:
            _require_nonnegative_int("evaluated_scope_indices", value)

        for name in (
            "query_count",
            "stored_count_sum",
            "metadata_eligible_count_sum",
            "scored_vector_count_sum",
            "above_threshold_count_sum",
            "returned_count_sum",
            "cumulative_unique_candidate_count",
            "cumulative_activated_candidate_count",
            "cumulative_selected_count",
            "peak_selected_count",
            "procedure_attempt_count",
            "mismatch_count",
            "forced_recovery_scope_count",
        ):
            _require_nonnegative_int(name, getattr(self, name))

        if not (
            self.returned_count_sum
            <= self.above_threshold_count_sum
            <= self.scored_vector_count_sum
            <= self.metadata_eligible_count_sum
            <= self.stored_count_sum
        ):
            raise ValueError("retrieval count sums must be monotonically bounded")
        if self.cumulative_activated_candidate_count > self.cumulative_unique_candidate_count:
            raise ValueError(
                "cumulative_activated_candidate_count cannot exceed cumulative_unique_candidate_count"
            )
        if self.cumulative_selected_count > self.cumulative_activated_candidate_count:
            raise ValueError(
                "cumulative_selected_count cannot exceed cumulative_activated_candidate_count"
            )
        if self.peak_selected_count > self.cumulative_selected_count:
            raise ValueError("peak_selected_count cannot exceed cumulative_selected_count")
        require_unique_nonempty(
            "final_selected_memory_ids", self.final_selected_memory_ids
        )
        if len(self.final_selected_memory_ids) > self.peak_selected_count:
            raise ValueError(
                "final_selected_memory_ids cannot exceed peak_selected_count"
            )

        require_unique_nonempty("execution_ids", self.execution_ids)
        if self.procedure_attempt_count != len(self.execution_ids):
            raise ValueError(
                "procedure_attempt_count must equal len(execution_ids)"
            )
        if len(self.procedure_states) != self.procedure_attempt_count:
            raise ValueError(
                "procedure_states length must equal procedure_attempt_count"
            )
        for state in self.procedure_states:
            require_nonempty("procedure_states", state)
        if self.mismatch_count > self.procedure_attempt_count:
            raise ValueError("mismatch_count cannot exceed procedure_attempt_count")
        if self.forced_recovery_scope_count > max(
            0, self.procedure_attempt_count - 1
        ):
            raise ValueError(
                "forced_recovery_scope_count cannot exceed replay count"
            )
        _require_bool(
            "same_name_identity_preserved", self.same_name_identity_preserved
        )
        for kind, refs in self.trace_signature:
            require_nonempty("trace kind", kind)
            require_unique_nonempty("trace refs", refs)


@dataclass(frozen=True, slots=True)
class ComparisonCaseResult:
    case_id: str
    shared_input_fingerprint: str
    validation_error_observed: bool
    validation_error: str | None
    runs: tuple[ComparisonRunResult, ...]
    expected_primary_case: bool

    def __post_init__(self) -> None:
        require_nonempty("case_id", self.case_id)
        require_nonempty("shared_input_fingerprint", self.shared_input_fingerprint)
        _require_bool("validation_error_observed", self.validation_error_observed)
        _require_bool("expected_primary_case", self.expected_primary_case)
        variants: list[ComparisonVariant] = []
        for run in self.runs:
            if not isinstance(run, ComparisonRunResult):
                raise ValueError("runs must contain ComparisonRunResult values")
            if run.case_id != self.case_id:
                raise ValueError("run case_id must match case result case_id")
            variants.append(run.variant)
        if len(variants) != len(set(variants)):
            raise ValueError("runs must contain unique variant values")
        if self.validation_error_observed:
            if self.validation_error is None:
                raise ValueError(
                    "validation_error_observed requires validation_error"
                )
            require_nonempty("validation_error", self.validation_error)
        elif self.validation_error is not None:
            raise ValueError(
                "validation_error must be None when no validation error was observed"
            )


@dataclass(frozen=True, slots=True)
class BaselineComparisonReport:
    case_results: tuple[ComparisonCaseResult, ...]
    case_count: int
    valid_case_count: int
    invalid_case_count: int
    primary_case_count: int
    asca_success_count: int
    dense_success_count: int
    shared_success_count: int
    dense_only_success_count: int
    asca_only_success_count: int
    asca_final_state_correct_count: int
    dense_final_state_correct_count: int
    asca_query_count: int
    dense_query_count: int
    asca_scored_vector_count: int
    dense_scored_vector_count: int
    asca_cumulative_selected_count: int
    dense_cumulative_selected_count: int
    asca_peak_selected_count: int
    dense_peak_selected_count: int
    asca_procedure_attempt_count: int
    dense_procedure_attempt_count: int
    identity_failure_count: int
    duplicate_execution_id_failure_count: int
    post_completion_extra_attempt_failure_count: int
    designated_parity_reduction_count: int
    asca_deterministic_repeat_match: bool
    dense_deterministic_repeat_match: bool

    def __post_init__(self) -> None:
        if any(
            not isinstance(item, ComparisonCaseResult) for item in self.case_results
        ):
            raise ValueError(
                "case_results must contain ComparisonCaseResult values"
            )
        for name in (
            "case_count",
            "valid_case_count",
            "invalid_case_count",
            "primary_case_count",
            "asca_success_count",
            "dense_success_count",
            "shared_success_count",
            "dense_only_success_count",
            "asca_only_success_count",
            "asca_final_state_correct_count",
            "dense_final_state_correct_count",
            "asca_query_count",
            "dense_query_count",
            "asca_scored_vector_count",
            "dense_scored_vector_count",
            "asca_cumulative_selected_count",
            "dense_cumulative_selected_count",
            "asca_peak_selected_count",
            "dense_peak_selected_count",
            "asca_procedure_attempt_count",
            "dense_procedure_attempt_count",
            "identity_failure_count",
            "duplicate_execution_id_failure_count",
            "post_completion_extra_attempt_failure_count",
            "designated_parity_reduction_count",
        ):
            _require_nonnegative_int(name, getattr(self, name))
        _require_bool(
            "asca_deterministic_repeat_match", self.asca_deterministic_repeat_match
        )
        _require_bool(
            "dense_deterministic_repeat_match",
            self.dense_deterministic_repeat_match,
        )
        if self.case_count != len(self.case_results):
            raise ValueError("case_count must equal len(case_results)")
        if self.case_count != self.valid_case_count + self.invalid_case_count:
            raise ValueError(
                "case_count must equal valid_case_count + invalid_case_count"
            )
        if self.primary_case_count > self.valid_case_count:
            raise ValueError("primary_case_count cannot exceed valid_case_count")
        for name in ("asca_success_count", "dense_success_count"):
            if getattr(self, name) > self.primary_case_count:
                raise ValueError(f"{name} cannot exceed primary_case_count")
        if self.shared_success_count > min(
            self.asca_success_count, self.dense_success_count
        ):
            raise ValueError(
                "shared_success_count cannot exceed either success count"
            )
        if (
            self.shared_success_count + self.dense_only_success_count
            != self.dense_success_count
        ):
            raise ValueError(
                "dense_success_count must equal shared_success_count + dense_only_success_count"
            )
        if (
            self.shared_success_count + self.asca_only_success_count
            != self.asca_success_count
        ):
            raise ValueError(
                "asca_success_count must equal shared_success_count + asca_only_success_count"
            )
        if self.asca_final_state_correct_count > self.asca_success_count:
            raise ValueError(
                "asca_final_state_correct_count cannot exceed asca_success_count"
            )
        if self.dense_final_state_correct_count > self.dense_success_count:
            raise ValueError(
                "dense_final_state_correct_count cannot exceed dense_success_count"
            )
        if self.identity_failure_count > self.valid_case_count:
            raise ValueError(
                "identity_failure_count cannot exceed valid_case_count"
            )
        if self.designated_parity_reduction_count > self.shared_success_count:
            raise ValueError(
                "designated_parity_reduction_count cannot exceed shared_success_count"
            )
