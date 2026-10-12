"""One pinned generation, full public information, shared mechanical verification."""
from dataclasses import dataclass
from collections.abc import Mapping
from project_asca.agent_runtime.values import (FrozenRecord,RunVariant,BaselinePurpose,TaskKind,EvidenceKind,
    Phase,TerminalStatus,TerminalReason,fingerprint,canonical_bytes)
from project_asca.agent_runtime.contracts import AgentResult,parse_agent_request
from project_asca.agent_runtime.control import RunControl,MonotonicClock
from project_asca.agent_runtime.budgets import BudgetStop,CancelledStop,IntegrityStop
from project_asca.agent_runtime.broker import ModelBroker,strict_json_object
from project_asca.agent_runtime.goals import GoalCompiler,TaskSchemaRegistry
from project_asca.agent_runtime.interpretation import validate_intent_proposal
from project_asca.agent_runtime.semantics import EvidenceRecord,EvidenceCoverage
from project_asca.agent_runtime.plans import ActionProposal,PlanStep,ValueBinding
from project_asca.agent_runtime.strategy import validate_plan,parse_plan_proposal
from project_asca.agent_runtime.execution import execute_attempt
from project_asca.agent_runtime.capabilities import CapabilityRegistry,StageAAuthorization
from project_asca.agent_runtime.adapters.procedures import ProcedureExecutionAdapter
from project_asca.agent_runtime.verification import CompletionCandidate,verify_completion,candidate_from_attempt
from project_asca.agent_runtime.rendering import render_result_data
from project_asca.agent_runtime.trace import TraceEvent
from .fixture import render_direct_prompt

@dataclass(frozen=True,slots=True)
class PublicBindingContext(FrozenRecord):
    snapshot_id:str
    items:tuple
    coverage:EvidenceCoverage
    def __post_init__(self):
        super(PublicBindingContext,self).__post_init__()
        if len(self.items)>256 or len(canonical_bytes(self.items))>65536:raise ValueError("full public binder bound")

def public_records(configuration):
    k=configuration.knowledge;sid=k.snapshot_id;records=[]
    for f in k.facts:records.append(EvidenceRecord(f["id"],EvidenceKind.STORED_FACT,f["id"],sid,f))
    for n in k.entities:records.append(EvidenceRecord("node:"+n["id"],EvidenceKind.RELATION_PATH,n["id"],sid,
                                                     {"record_kind":"node",**dict(n)}))
    for e in k.edges:
        records.append(EvidenceRecord("edge:"+e["id"],EvidenceKind.RELATION_PATH,e["id"],sid,{"record_kind":"edge",**dict(e)}))
        eid="evidence:"+e["id"]
        records.append(EvidenceRecord(eid,EvidenceKind.RELATION_PATH,e["id"],sid,
            {"record_kind":"edge_evidence","id":eid,"edge_id":e["id"],"confidence":e["confidence"],"version":e["version"]}))
    return tuple(records)
def bind_answer(proposal,goal,records,configuration):
    if set(proposal)!={"type","data","evidence_ids"}:raise ValueError("closed answer schema")
    refs=proposal["evidence_ids"]
    if not isinstance(refs,(tuple,list)) or len(set(refs))!=len(refs) or any(not isinstance(r,str) for r in refs):
        raise ValueError("unique public evidence references")
    by_id={r.evidence_id:r for r in records};selected=[]
    for ref in refs:
        identifier=ref if ref in by_id else "edge:"+ref if "edge:"+ref in by_id else "node:"+ref
        if identifier not in by_id:raise ValueError("unknown evidence reference")
        selected.append(identifier)
    data=proposal["data"];extra=[]
    if goal.kind is TaskKind.RELATION:
        if not isinstance(data,Mapping) or set(data)!={"paths"} or not isinstance(data["paths"],(tuple,list)):
            raise ValueError("typed path answer")
        for path in data["paths"]:
            if not isinstance(path,Mapping) or set(path)!={"node_ids","edge_ids","evidence_ids"}:raise ValueError("path schema")
            constituents=tuple("node:"+n for n in path["node_ids"])+tuple(
                x for edge in path["edge_ids"] for x in ("edge:"+edge,"evidence:"+edge))
            if any(r not in by_id for r in constituents):raise ValueError("unknown path constituent")
            identifier="path:"+fingerprint({"nodes":path["node_ids"],"edges":path["edge_ids"],"snapshot":configuration.knowledge.snapshot_id})
            wrapper=EvidenceRecord(identifier,EvidenceKind.RELATION_PATH,identifier,configuration.knowledge.snapshot_id,
                {"record_kind":"path",**dict(path)},constituents)
            extra.append(wrapper);selected.extend((identifier,*constituents))
    return data,tuple(dict.fromkeys(selected)),records+tuple(extra)
def justified_stop(goal,configuration):
    if goal.parameters["task"]=="state_range" and goal.parameters["min"]>goal.parameters["max"]:
        return TerminalReason.NO_VALID_PLAN
    for ref in goal.required_evidence:
        if ref.startswith("relation:"):continue
        if "." in ref:
            entity,field=ref.rsplit(".",1)
            f=[f for f in configuration.knowledge.facts if f["subject"]==entity and f["field"]==field]
            if not f:return TerminalReason.MISSING_EVIDENCE
            if f[0]["confidence"]<.5:return TerminalReason.INSUFFICIENT_CONFIDENCE
    if goal.kind is TaskKind.RELATION:
        edges=[e for e in configuration.knowledge.edges if e["source"]==goal.parameters["entity"]
               and e["relation"] in goal.parameters["relations"]]
        if not edges:return TerminalReason.MISSING_EVIDENCE
        if not any(e["confidence"]>=.5 for e in edges):return TerminalReason.INSUFFICIENT_CONFIDENCE
    return None

class DirectPinnedRunner:
    def __init__(self,configuration,broker,*,clock=None):
        self.configuration=configuration;self.broker=broker;self.clock=clock or MonotonicClock()
        self.complete_public=configuration.public;self.model_records=[]
        self.schemas=TaskSchemaRegistry.from_public(configuration);self.registry=CapabilityRegistry.from_public(configuration)
        self.records=public_records(configuration)
    def run(self,text,*,cancellation=None):
        request=parse_agent_request(text);cfg=self.configuration
        c=RunControl.create(request,cfg.profile,self.clock,cancellation,RunVariant.DIRECT_PINNED_MODEL)
        start=self.clock.now();goal=None;candidate=None;verification=None;attempt=None
        model=self.broker.model.for_control(c) if hasattr(self.broker.model,"for_control") else self.broker.model
        broker=ModelBroker(model,self.broker.bounds,self.broker.identity)
        def publish(status,reason):
            if status is TerminalStatus.SUCCEEDED:c.check_dispatch()
            language="th" if any("\u0e00"<=x<="\u0e7f" for x in request.text) else "en"
            answer=render_result_data(candidate,verification,language=language) if status is TerminalStatus.SUCCEEDED else "Task not completed: "+reason.value
            c.terminal=True;c.phase=Phase.TERMINAL
            c.ledger.record_span("end_to_end",max(0.0,self.clock.now()-start))
            c.trace.terminal(TraceEvent(len(c.trace.freeze()),"terminal",c.run_id,{"status":status.value,"reason":reason.value}))
            return AgentResult(request.request_id,c.run_id,status,reason,goal,answer,
                candidate.data if candidate else None,verification,candidate.evidence_refs if candidate else (),
                attempt.final_state.snapshot_id if attempt else None,c.ledger.snapshot(),c.trace.freeze(),
                status is not TerminalStatus.SUCCEEDED and attempt is not None)
        try:
            generated=broker.generate(BaselinePurpose.DIRECT_SOLUTION,render_direct_prompt(request.text,cfg.public),
                                      control=c,max_output_tokens=1024)
            if generated.error:
                reason=TerminalReason(generated.error)
                status=(TerminalStatus.CANCELLED if reason is TerminalReason.CANCELLED else
                        TerminalStatus.REJECTED if reason in (TerminalReason.IDENTITY_MISMATCH,TerminalReason.PROVENANCE_INVALID,TerminalReason.CONTROL_VIOLATION)
                        else TerminalStatus.BOUNDED_FAILURE)
                return publish(status,reason)
            c.check_dispatch();mechanical_started=self.clock.now()
            raw=strict_json_object(generated.response.content)
            if set(raw)!={"intent","proposal"} or not isinstance(raw["proposal"],Mapping):raise ValueError("closed direct output schema")
            proposal=raw["proposal"];found=validate_intent_proposal(raw["intent"],request,self.schemas)
            c.ledger.record("model_claimed_success",int(proposal.get("type")!="stop"))
            if found.intent is None:
                status=TerminalStatus.NEEDS_CLARIFICATION if found.clarification else TerminalStatus.UNSUPPORTED
                reason=TerminalReason.AMBIGUOUS_INPUT if found.clarification else TerminalReason.UNSUPPORTED_CAPABILITY
                if dict(proposal)!={"type":"stop","status":status.value,"reason":reason.value}:raise ValueError("contradictory stop")
                return publish(status,reason)
            goal=GoalCompiler().compile(found.intent,request,self.schemas)
            if proposal.get("type")=="stop":
                reason=justified_stop(goal,cfg)
                if reason is None or dict(proposal)!={"type":"stop","status":"BOUNDED_FAILURE","reason":reason.value}:
                    raise ValueError("unverified bounded stop")
                return publish(TerminalStatus.BOUNDED_FAILURE,reason)
            data=None;refs=();records=self.records
            if proposal.get("type")=="structured-answer":
                data,refs,records=bind_answer(proposal,goal,records,cfg)
                version=self.registry.descriptors["assert"].version
                value=ValueBinding("literal",value=data)
                plan=ActionProposal("direct:"+c.run_id,0,(PlanStep("answer-check","assert",version,
                    {"actual":value,"op":ValueBinding("literal",value="eq"),"value":value}),),{})
            else:plan=parse_plan_proposal(proposal)
            context=PublicBindingContext(cfg.knowledge.snapshot_id,records,EvidenceCoverage(goal.required_evidence,goal.required_evidence,True))
            checked=validate_plan(plan,goal,context,catalog=cfg.catalog,registry=self.registry,control=c)
            if checked.plan is None:
                c.ledger.record("rejected_proposals");return publish(TerminalStatus.BOUNDED_FAILURE,TerminalReason.INVALID_PLAN)
            c.phase=Phase.EXECUTING
            attempt=execute_attempt(checked.plan,goal,context,initial=cfg.initial_state,catalog=cfg.catalog,
                    registry=self.registry,authorization=StageAAuthorization(),control=c,executor=ProcedureExecutionAdapter())
            c.check_dispatch();c.phase=Phase.VERIFYING
            candidate=(CompletionCandidate(data,refs,attempt,records) if proposal["type"]=="structured-answer" else
                       candidate_from_attempt(goal,records,attempt))
            verification=verify_completion(goal,candidate,knowledge=cfg.knowledge,final_state=attempt.final_state,
                                           control_snapshot=c.snapshot())
            c.ledger.record_span("direct:mechanical",max(0.0,self.clock.now()-mechanical_started))
            if verification.passed:return publish(TerminalStatus.SUCCEEDED,TerminalReason.VERIFIED)
            c.ledger.record("rejected_proposals")
            reason=TerminalReason(attempt.deficits[0].kind) if attempt.deficits else TerminalReason.OBSERVED_MISMATCH
            return publish(TerminalStatus.BOUNDED_FAILURE,reason)
        except CancelledStop:return publish(TerminalStatus.CANCELLED,TerminalReason.CANCELLED)
        except BudgetStop as exc:return publish(TerminalStatus.BOUNDED_FAILURE,exc.reason)
        except IntegrityStop as exc:
            if not c.ledger.snapshot().integrity_failures:c.ledger.record("integrity_failures")
            return publish(TerminalStatus.REJECTED,exc.reason)
        except (ValueError,TypeError,KeyError,AttributeError):
            c.ledger.record("rejected_proposals")
            return publish(TerminalStatus.BOUNDED_FAILURE,TerminalReason.INVALID_PLAN)
        finally:self.model_records.extend(broker.records)
