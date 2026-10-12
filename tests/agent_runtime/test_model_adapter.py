import pytest
from .conftest import api

class FakeTransport:
    def __init__(self):
        self.calls=[];self.changed=False;self.override_deadline=None;self.override_cancellation=None
    def request_json(self,method,path,payload,timeout_seconds):
        p=api("profile");self.calls.append((method,path,payload))
        if path=="/api/version":return {"version":"0.32.15"}
        if path=="/api/tags":
            return {"models":[{"name":"qwen3.5:4b","digest":"changed" if self.changed else p.GENERATION_DIGEST},
                              {"name":"qwen3-embedding:0.6b","digest":p.EMBEDDING_DIGEST}]}
        if path=="/api/show":
            embedding=payload["model"].startswith("qwen3-")
            arch="qwen3" if embedding else "qwen35"
            return {"template":"{{ .Prompt }}","modelfile":"RENDERER qwen3.5\n",
                    "model_info":{"general.architecture":arch,arch+".embedding_length":1024 if embedding else 2560,
                                  arch+".context_length":32768 if embedding else 262144,
                                  "tokenizer.ggml.pre":"qwen2" if embedding else "qwen35",
                                  "tokenizer.ggml.model":"gpt2"},
                    "details":{"parameter_size":"4.7B","quantization_level":"Q4_K_M"},
                    "capabilities":["embedding"] if embedding else ["completion"]}
        if path=="/api/chat":
            return {"model":"qwen3.5:4b","done":True,"message":{"role":"assistant","content":'{"ok":true}'},
                    "prompt_eval_count":17,"eval_count":3,"total_duration":10}
        raise AssertionError(path)

def test_pinned_model_reuses_legacy_adapter_and_calls_once(clock):
    m=api("adapters.model");c=api("contracts");control=api("control").RunControl.create(c.AgentRequest("task"),clock=clock)
    transport=FakeTransport();identity=m.probe_physical_identity("http://localhost:11434",transport=transport)
    port=m.PinnedModelPort("http://localhost:11434",control,identity,transport=transport)
    prompt=c.ModelPrompt((c.ModelMessage("system","schema"),c.ModelMessage("user","text")),"x","y")
    response=port.generate(c.BrokerModelRequest("sub",prompt,192),deadline=100,cancellation=control.cancellation)
    calls=[payload for _,path,payload in transport.calls if path=="/api/chat"]
    assert len(calls)==1
    assert calls[0]["options"]=={"num_ctx":8192,"num_predict":192,"temperature":0.0,"seed":0}
    assert calls[0]["think"] is False
    assert response.subrequest_id=="sub" and response.usage.prompt_tokens==17
    assert response.transport_dispatches==1

def test_probe_is_fresh_and_identity_mismatch_prevents_chat(clock):
    m=api("adapters.model");c=api("contracts");control=api("control").RunControl.create(c.AgentRequest("task"),clock=clock)
    transport=FakeTransport();identity=m.probe_physical_identity("http://localhost:11434",transport=transport)
    transport.changed=True
    prompt=c.ModelPrompt((c.ModelMessage("system","schema"),c.ModelMessage("user","text")),"x","y")
    port=m.PinnedModelPort("http://localhost:11434",control,identity,transport=transport)
    with pytest.raises(api("budgets").IntegrityStop):
        port.generate(c.BrokerModelRequest("sub",prompt,192),deadline=100,cancellation=control.cancellation)
    assert not any(path=="/api/chat" for _,path,_ in transport.calls)
