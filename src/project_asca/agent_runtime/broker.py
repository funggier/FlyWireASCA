"""One broker for all admitted generation, including the frozen A014 adapter."""
from __future__ import annotations
import json
import uuid
from .contracts import BrokerModelRequest,BrokerResult
from .values import fingerprint,freeze_json,ModelPurpose,BaselinePurpose,TerminalReason
from .budgets import Resource,BudgetStop,IntegrityStop,CancelledStop
from .trace import TraceEvent

def strict_json_object(raw):
    if not isinstance(raw,str) or len(raw.encode("utf-8"))>65536:
        raise ValueError("bounded JSON object required")
    def pairs(items):
        result={}
        for key,value in items:
            if key in result:raise ValueError("duplicate JSON key")
            result[key]=value
        return result
    def constant(value):raise ValueError("non-finite JSON number")
    parsed=json.loads(raw,object_pairs_hook=pairs,parse_constant=constant)
    if not isinstance(parsed,dict):raise ValueError("JSON object required")
    return freeze_json(parsed)

def identity_key(identity):
    return (identity.model_name,identity.model_digest,identity.embedding_name,
            identity.embedding_digest,identity.embedding_dimension,identity.backend_version)

class ModelBroker:
    def __init__(self,model,bounds,identity):
        self.model=model;self.bounds=bounds;self.identity=identity
        self.records=[]

    def generate(self,purpose,prompt,*,control,max_output_tokens):
        reservations=();trace_reservation=None;invoked=False
        record={"run_id":control.run_id,"purpose":purpose.value,
                "prompt_fingerprint":fingerprint(prompt),"template_hash":prompt.template_hash,
                "requested_output_tokens":0,"prompt_upper_bound":None,
                "subrequest_id":control.run_id+":"+str(uuid.uuid4()),
                "invoked":False,"transport_dispatches":None,"output":None,"error":None,
                "prompt_tokens":None,"output_tokens":None,"timings":{},
                "identity":identity_key(self.identity)}
        error=None;accepted=None
        started=control.clock.now()
        try:
            control.check_dispatch()
            # The scope itself rejects a role/variant escalation before dispatch.
            with control.model_assist(purpose,record["prompt_fingerprint"]):
                bound=self.bounds.bound(prompt)
                remaining=control.profile.output_tokens-control.ledger.snapshot().output_token_reservations
                requested=min(max_output_tokens,control.profile.output_per_call,remaining)
                if requested<=0 or bound.upper_tokens+requested>control.profile.model_context:
                    raise BudgetStop(message="model prompt/output context admission")
                record["requested_output_tokens"]=requested
                record["prompt_upper_bound"]=bound.upper_tokens
                record["certificate_hash"]=bound.certificate_hash
                trace_reservation=control.trace.reserve(2048)
                reservations=control.ledger.reserve_bundle({
                    Resource.MODEL_CALLS:1,Resource.PROMPT_TOKENS:bound.upper_tokens,
                    Resource.OUTPUT_TOKENS:requested})
                request=BrokerModelRequest(record["subrequest_id"],prompt,requested)
                control.check_dispatch()
                invoked=True;record["invoked"]=True
                control.ledger.record("model_invocations")
                control.ledger.reconcile(reservations[0],1)
                response=self.model.generate(request,
                    deadline=min(control.ledger.deadline,control.clock.now()+control.profile.model_call_seconds),
                    cancellation=control.cancellation)
                record["transport_dispatches"]=response.transport_dispatches
                record["output"]=response.content
                record["timings"]=dict(response.timings)
                record["abort_outcome"]=response.abort_outcome
                control.check_dispatch()
                if response.subrequest_id!=request.subrequest_id or identity_key(response.identity)!=identity_key(self.identity):
                    raise IntegrityStop(TerminalReason.IDENTITY_MISMATCH,"generation identity mismatch")
                record["prompt_tokens"]=response.usage.prompt_tokens
                record["output_tokens"]=response.usage.output_tokens
                # Reconcile each resource even when one reports an overrun.
                mismatch=None
                for r,actual in zip(reservations[1:],(response.usage.prompt_tokens,response.usage.output_tokens)):
                    try:control.ledger.reconcile(r,actual)
                    except IntegrityStop as exc:mismatch=exc
                if mismatch is not None:raise mismatch
                accepted=response
        except BudgetStop as exc:error=exc.reason.value
        except CancelledStop:error=TerminalReason.CANCELLED.value
        except IntegrityStop as exc:
            error=exc.reason.value
            if not control.ledger.snapshot().integrity_failures:control.ledger.record("integrity_failures")
        except (TimeoutError,ConnectionError) as exc:
            error=TerminalReason.MODEL_UNAVAILABLE.value
            record["exception"]=type(exc).__name__
        except Exception as exc:
            error=TerminalReason.MODEL_UNAVAILABLE.value
            record["exception"]=type(exc).__name__
        finally:
            # Only undispatched work may be proved zero; an invoked failed call
            # retains unknown prompt/output reservations.
            for r in reservations:
                if r.reservation_id in control.ledger._open:
                    control.ledger.reconcile(r,None if invoked else 0)
            record["error"]=error
            record["wall_seconds"]=max(0.0,control.clock.now()-started)
            self.records.append(freeze_json(record))
            if trace_reservation is not None:
                event=TraceEvent(len(control.trace.freeze()),"model",control.run_id,
                    {"subrequest_id":record["subrequest_id"],"purpose":record["purpose"],
                     "prompt_fingerprint":record["prompt_fingerprint"],
                     "invoked":invoked,"error":error,"record_ref":fingerprint(record)})
                control.trace.append(trace_reservation,event)
            if not invoked:control.ledger.record("model_preflight_denials")
        return BrokerResult(accepted,error,record["subrequest_id"])
