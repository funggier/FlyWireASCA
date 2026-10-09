from __future__ import annotations

import json

import pytest

from flywire_asca.embedding import (
    EmbeddingDescriptor,
    EmbeddingRequest,
    EmbeddingResponse,
    normalize_embedding_values,
)
from flywire_asca.vector_memory import (
    GraphDecision,
    VectorMemoryBenchmarkReport,
    build_a005_portable_calibration_fixture,
    build_a005_portable_qualification_fixture,
    calibrate_a005_threshold,
    benchmark_report_payload,
    decide_graph_need,
    qualify_a005_report,
    run_vector_memory_benchmark,
)


class FixtureEmbeddingAdapter:
    def __init__(self, vector_entries, *, digest="fixture-digest"):
        self.vectors = dict(vector_entries)
        dimension = len(next(iter(self.vectors.values())))
        self.descriptor = EmbeddingDescriptor(
            backend_name="fixture",
            backend_version="1",
            model_name="fixture-embedder",
            model_digest=digest,
            architecture="fixture",
            parameter_count=None,
            parameter_size=None,
            quantization=None,
            context_length=8192,
            embedding_dimension=dimension,
            capabilities=("embedding",),
        )
        self.requests: list[EmbeddingRequest] = []

    def inspect(self):
        return self.descriptor

    def embed(self, request):
        self.requests.append(request)
        vectors = tuple(
            normalize_embedding_values(
                self.vectors[text],
                expected_dimension=self.descriptor.embedding_dimension,
            )
            for text in request.texts
        )
        return EmbeddingResponse(
            request.request_id,
            self.descriptor.model_name,
            self.descriptor.model_digest,
            vectors,
            len(vectors),
            None,
            None,
            None,
        )


def test_portable_calibration_and_qualification_fixtures_are_disjoint():
    calibration = build_a005_portable_calibration_fixture()
    cal_adapter = FixtureEmbeddingAdapter(calibration.embedding_vectors)
    threshold = calibrate_a005_threshold(
        calibration.documents,
        cal_adapter,
        calibration.cases,
        embedding_profile=calibration.embedding_profile,
    )
    qualification = build_a005_portable_qualification_fixture(
        frozen_threshold=threshold
    )

    assert -1.0 <= threshold <= 1.0
    assert threshold == pytest.approx(0.5)
    assert {case.case_id for case in calibration.cases}.isdisjoint(
        {case.case_id for case in qualification.cases}
    )
    assert qualification.frozen_threshold == threshold
    assert "portable" in qualification.embedding_profile
    assert qualification.threshold_origin == "portable_fake_geometry_only"


def test_portable_qualification_fixture_covers_required_cases_and_distractors():
    calibration = build_a005_portable_calibration_fixture()
    threshold = calibrate_a005_threshold(
        calibration.documents,
        FixtureEmbeddingAdapter(calibration.embedding_vectors),
        calibration.cases,
        embedding_profile=calibration.embedding_profile,
    )
    fixture = build_a005_portable_qualification_fixture(
        frozen_threshold=threshold
    )
    case_ids = {case.case_id for case in fixture.cases}
    assert {
        "english-paraphrase",
        "thai-paraphrase",
        "thai-to-english",
        "english-to-thai",
        "exact-wording",
        "same-name-ambiguity",
        "entity-filter",
        "context-filter",
        "confidence-independence",
        "distractor-corpus",
        "threshold-no-hit",
        "tie-order",
    } == case_ids
    assert len(
        [doc for doc in fixture.documents if doc.memory.memory_id.startswith("distractor-")]
    ) == 256


def test_portable_report_meets_declared_retrieval_gates_deterministically():
    calibration = build_a005_portable_calibration_fixture()
    threshold = calibrate_a005_threshold(
        calibration.documents,
        FixtureEmbeddingAdapter(calibration.embedding_vectors),
        calibration.cases,
        embedding_profile=calibration.embedding_profile,
    )
    fixture = build_a005_portable_qualification_fixture(
        frozen_threshold=threshold
    )
    adapter = FixtureEmbeddingAdapter(fixture.embedding_vectors)
    report = run_vector_memory_benchmark(
        fixture.documents,
        adapter,
        fixture.cases,
        embedding_profile=fixture.embedding_profile,
        frozen_threshold=fixture.frozen_threshold,
        threshold_origin=fixture.threshold_origin,
    )

    assert report.case_count == 12
    assert report.frozen_threshold == pytest.approx(0.5)
    assert report.threshold_origin == "portable_fake_geometry_only"
    assert report.recall_at_1 == 1.0
    assert report.recall_at_k == 1.0
    assert report.mean_reciprocal_rank == 1.0
    assert report.no_hit_correctness == 1.0
    assert report.metadata_filter_correctness == 1.0
    assert report.false_retrieval_count == 0
    assert report.ambiguity_failure_count == 0
    assert report.relation_semantic_failure_count == 0
    assert report.embedding_request_count == 13
    assert report.embedding_input_count == len(fixture.documents) + 12
    assert qualify_a005_report(report) == []
    assert decide_graph_need(report) is GraphDecision.VECTOR_SUFFICIENT

    payload1 = benchmark_report_payload(report)
    payload2 = benchmark_report_payload(report)
    assert payload1 == payload2
    encoded = json.dumps(payload1, sort_keys=True).lower()
    assert "flop" not in encoded
    assert "energy" not in encoded


def _synthetic_report(**overrides):
    values = dict(
        scope="controlled_fixture_only",
        frozen_threshold=0.5,
        threshold_origin="synthetic",
        case_results=(),
        case_count=0,
        recall_at_1=1.0,
        recall_at_k=1.0,
        mean_reciprocal_rank=1.0,
        no_hit_correctness=1.0,
        metadata_filter_correctness=1.0,
        false_retrieval_count=0,
        ambiguity_failure_count=0,
        relation_semantic_failure_count=0,
        scalability_warning_count=0,
        stored_memory_count=0,
        vector_scored_total=0,
        embedding_request_count=0,
        embedding_input_count=0,
        embedding_model_name="synthetic",
        embedding_model_digest="digest",
        embedding_profile="profile",
    )
    values.update(overrides)
    return VectorMemoryBenchmarkReport(**values)


def test_graph_decision_has_three_deterministic_branches():
    assert (
        decide_graph_need(_synthetic_report())
        is GraphDecision.VECTOR_SUFFICIENT
    )
    assert (
        decide_graph_need(_synthetic_report(scalability_warning_count=1))
        is GraphDecision.VECTOR_NEEDS_INDEX_OR_METADATA
    )
    assert (
        decide_graph_need(_synthetic_report(recall_at_k=0.8))
        is GraphDecision.VECTOR_NEEDS_INDEX_OR_METADATA
    )
    assert (
        decide_graph_need(_synthetic_report(relation_semantic_failure_count=1))
        is GraphDecision.GRAPH_JUSTIFIED
    )


def test_qualifier_rejects_wrong_metrics_without_biasing_graph_decision():
    report = _synthetic_report(
        recall_at_1=0.0,
        recall_at_k=0.0,
        mean_reciprocal_rank=0.0,
        no_hit_correctness=0.0,
        metadata_filter_correctness=0.0,
        false_retrieval_count=2,
        ambiguity_failure_count=1,
    )
    errors = qualify_a005_report(report)
    assert "recall_at_1 must be 1.0" in errors
    assert "recall_at_k must be 1.0" in errors
    assert "false_retrieval_count must be 0" in errors
    assert decide_graph_need(report) is GraphDecision.VECTOR_NEEDS_INDEX_OR_METADATA
