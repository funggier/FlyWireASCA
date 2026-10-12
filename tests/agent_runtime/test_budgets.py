import pytest
from .conftest import api

def test_unknown_usage_keeps_charge(ledger):
    b=api("budgets"); r=ledger.reserve(b.Resource.MODEL_CALLS,1)
    ledger.reconcile(r,None)
    assert ledger.snapshot().model_call_reservations==1
    assert ledger.snapshot().unknown_usage

def test_atomic_admission_does_not_spend_call_on_token_denial(ledger):
    b=api("budgets")
    with pytest.raises(b.BudgetStop):
        ledger.reserve_bundle({b.Resource.MODEL_CALLS:1,b.Resource.OUTPUT_TOKENS:2049})
    assert ledger.snapshot().model_call_reservations==0

def test_actual_usage_refunds_only_known_difference(ledger):
    b=api("budgets"); r=ledger.reserve(b.Resource.PROMPT_TOKENS,8000)
    ledger.reconcile(r,100)
    assert ledger.snapshot().prompt_token_reservations==100
    assert ledger.snapshot().reported_prompt_tokens==100

def test_reported_overrun_and_duplicate_reconciliation_are_integrity_errors(ledger):
    b=api("budgets"); r=ledger.reserve(b.Resource.OUTPUT_TOKENS,192)
    with pytest.raises(b.IntegrityStop): ledger.reconcile(r,193)
    assert ledger.snapshot().integrity_failures==1
    assert ledger.snapshot().reported_output_tokens == 193
    with pytest.raises(b.IntegrityStop): ledger.reconcile(r,100)

@pytest.mark.parametrize("amount",[True,-1,float("nan"),1.5])
def test_invalid_reservation_counts(ledger,amount):
    with pytest.raises(ValueError): ledger.reserve(api("budgets").Resource.MODEL_CALLS,amount)

def test_global_and_per_attempt_budgets_never_reset(ledger):
    b=api("budgets")
    for attempt in ("a","b","c"): ledger.reserve(b.Resource.ACTIONS,32,attempt_id=attempt)
    with pytest.raises(b.BudgetStop): ledger.reserve(b.Resource.ACTIONS,1,attempt_id="d")
    assert ledger.snapshot().action_reservations==96

def test_33_actions_in_one_attempt_denied(ledger):
    b=api("budgets")
    with pytest.raises(b.BudgetStop): ledger.reserve(b.Resource.ACTIONS,33,attempt_id="a")
    assert ledger.snapshot().action_reservations==0

def test_deadline_is_monotonic(ledger,clock):
    b=api("budgets"); clock.value=180
    with pytest.raises(b.BudgetStop): ledger.reserve(b.Resource.MODEL_CALLS,1)

def test_run_ids_and_cancellation_are_independent(profile,clock):
    c=api("control"); req=api("contracts").AgentRequest("work",request_id="same")
    a=c.RunControl.create(req,profile,clock)
    d=c.RunControl.create(req,profile,clock)
    assert a.run_id!=d.run_id
    a.cancellation.cancel()
    with pytest.raises(c.CancelledStop): a.check_dispatch()
    d.check_dispatch()
