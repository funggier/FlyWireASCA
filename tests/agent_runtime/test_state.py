import pytest
from .conftest import api

def test_fresh_sessions_do_not_share_mutable_state(configuration):
    t=api("state")
    first=t.InMemorySession(configuration.initial_state,"one")
    second=t.InMemorySession(configuration.initial_state,"two")
    first.set_values("T2",{"quantity":18})
    assert first.snapshot().values["T2"]["quantity"]==18
    assert second.snapshot().values["T2"]["quantity"]==0
    assert first.snapshot().revision==1
    assert first.snapshot().snapshot_id!=second.snapshot().snapshot_id

def test_state_type_and_byte_checks_precede_mutation(configuration):
    t=api("state");session=t.InMemorySession(configuration.initial_state,"one")
    before=session.snapshot()
    with pytest.raises(ValueError):session.set_values("T2",{"quantity":True})
    with pytest.raises(ValueError):session.set_values("O1",{"status":"x"*65537})
    assert session.snapshot()==before
