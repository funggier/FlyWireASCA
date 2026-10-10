from pathlib import Path
import re
import sys
from typing import NamedTuple
from urllib.parse import unquote


_WINDOWS_ABSOLUTE = re.compile(r"(?<![A-Za-z0-9_])[A-Za-z]:[\\/]")
_POSIX_USER_ABSOLUTE = re.compile(r"(?<![A-Za-z0-9_])/(?:home|Users)/")
_ROADMAP_ROW = re.compile(
    r"^\|\s*(A\d{3})\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*$"
)
_CURRENT_FIELD = re.compile(r"^(Current task|Status|GitHub Issue):\s*(.+?)\s*$")
_TASK_HEADING = re.compile(r"^#\s+((?:A\d{3})|(?:PRE-A\d{3}))\b")
_TASK_FILENAME_ID = re.compile(r"^((?:A\d{3})|(?:PRE-A\d{3}))-")
_NUMERIC_ISSUE = re.compile(r"^#\d+(?:\b|\s|$)")
_MARKDOWN_LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
_ALLOWED_STATUSES = frozenset({"PLANNED", "ACTIVE", "BLOCKED", "DONE"})


class RoadmapEntry(NamedTuple):
    task_id: str
    milestone: str
    status: str


class CurrentTaskState(NamedTuple):
    task_id: str
    status: str
    github_issue: str


def _parse_roadmap(text: str) -> tuple[RoadmapEntry, ...]:
    entries: list[RoadmapEntry] = []
    for line in text.splitlines():
        match = _ROADMAP_ROW.match(line)
        if match is None:
            continue
        entries.append(
            RoadmapEntry(
                task_id=match.group(1).strip(),
                milestone=match.group(2).strip(),
                status=match.group(3).strip(),
            )
        )
    return tuple(entries)


def _parse_current(text: str) -> CurrentTaskState:
    fields: dict[str, str] = {}
    for line in text.splitlines():
        match = _CURRENT_FIELD.match(line)
        if match is not None:
            name = match.group(1)
            if name in fields:
                raise ValueError(f"duplicate CURRENT.md field {name}")
            fields[name] = match.group(2).strip()
    missing = [name for name in ("Current task", "Status", "GitHub Issue") if name not in fields]
    if missing:
        raise ValueError("CURRENT.md missing fields: " + ", ".join(missing))
    return CurrentTaskState(
        task_id=fields["Current task"],
        status=fields["Status"],
        github_issue=fields["GitHub Issue"],
    )


def _task_files(tasks_root: Path, task_id: str) -> tuple[Path, ...]:
    return tuple(sorted(tasks_root.glob(f"{task_id}-*.md")))


def _task_status(text: str) -> str | None:
    for line in text.splitlines():
        if line.startswith("Status:"):
            return line.split(":", 1)[1].strip()
    return None


def _task_github_issue(text: str) -> str | None:
    for line in text.splitlines():
        if line.startswith("GitHub Issue:"):
            return line.split(":", 1)[1].strip()
    return None


def _numeric_issue(value: str | None) -> str | None:
    if value is None:
        return None
    match = re.match(r"^(#\d+)\b", value)
    return match.group(1) if match is not None else None


def _heading_task_id(text: str) -> str | None:
    first = text.splitlines()[0] if text.splitlines() else ""
    match = _TASK_HEADING.match(first)
    return match.group(1) if match is not None else None


def _filename_task_id(path: Path) -> str | None:
    match = _TASK_FILENAME_ID.match(path.name)
    return match.group(1) if match is not None else None


def _acceptance_section(text: str) -> str | None:
    lines = text.splitlines()
    start: int | None = None
    for index, line in enumerate(lines):
        if line.lower().startswith("## acceptance criter"):
            start = index + 1
            break
    if start is None:
        return None
    end = len(lines)
    for index in range(start, len(lines)):
        if lines[index].startswith("## "):
            end = index
            break
    return "\n".join(lines[start:end])


def _task_structure_errors(path: Path, text: str) -> list[str]:
    errors: list[str] = []
    filename_id = _filename_task_id(path)
    heading_id = _heading_task_id(text)
    if filename_id is None:
        return errors
    if heading_id is None:
        errors.append(f"{path.name} does not start with a task heading ID")
    elif filename_id != heading_id:
        errors.append(
            f"{path.name} filename task ID {filename_id} does not match heading task ID {heading_id}"
        )

    status = _task_status(text)
    if status is None:
        errors.append(f"{path.name} does not contain Status")
        return errors
    if status not in _ALLOWED_STATUSES:
        errors.append(f"{path.name} has invalid task status {status}")

    lower = text.lower()
    for required in ("## goal", "## acceptance criter", "## current action", "## next action"):
        if required not in lower:
            errors.append(f"{path.name} is missing required section {required}")

    if status == "DONE":
        acceptance = _acceptance_section(text)
        if acceptance is None:
            errors.append(f"DONE task {filename_id} is missing Acceptance Criteria")
        elif "- [ ]" in acceptance:
            errors.append(f"DONE task {filename_id} contains unchecked acceptance")

    return errors


def _validate_lifecycle(root: Path) -> list[str]:
    errors: list[str] = []
    tasks_root = root / "docs" / "development" / "tasks"
    roadmap_path = tasks_root / "ROADMAP.md"
    current_path = tasks_root / "CURRENT.md"

    if not roadmap_path.is_file():
        errors.append("docs/development/tasks/ROADMAP.md is missing")
        return errors

    roadmap_text = roadmap_path.read_text(encoding="utf-8")
    for line in roadmap_text.splitlines():
        task_like = re.match(r"^\|\s*(A\d{3})\b", line)
        if task_like is not None and _ROADMAP_ROW.match(line) is None:
            errors.append(
                f"malformed ROADMAP task row {task_like.group(1)}: {line.strip()}"
            )
    entries = _parse_roadmap(roadmap_text)
    if not entries:
        errors.append("ROADMAP.md contains no A-numbered task rows")
        return errors

    seen: set[str] = set()
    numbers: list[int] = []
    by_id: dict[str, RoadmapEntry] = {}
    for entry in entries:
        if entry.task_id in seen:
            errors.append(f"duplicate ROADMAP task ID {entry.task_id}")
        else:
            seen.add(entry.task_id)
            by_id[entry.task_id] = entry
        numbers.append(int(entry.task_id[1:]))
        if entry.status not in _ALLOWED_STATUSES:
            errors.append(
                f"invalid ROADMAP status {entry.status} for {entry.task_id}"
            )
    if numbers != sorted(numbers) or len(numbers) != len(set(numbers)):
        errors.append("ROADMAP A-numbered task IDs must be unique and monotonic")

    for entry in entries:
        files = _task_files(tasks_root, entry.task_id)
        if not files:
            if entry.task_id == "A011" and entry.status == "PLANNED":
                continue
            errors.append(f"{entry.task_id} ROADMAP row has no matching task document")
            continue
        if len(files) != 1:
            errors.append(f"{entry.task_id} has multiple task documents")
            continue
        text = files[0].read_text(encoding="utf-8")
        errors.extend(_task_structure_errors(files[0], text))
        task_status = _task_status(text)
        if task_status != entry.status:
            errors.append(
                f"{entry.task_id} task status {task_status} does not match ROADMAP status {entry.status}"
            )

    if not current_path.is_file():
        errors.append("docs/development/tasks/CURRENT.md is missing")
        return errors
    try:
        current = _parse_current(current_path.read_text(encoding="utf-8"))
    except ValueError as exc:
        errors.append(str(exc))
        return errors

    if current.status not in _ALLOWED_STATUSES:
        errors.append(f"CURRENT.md has invalid status {current.status}")

    if current.status == "PLANNED" and _NUMERIC_ISSUE.match(current.github_issue):
        errors.append("PLANNED current task must not record a numeric GitHub issue")
    if current.status == "ACTIVE" and _numeric_issue(current.github_issue) is None:
        errors.append("ACTIVE current task must record a numeric GitHub issue")

    current_files = _task_files(tasks_root, current.task_id)
    if current.task_id.startswith("PRE-"):
        if len(current_files) != 1:
            errors.append(
                f"{current.task_id} maintenance task document must exist exactly once"
            )
        else:
            current_text = current_files[0].read_text(encoding="utf-8")
            errors.extend(_task_structure_errors(current_files[0], current_text))
            task_status = _task_status(current_text)
            if task_status != current.status:
                errors.append(
                    f"{current.task_id} maintenance task status {task_status} does not match CURRENT status {current.status}"
                )
            task_issue = _numeric_issue(_task_github_issue(current_text))
            if current.status == "ACTIVE":
                if task_issue is None:
                    errors.append("ACTIVE task file must record a numeric GitHub issue")
                current_issue = _numeric_issue(current.github_issue)
                if (
                    current_issue is not None
                    and task_issue is not None
                    and current_issue != task_issue
                ):
                    errors.append(
                        f"CURRENT GitHub Issue {current_issue} does not match task GitHub Issue {task_issue}"
                    )
    elif re.fullmatch(r"A\d{3}", current.task_id):
        entry = by_id.get(current.task_id)
        if entry is None:
            errors.append(f"CURRENT task {current.task_id} is missing from ROADMAP")
        elif current.status != entry.status:
            errors.append(
                f"CURRENT status {current.status} does not match ROADMAP status {entry.status}"
            )
        if len(current_files) == 1 and current.status == "ACTIVE":
            current_text = current_files[0].read_text(encoding="utf-8")
            task_issue = _numeric_issue(_task_github_issue(current_text))
            if task_issue is None:
                errors.append("ACTIVE task file must record a numeric GitHub issue")
            current_issue = _numeric_issue(current.github_issue)
            if (
                current_issue is not None
                and task_issue is not None
                and current_issue != task_issue
            ):
                errors.append(
                    f"CURRENT GitHub Issue {current_issue} does not match task GitHub Issue {task_issue}"
                )
    else:
        errors.append(f"CURRENT task ID {current.task_id} is not A### or PRE-A###")

    return errors


def _validate_markdown_links(root: Path) -> list[str]:
    errors: list[str] = []
    candidates: list[Path] = []
    readme = root / "README.md"
    if readme.is_file():
        candidates.append(readme)
    docs_root = root / "docs"
    if docs_root.is_dir():
        candidates.extend(sorted(docs_root.rglob("*.md")))

    for path in candidates:
        text = path.read_text(encoding="utf-8")
        for raw_target in _MARKDOWN_LINK.findall(text):
            target = raw_target.strip().strip("<>")
            if not target or target.startswith("#"):
                continue
            if re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", target):
                continue
            path_part = unquote(target.split("#", 1)[0])
            if not path_part:
                continue
            if path_part.startswith("/"):
                resolved = root / path_part.lstrip("/")
            else:
                resolved = path.parent / path_part
            if not resolved.exists():
                relative = path.relative_to(root).as_posix()
                errors.append(
                    f"{relative} contains broken relative Markdown link: {raw_target}"
                )
    return errors


def qualify_repository(root: Path) -> list[str]:
    root = Path(root)
    errors: list[str] = []

    license_path = root / "LICENSE"
    if not license_path.is_file():
        errors.append("LICENSE is missing")
    else:
        license_text = license_path.read_text(encoding="utf-8")
        if "Permission is hereby granted, free of charge" not in license_text:
            errors.append("LICENSE does not contain the MIT grant")

    current_path = root / "docs" / "development" / "tasks" / "CURRENT.md"
    if not current_path.is_file():
        errors.append("docs/development/tasks/CURRENT.md is missing")
    else:
        current_text = current_path.read_text(encoding="utf-8")
        if "Current task:" not in current_text or "Status:" not in current_text:
            errors.append("CURRENT.md does not contain a recoverable task pointer")

    readme_path = root / "README.md"
    if not readme_path.is_file():
        errors.append("README.md is missing")
    else:
        readme_text = readme_path.read_text(encoding="utf-8")
        readme_lower = readme_text.lower()
        if "FlyWireLLM" not in readme_text or "independent" not in readme_lower:
            errors.append(
                "README.md must state the FlyWireLLM independence boundary"
            )

    package_root = root / "src" / "flywire_asca"
    if not package_root.is_dir():
        errors.append("src/flywire_asca package directory is missing")
    else:
        for path in sorted(package_root.rglob("*.py")):
            text = path.read_text(encoding="utf-8")
            if _WINDOWS_ABSOLUTE.search(text) or _POSIX_USER_ABSOLUTE.search(text):
                relative = path.relative_to(root).as_posix()
                errors.append(
                    f"{relative} contains an absolute machine-local path"
                )

    if (root / "docs" / "development" / "tasks").is_dir():
        errors.extend(_validate_lifecycle(root))
    errors.extend(_validate_markdown_links(root))

    return errors


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    errors = qualify_repository(root)
    if errors:
        print("repository_qualification=FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    print("repository_qualification=PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())