"""Source-bound raw evidence, content references and independent offline replay."""
from dataclasses import dataclass,replace,fields
from pathlib import Path
from collections.abc import Mapping
import json,re,math
from .source import SourceFingerprint,source_fingerprint,verify_frozen_anchors,G2_COMMIT,SPEC_COMMIT,PLAN_COMMIT,SPEC_PATH,git
from .decision import EvidenceValidation,ArchitectureOutcome,classify_comparison
from .oracle import aggregate_trials,evaluate_trial
from .fixture import load_frozen_workload,bounds_from_workload,render_direct_prompt
from .freeze import validate_freeze
from . import codec
from project_asca.agent_runtime.values import canonical_bytes,fingerprint,thaw_json,TerminalStatus,Phase
from project_asca.agent_runtime.contracts import PhysicalIdentity
from project_asca.agent_runtime.profile import RuntimeProfile,GENERATION_DIGEST,EMBEDDING_DIGEST
from project_asca.agent_runtime.verification import CompletionCandidate,verify_completion
from project_asca.agent_runtime.control import RunControl
from project_asca.agent_runtime.domain import load_public_configuration
from project_asca.agent_runtime.capabilities import CapabilityRegistry
from project_asca.agent_runtime.strategy import validate_plan
from project_asca.agent_runtime.plans import ActionProposal,AttemptResult,ExecutionReceipt
from project_asca.agent_runtime.semantics import VerificationRecord
from project_asca.agent_runtime.prompts import template
SCHEMA="a015-physical-evidence-v1"
@dataclass(frozen=True,slots=True)
class PhysicalRunMetadata:
    run_id:str
    behavior_commit:str
    source:SourceFingerprint
    freeze_commit:str
    workload_hash:str
    components:Mapping
    spec_commit:str
    plan_commit:str
    spec_blob:str
    identity_before:PhysicalIdentity
    identity_after:PhysicalIdentity|None
    environment:Mapping
    setup:Mapping
    g4_ci:Mapping
    physical:bool
    evidence_kind:str
    repetitions:int
    seed:int
    started_at:str
    finished_at:str
    complete:bool
    interruption:str|None=None
@dataclass(frozen=True,slots=True)
class PhysicalEvidence:
    schema:str
    metadata:PhysicalRunMetadata
    trials:tuple
    totals:object
    outcome:ArchitectureOutcome
    references:Mapping
    trial_references:tuple
    payload_hash:str
    reference_contents:Mapping
def evidence_to_wire(e):
    return thaw_json({k:getattr(e,k) for k in ("schema","metadata","trials","totals","outcome","references","trial_references","payload_hash")})
def wire_fingerprint(raw):
    return fingerprint({k:v for k,v in raw.items() if k!="payload_hash"})
def _references(trials):
    references={};contents={};rows=[]
    def store(value):
        key=fingerprint(value);body=canonical_bytes(value)
        references[key]={"path":key+".json","bytes":len(body)};contents[key]=value;return key
    for t in trials:
        rows.append({"run_id":t.result.run_id,"result":store(t.result),"trace":store(t.result.trace),
                     "models":store(t.model_records)})
    return references,contents,tuple(rows)
def build_evidence(trials,metadata):
    trials=tuple(trials);totals=aggregate_trials(trials)
    usage=all(t.result.metrics.reported_prompt_tokens is not None and t.result.metrics.reported_output_tokens is not None for t in trials)
    outcome=classify_comparison(totals,EvidenceValidation(metadata.complete,metadata.physical,usage))
    refs,contents,rows=_references(trials)
    e=PhysicalEvidence(SCHEMA,metadata,trials,totals,outcome,refs,rows,"",contents)
    return replace(e,payload_hash=wire_fingerprint(evidence_to_wire(e)))
def decode_evidence(raw,*,reference_contents):
    allowed={"schema","metadata","trials","totals","outcome","references","trial_references","payload_hash"}
    if not isinstance(raw,Mapping) or set(raw)!=allowed:raise ValueError("closed evidence schema")
    metadata=codec.dto(PhysicalRunMetadata,raw["metadata"],source=lambda v:codec.dto(SourceFingerprint,v),
                       identity_before=codec.identity,identity_after=codec.optional(codec.identity))
    return PhysicalEvidence(raw["schema"],metadata,tuple(codec.trial(v) for v in raw["trials"]),
         codec.totals(raw["totals"]),ArchitectureOutcome(raw["outcome"]),raw["references"],
         tuple(raw["trial_references"]),raw["payload_hash"],reference_contents)
def _read_json(path,max_bytes):
    if path.stat().st_size>max_bytes:raise ValueError("bounded evidence file")
    def pairs(items):
        d={}
        for k,v in items:
            if k in d:raise ValueError("duplicate evidence key")
            d[k]=v
        return d
    def constant(v):raise ValueError("nonfinite evidence number")
    return json.loads(path.read_text(encoding="utf-8"),object_pairs_hook=pairs,parse_constant=constant)
def write_evidence(e,output):
    output=Path(output);directory=output.with_suffix("");directory.mkdir(parents=True,exist_ok=True)
    for key,ref in e.references.items():
        path=directory/ref["path"];body=canonical_bytes(e.reference_contents[key])
        if path.exists() and path.read_bytes()!=body:raise ValueError("content reference collision")
        if not path.exists():path.write_bytes(body)
    output.parent.mkdir(parents=True,exist_ok=True)
    temp=output.with_suffix(output.suffix+".tmp");temp.write_bytes(canonical_bytes(evidence_to_wire(e))+b"\n")
    temp.replace(output)
def load_evidence(output):
    output=Path(output);raw=_read_json(output,256*1024*1024);directory=output.with_suffix("");contents={}
    for key,ref in raw.get("references",{}).items():
        if (not re.fullmatch(r"[0-9a-f]{64}",key) or set(ref)!={"path","bytes"} or ref["path"]!=key+".json"
            or type(ref["bytes"]) is not int or not 0<=ref["bytes"]<=2*1024*1024):raise ValueError("reference schema/bound")
        path=directory/ref["path"]
        try:value=_read_json(path,2*1024*1024)
        except (OSError,ValueError) as exc:raise ValueError("reference unavailable/invalid") from exc
        if fingerprint(value)!=key or len(canonical_bytes(value))!=ref["bytes"]:raise ValueError("reference content hash")
        contents[key]=value
    return decode_evidence(raw,reference_contents=contents)
def _assert(value,message):
    if not value:raise ValueError(message)
def _records_and_metrics(t,case,cfg,bounds,physical):
    r=t.result;m=r.metrics;profile=cfg.profile
    for name,value in m.counters.items():
        _assert(type(value) is int and value>=0,"metric counter type")
    for name,value in m.reservations.items():
        _assert(type(value) is int and value>=0 and hasattr(profile,name) and value<=getattr(profile,name),"resource bound")
    links={"model_invocations":"model_calls","actual_retrieval_queries":"retrieval_queries","vectors_scored":"vectors_scored",
       "relation_invocations":"relation_invocations","relation_visit_events":"relation_visits","relation_scanned_edges":"relation_edges",
       "strategy_attempts":"strategy_attempts","recovery_rounds":"recovery_rounds","primitive_action_attempts":"actions","transitions":"transitions"}
    for name,resource in links.items():_assert(m.counters.get(name,0)<=m.reservations.get(resource,0),"counter beyond reservation")
    _assert(len(r.trace)<=profile.trace_events,"trace event bound")
    _assert(all(e.sequence==i and e.run_id==r.run_id for i,e in enumerate(r.trace)),"trace ownership/order")
    terminals=[e for e in r.trace if e.kind=="terminal"]
    _assert(len(terminals)==1 and r.trace[-1] is terminals[0],"terminal publication/order")
    _assert(terminals[0].payload["status"]==r.status.value and terminals[0].payload["reason"]==r.reason.value,"terminal result")
    size=sum(len(canonical_bytes(e)) for e in r.trace)
    for key,value in r.artifacts.items():
        _assert(fingerprint(value)==key and len(canonical_bytes(value))<=profile.state_bytes,"snapshot reference")
        size+=len(canonical_bytes(value))
    _assert(size<=profile.trace_bytes,"trace/snapshot global bytes")
    actions=[e for e in r.trace if e.kind=="action"]
    _assert(len(actions)==m.counters.get("primitive_action_attempts",0),"actual primitive attempts")
    _assert(sum(e.payload["executed"] is True for e in actions)==m.primitive_actions,"actual primitive effects")
    invocations=sum(record["invoked"] is True for record in t.model_records)
    _assert(invocations==m.model_invocations,"model invocation counter")
    _assert(invocations<= (1 if t.variant.value=="DIRECT_PINNED_MODEL" else 4),"variant call ceiling")
    if t.variant.value=="DIRECT_PINNED_MODEL":
        _assert(not m.context_applicable and m.actual_retrieval_queries==0 and m.relation_invocations==0
                and m.recovery_rounds==0,"baseline selective control leakage")
        _assert(len(t.model_records)==1,"one-shot baseline record")
    else:_assert(m.context_applicable,"runtime context metric applicability")
    usage=True;prompt_sum=output_sum=0
    for record in t.model_records:
        _assert(record["run_id"]==r.run_id and record["subrequest_id"].startswith(r.run_id+":"),"model call ownership")
        prompt=record["prompt"]
        _assert(fingerprint(prompt)==record["prompt_fingerprint"],"prompt fingerprint")
        purpose=record["purpose"]
        if t.variant.value=="DIRECT_PINNED_MODEL":
            _assert(purpose=="DIRECT_SOLUTION" and fingerprint(prompt)==fingerprint(render_direct_prompt(case.text,cfg.public)),
                    "complete direct information/prompt")
        elif purpose=="STRUCTURAL_ROUTING":
            from flywire_asca.structural_routing.model_router import A014_ROUTER_SYSTEM_PROMPT,router_prompt_fingerprint
            _assert(prompt.messages[0].content==A014_ROUTER_SYSTEM_PROMPT and prompt.messages[1].content==case.text
                    and prompt.template_hash==router_prompt_fingerprint(),"query-only A014 prompt")
        else:
            _assert(purpose in ("INTENT","QUERY_PROPOSAL","PLAN_PROPOSAL","PLAN_REPAIR"),"runtime role")
            system,digest=template(purpose)
            _assert(prompt.messages[0].content==system and prompt.template_hash==digest,"frozen role template")
        _assert(tuple(record["identity"])[:5]==("qwen3.5:4b",GENERATION_DIGEST,"qwen3-embedding:0.6b",EMBEDDING_DIGEST,1024),"generation pin")
        if record["invoked"]:
            params=record["request_parameters"]
            _assert(fingerprint(params)==fingerprint({"context_limit":8192,"temperature":0.0,"seed":0,"thinking":False,
                            "max_output_tokens":record["requested_output_tokens"]}),"model settings")
            upper=bounds.bound(prompt).upper_tokens
            _assert(upper==record["prompt_upper_bound"] and upper+record["requested_output_tokens"]<=8192,"token context admission")
            if record["response_identity"] is not None:
                observed=record["response_identity"]
                _assert(record["response_subrequest_id"]==record["subrequest_id"] or record["error"]=="IDENTITY_MISMATCH","response ownership")
                if not record["error"]:_assert(observed.model_digest==GENERATION_DIGEST and observed.embedding_digest==EMBEDDING_DIGEST,"response identity")
            if physical:
                _assert(not record["timings"].get("scripted"),"scripted physical response")
                if not record["error"]:_assert(record["transport_dispatches"]==1,"confirmed generation dispatch")
            if record["prompt_tokens"] is None or record["output_tokens"] is None:usage=False
            else:
                _assert(type(record["prompt_tokens"]) is int and 0<=record["prompt_tokens"]<=upper,"reported prompt bound")
                _assert(type(record["output_tokens"]) is int and 0<=record["output_tokens"]<=record["requested_output_tokens"],"reported output bound")
                prompt_sum+=record["prompt_tokens"];output_sum+=record["output_tokens"]
        for event in r.trace:
            if event.kind=="model" and event.payload["subrequest_id"]==record["subrequest_id"]:
                _assert(event.payload["record_ref"]==fingerprint(record),"model trace record reference")
    if usage:
        _assert((m.reported_prompt_tokens,m.reported_output_tokens)==(prompt_sum,output_sum),"reported usage totals")
    else:_assert(m.reported_prompt_tokens is None or m.reported_output_tokens is None,"unknown usage flag")
    for name,seconds in m.stage_seconds.items():_assert(isinstance(seconds,(float,int)) and not isinstance(seconds,bool) and math.isfinite(seconds) and seconds>=0,"stage timing")
    if "end_to_end" in m.stage_seconds:
        _assert(sum(v for k,v in m.stage_seconds.items() if k.startswith("phase:"))<=m.stage_seconds["end_to_end"]+.001,"exclusive stage timing")
    return usage
def _completion_replay(t,cfg):
    r=t.result
    for event in r.trace:
        if event.kind!="verification":continue
        snapshot=r.artifacts.get(event.payload["control_ref"])
        original=r.artifacts.get(event.payload["verification_ref"])
        _assert(snapshot is not None and isinstance(original,VerificationRecord),"verification references")
        candidate=r.artifacts.get(original.candidate_fingerprint)
        _assert(isinstance(candidate,CompletionCandidate),"candidate reference")
        replay=verify_completion(r.interpreted_goal,candidate,knowledge=cfg.knowledge,
            final_state=candidate.attempt.final_state,control_snapshot=snapshot)
        _assert(fingerprint(replay)==fingerprint(original),"independent completion replay")
        if r.status is TerminalStatus.SUCCEEDED and original.execution_id==r.verification.execution_id:
            _assert(replay.passed and fingerprint(replay)==fingerprint(r.verification)
                    and fingerprint(candidate.data)==fingerprint(r.data),"verified terminal candidate")
    if r.status is TerminalStatus.SUCCEEDED:
        _assert(any(e.kind=="verification" for e in r.trace),"missing verification event")
def verify_evidence(evidence,*,root):
    e=evidence;m=e.metadata;errors=[];usage=True;source_valid=True;identity_valid=True
    try:
        _assert(e.schema==SCHEMA and e.payload_hash==wire_fingerprint(evidence_to_wire(e)),"evidence schema/hash")
        _assert(m.repetitions==3 and type(m.seed) is int and m.seed==0,"fixed protocol metadata")
        _assert((m.physical and m.evidence_kind=="PHYSICAL_MODEL_COMPARISON") or
                (not m.physical and m.evidence_kind=="HARNESS_CONTRACT_TEST"),"evidence kind")
        w=load_frozen_workload(Path(root)/"fixtures/a015/stage-a-v1")
        bounds=bounds_from_workload(w);freeze=validate_freeze(w,bounds);cfg=load_public_configuration(w.public,w.profile)
        _assert(freeze.valid and freeze.aggregate_hash==m.workload_hash and freeze.components==dict(m.components),"frozen input identity")
        actual=source_fingerprint(root,m.behavior_commit,w.lock["source_universe"])
        _assert(fingerprint(actual)==fingerprint(m.source),"behavior source universe/mode/blob")
        verify_frozen_anchors(root,m.behavior_commit,w)
        _assert((m.freeze_commit,m.spec_commit,m.plan_commit)==(G2_COMMIT,SPEC_COMMIT,PLAN_COMMIT),"approval/freeze ancestry")
        _assert(m.spec_blob==git(root,"rev-parse",SPEC_COMMIT+":"+SPEC_PATH).decode().strip(),"spec blob")
        expected=PhysicalIdentity(**w.certificate["identity"])
        _assert(fingerprint(m.identity_before)==fingerprint(expected),"physical pre-identity")
        _assert(m.identity_after is not None and fingerprint(m.identity_after)==fingerprint(expected),"physical post-identity")
        if m.physical:
            _assert(m.g4_ci.get("head_sha")==m.behavior_commit and m.g4_ci.get("conclusion")=="success","G4 exact feature CI")
            _assert(m.environment.get("hostname")=="CDQ-P" and m.environment.get("python") and m.environment.get("os"),"native environment")
            _assert(m.setup.get("common_warmup") and m.setup.get("index_setup"),"warm-up/setup metadata")
        refs,contents,rows=_references(e.trials)
        _assert(fingerprint(refs)==fingerprint(e.references) and fingerprint(rows)==fingerprint(e.trial_references),"raw trial reference manifest")
        _assert(set(contents)==set(e.reference_contents),"reference universe")
        for key,value in contents.items():_assert(fingerprint(e.reference_contents[key])==key,"raw reference content")
        from .schedule import trial_schedule
        schedule=trial_schedule(w);_assert(len(e.trials)<=384,"trial universe size")
        _assert(m.complete==(len(e.trials)==384),"completion denominator")
        ids=set();cases={c.case_id:c for c in w.cases}
        for slot,t in zip(schedule,e.trials):
            _assert((t.case_id,t.variant,t.repetition)==(slot.case.case_id,slot.variant,slot.repetition),"schedule/order/repetitions")
            _assert(t.request_fingerprint==fingerprint(slot.case.text),"ordinary request fingerprint")
            _assert(t.result.run_id not in ids and t.result.run_id!=t.case_id,"fresh run ID")
            ids.add(t.result.run_id)
            _assert(fingerprint(evaluate_trial(slot.case,w.oracle[t.case_id],t.result))==fingerprint(t.oracle_verdict),"independent oracle verdict")
            usage=_records_and_metrics(t,slot.case,cfg,bounds,m.physical) and usage
            _completion_replay(t,cfg)
        totals=aggregate_trials(e.trials)
        _assert(fingerprint(totals)==fingerprint(e.totals),"recomputed denominators/counters/paired totals")
        outcome=classify_comparison(totals,EvidenceValidation(m.complete,m.physical,usage))
        _assert(outcome==e.outcome,"ordered architecture outcome")
    except (ValueError,TypeError,KeyError,AttributeError,IndexError,OSError) as exc:
        errors.append(str(exc))
        source_valid="source" not in str(exc) and "Git" not in str(exc)
        identity_valid="identity" not in str(exc)
    return EvidenceValidation(not errors,m.physical,usage,source_valid,identity_valid,tuple(errors))
