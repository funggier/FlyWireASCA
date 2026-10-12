from dataclasses import dataclass, fields
import math
from .values import nonblank

GENERATION_DIGEST="2a654d98e6fba55d452b7043684e9b57a947e393bbffa62485a7aac05ee4eefd"
EMBEDDING_DIGEST="ac6da0dfba84a81fdbfbaf330198c33cd77c4cdfc53e8bc50eb581914a15621d"

@dataclass(frozen=True,slots=True)
class RuntimeProfile:
    profile_id:str="a015-stage-a-v1"
    request_bytes:int=8192
    model_calls:int=4
    model_context:int=8192
    prompt_tokens:int=32768
    output_per_call:int=1024
    output_tokens:int=2048
    context_rounds:int=3
    queries_per_round:int=2
    retrieval_queries:int=6
    indexed_records:int=256
    vectors_scored:int=1536
    context_items:int=24
    context_bytes:int=16384
    relation_invocations:int=3
    relation_hops:int=3
    relation_visits_per_call:int=8
    relation_edges_per_call:int=32
    relation_visits:int=24
    relation_edges:int=96
    strategy_attempts:int=3
    recovery_rounds:int=2
    actions_per_attempt:int=32
    actions:int=96
    call_depth:int=8
    transitions:int=64
    trace_events:int=256
    trace_bytes:int=262144
    state_bytes:int=65536
    deadline_seconds:float=180.0
    model_call_seconds:float=120.0
    def __post_init__(self):
        nonblank(self.profile_id,"profile")
        for f in fields(self):
            if f.name=="profile_id":continue
            value=getattr(self,f.name)
            if f.name.endswith("_seconds"):
                if isinstance(value,bool) or not isinstance(value,(float,int)) or not math.isfinite(value) or not 0<value<=f.default:raise ValueError("invalid deadline")
            elif not isinstance(value,int) or isinstance(value,bool) or not 0<=value<=f.default:
                raise ValueError("invalid resource limit "+f.name)
        if self.trace_events<2 or self.trace_bytes<2048:raise ValueError("terminal trace reserve required")
