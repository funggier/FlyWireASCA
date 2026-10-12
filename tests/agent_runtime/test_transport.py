import threading
import time
import pytest
from .conftest import api

def test_control_returns_at_deadline():
    t=api("adapters.transport");gate=t.BoundedWorkerGate();cancel=api("control").Cancellation()
    release=threading.Event()
    started=time.monotonic()
    with pytest.raises(TimeoutError):
        gate.run(lambda:release.wait(2),deadline=started+.04,cancellation=cancel)
    assert time.monotonic()-started<.5
    assert gate.busy
    release.set()

def test_cancelled_worker_does_not_allow_duplicate_dispatch():
    t=api("adapters.transport");gate=t.BoundedWorkerGate();cancel=api("control").Cancellation()
    started=threading.Event();release=threading.Event()
    def work():started.set();release.wait(2);return "late"
    def cancellation():started.wait(1);cancel.cancel()
    thread=threading.Thread(target=cancellation);thread.start()
    with pytest.raises(t.TransportCancelled):
        gate.run(work,deadline=time.monotonic()+1,cancellation=cancel)
    with pytest.raises(t.TransportBusy):
        gate.run(lambda:"second",deadline=time.monotonic()+1,cancellation=api("control").Cancellation())
    release.set();thread.join(1)

def test_transport_allows_only_registered_inference_endpoints(clock):
    t=api("adapters.transport");control=api("control").RunControl.create(api("contracts").AgentRequest("task"),clock=clock)
    transport=t.DeadlineJsonTransport("http://127.0.0.1:11434",control,t.TransportLog())
    with pytest.raises(ValueError):transport.request_json("POST","/api/delete",{},1)

def test_chat_disables_truncation_and_log_distinguishes_inspection(clock):
    import io,json
    t=api("adapters.transport");c=api("contracts")
    control=api("control").RunControl.create(c.AgentRequest("task"),clock=clock)
    class Opener:
        def open(self,request,timeout):
            body=json.loads(request.data)
            assert body["truncate"] is False and body["think"] is False
            return io.BytesIO(b'{"done":true}')
    log=t.TransportLog()
    transport=t.DeadlineJsonTransport("http://localhost:11434",control,log,opener=Opener())
    assert transport.request_json("POST","/api/chat",{"think":False},1)=={"done":True}
    assert log.generation_dispatches==1
    control.terminal=True
    with pytest.raises(api("budgets").IntegrityStop):
        transport.request_json("POST","/api/chat",{"think":False},1)
    assert log.generation_dispatches==1
