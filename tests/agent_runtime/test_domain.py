import json
from pathlib import Path
import pytest
from .conftest import api

FIXTURE=Path(__file__).resolve().parents[2]/"fixtures/a015/stage-a-v1"

def public():
    return json.loads((FIXTURE/"public.json").read_text(encoding="utf-8"))

def profile():
    return json.loads((FIXTURE/"profile.json").read_text(encoding="utf-8"))

def test_public_configuration_is_immutable_and_fresh_state_is_independent():
    d=api("domain");p=public();c=d.load_public_configuration(p,profile())
    p["initial"]["by_kind"]["tray"]["quantity"]=999
    assert c.initial_state.values["T1"]["quantity"]==0
    with pytest.raises(TypeError):c.initial_state.values["T1"]["quantity"]=999
    assert len(c.knowledge.memories)+len(c.catalog.descriptors)<=256

def test_unknown_public_control_or_identity_corruption_is_rejected():
    d=api("domain");p=public();p["oracle"]={}
    with pytest.raises(ValueError):d.load_public_configuration(p,profile())
    p=public();p["entities"].append(p["entities"][0])
    with pytest.raises(ValueError):d.load_public_configuration(p,profile())
