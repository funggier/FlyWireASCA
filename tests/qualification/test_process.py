from pathlib import Path
from types import SimpleNamespace
import subprocess
import pytest
from flywire_asca.qualification.process import CommandSpec, SubprocessRunner


def test_subprocess_uses_argument_array_same_cwd_and_no_shell(monkeypatch, tmp_path):
    calls = []
    def run(argv, **kwargs):
        calls.append((argv, kwargs))
        return SimpleNamespace(returncode=0, stdout=b"out", stderr=b"err")
    monkeypatch.setattr(subprocess, "run", run)
    command = CommandSpec("P04_A003", ("python with space", "script", "--qualify"), tmp_path, None, 5.0)
    evidence = SubprocessRunner().run(command)
    assert len(calls) == 1
    assert calls[0][0] == list(command.argv)
    assert calls[0][1]["shell"] is False
    assert calls[0][1]["cwd"] == tmp_path
    assert calls[0][1]["capture_output"] is True
    assert evidence.stdout == b"out" and evidence.stderr == b"err" and evidence.exit_code == 0


@pytest.mark.parametrize("mode", ["nonzero", "launch", "timeout"])
def test_nonzero_and_launch_error_preserve_diagnostics(monkeypatch, tmp_path, mode):
    def run(*args, **kwargs):
        if mode == "launch":
            raise OSError("cannot launch")
        if mode == "timeout":
            raise subprocess.TimeoutExpired("child", 1, output=b"partial", stderr=b"timeout diagnostic")
        return SimpleNamespace(returncode=7, stdout=b"partial", stderr=b"diagnostic")
    monkeypatch.setattr(subprocess, "run", run)
    result = SubprocessRunner().run(CommandSpec("P04_A003", ("python", "child"), tmp_path, None, 1.0))
    assert result.exit_code != 0
    assert result.execution_error or result.stderr
    if mode != "launch":
        assert result.stdout == b"partial"


def test_physical_process_has_no_new_deadline(monkeypatch, tmp_path):
    seen = []
    def run(*args, **kwargs):
        seen.append(kwargs["timeout"])
        return SimpleNamespace(returncode=0, stdout=b"{}", stderr=b"")
    monkeypatch.setattr(subprocess, "run", run)
    physical_command = CommandSpec("H01_A004", ("python", "child"), tmp_path, tmp_path/"output.json", None)
    assert physical_command.timeout_seconds is None
    SubprocessRunner().run(physical_command)
    assert seen == [None]
