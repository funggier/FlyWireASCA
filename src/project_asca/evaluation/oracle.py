"""Offline task truth and raw aggregation; no channel back into the runtime."""
from dataclasses import dataclass
from collections.abc import Mapping
from collections import defaultdict
from decimal import Decimal
import math
from .decision import VariantTotals,ComparisonTotals
from project_asca.agent_runtime.values import RunVariant,TerminalStatus,TaskKind
@dataclass(frozen=True,slots=True)
class OracleVerdict:
    case_id:str
    pair_id:str
    language:str
    family:str
    expected_status:str
    status_correct:bool
    answer_correct:bool|None
    state_correct:bool|None
    task_completed:bool
    false_success:bool
    control_correct:bool
    bounded_failure_correct:bool
    genuine_recovery:bool
@dataclass(frozen=True,slots=True)
class RawTrial:
    case_id:str
    variant:RunVariant
    repetition:int
    request_fingerprint:str
    result:object
    oracle_verdict:OracleVerdict
    model_records:tuple
    wall_seconds:float
    def __post_init__(self):
        object.__setattr__(self,"variant",RunVariant(self.variant))
        if (isinstance(self.repetition,bool) or self.repetition not in (1,2,3)
            or not math.isfinite(self.wall_seconds) or self.wall_seconds<0):raise ValueError("raw trial bounds")
def semantic_equal(a,b):
    if isinstance(a,bool) or isinstance(b,bool):return type(a) is type(b) and a==b
    if isinstance(a,(int,float)) and isinstance(b,(int,float)):
        return math.isfinite(a) and math.isfinite(b) and Decimal(str(a))==Decimal(str(b))
    if isinstance(a,Mapping) and isinstance(b,Mapping):
        return set(a)==set(b) and all(semantic_equal(a[k],b[k]) for k in a)
    if isinstance(a,(tuple,list)) and isinstance(b,(tuple,list)):
        return len(a)==len(b) and all(semantic_equal(x,y) for x,y in zip(a,b))
    return type(a) is type(b) and a==b
def normalize_answer(data):
    if isinstance(data,Mapping):
        if set(data) in ({"value"},{"list"},{"map"},{"names"}):return next(iter(data.values()))
        if set(data)=={"list","sum"}:return {"values":data["list"],"sum":data["sum"]}
    return data
def _relation_answer(expected,result):
    goal=result.interpreted_goal;data=result.data
    if goal is None or goal.kind is not TaskKind.RELATION or not isinstance(data,Mapping) or set(data)!={"paths"}:return False
    if set(goal.parameters.get("relations",()))!=set(expected.required_relations):return False
    paths=data["paths"]
    if not isinstance(paths,(tuple,list)):return False
    targets=[]
    for path in paths:
        if not isinstance(path,Mapping) or set(path)!={"node_ids","edge_ids","evidence_ids"}:return False
        nodes,edges=path["node_ids"],path["edge_ids"]
        if (not edges or len(nodes)!=len(edges)+1 or nodes[0]!=goal.parameters["entity"]
            or len(path["evidence_ids"])!=len(edges)):return False
        if len(edges)>=expected.min_path_hops:targets.append(nodes[-1])
    required=expected.required_values
    wanted=tuple(required.values()) if isinstance(required,Mapping) else (required,)
    return bool(targets) and all(any(semantic_equal(v,t) for t in targets) for v in wanted)
def _genuine(result):
    goal=result.interpreted_goal
    if goal is None or result.verification is None:return False
    trace=result.trace;attempts=[e for e in trace if e.kind=="attempt"]
    final=[e for e in attempts if e.payload["execution_id"]==result.verification.execution_id]
    if len(final)!=1 or not final[0].payload["completed"]:return False
    last=final[0]
    for failed in trace:
        if failed.kind!="action" or failed.payload.get("executed") or not failed.payload.get("error"):continue
        prior=[e for e in attempts if e.payload["execution_id"]==failed.payload["execution_id"]]
        if len(prior)!=1:continue
        old=prior[0]
        if (old.payload["execution_id"]==last.payload["execution_id"] or old.payload["goal"]!=goal.goal_id
            or last.payload["goal"]!=goal.goal_id or old.payload["initial_state"]!=last.payload["initial_state"]):continue
        for remedy in trace:
            if (remedy.kind!="recovery" or not failed.sequence<remedy.sequence<last.sequence
                or failed.payload["observation_ref"] not in remedy.payload["remedy"]["observation_refs"]):continue
            if (remedy.payload["context"]!=old.payload["context_fingerprint"]
                or remedy.payload["plan"]!=old.payload["plan_fingerprint"]):continue
            if (old.payload["context_fingerprint"]!=last.payload["context_fingerprint"]
                or old.payload["plan_fingerprint"]!=last.payload["plan_fingerprint"]):return True
    return False
def evaluate_trial(case,expected,result):
    succeeded=result.status is TerminalStatus.SUCCEEDED
    answer=None;state=None
    if expected.required_values is not None:
        answer=(_relation_answer(expected,result) if expected.required_relations else
                semantic_equal(normalize_answer(result.data),expected.required_values))
    if expected.required_state:
        data=result.data
        state=isinstance(data,Mapping) and set(data)=={"entity","state"} and data["entity"] in expected.required_state
        state=bool(state and set(expected.required_state)=={data["entity"]} and isinstance(data["state"],Mapping)
            and all(k in data["state"] and semantic_equal(data["state"][k],v)
                    for k,v in expected.required_state[data["entity"]].items()))
    status=result.status.value==expected.status
    correct=status and result.reason.value==expected.reason_category
    completed=bool(expected.status=="SUCCEEDED" and succeeded and correct and answer is not False and state is not False
                   and (answer is not None or state is not None))
    false_success=bool(succeeded and not completed)
    return OracleVerdict(case.case_id,case.pair_id,case.language,case.family,expected.status,status,answer,state,
        completed,false_success,correct if expected.status!="SUCCEEDED" else False,
        correct if expected.status=="BOUNDED_FAILURE" else False,
        bool(completed and expected.recovery_required and _genuine(result)))
def aggregate_trials(trials):
    variants={};paired=defaultdict(dict)
    for variant in RunVariant:
        selected=[t for t in trials if t.variant is variant]
        counters=defaultdict(int);spans=defaultdict(float);reps=defaultdict(lambda:defaultdict(int))
        groups=defaultdict(int);recoveries=defaultdict(int);prompt=0;output=0
        completed=pub=fs=controls=bf=ansapp=anscorrect=stateapp=statecorrect=genuine=violations=calls=0
        solvable=bounded=control_count=0
        for t in selected:
            v=t.oracle_verdict;m=t.result.metrics
            n=v.expected_status=="SUCCEEDED";b=v.expected_status=="BOUNDED_FAILURE"
            solvable+=n;bounded+=b;control_count+=not n
            completed+=v.task_completed;pub+=t.result.status is TerminalStatus.SUCCEEDED;fs+=v.false_success
            controls+=v.control_correct;bf+=v.bounded_failure_correct
            ansapp+=v.answer_correct is not None;anscorrect+=v.answer_correct is True
            stateapp+=v.state_correct is not None;statecorrect+=v.state_correct is True
            genuine+=v.genuine_recovery;violations+=m.integrity_failures;calls+=m.model_invocations
            if prompt is not None:prompt=None if m.reported_prompt_tokens is None else prompt+m.reported_prompt_tokens
            if output is not None:output=None if m.reported_output_tokens is None else output+m.reported_output_tokens
            for k,value in m.counters.items():counters[k]+=value
            for k,value in m.stage_seconds.items():spans[k]+=value
            group=v.language+":"+v.family;groups[group]+=v.task_completed
            recoveries[str(t.repetition)+":"+v.language]+=v.genuine_recovery
            row=reps[str(t.repetition)];row["cost_requests"]+=1;row["solvable_requests"]+=n
            row["bounded_failure_requests"]+=b;row["control_requests"]+=not n;row["completed"]+=v.task_completed
            if n:paired[(t.repetition,t.case_id)][variant.value]=v.task_completed
        variants[variant.value]=VariantTotals(len(selected),solvable,bounded,control_count,completed,pub,fs,controls,bf,
            ansapp,anscorrect,stateapp,statecorrect,calls,prompt,output,genuine,violations,dict(recoveries),dict(groups),
            {k:dict(v) for k,v in reps.items()},dict(counters),dict(spans),tuple(t.wall_seconds for t in selected))
    base_only=unified_only=0;rows=[]
    for (repetition,case_id),values in sorted(paired.items()):
        u=values.get("UNIFIED_RUNTIME");d=values.get("DIRECT_PINNED_MODEL")
        base_only+=d is True and u is False;unified_only+=u is True and d is False
        rows.append({"repetition":repetition,"case_id":case_id,"unified":u,"direct":d})
    return ComparisonTotals(variants,base_only,unified_only,tuple(rows))
