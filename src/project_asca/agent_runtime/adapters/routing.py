"""A014 hybrid query-only routing through the single metered broker."""
from ..contracts import ModelPrompt,ModelMessage
from ..values import ModelPurpose,fingerprint
from ..semantics import RouteDecision
from ..budgets import IntegrityStop
from flywire_asca.model.contracts import ModelDescriptor,ModelResponse
from flywire_asca.model.errors import ModelUnavailableError
from flywire_asca.structural_routing import runner as routing_runner
from flywire_asca.structural_routing.models import StructuralRoutingRequest,RoutingPolicy
from flywire_asca.structural_routing.model_router import router_prompt_fingerprint,A014_ROUTER_SYSTEM_PROMPT

class LegacyBrokerAdapter:
    def __init__(self,broker,control):self.broker=broker;self.control=control
    def inspect(self):
        i=self.broker.identity
        return ModelDescriptor("ollama",i.backend_version,i.model_name,i.model_digest,"qwen35",None,"4.7B",
                               "Q4_K_M",8192,2560,("completion",))
    def generate(self,request):
        if (request.max_output_tokens!=192 or request.context_limit!=8192 or request.temperature!=0
            or request.seed!=0 or request.thinking or len(request.messages)!=2
            or request.messages[0].content!=A014_ROUTER_SYSTEM_PROMPT
            or self.control.run_id not in request.request_id):
            raise IntegrityStop(message="A014 bridge contract/ownership")
        prompt=ModelPrompt(tuple(ModelMessage(m.role.value,m.content) for m in request.messages),
                           "a014-router",router_prompt_fingerprint())
        result=self.broker.generate(ModelPurpose.STRUCTURAL_ROUTING,prompt,control=self.control,max_output_tokens=192)
        if result.error:raise ModelUnavailableError(result.error)
        r=result.response;t=r.timings
        return ModelResponse(request.request_id,r.identity.model_name,r.identity.model_digest,r.content,None,
             r.usage.prompt_tokens,r.usage.output_tokens,t.get("total_duration_ns"),t.get("load_duration_ns"),
             t.get("prompt_eval_duration_ns"),t.get("eval_duration_ns"))

class RoutingAdapter:
    def __init__(self,broker):self.broker=broker;self.cache={}
    def route(self,request,*,control):
        control.check_dispatch()
        if request!=control.request:raise IntegrityStop(message="routing request ownership")
        key=(control.run_id,fingerprint(request))
        if key in self.cache:
            control.ledger.record("routing_cache_hits");return self.cache[key]
        control.ledger.record("routing_invocations")
        local=StructuralRoutingRequest(control.run_id+":"+request.request_id,request.text,request.language_hint)
        result=routing_runner.run_structural_routing(local,policy=RoutingPolicy.HYBRID_RULE_THEN_MODEL,
                            model_adapter=LegacyBrokerAdapter(self.broker,control))
        control.check_dispatch()
        decision=RouteDecision(result.status.value,
             tuple(r.name for r in result.structural_need.required_relations),
             result.structural_need.requires_path_provenance,result.rule_evidence_ids)
        self.cache[key]=decision
        control.event("routing",{"status":decision.status,"relations":decision.relation_types,
                                "source":result.source.value,"prompt_hash":router_prompt_fingerprint()})
        return decision
