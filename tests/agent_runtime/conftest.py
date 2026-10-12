import importlib
import pytest

def api(name):
    try:
        return importlib.import_module("project_asca.agent_runtime." + name)
    except ImportError as exc:
        pytest.fail(f"Required A015 module {name} is absent: {exc}", pytrace=False)

class Clock:
    def __init__(self): self.value = 0.0
    def now(self): return self.value

@pytest.fixture
def clock(): return Clock()

@pytest.fixture
def profile(): return api("profile").RuntimeProfile()

@pytest.fixture
def ledger(profile, clock): return api("budgets").BudgetLedger(profile, clock, 0.0)
