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
- **uv builds the package itself** (the `uv_build` backend, version-matched to uv), so
  building downloads nothing that `uv.lock` doesn't cover.
- **uv's cache is inside the project** (`.uv-cache/`, set in `pyproject.toml`). The
  sandbox can't write to `~/.cache`, and a sandboxed command can't tamper with the
  shared cache that other projects use. The path is relative to the current folder, so
  uv is run from the project root.
- **pytest** for tests and **ruff** for lint and format, both dev-only.
- **`make check`** is the one command that runs every check, locally and in CI.
- **The standard library first:** argparse for the command line. A new library needs a
  reason and the owner's approval (`docs/dependencies.md`).
- The sandbox allows PyPI (`pypi.org`, `files.pythonhosted.org`) and nothing else for
  Python. Python itself is installed once, outside the sandbox, with
  `uv python install`.

## Consequences

- One tool to install (uv) besides git and Claude Code; setup is fast.
- This project's `.venv/` and `.uv-cache/` are writable from the sandbox and
  git-ignored, so the owner's terminal shouldn't run SmugBack with real credentials
  from them (see the threat model).
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
  affect what other projects install.
- **hatchling as build backend:** common, but downloaded unpinned on every build;
  `uv_build` needs nothing extra.
