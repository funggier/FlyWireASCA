from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

import pytest

from flywire_asca.contracts import Cue, CueKind, RetrievalState
from flywire_asca.familiarity import (
    FamiliarityBenchmarkCase,
    FamiliarityBenchmarkCaseResult,
    FamiliarityBenchmarkReport,
    FamiliarityTrace,
    benchmark_report_payload,
    build_a003_qualification_fixture,
    qualify_a003_report,
    run_familiarity_benchmark,
)


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "run_familiarity_benchmark_a003.py"


def _cue(cue_id: str, kind: CueKind, value: str) -> Cue:
    return Cue(cue_id, kind, value, 1.0)


def test_benchmark_case_validates_state_regions_universe_and_ambiguity():
    case = FamiliarityBenchmarkCase(
        "case-1",
        _cue("cue-1", CueKind.ENTITY, "A"),
        RetrievalState.FAMILIAR,
        ("region-a",),
        universe_region_count=10,
    )
    assert case.expected_region_ids == ("region-a",)

    with pytest.raises(ValueError, match="expected_state"):
        FamiliarityBenchmarkCase(
            "bad-state",
            _cue("cue", CueKind.ENTITY, "A"),
            RetrievalState.RECALLED,
            ("region-a",),
        )
    with pytest.raises(ValueError, match="expected_region_ids"):
        FamiliarityBenchmarkCase(
            "bad-order",
            _cue("cue", CueKind.ENTITY, "A"),
            RetrievalState.FAMILIAR,
            ("region-z", "region-a"),
        )
    with pytest.raises(ValueError, match="universe_region_count"):
        FamiliarityBenchmarkCase(
            "bad-universe",
            _cue("cue", CueKind.ENTITY, "A"),
            RetrievalState.FAMILIAR,
            ("region-a", "region-b"),
            universe_region_count=1,
        )
    with pytest.raises(ValueError, match="ambiguity_expected"):
        FamiliarityBenchmarkCase(
            "bad-ambiguity",
            _cue("cue", CueKind.ENTITY, "A"),
            RetrievalState.FAMILIAR,
            ("region-a",),
            ambiguity_expected=True,
        )


def test_run_rejects_duplicate_case_ids():
    traces = (FamiliarityTrace("trace-a", CueKind.ENTITY, "A", "region-a"),)
    case = FamiliarityBenchmarkCase(
        "case-1",
        _cue("cue", CueKind.ENTITY, "A"),
        RetrievalState.FAMILIAR,
        ("region-a",),
    )
    with pytest.raises(ValueError, match="duplicate case_id"):
        run_familiarity_benchmark(traces, (case, case))


def test_a003_fixture_covers_declared_cases_and_256_distractors():
    traces, cases = build_a003_qualification_fixture()
    distractors = tuple(
        trace for trace in traces if trace.trace_id.startswith("trace-distractor-")
    )
    assert len(distractors) == 256
    assert len({trace.region_id for trace in distractors}) == 256

    case_ids = {case.case_id for case in cases}
    assert {
        "known-unique",
        "unknown",
        "normalization-equivalent",
        "cross-kind-negative",
        "same-name-ambiguity",
        "duplicate-traces-one-region",
        "thai-unicode",
        "synthetic-known",
        "synthetic-unknown",
    } <= case_ids


def test_controlled_fixture_qualifies_with_exact_expected_metrics():
    traces, cases = build_a003_qualification_fixture()
    report = run_familiarity_benchmark(traces, cases)

    assert report.scope == "controlled_fixture_only"
    assert report.case_count == len(cases) == 9
    assert report.total_trace_count == len(traces) == 263
    assert report.correct_classification_count == 9
    assert report.classification_accuracy == 1.0
    assert report.false_familiarity_count == 0
    assert report.false_unfamiliar_count == 0
    assert report.ambiguity_failure_count == 0
    assert report.semantic_mismatch_count == 0
    assert report.exact_logical_probes == 9
    assert report.exhaustive_logical_probes == 9 * 263
    assert qualify_a003_report(report) == []

    ambiguity = next(
        result for result in report.case_results
        if result.case_id == "same-name-ambiguity"
    )
    assert ambiguity.actual_region_ids == (
        "person-a-neighbor",
        "person-a-primary",
    )
    assert ambiguity.ambiguity_preserved is True
    assert ambiguity.semantic_equivalent is True

    no_universe = FamiliarityBenchmarkCase(
        "no-universe",
        _cue("cue-no-universe", CueKind.ENTITY, "Alice"),
        RetrievalState.FAMILIAR,
        ("person-alice",),
    )
    one = run_familiarity_benchmark(traces, (no_universe,))
    assert one.case_results[0].candidate_region_count == 1
    assert one.case_results[0].candidate_region_fraction is None


def test_qualifier_rejects_nonqualifying_report_deterministically():
    result = FamiliarityBenchmarkCaseResult(
        case_id="bad",
        expected_state=RetrievalState.FAMILIAR,
        actual_state=RetrievalState.UNFAMILIAR,
        expected_region_ids=("region-a",),
        actual_region_ids=(),
        classification_correct=False,
        regions_correct=False,
        ambiguity_preserved=True,
        candidate_region_count=0,
        candidate_region_fraction=0.0,
        matched_trace_count=0,
        exact_logical_probes=1,
        exhaustive_logical_probes=1,
        semantic_equivalent=True,
    )
    report = FamiliarityBenchmarkReport(
        scope="controlled_fixture_only",
        total_trace_count=1,
        case_results=(result,),
        case_count=1,
        correct_classification_count=0,
        classification_accuracy=0.0,
        false_familiarity_count=0,
        false_unfamiliar_count=1,
        ambiguity_failure_count=0,
        semantic_mismatch_count=0,
        exact_logical_probes=1,
        exhaustive_logical_probes=1,
    )
    errors = qualify_a003_report(report)
    assert errors == [
        "classification_accuracy must be 1.0",
        "false_unfamiliar_count must be 0",
        "region mismatch cases must be 0",
    ]


def test_benchmark_payload_is_deterministic_and_does_not_overclaim_hardware_compute():
    traces, cases = build_a003_qualification_fixture()
    report = run_familiarity_benchmark(traces, cases)
    left = benchmark_report_payload(report)
    right = benchmark_report_payload(report)
    assert left == right
    encoded = json.dumps(left, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    lowered = encoded.lower()
    assert '"scope":"controlled_fixture_only"' in encoded
    assert "flop" not in lowered
    assert "energy" not in lowered
    assert "hardware_compute_reduction" not in lowered


def test_cli_is_byte_deterministic_and_qualifies_builtin_fixture():
    command = [sys.executable, str(SCRIPT), "--qualify"]
    first = subprocess.run(
        command,
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    second = subprocess.run(
        command,
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    assert first.returncode == second.returncode == 0
    assert first.stderr == second.stderr == ""
    assert first.stdout == second.stdout
    payload = json.loads(first.stdout)
    assert payload["scope"] == "controlled_fixture_only"
    assert payload["classification_accuracy"] == 1.0
    assert payload["semantic_mismatch_count"] == 0

def test_qualifier_rejects_wrong_candidate_regions_even_when_engines_agree():
    result = FamiliarityBenchmarkCaseResult(
        case_id="wrong-region",
        expected_state=RetrievalState.FAMILIAR,
        actual_state=RetrievalState.FAMILIAR,
        expected_region_ids=("region-expected",),
        actual_region_ids=("region-wrong",),
        classification_correct=True,
        regions_correct=False,
        ambiguity_preserved=True,
        candidate_region_count=1,
        candidate_region_fraction=1.0,
        matched_trace_count=1,
        exact_logical_probes=1,
        exhaustive_logical_probes=1,
        semantic_equivalent=True,
    )
    report = FamiliarityBenchmarkReport(
        scope="controlled_fixture_only",
        total_trace_count=1,
        case_results=(result,),
        case_count=1,
        correct_classification_count=1,
        classification_accuracy=1.0,
        false_familiarity_count=0,
        false_unfamiliar_count=0,
        ambiguity_failure_count=0,
        semantic_mismatch_count=0,
        exact_logical_probes=1,
        exhaustive_logical_probes=1,
    )
    assert qualify_a003_report(report) == [
        "region mismatch cases must be 0",
    ]
