import pytest
from .conftest import api

def setup(clock,handler=None,upper=3000):
    c=api("contracts");b=api("broker");ctl=api("control")
    identity=c.PhysicalIdentity("qwen3.5:4b","digest","qwen3-embedding:0.6b","embed",1024,"0.32.15")
    prompt=c.ModelPrompt((c.ModelMessage("system","schema"),c.ModelMessage("user","task")),"test","hash")
    class Bounds:
        def bound(self,p):return c.PromptBound(upper,"cert")
    class Port:
        def generate(self,request,**kwargs):
            if handler:return handler(request,identity)
            return c.BrokerModelResponse(request.subrequest_id,identity,'{"value":7}',c.Usage(17,3,True))
    control=ctl.RunControl.create(c.AgentRequest("task"),clock=clock)
    return b.ModelBroker(Port(),Bounds(),identity),control,prompt

def test_failed_generation_retains_reservations(clock):
    def timeout(*args):raise TimeoutError("unknown backend work")
    broker,control,prompt=setup(clock,timeout)
    result=broker.generate(api("contracts").ModelPurpose.INTENT,prompt,control=control,max_output_tokens=1024)
    assert result.error is not None
    assert control.snapshot().metrics.model_invocations==1
    assert control.snapshot().metrics.output_token_reservations==1024
    assert control.snapshot().metrics.reported_output_tokens is None
    assert control.snapshot().metrics.unknown_usage

def test_known_usage_and_192_share_one_ledger(clock):
    broker,control,prompt=setup(clock)
    result=broker.generate(api("contracts").ModelPurpose.STRUCTURAL_ROUTING,prompt,control=control,max_output_tokens=192)
    assert result.error is None
    assert control.snapshot().metrics.model_invocations==1
    assert control.snapshot().metrics.reported_output_tokens==3
    assert broker.records[0]["requested_output_tokens"]==192
    assert broker.records[0]["purpose"]=="STRUCTURAL_ROUTING"

def test_prompt_and_output_share_context_limit(clock):
    broker,control,prompt=setup(clock,upper=8000)
    result=broker.generate(api("contracts").ModelPurpose.INTENT,prompt,control=control,max_output_tokens=1024)
    assert result.error=="BUDGET_EXHAUSTED"
    assert control.snapshot().metrics.model_invocations==0

def test_wrong_response_identity_is_not_accepted(clock):
    c=api("contracts")
    def wrong(r,identity):return c.BrokerModelResponse("another-run",identity,"{}",c.Usage(5,2,True))
    broker,control,prompt=setup(clock,wrong)
    result=broker.generate(c.ModelPurpose.INTENT,prompt,control=control,max_output_tokens=192)
    assert result.error=="IDENTITY_MISMATCH"
    assert control.snapshot().metrics.integrity_failures==1

def test_late_response_and_reused_correlation_id(clock):
    c=api("contracts")
    broker,control,prompt=setup(clock)
    def late(request,*,deadline,cancellation):
        control.cancellation.cancel()
        return c.BrokerModelResponse(request.subrequest_id,broker.identity,"{}",c.Usage(5,2,True))
    broker.model.generate=late
    other=api("control").RunControl.create(c.AgentRequest("task",request_id=control.request.request_id),clock=clock)
    result=broker.generate(c.ModelPurpose.INTENT,prompt,control=control,max_output_tokens=192)
    assert result.error=="CANCELLED"
    assert result.response is None and other.run_id!=control.run_id
    assert other.snapshot().metrics.model_invocations==0

def test_output_overrun_is_a_control_failure(clock):
    c=api("contracts")
    def too_much(r,identity):return c.BrokerModelResponse(r.subrequest_id,identity,"{}",c.Usage(17,193,True))
    broker,control,prompt=setup(clock,too_much)
    result=broker.generate(c.ModelPurpose.STRUCTURAL_ROUTING,prompt,control=control,max_output_tokens=192)
    assert result.error=="CONTROL_VIOLATION"
    assert control.snapshot().metrics.reported_output_tokens==193

@pytest.mark.parametrize("raw",['{"a":1,"a":2}','{"a":NaN}','{} trailing','[]','```json\n{}\n```'])
def test_strict_json_rejects_partial_or_duplicate_data(raw):
    with pytest.raises(ValueError):api("broker").strict_json_object(raw)

def test_terminal_control_denies_even_bound_probe(clock):
    broker,control,prompt=setup(clock);control.terminal=True
    result=broker.generate(api("contracts").ModelPurpose.INTENT,prompt,control=control,max_output_tokens=192)
    assert result.error=="CONTROL_VIOLATION"
    assert control.snapshot().metrics.model_invocations==0
