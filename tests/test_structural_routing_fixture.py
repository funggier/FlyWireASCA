from __future__ import annotations

from collections import Counter
from dataclasses import replace

import pytest

from flywire_asca.contracts import RelationType
from flywire_asca.relational_activation import StructuralNeed, build_a013_deterministic_fixture
from flywire_asca.structural_routing import StructuralRoutingRequest
from flywire_asca.structural_routing.benchmark_fixture import (
    EXPECTED_A014_CASE_IDS,
    EXPECTED_A014_EVALUATOR_FINGERPRINTS,
    EXPECTED_A014_FIXTURE_FINGERPRINT,
    EXPECTED_A014_RUNTIME_INPUT_FINGERPRINTS,
    a014_fixture_fingerprint,
    build_a014_frozen_fixture,
    build_a014_invalid_request_control,
    evaluator_metadata_fingerprint,
    runtime_input_fingerprint,
)


QUERY_MATRIX = (
    ("ownership-workplace-one-hop", "Where does Ada work?", "Ada สังกัดบริษัทใด?"),
    ("causal-one-hop", "What caused the observed outage?", "ต้นตอของเหตุขัดข้องที่สังเกตพบคืออะไร?"),
    ("temporal-one-hop", "Which event happened after event Alpha?", "เหตุการณ์ถัดจาก Alpha คือเหตุการณ์ใด?"),
    ("part-of-two-hop", "Which whole system is this sensor part of?", "เซนเซอร์นี้เป็นส่วนหนึ่งของระบบใด?"),
    ("used-for-one-hop", "What is the caliper used for?", "คาลิเปอร์มีหน้าที่อะไร?"),
    ("same-name-disambiguated-ownership", "Identify this Alex's employer.", "Alex คนนี้ทำงานที่ไหน?"),
    ("cycle-control", "Which larger assembly is this component part of?", "ชิ้นส่วนนี้สังกัดชุดประกอบใด?"),
    ("low-confidence-edge-control", "What caused this observed failure?", "ต้นตอของความขัดข้องนี้คืออะไร?"),
    ("relation-allowlist-control", "What purpose does this component serve?", "ชิ้นส่วนนี้ใช้ทำอะไร?"),
    ("missing-target-control", "Who employs this person?", "บุคคลนี้ทำงานที่ไหน?"),
    ("vector-direct-control", "What fact is stated directly?", "ข้อเท็จจริงที่ระบุไว้โดยตรงคืออะไร?"),
    ("vector-direct-context-control", "What context is stated directly?", "บริบทที่ระบุไว้โดยตรงคืออะไร?"),
    ("vector-direct-procedure-control", "What procedure is stated directly?", "ขั้นตอนที่ระบุไว้โดยตรงคืออะไร?"),
    ("vector-direct-causal-control", "What cause is stated directly?", "สาเหตุที่ระบุไว้โดยตรงคืออะไร?"),
    ("vector-direct-episodic-control", "What event is stated directly?", "เหตุการณ์ที่ระบุไว้โดยตรงคืออะไร?"),
    ("vector-direct-spatial-control", "What location is stated directly?", "ตำแหน่งที่ระบุไว้โดยตรงคืออะไร?"),
)


def test_fixture_freezes_exact_bilingual_query_matrix_and_order():
    cases = build_a014_frozen_fixture()
    assert len(cases) == 32
    expected_rows = []
    for base_id, en, th in QUERY_MATRIX:
        expected_rows.extend(
            [
                (f"{base_id}:en", base_id, "en", en),
                (f"{base_id}:th", base_id, "th", th),
            ]
        )
    observed = [
        (case.routing_case_id, case.base_a013_case_id, case.language, case.query_text)
        for case in cases
    ]
    assert observed == expected_rows
    assert tuple(case.routing_case_id for case in cases) == EXPECTED_A014_CASE_IDS


def test_every_valid_a013_semantic_appears_exactly_twice_and_invalid_is_excluded():
    a013 = build_a013_deterministic_fixture()
    valid_ids = tuple(case.case_id for case in a013 if case.case_id != "invalid-contract-control")
    cases = build_a014_frozen_fixture()
    counts = Counter(case.base_a013_case_id for case in cases)
    assert set(counts) == set(valid_ids)
    assert set(counts.values()) == {2}
    assert "invalid-contract-control" not in counts


def test_fixture_preserves_expected_category_balance():
    cases = build_a014_frozen_fixture()
    relation_positive = sum(case.primary_relation_positive for case in cases)
    structural_controls = sum(
        case.expected_structural_need.active and not case.primary_relation_positive
        for case in cases
    )
    direct_controls = sum(not case.expected_structural_need.active for case in cases)
    assert (relation_positive, structural_controls, direct_controls) == (12, 8, 12)


def test_invalid_request_control_is_separate_and_rejected_by_runtime_contract():
    invalid = build_a014_invalid_request_control()
    assert invalid.case_id == "invalid-request-control"
    assert invalid.query_text == ""
    assert invalid.expected_error_contains == "query_text"
    with pytest.raises(ValueError, match="query_text"):
        StructuralRoutingRequest(
            invalid.request_id, invalid.query_text, invalid.language_hint
        )


def test_literal_runtime_evaluator_and_whole_fixture_fingerprints_match():
    cases = build_a014_frozen_fixture()
    runtime = tuple(
        (case.routing_case_id, runtime_input_fingerprint(case)) for case in cases
    )
    evaluator = tuple(
        (case.routing_case_id, evaluator_metadata_fingerprint(case)) for case in cases
    )
    assert runtime == EXPECTED_A014_RUNTIME_INPUT_FINGERPRINTS
    assert evaluator == EXPECTED_A014_EVALUATOR_FINGERPRINTS
    assert a014_fixture_fingerprint(cases) == EXPECTED_A014_FIXTURE_FINGERPRINT


def test_runtime_fingerprint_tracks_runtime_text_but_excludes_evaluator_truth():
    case = build_a014_frozen_fixture()[0]
    original = runtime_input_fingerprint(case)
    changed_text = replace(case, query_text=case.query_text + " extra")
    assert runtime_input_fingerprint(changed_text) != original

    changed_truth = replace(
        case,
        expected_structural_need=StructuralNeed((RelationType.USED_FOR,), True),
        expected_target_ids=("invented-evaluator-target",),
        expected_found=not case.expected_found,
    )
    assert runtime_input_fingerprint(changed_truth) == original


def test_evaluator_fingerprint_tracks_expected_structural_need():
    case = next(
        item for item in build_a014_frozen_fixture()
        if item.base_a013_case_id == "vector-direct-control" and item.language == "en"
    )
    original = evaluator_metadata_fingerprint(case)
    changed = replace(
        case,
        expected_structural_need=StructuralNeed((RelationType.WORKS_AT,), True),
    )
    assert evaluator_metadata_fingerprint(changed) != original


def test_case_expected_truth_matches_frozen_a013_semantics():
    by_id = {case.case_id: case for case in build_a013_deterministic_fixture()}
    for case in build_a014_frozen_fixture():
        base = by_id[case.base_a013_case_id]
        assert case.expected_structural_need == base.structural_need
        assert case.expected_target_ids == base.expected_target_ids
        assert case.expected_found == base.expected_found
        assert case.primary_relation_positive == base.primary_relation_positive
