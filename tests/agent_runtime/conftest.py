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

@pytest.fixture
def configuration():
    import json
    from pathlib import Path
    root=Path(__file__).resolve().parents[2]/"fixtures/a015/stage-a-v1"
    return api("domain").load_public_configuration(
        json.loads((root/"public.json").read_text(encoding="utf-8")),
        json.loads((root/"profile.json").read_text(encoding="utf-8")))

@pytest.fixture
def registry(configuration):return api("capabilities").CapabilityRegistry.from_public(configuration)

@pytest.fixture
def schemas(configuration):return api("goals").TaskSchemaRegistry.from_public(configuration)
