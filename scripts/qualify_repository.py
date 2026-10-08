from __future__ import annotations

from pathlib import Path
import re
import sys


_WINDOWS_ABSOLUTE = re.compile(r"(?<![A-Za-z0-9_])[A-Za-z]:[\\/]")
_POSIX_USER_ABSOLUTE = re.compile(r"(?<![A-Za-z0-9_])/(?:home|Users)/")


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
