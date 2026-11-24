import subprocess
import sys
import tomllib
from pathlib import Path

import pytest

from smugback.cli import main

PYPROJECT = Path(__file__).parent.parent / "pyproject.toml"


def test_cr0002_ac1_prints_version():
    version = tomllib.loads(PYPROJECT.read_text())["project"]["version"]
    # The installed command, next to the test run's Python, so the console-script
    # entry in pyproject.toml is tested too
    command = Path(sys.executable).parent / "smugback"

    result = subprocess.run(
        [command, "--version"], capture_output=True, text=True, check=False
    )

    assert result.returncode == 0
    assert result.stdout == f"smugback {version}\n"


def test_cr0002_ac2_help_exits_cleanly(capsys):
    with pytest.raises(SystemExit) as exit_info:
        main(["--help"])

    assert exit_info.value.code == 0
    out = capsys.readouterr().out
    assert "usage: smugback" in out
