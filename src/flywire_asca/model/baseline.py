from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from enum import Enum
import unicodedata

from flywire_asca.contracts.validation import require_nonempty

from .adapter import ModelAdapter
from .contracts import (
    ModelMessage,
    ModelRequest,
    ModelResponse,
    ModelRole,
)


class BaselineScoring(str, Enum):
    EXACT_NORMALIZED = "exact_normalized"
    ALLOWED_NORMALIZED = "allowed_normalized"


def normalize_baseline_answer(text: str) -> str:
    normalized = unicodedata.normalize("NFKC", text)
    collapsed = " ".join(normalized.split()).casefold()
    if not collapsed:
        raise ValueError("baseline answer must not be empty after normalization")
    return collapsed


def _require_optional_nonnegative_int(name: str, value: int | None) -> None:
    if value is None:
        return
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise ValueError(f"{name} must be a nonnegative integer or None")


@dataclass(frozen=True, slots=True)
class ModelBaselineCase:
    case_id: str
    messages: tuple[ModelMessage, ...]
    scoring: BaselineScoring
    expected_answers: tuple[str, ...]

    def __post_init__(self) -> None:
        require_nonempty("case_id", self.case_id)
        if not self.messages:
            raise ValueError("messages must not be empty")
        if not self.expected_answers:
            raise ValueError("expected_answers must not be empty")
        canonical = tuple(
            sorted({normalize_baseline_answer(value) for value in self.expected_answers})
        )
        if not canonical:
            raise ValueError("expected_answers must not be empty")
        object.__setattr__(self, "expected_answers", canonical)
        if (
            self.scoring is BaselineScoring.EXACT_NORMALIZED
            and len(canonical) != 1
        ):
            raise ValueError(
                "exact_normalized scoring requires exactly one expected answer"
            )


@dataclass(frozen=True, slots=True)
class ModelBaselineCaseResult:
    case_id: str
    passed: bool
    normalized_output: str
    prompt_tokens: int | None
    generated_tokens: int | None
    total_duration_ns: int | None
    load_duration_ns: int | None
    prompt_eval_duration_ns: int | None
    eval_duration_ns: int | None

    def __post_init__(self) -> None:
        require_nonempty("case_id", self.case_id)
        require_nonempty("normalized_output", self.normalized_output)
        if not isinstance(self.passed, bool):
            raise ValueError("passed must be bool")
        for name in (
            "prompt_tokens",
            "generated_tokens",
            "total_duration_ns",
            "load_duration_ns",
            "prompt_eval_duration_ns",
            "eval_duration_ns",
        ):
            _require_optional_nonnegative_int(name, getattr(self, name))


@dataclass(frozen=True, slots=True)
class ModelBaselineReport:
    profile_name: str
    model_name: str
    model_digest: str | None
    case_results: tuple[ModelBaselineCaseResult, ...]
    case_count: int
    passed_case_count: int
    pass_rate: float
    prompt_tokens_total: int | None
    generated_tokens_total: int | None
    total_duration_ns: int | None
    load_duration_ns: int | None
    prompt_eval_duration_ns: int | None
    eval_duration_ns: int | None

    def __post_init__(self) -> None:
        require_nonempty("profile_name", self.profile_name)
        require_nonempty("model_name", self.model_name)
        if self.model_digest is not None:
            require_nonempty("model_digest", self.model_digest)
        if (
            not isinstance(self.case_count, int)
            or isinstance(self.case_count, bool)
            or self.case_count < 0
        ):
            raise ValueError("case_count must be a nonnegative integer")
        if self.case_count != len(self.case_results):
            raise ValueError("case_count must equal len(case_results)")
        actual_passed = sum(1 for result in self.case_results if result.passed)
        if self.passed_case_count != actual_passed:
            raise ValueError(
                "passed_case_count must equal passed case result count"
            )
        expected_rate = (
            actual_passed / self.case_count
            if self.case_count
            else 0.0
        )
        if self.pass_rate != expected_rate:
            raise ValueError("pass_rate must equal passed_case_count / case_count")
        for name in (
            "prompt_tokens_total",
            "generated_tokens_total",
            "total_duration_ns",
            "load_duration_ns",
            "prompt_eval_duration_ns",
            "eval_duration_ns",
        ):
            _require_optional_nonnegative_int(name, getattr(self, name))


def _system_exact() -> ModelMessage:
    return ModelMessage(
        ModelRole.SYSTEM,
        "Follow the user's instruction exactly. Return only the requested answer with no explanation.",
    )


def build_qwen_a004_baseline_cases() -> tuple[ModelBaselineCase, ...]:
    system = _system_exact()
    return (
        ModelBaselineCase(
            "english-exact",
            (
                system,
                ModelMessage(
                    ModelRole.USER,
                    "Output only the word BLUE.",
                ),
            ),
            BaselineScoring.EXACT_NORMALIZED,
            ("blue",),
        ),
        ModelBaselineCase(
            "thai-exact",
            (
                system,
                ModelMessage(
                    ModelRole.USER,
                    "ตอบเพียงคำว่า แมว เท่านั้น",
                ),
            ),
            BaselineScoring.EXACT_NORMALIZED,
            ("แมว",),
        ),
        ModelBaselineCase(
            "context-selection",
            (
                system,
                ModelMessage(
                    ModelRole.USER,
                    "Given only this supplied context: alpha=17, beta=29. Output only the value of beta.",
                ),
            ),
            BaselineScoring.EXACT_NORMALIZED,
            ("29",),
        ),
        ModelBaselineCase(
            "context-middle",
            (
                system,
                ModelMessage(
                    ModelRole.USER,
                    "Given this supplied sequence: red | green | blue. Output only the middle item.",
                ),
            ),
            BaselineScoring.EXACT_NORMALIZED,
            ("green",),
        ),
        ModelBaselineCase(
            "insufficient-context",
            (
                system,
                ModelMessage(
                    ModelRole.USER,
                    "Supplied context: city=Bangkok. The requested project code is not present. Output only INSUFFICIENT_CONTEXT.",
                ),
            ),
            BaselineScoring.EXACT_NORMALIZED,
            ("insufficient_context",),
        ),
        ModelBaselineCase(
            "boolean-allowed",
            (
                system,
                ModelMessage(
                    ModelRole.USER,
                    "Using only this supplied statement: 2 is less than 3. Output only yes or true.",
                ),
            ),
            BaselineScoring.ALLOWED_NORMALIZED,
            ("true", "yes"),
        ),
    )


def _sum_complete(values: list[int | None]) -> int | None:
    if any(value is None for value in values):
        return None
    return sum(value for value in values if value is not None)


def run_model_baseline(
    adapter: ModelAdapter,
    cases: Iterable[ModelBaselineCase],
    *,
    profile_name: str,
) -> ModelBaselineReport:
    require_nonempty("profile_name", profile_name)
    case_tuple = tuple(cases)
    case_ids = tuple(case.case_id for case in case_tuple)
    if len(set(case_ids)) != len(case_ids):
        raise ValueError("duplicate case_id values are not allowed")

    descriptor = adapter.inspect()
    results: list[ModelBaselineCaseResult] = []
    responses: list[ModelResponse] = []
    for case in case_tuple:
        request = ModelRequest(
            request_id=f"a004-{case.case_id}",
            messages=case.messages,
            max_output_tokens=256,
            context_limit=8192,
            temperature=0.0,
            seed=0,
            thinking=False,
        )
        response = adapter.generate(request)
        normalized_output = normalize_baseline_answer(response.content)
        passed = normalized_output in case.expected_answers
        responses.append(response)
        results.append(
            ModelBaselineCaseResult(
                case_id=case.case_id,
                passed=passed,
                normalized_output=normalized_output,
                prompt_tokens=response.prompt_tokens,
                generated_tokens=response.generated_tokens,
                total_duration_ns=response.total_duration_ns,
                load_duration_ns=response.load_duration_ns,
                prompt_eval_duration_ns=response.prompt_eval_duration_ns,
                eval_duration_ns=response.eval_duration_ns,
            )
        )

    passed_count = sum(1 for result in results if result.passed)
    case_count = len(results)
    return ModelBaselineReport(
        profile_name=profile_name,
        model_name=descriptor.model_name,
        model_digest=descriptor.model_digest,
        case_results=tuple(results),
        case_count=case_count,
        passed_case_count=passed_count,
        pass_rate=(passed_count / case_count if case_count else 0.0),
        prompt_tokens_total=_sum_complete(
            [response.prompt_tokens for response in responses]
        ),
        generated_tokens_total=_sum_complete(
            [response.generated_tokens for response in responses]
        ),
        total_duration_ns=_sum_complete(
            [response.total_duration_ns for response in responses]
        ),
        load_duration_ns=_sum_complete(
            [response.load_duration_ns for response in responses]
        ),
        prompt_eval_duration_ns=_sum_complete(
            [response.prompt_eval_duration_ns for response in responses]
        ),
        eval_duration_ns=_sum_complete(
            [response.eval_duration_ns for response in responses]
        ),
    )


def qualify_qwen_a004_report(report: ModelBaselineReport) -> list[str]:
    errors: list[str] = []
    if report.profile_name != "qwen3.5-4b-thinking-off-v1":
        errors.append(
            'profile_name must be "qwen3.5-4b-thinking-off-v1"'
        )
    if report.case_count != 6:
        errors.append("case_count must be 6")
    if report.pass_rate != 1.0:
        errors.append("pass_rate must be 1.0")
    if report.passed_case_count != report.case_count:
        errors.append("passed_case_count must equal case_count")
    if not report.model_name.strip():
        errors.append("model_name must be nonblank")
    if report.model_digest is None or not report.model_digest.strip():
        errors.append("model_digest must be nonblank")
    return errors
