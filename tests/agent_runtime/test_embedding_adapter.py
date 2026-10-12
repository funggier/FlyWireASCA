from .conftest import api
from .test_model_adapter import FakeTransport

def test_pinned_embedding_preserves_legacy_normalization_and_new_owner(clock):
    m=api("adapters.model");c=api("contracts");p=api("profile")
    control=api("control").RunControl.create(c.AgentRequest("development"),clock=clock)
    class Transport(FakeTransport):
        def request_json(self,method,path,payload,timeout_seconds):
            if path=="/api/embed":
                self.calls.append((method,path,payload))
                return {"model":"qwen3-embedding:0.6b",
                    "embeddings":[[2.0]+[0.0]*1023 for _ in payload["input"]],"prompt_eval_count":7}
            return super().request_json(method,path,payload,timeout_seconds)
    transport=Transport()
    identity=m.probe_physical_identity("http://localhost:11434",transport=transport)
    port=m.PinnedEmbeddingPort("http://localhost:11434",control,identity,transport=transport)
    result=port.embed(("document",),deadline=100,cancellation=control.cancellation)
    assert result.vectors[0][0]==1 and result.dimension==1024 and result.prompt_tokens==7
    assert len([v for _,path,v in transport.calls if path=="/api/embed"])==1
    control.terminal=True
    newer=api("control").RunControl.create(c.AgentRequest("new"),clock=clock)
    rebound=port.for_control(newer)
    assert rebound.control is newer and rebound.gate is port.gate
