"""Explicit one-shot subprocess execution with byte diagnostics."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
import math
from pathlib import Path
import subprocess
from typing import Protocol
from .records import QualificationError


@dataclass(frozen=True)
class CommandSpec:
    gate_id: str
    argv: tuple[str, ...]
    cwd: Path
    output_path: Path | None
    timeout_seconds: float | None

    def __post_init__(self):
        if type(self.gate_id) is not str or not self.argv or not all(type(a) is str for a in self.argv):
            raise QualificationError("EVIDENCE_INVALID", "Invalid command argument array")
        object.__setattr__(self, "argv", tuple(self.argv))
        if not isinstance(self.cwd, Path) or self.output_path is not None and not isinstance(self.output_path, Path):
            raise QualificationError("EVIDENCE_INVALID", "Command paths must be Path objects")
        timeout = self.timeout_seconds
        if timeout is not None and (type(timeout) not in (float, int) or not math.isfinite(timeout) or timeout <= 0):
            raise QualificationError("EVIDENCE_INVALID", "Invalid process deadline")
        if self.gate_id.startswith("H") and timeout is not None:
            raise QualificationError("EVIDENCE_INVALID", "Physical process cannot add a deadline")


@dataclass(frozen=True)
class ProcessEvidence:
    command: CommandSpec
    started_at: str
    finished_at: str
    exit_code: int | None
    stdout: bytes
    stderr: bytes
    execution_error: str | None


class ProcessRunner(Protocol):
    def run(self, command: CommandSpec) -> ProcessEvidence: ...


def _now():
    return datetime.now(timezone.utc).isoformat()


class SubprocessRunner:
    def run(self, command):
        started = _now()
        exit_code = None
        stdout = stderr = b""
        error = None
        try:
            completed = subprocess.run(list(command.argv), cwd=command.cwd, shell=False,
                capture_output=True, text=False, timeout=command.timeout_seconds, check=False)
            exit_code, stdout, stderr = completed.returncode, completed.stdout, completed.stderr
        except subprocess.TimeoutExpired as exc:
            stdout, stderr = exc.stdout or b"", exc.stderr or b""
            error = f"TimeoutExpired: {exc}"
        except OSError as exc:
            error = f"{type(exc).__name__}: {exc}"
        return ProcessEvidence(command, started, _now(), exit_code, stdout, stderr, error)
