"""Supplemental dependency/effect audit for both ASCA namespaces."""
from __future__ import annotations
import ast
from pathlib import Path
import sys

EDGES={
 "_root":{"__init__"},
 "values":set(),
 "profile":{"values"},
 "semantics":{"values"},
 "plans":{"values","semantics"},
 "contracts":{"values","semantics"},
 "ports":{"contracts","semantics","plans","values"},
 "budgets":{"contracts","profile","values"},
 "trace":{"values","budgets","profile"},
 "control":{"contracts","values","profile","budgets","trace","ports"},
 "__init__":{"contracts","controller","factory","values","profile"},
 "broker":{"contracts","values","profile","control","budgets","ports"},
 "prompts":{"contracts","values"},
 "domain":{"contracts","values","semantics","plans","profile"},
 "capabilities":{"values","plans","semantics","state","contracts","profile"},
 "state":{"values","semantics","profile"},
 "goals":{"values","semantics","plans","domain"},
 "interpretation":{"values","contracts","semantics","goals","broker","prompts","domain","control"},
 "context":{"values","contracts","semantics","plans","control","broker","ports","prompts","domain"},
 "strategy":{"values","contracts","semantics","plans","capabilities","goals","control","broker","prompts","domain"},
 "execution":{"values","contracts","semantics","plans","capabilities","state","control","ports","strategy"},
 "verification":{"contracts","values","semantics","plans","capabilities","domain"},
 "recovery":{"contracts","values","semantics","plans","control"},
 "rendering":{"values","contracts","semantics","plans","verification"},
 "controller":{"contracts","values","semantics","plans","control","interpretation","goals","context","strategy","execution","verification","recovery","rendering","profile","ports","capabilities"},
 "factory":{"contracts","values","semantics","plans","control","interpretation","goals","context","strategy","execution","verification","recovery","rendering","profile","ports","capabilities","controller","domain"},
}
ADAPTER_CORE={"contracts","values","semantics","plans","profile","ports","control","budgets","trace","broker","capabilities","state","domain"}
LEGACY={"contracts","familiarity","model","embedding","vector_memory","selective_activation","uncertainty_expansion","procedural_memory","relational_activation","structural_routing"}
BANNED_MODULES={"subprocess","shlex","os","ctypes","winreg","flywire_llm","FlyWireLLM","importlib"}
NETWORK_MODULES={"urllib","http","requests","socket","aiohttp","ftplib"}
UNSAFE_NAMES={"eval","exec","compile","__import__","open"}
FORBIDDEN_BINDINGS={"expected_target_ids","expected_answer_ids","EXPECTED_CASE_IDS","EXPECTED_TARGET_IDS"}

def _imports(tree,package):
    for node in ast.walk(tree):
        if isinstance(node,ast.Import):
            for alias in node.names:yield alias.name,alias.name,node
        elif isinstance(node,ast.ImportFrom):
            if node.level:
                parts=package.split(".")
                base=".".join(parts[:len(parts)-node.level+1])
                module=base+("."+node.module if node.module else "")
            else:module=node.module or ""
            for alias in node.names:
                full=module if node.module is not None else module+"."+alias.name
                yield full,alias.name,node

def _type_only_nodes(tree):
    ids=set()
    for node in ast.walk(tree):
        if isinstance(node,ast.If) and ((isinstance(node.test,ast.Name) and node.test.id=="TYPE_CHECKING")
             or (isinstance(node.test,ast.Attribute) and node.test.attr=="TYPE_CHECKING")):
            for body in node.body:
                ids.update(id(n) for n in ast.walk(body))
    return ids

def _cycle_errors(graph):
    errors=[];seen=set();active=[]
    def visit(name):
        if name in active:
            errors.append("runtime dependency cycle: "+" -> ".join(active[active.index(name):]+[name]))
            return
        if name in seen:return
        active.append(name)
        for target in sorted(graph.get(name,set())):visit(target)
        active.pop();seen.add(name)
    for name in sorted(graph):visit(name)
    return errors

def audit_agent_runtime_contract(root:Path)->list[str]:
    root=Path(root)
    errors=[];graph={}
    runtime=root/"src/project_asca/agent_runtime"
    paths=sorted(runtime.rglob("*.py")) if runtime.exists() else []
    initializer=root/"src/project_asca/__init__.py"
    if initializer.exists():paths.append(initializer)
    for path in paths:
        is_root=path==initializer
        relative=Path("_root.py") if is_root else path.relative_to(runtime)
        parts=relative.with_suffix("").parts
        unit=".".join(parts)
        adapter=parts[0]=="adapters"
        infrastructure=adapter and parts[-1] in {"transport","token_bounds","model"}
        package="project_asca" if is_root else "project_asca.agent_runtime"+("."+".".join(parts[:-1]) if len(parts)>1 else "")
        try:tree=ast.parse(path.read_text(encoding="utf-8-sig"))
        except SyntaxError as exc:
            errors.append(f"{relative}: syntax error {exc}");continue
        type_only=_type_only_nodes(tree)
        graph.setdefault(unit,set())
        for module,binding,node in _imports(tree,package):
            top=module.split(".")[0]
            if top in BANNED_MODULES:errors.append(f"{relative}: forbidden module {module}")
            if (top in NETWORK_MODULES or top=="pathlib") and not infrastructure:errors.append(f"{relative}: external transport dependency")
            if module.startswith("project_asca.evaluation") or (module=="project_asca" and binding=="evaluation"):
                errors.append(f"{relative}: evaluator/oracle dependency")
            if module.startswith("flywire_asca"):
                pieces=module.split(".")
                legacy=pieces[1] if len(pieces)>1 else ""
                forbidden=any("benchmark" in p or "fixture" in p for p in pieces)
                if not adapter or legacy not in LEGACY or forbidden:
                    errors.append(f"{relative}: forbidden legacy dependency {module}")
                if binding in FORBIDDEN_BINDINGS or binding.startswith("EXPECTED_") or ("build" in binding and "fixture" in binding):
                    errors.append(f"{relative}: forbidden fixture binding {binding}")
            if module=="project_asca.agent_runtime" or module.startswith("project_asca.agent_runtime."):
                target="__init__" if module=="project_asca.agent_runtime" else module[len("project_asca.agent_runtime."):]
                if target==unit:continue
                target_unit=target.split(".")[0]
                allowed=ADAPTER_CORE if adapter else EDGES.get(unit,set())
                if target_unit=="adapters":
                    if unit!="factory" and not adapter:errors.append(f"{relative}: concrete adapter outside composition root")
                elif target_unit not in allowed:
                    errors.append(f"{relative}: undeclared unit dependency {unit} -> {target}")
                if id(node) not in type_only:graph[unit].add(target)
        for node in ast.walk(tree):
            if isinstance(node,ast.Call):
                name=node.func.id if isinstance(node.func,ast.Name) else None
                if name in UNSAFE_NAMES and not (name=="open" and infrastructure):
                    errors.append(f"{relative}: forbidden dispatch {name}")
                if isinstance(node.func,ast.Attribute) and (node.func.attr in {"system","popen","run_command","create_subprocess_exec","import_module"} or (not infrastructure and node.func.attr in {"open","write_text","write_bytes","unlink","rename","mkdir","rmdir","read_text","read_bytes"})):
                    errors.append(f"{relative}: forbidden dynamic dispatch {node.func.attr}")
                if isinstance(node.func,ast.Name) and node.func.id=="getattr":
                    if any(isinstance(a,ast.Constant) and isinstance(a.value,str) and (a.value in FORBIDDEN_BINDINGS or a.value.startswith("EXPECTED_")) for a in node.args):
                        errors.append(f"{relative}: forbidden expected-label introspection")
            if isinstance(node,ast.Attribute) and (node.attr in FORBIDDEN_BINDINGS or node.attr.startswith("EXPECTED_")):
                errors.append(f"{relative}: forbidden expected-label access")
        if not adapter and unit not in EDGES:errors.append(f"{relative}: undeclared runtime unit")
    legacy=root/"src/flywire_asca"
    for path in sorted(legacy.rglob("*.py")) if legacy.exists() else ():
        try:tree=ast.parse(path.read_text(encoding="utf-8-sig"))
        except SyntaxError:continue
        for module,_,_ in _imports(tree,"flywire_asca"):
            if module.startswith("project_asca"):errors.append(f"{path.name}: forbidden legacy reverse dependency")
    errors.extend(_cycle_errors(graph))
    return sorted(set(errors))

def main():
    errors=audit_agent_runtime_contract(Path(__file__).resolve().parents[1])
    print("agent_runtime_contract_audit="+("FAIL" if errors else "PASS"))
    for error in errors:print(error)
    return bool(errors)

if __name__=="__main__":sys.exit(main())
