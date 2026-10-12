import pytest
from .conftest import api

def test_trace_reserves_terminal_evidence(profile):
    t=api("trace"); trace=t.TraceLedger(profile)
    for i in range(254):
        r=trace.reserve(200)
        trace.append(r,t.TraceEvent(i,"primitive","run",{"executed":True}))
    with pytest.raises(t.BudgetStop): trace.reserve(200)
    trace.terminal(t.TraceEvent(254,"terminal","run",{"status":"BOUNDED_FAILURE"}))
    assert len(trace.freeze())==255
    assert trace.freeze()[-1].kind=="terminal"

def test_trace_actual_bytes_cannot_exceed_reservation(profile):
    t=api("trace"); trace=t.TraceLedger(profile); r=trace.reserve(20)
    with pytest.raises(t.IntegrityStop):
        trace.append(r,t.TraceEvent(0,"primitive","run",{"payload":"x"*200}))
    assert not trace.freeze()

def test_trace_payload_is_detached(profile):
    t=api("trace"); trace=t.TraceLedger(profile); raw={"value":[1,2]}
    r=trace.reserve(300);trace.append(r,t.TraceEvent(0,"observation","run",raw))
    raw["value"].append(3)
    assert trace.freeze()[0].payload["value"]==(1,2)

def test_trace_byte_overflow_blocks_before_work(profile):
    t=api("trace"); trace=t.TraceLedger(profile)
    with pytest.raises(t.BudgetStop): trace.reserve(262145)
