from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from flywire_asca.model import (
    BaselineScoring,
    ModelBaselineCase,
    ModelBaselineReport,
    ModelDescriptor,
    ModelMessage,
    ModelRequest,
    ModelResponse,
    ModelRole,
    build_qwen_a004_baseline_cases,
    normalize_baseline_answer,
    qualify_qwen_a004_report,
    run_model_baseline,
)


TARGET_DIGEST = "2a654d98e6fba55d452b7043684e9b57a947e393bbffa62485a7aac05ee4eefd"


class FakeAdapter:
    def __init__(self, outputs, *, incomplete_metrics: bool = False):
        self.outputs = outputs
        self.incomplete_metrics = incomplete_metrics
        self.requests: list[ModelRequest] = []
        self.descriptor = ModelDescriptor(
            backend_name="fake",
            backend_version="1",
            model_name="qwen3.5:4b",
            model_digest=TARGET_DIGEST,
            architecture="qwen35",
            parameter_count=4659865088,
            parameter_size="4.7B",
            quantization="Q4_K_M",
            context_length=262144,
            embedding_length=2560,
            capabilities=("completion", "thinking", "tools", "vision"),
        )

    def inspect(self):
        return self.descriptor

    def generate(self, request):
        self.requests.append(request)
        content = self.outputs[request.request_id]
        missing = self.incomplete_metrics and request.request_id.endswith("thai-exact")
        return ModelResponse(
            request_id=request.request_id,
            model_name=self.descriptor.model_name,
            model_digest=self.descriptor.model_digest,
            content=content,
            finish_reason="stop",
            prompt_tokens=None if missing else 10,
            generated_tokens=None if missing else 2,
            total_duration_ns=None if missing else 100,
            load_duration_ns=None if missing else 10,
            prompt_eval_duration_ns=None if missing else 20,
            eval_duration_ns=None if missing else 70,
        )


def test_normalize_baseline_answer_uses_unicode_nfkc_whitespace_and_casefold():
    assert normalize_baseline_answer("  ＢＬＵＥ  ") == "blue"
    assert normalize_baseline_answer("แมว\u00a0  ") == "แมว"


def test_baseline_case_is_frozen_and_canonicalizes_expected_answers():
    case = ModelBaselineCase(
        "case-1",
        (ModelMessage(ModelRole.USER, "Reply yes"),),
        BaselineScoring.ALLOWED_NORMALIZED,
        (" TRUE ", "Yes", "yes"),
    )
    assert case.expected_answers == ("true", "yes")
    with pytest.raises(FrozenInstanceError):
        case.case_id = "changed"  # type: ignore[misc]

    with pytest.raises(ValueError, match="case_id"):
        ModelBaselineCase(
            "",
            (ModelMessage(ModelRole.USER, "x"),),
            BaselineScoring.EXACT_NORMALIZED,
            ("x",),
        )
    with pytest.raises(ValueError, match="messages"):
        ModelBaselineCase(
            "bad",
            (),
            BaselineScoring.EXACT_NORMALIZED,
            ("x",),
        )
    with pytest.raises(ValueError, match="expected_answers"):
        ModelBaselineCase(
            "bad",
            (ModelMessage(ModelRole.USER, "x"),),
            BaselineScoring.EXACT_NORMALIZED,
            (),
        )
    with pytest.raises(ValueError, match="exact_normalized"):
        ModelBaselineCase(
            "bad",
            (ModelMessage(ModelRole.USER, "x"),),
            BaselineScoring.EXACT_NORMALIZED,
            ("x", "y"),
        )


def test_fixture_contains_exact_six_stable_prompt_only_cases():
    cases = build_qwen_a004_baseline_cases()
    assert tuple(case.case_id for case in cases) == (
        "english-exact",
        "thai-exact",
        "context-selection",
        "context-middle",
        "insufficient-context",
        "boolean-allowed",
    )
    assert len(cases) == 6
    assert all(case.messages for case in cases)
    all_text = " ".join(
        message.content for case in cases for message in case.messages
    ).lower()
    assert "blue" in all_text
    assert "แมว" in all_text
    assert "alpha=17" in all_text and "beta=29" in all_text
    assert "red | green | blue" in all_text
    assert "insufficient_context" in all_text


def test_fake_adapter_runs_all_cases_with_default_thinking_off_profile():
    cases = build_qwen_a004_baseline_cases()
    outputs = {
        "a004-english-exact": " BLUE\n",
        "a004-thai-exact": "แมว",
        "a004-context-selection": "29",
        "a004-context-middle": "green",
        "a004-insufficient-context": "INSUFFICIENT_CONTEXT",
        "a004-boolean-allowed": "TRUE",
    }
    adapter = FakeAdapter(outputs)
    report = run_model_baseline(
        adapter,
        cases,
        profile_name="qwen3.5-4b-thinking-off-v1",
    )
    assert report.case_count == 6
    assert report.passed_case_count == 6
    assert report.pass_rate == 1.0
    assert report.model_name == "qwen3.5:4b"
    assert report.model_digest == TARGET_DIGEST
    assert report.prompt_tokens_total == 60
    assert report.generated_tokens_total == 12
    assert report.total_duration_ns == 600
    assert report.load_duration_ns == 60
    assert report.prompt_eval_duration_ns == 120
    assert report.eval_duration_ns == 420
    assert all(result.passed for result in report.case_results)
    assert all(request.thinking is False for request in adapter.requests)
    assert all(request.context_limit == 8192 for request in adapter.requests)
    assert all(request.max_output_tokens == 256 for request in adapter.requests)
    assert all(request.temperature == 0.0 for request in adapter.requests)
    assert all(request.seed == 0 for request in adapter.requests)
    assert qualify_qwen_a004_report(report) == []


def test_one_wrong_output_fails_deterministically_and_scorer_uses_only_content():
    cases = build_qwen_a004_baseline_cases()
    outputs = {
        "a004-english-exact": "RED",
        "a004-thai-exact": "แมว",
        "a004-context-selection": "29",
        "a004-context-middle": "green",
        "a004-insufficient-context": "INSUFFICIENT_CONTEXT",
        "a004-boolean-allowed": "yes",
    }
    report = run_model_baseline(
        FakeAdapter(outputs),
        cases,
        profile_name="qwen3.5-4b-thinking-off-v1",
    )
    assert report.passed_case_count == 5
    assert report.pass_rate == 5 / 6
    failed = [result for result in report.case_results if not result.passed]
    assert [(result.case_id, result.normalized_output) for result in failed] == [
        ("english-exact", "red")
    ]
    assert qualify_qwen_a004_report(report) == [
        "pass_rate must be 1.0",
        "passed_case_count must equal case_count",
    ]


def test_aggregate_metrics_become_none_if_any_case_metric_is_missing():
    cases = build_qwen_a004_baseline_cases()
    outputs = {
        "a004-english-exact": "blue",
        "a004-thai-exact": "แมว",
        "a004-context-selection": "29",
        "a004-context-middle": "green",
        "a004-insufficient-context": "insufficient_context",
        "a004-boolean-allowed": "yes",
    }
    report = run_model_baseline(
        FakeAdapter(outputs, incomplete_metrics=True),
        cases,
        profile_name="qwen3.5-4b-thinking-off-v1",
    )
    assert report.prompt_tokens_total is None
    assert report.generated_tokens_total is None
    assert report.total_duration_ns is None
    assert report.load_duration_ns is None
    assert report.prompt_eval_duration_ns is None
    assert report.eval_duration_ns is None


def test_report_validates_count_and_rate_consistency():
    with pytest.raises(ValueError, match="case_count"):
        ModelBaselineReport(
            profile_name="p",
            model_name="m",
            model_digest="d",
            case_results=(),
            case_count=1,
            passed_case_count=0,
            pass_rate=0.0,
            prompt_tokens_total=None,
            generated_tokens_total=None,
            total_duration_ns=None,
            load_duration_ns=None,
            prompt_eval_duration_ns=None,
            eval_duration_ns=None,
        )