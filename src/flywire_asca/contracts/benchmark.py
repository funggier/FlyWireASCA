from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .validation import require_nonempty, require_unique_nonempty


class BaselineMode(str, Enum):
    DENSE_DIRECT = "dense_direct"
    ASCA_SELECTIVE = "asca_selective"
    ASCA_NO_SURPRISE_EXPANSION = "asca_no_surprise_expansion"
    ASCA_NO_FAMILIARITY = "asca_no_familiarity"


REQUIRED_BASELINE_MODES = (
    BaselineMode.DENSE_DIRECT,
    BaselineMode.ASCA_SELECTIVE,
    BaselineMode.ASCA_NO_SURPRISE_EXPANSION,
    BaselineMode.ASCA_NO_FAMILIARITY,
)


class EvaluationMetric(str, Enum):
    TASK_CORRECTNESS = "task_correctness"
    RECALL_ACCURACY = "recall_accuracy"
    FALSE_FAMILIARITY_RATE = "false_familiarity_rate"
    IDENTITY_CONFUSION_RATE = "identity_confusion_rate"
    ACTIVATION_MISS_RATE = "activation_miss_rate"
    MISS_RECOVERY_RATE = "miss_recovery_rate"
    ACTIVE_MEMORY_FRACTION = "active_memory_fraction"
    ACTIVE_MODULE_FRACTION = "active_module_fraction"
    WORKING_SET_SIZE = "working_set_size"
    RETRIEVAL_EXPANSIONS = "retrieval_expansions"
    MODEL_INPUT_TOKENS = "model_input_tokens"
    COMPUTE = "compute"
    LATENCY = "latency"
    MEMORY_IO = "memory_io"
    PROCEDURAL_REUSE_RATE = "procedural_reuse_rate"
    SURPRISE_DETECTION = "surprise_detection"
    POST_SURPRISE_RECOVERY_QUALITY = "post_surprise_recovery_quality"


@dataclass(frozen=True, slots=True)
class BenchmarkDefinition:
    benchmark_id: str
    description: str
    baselines: tuple[BaselineMode, ...]
    metrics: tuple[EvaluationMetric, ...]
    tags: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        require_nonempty("benchmark_id", self.benchmark_id)
        require_nonempty("description", self.description)
        if not self.baselines:
            raise ValueError("baselines must not be empty")
        if len(set(self.baselines)) != len(self.baselines):
            raise ValueError("baselines must contain unique modes")
        if not self.metrics:
            raise ValueError("metrics must not be empty")
        if len(set(self.metrics)) != len(self.metrics):
            raise ValueError("metrics must contain unique values")
        require_unique_nonempty("tags", self.tags)
