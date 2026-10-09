from flywire_asca.procedural_memory import (
    ProcedureExecutionMode,
    build_a008_fixture,
    classify_a008_hypothesis,
    qualify_a008_report,
    run_a008_benchmark,
)


def test_fixture_covers_success_failure_reuse_depth_and_invalid_families():
    cases=build_a008_fixture()
    ids={c.case_id for c in cases}
    assert {
        "tea-success","coffee-success","document-backup-success",
        "package-preparation-success","heat-water-failure",
        "direct-recursion-invalid","indirect-recursion-invalid",
        "missing-callee-invalid","depth-nine-invalid",
    } <= ids
    assert len(ids)==len(cases)


def test_shared_heat_water_is_reused_by_distinct_parents():
    report=run_a008_benchmark(build_a008_fixture())
    reuse=dict(report.chunk_reuse_counts)
    assert reuse["heat-water"] >= 2
    assert "heat-water" in report.reused_procedure_ids


def test_success_cases_preserve_flat_chunked_sequence_and_final_state():
    report=run_a008_benchmark(build_a008_fixture())
    assert report.success_case_count >= 4
    assert report.flat_success_count==report.success_case_count
    assert report.chunked_success_count==report.success_case_count
    assert report.blind_success_count==report.success_case_count
    assert report.primitive_sequence_equivalence_count==report.success_case_count
    assert report.flat_final_state_correct_count==report.success_case_count
    assert report.chunked_final_state_correct_count==report.success_case_count
    assert report.blind_final_state_correct_count==report.success_case_count


def test_chunked_reduces_root_visible_dispatch_and_compression_exceeds_one():
    report=run_a008_benchmark(build_a008_fixture())
    assert report.aggregate_chunked_root_visible_dispatches < report.aggregate_flat_root_visible_dispatches
    assert report.max_deliberative_compression_ratio > 1.0


def test_checked_failure_localization_and_blind_negative_control():
    report=run_a008_benchmark(build_a008_fixture())
    assert report.checked_failure_case_count >= 1
    assert report.flat_exact_failure_localization_count==report.checked_failure_case_count
    assert report.chunked_exact_failure_localization_count==report.checked_failure_case_count
    assert report.blind_boundary_localization_count==report.checked_failure_case_count
    assert report.explanation_provenance_correct_count==report.checked_failure_case_count * 3
    assert report.no_post_interruption_failure_count==0


def test_invalid_library_cases_fail_before_execution_and_are_excluded():
    report=run_a008_benchmark(build_a008_fixture())
    assert report.invalid_case_count==4
    assert report.invalid_validation_failure_count==0
    invalid=[r for r in report.case_results if r.expected_validation_error is not None]
    assert len(invalid)==4
    assert all(r.validation_error_observed for r in invalid)
    assert all(not r.mode_results for r in invalid)


def test_mode_metric_invariants_hold():
    report=run_a008_benchmark(build_a008_fixture())
    for case in report.case_results:
        if case.expected_validation_error is not None:
            continue
        by_mode={x.mode:x for x in case.mode_results}
        flat=by_mode[ProcedureExecutionMode.FLAT]
        chunk=by_mode[ProcedureExecutionMode.CHUNKED]
        blind=by_mode[ProcedureExecutionMode.BLIND_CHUNKED]
        assert flat.metrics.procedure_call_count==0
        assert flat.metrics.root_visible_dispatch_count==flat.metrics.primitive_action_count
        assert chunk.metrics.suppressed_internal_check_count==0
        assert blind.metrics.root_visible_dispatch_count==chunk.metrics.root_visible_dispatch_count


def test_report_is_deterministic_and_engineering_qualifier_passes():
    first=run_a008_benchmark(build_a008_fixture())
    second=run_a008_benchmark(build_a008_fixture())
    assert first==second
    assert first.deterministic_repeat_match is True
    assert qualify_a008_report(first)==[]


def test_primary_hypothesis_is_supported_by_frozen_fixture():
    report=run_a008_benchmark(build_a008_fixture())
    assert classify_a008_hypothesis(report)=="SUPPORTED"
