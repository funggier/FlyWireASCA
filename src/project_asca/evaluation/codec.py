"""Closed canonical evidence DTO decoding; arbitrary dictionaries never become grants."""
from dataclasses import fields
from collections.abc import Mapping
from project_asca.agent_runtime import contracts as c,semantics as s,plans as p
from project_asca.agent_runtime.values import Phase,thaw_json
from project_asca.agent_runtime.trace import TraceEvent
from project_asca.agent_runtime.verification import CompletionCandidate
from .direct import PublicBindingContext
from .oracle import RawTrial,OracleVerdict
from .decision import ComparisonTotals,VariantTotals
def dto(cls,raw,**converters):
    if not isinstance(raw,Mapping) or set(raw)!={f.name for f in fields(cls)}:
        raise ValueError("closed "+cls.__name__+" schema")
    values=dict(raw)
    for key,fn in converters.items():values[key]=fn(values[key])
    try:return cls(**values)
    except (TypeError,KeyError,AttributeError) as exc:raise ValueError(cls.__name__+" type") from exc
def many(fn):return lambda values:tuple(fn(v) for v in values)
def optional(fn):return lambda value:None if value is None else fn(value)
def span(raw):return dto(s.SpanBinding,raw)
def goal(raw):
    raw=dict(raw);parameters=dict(raw["parameters"])
    parameters["spans"]=tuple(span(v) for v in parameters.get("spans",()))
    raw["parameters"]=parameters
    return dto(s.GoalContract,raw,predicates=many(lambda v:dto(s.GoalPredicate,v)))
def evidence_record(raw):return dto(s.EvidenceRecord,raw)
def deficit(raw):return dto(s.Deficit,raw)
def coverage(raw):return dto(s.EvidenceCoverage,raw)
def context(raw):return dto(s.WorkingContext,raw,items=many(evidence_record),coverage=coverage,deficits=many(deficit))
def public_context(raw):return dto(PublicBindingContext,raw,items=many(evidence_record),coverage=coverage)
def proposal(raw):
    def step(v):return dto(p.PlanStep,v,inputs=lambda inputs:{k:dto(p.ValueBinding,b) for k,b in inputs.items()})
    return dto(p.ActionProposal,raw,steps=many(step))
def state(raw):return dto(s.StateSnapshot,raw)
def receipt(raw):return dto(p.ExecutionReceipt,raw)
def attempt(raw):return dto(p.AttemptResult,raw,observations=many(lambda v:dto(p.Observation,v)),final_state=state,deficits=many(deficit))
def metrics(raw):return dto(c.MetricSnapshot,raw)
def snapshot(raw):return dto(c.RunSnapshot,raw,phase=Phase,metrics=metrics,execution_receipt=optional(receipt))
def verification(raw):return dto(s.VerificationRecord,raw,predicates=many(lambda v:dto(s.PredicateVerdict,v)))
def candidate(raw):return dto(CompletionCandidate,raw,attempt=optional(attempt),evidence=many(evidence_record))
def identity(raw):return dto(c.PhysicalIdentity,raw)
ARTIFACT_TYPES={frozenset(f.name for f in fields(cls)):fn for cls,fn in (
    (s.GoalContract,goal),(s.WorkingContext,context),(PublicBindingContext,public_context),
    (p.ActionProposal,proposal),(s.StateSnapshot,state),(p.AttemptResult,attempt),
    (p.ExecutionReceipt,receipt),(c.RunSnapshot,snapshot),(s.VerificationRecord,verification),
    (s.RetrievalQuery,lambda raw:dto(s.RetrievalQuery,raw)),(s.RelationBatch,lambda raw:dto(s.RelationBatch,raw,paths=many(evidence_record),deficits=many(deficit))),
    (CompletionCandidate,candidate),(c.ModelPrompt,lambda raw:dto(c.ModelPrompt,raw,messages=many(lambda v:dto(c.ModelMessage,v)))))}
def artifact(raw):
    if isinstance(raw,Mapping):
        decode=ARTIFACT_TYPES.get(frozenset(raw))
        if decode:return decode(raw)
    return raw
def result(raw):
    return dto(c.AgentResult,raw,interpreted_goal=optional(goal),verification=optional(verification),metrics=metrics,
         trace=many(lambda v:dto(TraceEvent,v)),artifacts=lambda records:{k:artifact(v) for k,v in records.items()})
def model_record(raw):
    if not isinstance(raw,Mapping):raise ValueError("model record mapping")
    values=dict(raw);values["prompt"]=artifact(values["prompt"])
    if values.get("response_identity") is not None:values["response_identity"]=identity(values["response_identity"])
    return values
def trial(raw):
    return dto(RawTrial,raw,result=result,oracle_verdict=lambda v:dto(OracleVerdict,v),model_records=many(model_record))
def totals(raw):return dto(ComparisonTotals,raw,variants=lambda vs:{k:dto(VariantTotals,v) for k,v in vs.items()})
