from __future__ import annotations

from dataclasses import replace

import pytest

from flywire_asca.baseline_comparison import (
    BaselineComparisonReport,
    ComparisonCaseResult,
    ComparisonRunResult,
    ComparisonVariant,
)


def _run(**changes) -> ComparisonRunResult:
    value = ComparisonRunResult(
        variant=ComparisonVariant.ASCA_PRIMARY,
        case_id="case-a",
        procedure_success=True,
        final_state_correct=True,
        final_world_state_ref="world:done",
        evaluated_scope_indices=(0,),
        query_count=1,
        stored_count_sum=16,
        metadata_eligible_count_sum=16,
        scored_vector_count_sum=16,
        above_threshold_count_sum=4,
        returned_count_sum=4,
        cumulative_unique_candidate_count=4,
        cumulative_activated_candidate_count=4,
        cumulative_selected_count=2,
        peak_selected_count=2,
        final_selected_memory_ids=("mem-a", "mem-b"),
        procedure_attempt_count=1,
        execution_ids=("exec-0",),
        procedure_states=("COMPLETED",),
        mismatch_count=0,
        forced_recovery_scope_count=0,
        same_name_identity_preserved=True,
        trace_signature=(("TERMINAL", ("world:done",)),),
    )
    return replace(value, **changes)


def test_comparison_variant_vocabulary_is_exact():
    assert tuple(item.value for item in ComparisonVariant) == (
        "ASCA_PRIMARY",
        "DENSE_EXHAUSTIVE",
        "ASCA_ALWAYS_MAX_SCOPE",
        "ASCA_NO_STRUCTURAL_EXPANSION",
        "ASCA_FAMILIARITY_DISABLED",
    )


@pytest.mark.parametrize(
    ("changes", "message"),
    (
        ({"case_id": ""}, "case_id"),
        ({"query_count": -1}, "query_count"),
        ({"execution_ids": ("same", "same"), "procedure_attempt_count": 2, "procedure_states": ("INTERRUPTED", "COMPLETED")}, "execution_ids"),
        ({"procedure_attempt_count": 2}, "procedure_attempt_count"),
        ({"peak_selected_count": 3}, "peak_selected_count"),
        ({"procedure_success": 1}, "procedure_success"),
        ({"same_name_identity_preserved": 1}, "same_name_identity_preserved"),
    ),
)
def test_comparison_run_result_fails_closed_on_invalid_contract(changes, message):
    with pytest.raises(ValueError, match=message):
        _run(**changes)


def test_comparison_case_requires_unique_variant_runs_and_shared_identity():
    asca = _run()
    dense = replace(asca, variant=ComparisonVariant.DENSE_EXHAUSTIVE, execution_ids=("dense-0",))
    result = ComparisonCaseResult(
        case_id="case-a",
        shared_input_fingerprint="f" * 64,
        validation_error_observed=False,
        validation_error=None,
        runs=(asca, dense),
        expected_primary_case=True,
    )
    assert tuple(run.variant for run in result.runs) == (
        ComparisonVariant.ASCA_PRIMARY,
        ComparisonVariant.DENSE_EXHAUSTIVE,
    )
    with pytest.raises(ValueError, match="variant"):
        replace(result, runs=(asca, asca))


def test_report_rejects_impossible_success_and_identity_counts():
    case = ComparisonCaseResult(
        case_id="case-a",
        shared_input_fingerprint="f" * 64,
        validation_error_observed=False,
        validation_error=None,
        runs=(_run(),),
        expected_primary_case=True,
    )
    report = BaselineComparisonReport(
        case_results=(case,),
        case_count=1,
        valid_case_count=1,
        invalid_case_count=0,
        primary_case_count=1,
        asca_success_count=1,
        dense_success_count=1,
        shared_success_count=1,
        dense_only_success_count=0,
        asca_only_success_count=0,
        asca_final_state_correct_count=1,
        dense_final_state_correct_count=1,
        asca_query_count=1,
        dense_query_count=3,
        asca_scored_vector_count=16,
        dense_scored_vector_count=48,
        asca_cumulative_selected_count=2,
        dense_cumulative_selected_count=8,
        asca_peak_selected_count=2,
        dense_peak_selected_count=8,
        asca_procedure_attempt_count=1,
        dense_procedure_attempt_count=1,
        identity_failure_count=0,
        duplicate_execution_id_failure_count=0,
        post_completion_extra_attempt_failure_count=0,
        designated_parity_reduction_count=1,
        asca_deterministic_repeat_match=True,
        dense_deterministic_repeat_match=True,
    )
    assert report.case_count == 1
    with pytest.raises(ValueError, match="shared_success_count"):
        replace(report, shared_success_count=2)
    with pytest.raises(ValueError, match="identity_failure_count"):
        replace(report, identity_failure_count=2)

def test_comparison_case_requires_sha256_shared_input_fingerprint():
    asca = _run()
    with pytest.raises(ValueError, match="shared_input_fingerprint"):
        ComparisonCaseResult(
            case_id="case-a",
            shared_input_fingerprint="not-a-sha256",
            validation_error_observed=False,
            validation_error=None,
            runs=(asca,),
            expected_primary_case=True,
        )
