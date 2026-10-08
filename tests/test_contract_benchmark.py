from __future__ import annotations

import pytest

from flywire_asca.contracts import (
    BaselineMode,
    BenchmarkDefinition,
    EvaluationMetric,
    REQUIRED_BASELINE_MODES,
)


def test_required_baseline_modes_match_asca_design_contract():
    assert REQUIRED_BASELINE_MODES == (
        BaselineMode.DENSE_DIRECT,
        BaselineMode.ASCA_SELECTIVE,
        BaselineMode.ASCA_NO_SURPRISE_EXPANSION,
        BaselineMode.ASCA_NO_FAMILIARITY,
    )


def test_evaluation_metric_vocabulary_covers_primary_design_categories():
    required = {
        EvaluationMetric.TASK_CORRECTNESS,
        EvaluationMetric.RECALL_ACCURACY,
        EvaluationMetric.FALSE_FAMILIARITY_RATE,
        EvaluationMetric.IDENTITY_CONFUSION_RATE,
        EvaluationMetric.ACTIVATION_MISS_RATE,
        EvaluationMetric.MISS_RECOVERY_RATE,
        EvaluationMetric.ACTIVE_MEMORY_FRACTION,
        EvaluationMetric.WORKING_SET_SIZE,
        EvaluationMetric.MODEL_INPUT_TOKENS,
        EvaluationMetric.COMPUTE,
        EvaluationMetric.LATENCY,
        EvaluationMetric.PROCEDURAL_REUSE_RATE,
        EvaluationMetric.SURPRISE_DETECTION,
        EvaluationMetric.POST_SURPRISE_RECOVERY_QUALITY,
    }
    assert required <= set(EvaluationMetric)


def test_benchmark_definition_is_immutable_and_rejects_duplicate_modes():
    definition = BenchmarkDefinition(
        benchmark_id="identity-same-name",
        description="Distinguish same-person from same-name associations.",
        baselines=REQUIRED_BASELINE_MODES,
        metrics=(
            EvaluationMetric.TASK_CORRECTNESS,
            EvaluationMetric.IDENTITY_CONFUSION_RATE,
        ),
        tags=("identity", "memory"),
    )
    assert definition.baselines == REQUIRED_BASELINE_MODES

    with pytest.raises(ValueError, match="baselines"):
        BenchmarkDefinition(
            "bad",
            "duplicate",
            (BaselineMode.DENSE_DIRECT, BaselineMode.DENSE_DIRECT),
            (EvaluationMetric.TASK_CORRECTNESS,),
        )
