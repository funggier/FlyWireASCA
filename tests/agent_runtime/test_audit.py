import importlib.util
from pathlib import Path
import pytest

ROOT=Path(__file__).resolve().parents[2]
def audit(root):
    path=ROOT/"scripts/audit_agent_runtime_contract.py"
    assert path.exists(), "A015 audit is absent"
    spec=importlib.util.spec_from_file_location("a015_audit_tests",path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module.audit_agent_runtime_contract(root)

def inject(root,name,source):
    p=root/"src"/name;p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(source,encoding="utf-8")

@pytest.mark.parametrize("source",[
    "from project_asca.evaluation.oracle import expected\n",
    "from flywire_asca.integrated_loop.controller import run_cognitive_loop\n",
    "from flywire_asca.structural_routing.benchmark import build_fixture\n",
    "import subprocess\n",
    "import flywire_llm\n",
    "eval(user_text)\n",
    "open(user_text)\n",
    "__import__('project_asca.evaluation.oracle')\n",
])
def test_runtime_rejects_oracle_or_external_dispatch(tmp_path,source):
    inject(tmp_path,"project_asca/agent_runtime/context.py",source)
    assert audit(tmp_path)

def test_legacy_reverse_dependency_is_rejected(tmp_path):
    inject(tmp_path,"flywire_asca/model/bad.py","from project_asca.agent_runtime import AgentRequest\n")
    assert any("reverse" in e for e in audit(tmp_path))

def test_leaf_adapter_allowed_but_builder_binding_forbidden(tmp_path):
    name="project_asca/agent_runtime/adapters/model.py"
    inject(tmp_path,name,"from flywire_asca.model.contracts import ModelRequest\n")
    assert audit(tmp_path)==[]
    inject(tmp_path,name,"from flywire_asca.model import build_frozen_fixture\n")
    assert audit(tmp_path)

def test_relative_cycle_and_undeclared_unit_edge(tmp_path):
    inject(tmp_path,"project_asca/agent_runtime/values.py","from . import control\n")
    inject(tmp_path,"project_asca/agent_runtime/control.py","from . import values\n")
    errors=audit(tmp_path)
    assert any("cycle" in e for e in errors)
    assert any("undeclared" in e for e in errors)

def test_legacy_initializer_benchmark_import_is_preserved(tmp_path):
    inject(tmp_path,"flywire_asca/model/__init__.py","from .benchmark import build_fixture\n")
    inject(tmp_path,"project_asca/agent_runtime/adapters/model.py",
           "from flywire_asca.model.contracts import ModelRequest\n")
    assert audit(tmp_path)==[]

@pytest.mark.parametrize("name,source",[
 ("project_asca/__init__.py","from .evaluation import oracle\n"),
 ("project_asca/agent_runtime/context.py","from project_asca import evaluation\n"),
 ("project_asca/agent_runtime/adapters/routing.py","from flywire_asca.structural_routing import EXPECTED_A014_CASE_IDS as permitted\n"),
 ("project_asca/agent_runtime/capabilities.py","from pathlib import Path\nPath(user_input).write_text('effect')\n"),
])
def test_initializer_alias_and_path_effects_are_rejected(tmp_path,name,source):
    inject(tmp_path,name,source)
    assert audit(tmp_path), "All namespace entry points and aliases must retain the boundary"
