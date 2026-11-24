import tomllib
from pathlib import Path

import pytest
from smugback.cli import main

PYPROJECT = Path(__file__).parent.parent / "pyproject.toml"


def test_cr0002_ac1_prints_version(capsys):
    version = tomllib.loads(PYPROJECT.read_text())["project"]["version"]

    with pytest.raises(SystemExit) as exit_info:
        main(["--version"])

    assert exit_info.value.code == 0
    assert version in capsys.readouterr().out


def test_cr0002_ac2_help_exits_cleanly(capsys):
    with pytest.raises(SystemExit) as exit_info:
        main(["--help"])

    assert exit_info.value.code == 0
    out = capsys.readouterr().out
    assert "usage: smugback" in out
