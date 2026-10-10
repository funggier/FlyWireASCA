from __future__ import annotations

import ast
from pathlib import Path
import sys
import tomllib


EXPECTED_RETRIEVAL_STATES = (
    "UNFAMILIAR",
    "FAMILIAR",
    "KNOWN_BUT_NOT_RECALLED",
    "PARTIAL_RECALL",
    "RECALLED",
    "CONFLICTING_RECALL",
    "INSUFFICIENT_EVIDENCE",
)

EXPECTED_BASELINE_MODES = (
    "dense_direct",
    "asca_selective",
    "asca_no_surprise_expansion",
    "asca_no_familiarity",
)

ALLOWED_PACKAGE_DEPENDENCIES: dict[str, frozenset[str]] = {
    "contracts": frozenset(),
    "qualification": frozenset({"contracts"}),
    "model": frozenset({"contracts"}),
    "embedding": frozenset({"contracts"}),
    "familiarity": frozenset({"contracts"}),
    "procedural_memory": frozenset({"contracts"}),
    "vector_memory": frozenset({"contracts", "embedding"}),
    "selective_activation": frozenset({"contracts", "vector_memory"}),
    "uncertainty_expansion": frozenset({"contracts", "selective_activation"}),
    "integrated_loop": frozenset(
        {
            "contracts",
            "embedding",
            "familiarity",
            "model",
            "procedural_memory",
            "selective_activation",
            "uncertainty_expansion",
            "vector_memory",
        }
    ),
    "baseline_comparison": frozenset(
        {
            "contracts",
            "embedding",
            "familiarity",
            "integrated_loop",
            "model",
            "procedural_memory",
            "selective_activation",
            "uncertainty_expansion",
            "vector_memory",
        }
    ),
}


def _parse(path: Path) -> ast.Module:
    return ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


def _enum_values(path: Path, class_name: str) -> tuple[str, ...]:
    tree = _parse(path)
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            values: list[str] = []
            for statement in node.body:
                if (
                    isinstance(statement, ast.Assign)
                    and len(statement.targets) == 1
                    and isinstance(statement.targets[0], ast.Name)
                    and isinstance(statement.value, ast.Constant)
                    and isinstance(statement.value.value, str)
                ):
                    values.append(statement.value.value)
            return tuple(values)
    return ()


def _assigned_string(path: Path, name: str) -> str | None:
    tree = _parse(path)
    for node in tree.body:
        if (
            isinstance(node, ast.Assign)
            and len(node.targets) == 1
            and isinstance(node.targets[0], ast.Name)
            and node.targets[0].id == name
            and isinstance(node.value, ast.Constant)
            and isinstance(node.value.value, str)
        ):
            return node.value.value
    return None


def _class_annotation_names(path: Path, class_name: str) -> set[str]:
    tree = _parse(path)
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            return {
                statement.target.id
                for statement in node.body
                if isinstance(statement, ast.AnnAssign)
                and isinstance(statement.target, ast.Name)
            }
    return set()


def _flywirellm_imports(source_root: Path) -> list[str]:
    findings: list[str] = []
    for path in sorted(source_root.rglob("*.py")):
        try:
            tree = _parse(path)
        except SyntaxError as exc:
            findings.append(f"{path}: cannot parse source: {exc}")
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name == "flywire_llm" or alias.name.startswith("flywire_llm."):
                        findings.append(str(path))
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                if module == "flywire_llm" or module.startswith("flywire_llm."):
                    findings.append(str(path))
    return findings


def _source_package(source_root: Path, path: Path) -> str | None:
    relative = path.relative_to(source_root)
    if len(relative.parts) < 2:
        return None
    package = relative.parts[0]
    return package if package in ALLOWED_PACKAGE_DEPENDENCIES else None


def _absolute_dependency(module: str) -> str | None:
    if not module.startswith("flywire_asca."):
        return None
    parts = module.split(".")
    if len(parts) < 2:
        return None
    package = parts[1]
    return package if package in ALLOWED_PACKAGE_DEPENDENCIES else None


def _package_dependencies(source_root: Path) -> dict[str, set[str]]:
    graph = {name: set() for name in ALLOWED_PACKAGE_DEPENDENCIES}
    for path in sorted(source_root.rglob("*.py")):
        source_package = _source_package(source_root, path)
        if source_package is None:
            continue
        tree = _parse(path)
        for node in ast.walk(tree):
            dependencies: list[str] = []
            if isinstance(node, ast.Import):
                for alias in node.names:
                    dependency = _absolute_dependency(alias.name)
                    if dependency is not None:
                        dependencies.append(dependency)
            elif isinstance(node, ast.ImportFrom):
                if node.level == 0:
                    dependency = _absolute_dependency(node.module or "")
                    if dependency is not None:
                        dependencies.append(dependency)
                elif node.level >= 2:
                    if node.module:
                        candidates = (node.module.split(".", 1)[0],)
                    else:
                        candidates = tuple(
                            alias.name.split(".", 1)[0] for alias in node.names
                        )
                    for dependency in candidates:
                        if dependency in ALLOWED_PACKAGE_DEPENDENCIES:
                            dependencies.append(dependency)
            for dependency in dependencies:
                if dependency != source_package:
                    graph[source_package].add(dependency)
    return graph


def _cycle_paths(graph: dict[str, set[str]]) -> tuple[tuple[str, ...], ...]:
    state: dict[str, int] = {name: 0 for name in graph}
    stack: list[str] = []
    cycles: set[tuple[str, ...]] = set()

    def canonical(cycle: list[str]) -> tuple[str, ...]:
        body = cycle[:-1]
        rotations = [
            tuple(body[index:] + body[:index])
            for index in range(len(body))
        ]
        best = min(rotations)
        return best + (best[0],)

    def visit(node: str) -> None:
        state[node] = 1
        stack.append(node)
        for neighbor in sorted(graph[node]):
            if neighbor not in graph:
                continue
            if state[neighbor] == 0:
                visit(neighbor)
            elif state[neighbor] == 1:
                index = stack.index(neighbor)
                cycles.add(canonical(stack[index:] + [neighbor]))
        stack.pop()
        state[node] = 2

    for node in sorted(graph):
        if state[node] == 0:
            visit(node)
    return tuple(sorted(cycles))


def _dependency_errors(graph: dict[str, set[str]]) -> list[str]:
    errors: list[str] = []
    for source in sorted(graph):
        allowed = ALLOWED_PACKAGE_DEPENDENCIES[source]
        for target in sorted(graph[source]):
            if target not in allowed:
                errors.append(
                    f"undeclared package dependency {source} -> {target}"
                )
    for cycle in _cycle_paths(graph):
        errors.append("package dependency cycle: " + " -> ".join(cycle))
    return errors


def audit_architecture_contract(root: Path) -> list[str]:
    root = Path(root)
    errors: list[str] = []

    pyproject_path = root / "pyproject.toml"
    if not pyproject_path.is_file():
        errors.append("pyproject.toml is missing")
    else:
        project = tomllib.loads(pyproject_path.read_text(encoding="utf-8")).get("project", {})
        dependencies = project.get("dependencies", [])
        if dependencies:
            errors.append(
                "A002 contract must not add mandatory runtime dependencies: "
                + ", ".join(str(item) for item in dependencies)
            )

    source_root = root / "src" / "flywire_asca"
    imports = _flywirellm_imports(source_root) if source_root.is_dir() else []
    if imports:
        errors.append(
            "FlyWireLLM import is not allowed in A002 source: "
            + ", ".join(imports)
        )
    if source_root.is_dir():
        try:
            graph = _package_dependencies(source_root)
        except SyntaxError as exc:
            errors.append(f"cannot parse source for dependency audit: {exc}")
        else:
            errors.extend(_dependency_errors(graph))

    contracts_root = source_root / "contracts"
    init_path = contracts_root / "__init__.py"
    enums_path = contracts_root / "enums.py"
    benchmark_path = contracts_root / "benchmark.py"
    memory_path = contracts_root / "memory.py"

    if not init_path.is_file() or _assigned_string(init_path, "CONTRACT_VERSION") != "0.1":
        errors.append("contracts CONTRACT_VERSION must be exactly 0.1")

    if not enums_path.is_file() or _enum_values(enums_path, "RetrievalState") != EXPECTED_RETRIEVAL_STATES:
        errors.append("RetrievalState vocabulary does not match ASCA contract v0.1")

    if not benchmark_path.is_file() or _enum_values(benchmark_path, "BaselineMode") != EXPECTED_BASELINE_MODES:
        errors.append("BaselineMode vocabulary does not match ASCA contract v0.1")

    association_fields = (
        _class_annotation_names(memory_path, "AssociationEdge")
        if memory_path.is_file()
        else set()
    )
    if not {"activation_weight", "proposition_confidence"} <= association_fields:
        errors.append(
            "AssociationEdge must keep activation_weight and proposition_confidence separate"
        )

    doc_path = root / "docs" / "architecture" / "ASCA-CONTRACT-v0.1.md"
    if not doc_path.is_file():
        errors.append("ASCA contract document v0.1 is missing")
    else:
        text = doc_path.read_text(encoding="utf-8")
        if "ASCA Contract v0.1" not in text:
            errors.append("contract document does not identify ASCA Contract v0.1")
        if "FlyWireLLM" not in text:
            errors.append("contract document must state the FlyWireLLM boundary")

    return errors


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    errors = audit_architecture_contract(root)
    if errors:
        print("architecture_contract_audit=FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    print("architecture_contract_audit=PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())