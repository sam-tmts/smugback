# ADR-0005: Python with uv, pytest, ruff and `make check`

| Field      | Value                    |
|------------|--------------------------|
| Status     | Accepted                 |
| Date       | 2026-11-24               |
| Deciders   | Samuel Taylor (sam-tmts) |
| Related CR | CR-0002                  |

## Context

SmugBack is a small command-line tool. It needs a language toolchain that is quick to
set up, reproducible, works inside Claude Code's sandbox (ADR-0004), and adds as few
dependencies as possible.

## Decision

- **Python 3.12 or later**, src layout, with the version set in `.python-version`.
- **uv** manages Python, packages and the virtual environment. `uv.lock` is committed
  and every check runs with `--locked`, so CI and every developer use the same
  versions.
- **uv's cache is inside the project** (`.uv-cache/`, set in `pyproject.toml`). The
  sandbox can't write to `~/.cache`, and a project cache can't be tampered with by one
  project and reused by another, or by the owner's unsandboxed terminal.
- **pytest** for tests and **ruff** for lint and format, both dev-only.
- **`make check`** is the one command that runs every check, locally and in CI.
- **The standard library first:** argparse for the command line. A new library needs a
  reason and the owner's approval (`docs/dependencies.md`).
- The sandbox allows PyPI (`pypi.org`, `files.pythonhosted.org`) and nothing else for
  Python. Python itself is installed once, outside the sandbox, with
  `uv python install`.

## Consequences

- One tool to install (uv) besides git and Claude Code; setup is fast.
- uv must be run from the project root, because the cache path is relative.
- Each project downloads its own packages instead of sharing a cache: a little more
  disk and network, in exchange for isolation.
- Make is assumed present; it is on macOS (with the command-line tools) and on CI.

## Alternatives considered

- **pip and venv:** in the standard library, but no lockfile without extra tools, and
  slower.
- **Poetry:** a lockfile too, but slower and heavier than uv for the same job.
- **A CLI library such as Click or Typer:** nicer for many commands, but a dependency
  argparse makes unnecessary for a few subcommands.
- **A script or tox/nox instead of make:** make is more widely known and needs nothing
  installed.
- **The shared uv cache, opened to the sandbox:** simpler, but lets a sandboxed command
  affect what the owner's terminal and other projects install.
