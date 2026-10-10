from __future__ import annotations

from dataclasses import replace

from flywire_asca.relational_reasoning import (
    ArchitectureDecision,
    ComparisonVariant,
)
from flywire_asca.relational_reasoning.benchmark import (
    EXPECTED_A012_CASE_IDS,
    EXPECTED_A012_FIXTURE_FINGERPRINT,
    EXPECTED_A012_SHARED_INPUT_FINGERPRINTS,
    a012_fixture_fingerprint,
    build_a012_deterministic_fixture,
    classify_a012_architecture,
    qualify_a012_report,
    run_a012_benchmark,
    shared_input_fingerprint,
)


def _run(case_result, variant: ComparisonVariant):
    return next(item for item in case_result.runs if item.variant is variant)


def test_fixture_case_ids_and_fingerprints_are_stable():
    cases = build_a012_deterministic_fixture()
    assert tuple(case.case_id for case in cases) == EXPECTED_A012_CASE_IDS
    assert len(cases) == 12

    fixture_fp = a012_fixture_fingerprint(cases)
    assert len(fixture_fp) == 64
    int(fixture_fp, 16)
    assert a012_fixture_fingerprint(build_a012_deterministic_fixture()) == fixture_fp
    assert fixture_fp == EXPECTED_A012_FIXTURE_FINGERPRINT

    shared = tuple(shared_input_fingerprint(case) for case in cases)
    assert len(set(shared)) == len(shared)
    assert tuple(zip(EXPECTED_A012_CASE_IDS, shared)) == EXPECTED_A012_SHARED_INPUT_FINGERPRINTS


def test_literal_frozen_anchors_reject_semantic_fixture_mutation():
    cases = build_a012_deterministic_fixture()
    changed = replace(cases[0], query_text=cases[0].query_text + " changed")
    mutated = (changed, *cases[1:])
    report = run_a012_benchmark(mutated)

    errors = qualify_a012_report(report)
    assert any("fixture fingerprint" in error for error in errors)
    assert any("shared input fingerprint" in error for error in errors)


def test_primary_relation_cases_are_real_relation_only_recoveries():
    report = run_a012_benchmark(build_a012_deterministic_fixture())
    primary_ids = {
        "ownership-workplace-one-hop",
        "causal-one-hop",
        "temporal-one-hop",
        "part-of-two-hop",
        "used-for-one-hop",
        "same-name-disambiguated-ownership",
    }
    seen = set()

    for case in report.case_results:
        if case.case_id not in primary_ids:
            continue
        seen.add(case.case_id)
        vector = _run(case, ComparisonVariant.VECTOR_METADATA)
        relation = _run(case, ComparisonVariant.BOUNDED_RELATION)
        assert vector.task_success is False
        assert relation.task_success is True
        assert relation.relation_path_edge_ids
        assert relation.relation_path_memory_ids
        assert relation.provenance_complete is True

    assert seen == primary_ids
    assert report.primary_relation_case_count == 6
    assert report.relation_only_recovery_count == 6


def test_vector_direct_control_remains_shared_success_without_relation_scan():
    report = run_a012_benchmark(build_a012_deterministic_fixture())
    case = next(item for item in report.case_results if item.case_id == "vector-direct-control")
    vector = _run(case, ComparisonVariant.VECTOR_METADATA)
    relation = _run(case, ComparisonVariant.BOUNDED_RELATION)

    assert vector.task_success is True
    assert relation.task_success is True
    assert relation.relation_scanned_edge_count == 0
    assert relation.relation_path_edge_ids == ()


def test_negative_controls_fail_closed_without_false_target_discovery():
    report = run_a012_benchmark(build_a012_deterministic_fixture())
    for case_id in (
        "cycle-control",
        "low-confidence-edge-control",
        "relation-allowlist-control",
        "missing-target-control",
    ):
        case = next(item for item in report.case_results if item.case_id == case_id)
        relation = _run(case, ComparisonVariant.BOUNDED_RELATION)
        assert relation.task_success is True
        assert relation.found_target_ids == ()
        assert relation.false_target_count == 0

    assert report.identity_failure_count == 0
    assert report.provenance_failure_count == 0
    assert report.budget_violation_count == 0
    assert report.duplicate_visit_failure_count == 0


def test_same_name_case_selects_intended_seed_without_identity_collapse():
    report = run_a012_benchmark(build_a012_deterministic_fixture())
    case = next(
        item for item in report.case_results
        if item.case_id == "same-name-disambiguated-ownership"
    )
    relation = _run(case, ComparisonVariant.BOUNDED_RELATION)
    assert relation.initially_retrieved_ids == ("person-alex-b",)
    assert relation.found_target_ids == ("company-b",)
    assert "person-alex-a" not in relation.final_selected_ids
    assert relation.identity_preserved is True


def test_invalid_contract_is_first_class_and_not_executed():
    report = run_a012_benchmark(build_a012_deterministic_fixture())
    invalid = next(item for item in report.case_results if item.case_id == "invalid-contract-control")
    assert invalid.validation_error_observed is True
    assert invalid.runs == ()
    assert report.invalid_case_count == 1
    assert report.valid_case_count == 11


def test_empty_retrieval_seed_is_valid_miss_not_invalid_contract():
    from flywire_asca.contracts import RelationType
    from flywire_asca.embedding import (
        EmbeddingDescriptor,
        EmbeddingResponse,
        normalize_embedding_values,
    )
    from flywire_asca.relational_reasoning.benchmark import (
        RelationalBenchmarkCase,
        RelationalMemorySpec,
        run_a012_benchmark_with_adapter,
    )
    from flywire_asca.contracts import AssociationEdge

    class NoSeedAdapter:
        def inspect(self):
            return EmbeddingDescriptor(
                backend_name="fake",
                backend_version="1",
                model_name="fake",
                model_digest="digest",
                architecture="fake",
                parameter_count=None,
                parameter_size=None,
                quantization=None,
                context_length=1024,
                embedding_dimension=3,
                capabilities=("embedding",),
            )

        def embed(self, request):
            vectors = []
            for text in request.texts:
                raw = (1.0, 0.0, 0.0) if text == "query" else (0.0, 1.0, 0.0)
                vectors.append(normalize_embedding_values(raw))
            return EmbeddingResponse(
                request.request_id,
                "fake",
                "digest",
                tuple(vectors),
                len(vectors),
                0,
                0,
                0,
            )

    case = RelationalBenchmarkCase(
        case_id="no-seed-valid-miss",
        memories=(
            RelationalMemorySpec("seed", "seed-doc", (0.0, 1.0, 0.0)),
            RelationalMemorySpec("target", "target-doc", (0.0, 0.0, 1.0)),
        ),
        edges=(
            AssociationEdge(
                "edge",
                "seed",
                "target",
                RelationType.WORKS_AT,
                0.8,
                0.9,
                ("evidence",),
            ),
        ),
        query_text="query",
        query_vector=(1.0, 0.0, 0.0),
        target_memory_ids=("target",),
        allowed_relations=(RelationType.WORKS_AT,),
        expected_found=True,
        relation_dependent=True,
    )
    report = run_a012_benchmark_with_adapter(
        (case,),
        NoSeedAdapter(),
        minimum_similarity=0.9,
        embedding_profile="test",
    )
    assert report.valid_case_count == 1
    assert report.invalid_case_count == 0
    result = report.case_results[0]
    vector = _run(result, ComparisonVariant.VECTOR_METADATA)
    relation = _run(result, ComparisonVariant.BOUNDED_RELATION)
    assert vector.initially_retrieved_ids == ()
    assert vector.task_success is False
    assert relation.final_selected_ids == ()
    assert relation.task_success is False


def test_actual_fixture_justifies_explicit_relation_traversal():
    report = run_a012_benchmark(build_a012_deterministic_fixture())
    assert report.deterministic_repeat_match is True
    assert report.relation_success_count > report.vector_success_count
    assert report.relation_only_recovery_count >= 3
    assert report.regression_count == 0
    assert qualify_a012_report(report) == []
    assert (
        classify_a012_architecture(report)
        is ArchitectureDecision.EXPLICIT_RELATION_TRAVERSAL_JUSTIFIED
    )


def test_classifier_retains_vector_or_mixed_branches():
    report = run_a012_benchmark(build_a012_deterministic_fixture())

    vector_sufficient = replace(
        report,
        vector_success_count=report.relation_success_count,
        shared_success_count=report.relation_success_count,
        relation_only_recovery_count=0,
    )
    assert (
        classify_a012_architecture(vector_sufficient)
        is ArchitectureDecision.VECTOR_METADATA_REMAINS_SUFFICIENT
    )

    mixed = replace(report, regression_count=1)
    assert classify_a012_architecture(mixed) is ArchitectureDecision.MIXED


def test_qualifier_rejects_aggregate_and_fingerprint_drift():
    report = run_a012_benchmark(build_a012_deterministic_fixture())
    assert qualify_a012_report(report) == []

    errors = qualify_a012_report(
        replace(report, relation_only_recovery_count=report.relation_only_recovery_count + 1)
    )
    assert any("relation_only_recovery_count" in error for error in errors)

    first = report.case_results[0]
    drifted = replace(first, shared_input_fingerprint="0" * 64)
    errors = qualify_a012_report(
        replace(report, case_results=(drifted, *report.case_results[1:]))
    )
    assert any("fingerprint" in error.lower() for error in errors)
