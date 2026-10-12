import json,pytest
from pathlib import Path
from tests.agent_runtime.conftest import api,Clock
from tests.agent_runtime.test_public_runtime import Identity,Bounds,Model
from project_asca.evaluation.fixture import load_frozen_workload
@pytest.fixture
def workload():return load_frozen_workload(Path(__file__).resolve().parents[2]/"fixtures/a015/stage-a-v1")
@pytest.fixture
def configuration(workload):return api("domain").load_public_configuration(workload.public,workload.profile)
@pytest.fixture
def clock():return Clock()
def wire_intent(text,configuration):
    schemas=api("goals").TaskSchemaRegistry.from_public(configuration)
    found=api("interpretation").deterministic_intent(api("contracts").AgentRequest(text),schemas)
    if found is None:raise ValueError("development scripted grammar unresolved")
    if found.intent is None:
        return {"status":"NEEDS_CLARIFICATION" if found.clarification else "UNSUPPORTED",
                "reason":"AMBIGUOUS_INPUT" if found.clarification else "UNSUPPORTED_CAPABILITY"}
    b=found.intent.bindings;parameters=api("values").thaw_json(b["parameters"])
    return {"kind":found.intent.kind.value,"task":b["task"],"parameters":parameters,
        "spans":[{"name":k,"value":v,"start":0,"end":len(text)} for k,v in parameters.items()
                 if k not in ("operations","outputs","top_level")]}
def direct_for(configuration,clock,proposal,text):
    from project_asca.evaluation.direct import DirectPinnedRunner
    def response(request,deadline,cancellation):
        body={"intent":wire_intent(text,configuration),"proposal":proposal}
        return api("contracts").BrokerModelResponse(request.subrequest_id,Identity().inspect(),
            json.dumps(body,ensure_ascii=False),api("contracts").Usage(60,30,True))
    model=Model(response);broker=api("broker").ModelBroker(model,Bounds(),Identity().inspect())
    return DirectPinnedRunner(configuration,broker,clock=clock),model
