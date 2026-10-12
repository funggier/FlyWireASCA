"""Canonical balanced request schedule, independent of outcomes."""
from dataclasses import dataclass
from project_asca.agent_runtime.values import RunVariant
@dataclass(frozen=True,slots=True)
class TrialSlot:
    index:int
    repetition:int
    case:object
    variant:RunVariant
def trial_schedule(workload,*,repetitions=3,seed=0):
    if type(repetitions) is not int or repetitions!=3 or type(seed) is not int or seed!=0:
        raise ValueError("primary protocol requires repetitions3/seed0")
    pairs=list(dict.fromkeys(c.pair_id for c in workload.cases))
    if len(workload.cases)!=64 or len(pairs)!=32:raise ValueError("frozen bilingual universe")
    slots=[]
    for repetition in (1,2,3):
        for i,pair in enumerate(pairs):
            matched=[c for c in workload.cases if c.pair_id==pair]
            if len(matched)!=2 or [c.language for c in matched]!=["en","th"]:raise ValueError("canonical EN/TH order")
            order=(RunVariant.UNIFIED_RUNTIME,RunVariant.DIRECT_PINNED_MODEL)
            if (i+repetition-1)%2:order=tuple(reversed(order))
            for case in matched:
                for variant in order:slots.append(TrialSlot(len(slots),repetition,case,variant))
    return tuple(slots)
