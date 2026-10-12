"""Ordered predeclared research rules; portable evidence cannot decide preference."""
from dataclasses import dataclass,field
from enum import Enum
from collections.abc import Mapping
class ArchitectureOutcome(str,Enum):
    INVALID_INCOMPLETE="INVALID/INCOMPLETE"
    UNIFIED_RUNTIME_NOT_SUPPORTED="UNIFIED_RUNTIME_NOT_SUPPORTED"
    DIRECT_MODEL_PREFERRED="DIRECT_MODEL_PREFERRED"
    UNIFIED_RUNTIME_JUSTIFIED="UNIFIED_RUNTIME_JUSTIFIED"
    MIXED="MIXED"
@dataclass(frozen=True,slots=True)
class EvidenceValidation:
    valid:bool
    physical:bool
    usage_complete:bool
    source_valid:bool=True
    identity_valid:bool=True
    errors:tuple=()
@dataclass(frozen=True,slots=True)
class VariantTotals:
    cost_requests:int=0
    solvable_requests:int=0
    bounded_failure_requests:int=0
    control_requests:int=0
    completed:int=0
    published_successes:int=0
    false_success:int=0
    controls_correct:int=0
    bounded_failures_correct:int=0
    answer_applicable:int=0
    answers_correct:int=0
    state_applicable:int=0
    states_correct:int=0
    model_calls:int=0
    prompt_tokens:int|None=0
    output_tokens:int|None=0
    genuine_recoveries:int=0
    invariant_failures:int=0
    recovery_by_rep_language:Mapping=field(default_factory=dict)
    completion_by_language_family:Mapping=field(default_factory=dict)
    by_repetition:Mapping=field(default_factory=dict)
    counters:Mapping=field(default_factory=dict)
    stage_seconds:Mapping=field(default_factory=dict)
    latency_seconds:tuple=()
@dataclass(frozen=True,slots=True)
class ComparisonTotals:
    variants:Mapping
    baseline_only_successes:int
    unified_only_successes:int
    paired_results:tuple=()
def classify_comparison(totals,validation):
    O=ArchitectureOutcome
    if (not validation.valid or not validation.physical or not validation.usage_complete
        or not validation.source_valid or not validation.identity_valid):
        return O.INVALID_INCOMPLETE
    try:u=totals.variants["UNIFIED_RUNTIME"];d=totals.variants["DIRECT_PINNED_MODEL"]
    except KeyError:return O.INVALID_INCOMPLETE
    for v in (u,d):
        if (v.cost_requests,v.solvable_requests,v.bounded_failure_requests,v.control_requests)!=(192,144,24,48):
            return O.INVALID_INCOMPLETE
        if v.prompt_tokens is None or v.output_tokens is None:return O.INVALID_INCOMPLETE
        if (set(v.by_repetition)!={"1","2","3"} or any(
            (x["cost_requests"],x["solvable_requests"],x["bounded_failure_requests"],x["control_requests"])!=(64,48,8,16)
            for x in v.by_repetition.values())):return O.INVALID_INCOMPLETE
    if (u.false_success or u.controls_correct!=48 or u.bounded_failures_correct!=24
        or u.invariant_failures or u.completed==0 or u.genuine_recoveries==0):
        return O.UNIFIED_RUNTIME_NOT_SUPPORTED
    ut=u.prompt_tokens+u.output_tokens;dt=d.prompt_tokens+d.output_tokens
    if (totals.baseline_only_successes>0 and totals.unified_only_successes==0
        and d.controls_correct==48 and not d.false_success and not d.invariant_failures
        and d.model_calls<=u.model_calls and dt<=ut):
        return O.DIRECT_MODEL_PREFERRED
    recovery=all(u.recovery_by_rep_language.get((r,l),u.recovery_by_rep_language.get(str(r)+":"+l,0))>0
                 for r in (1,2,3) for l in ("en","th"))
    nonregression=all(u.completion_by_language_family.get(group,0)>=n
                     for group,n in d.completion_by_language_family.items())
    if (totals.baseline_only_successes==0 and u.completed>=d.completed and nonregression and recovery
        and u.model_calls<d.model_calls and ut<=dt):return O.UNIFIED_RUNTIME_JUSTIFIED
    return O.MIXED
