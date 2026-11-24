# CR-0002: Set up SmugBack and its Python toolchain

| Field         | Value                                                     |
|---------------|-----------------------------------------------------------|
| Status        | Approved                                                  |
| Author        | Claude, for sam-tmts                                      |
| Created       | 2026-11-23                                                |
| Semver impact | minor: first installable package with a working command   |

## Why

SmugBack starts from the template. This CR makes the repository SmugBack's own and
sets up a Python toolchain, so that later CRs go straight to features with tests and
CI already in place.

## Scope

**In:**

- Template placeholders replaced: project name and notes in `CLAUDE.md`, owner in
  `CODEOWNERS`, `SECURITY.md` and `LICENSE`, and a fresh `CHANGELOG.md`.
- README describing SmugBack, its agreed scope and what is out of scope.
- Python package `smugback` (src layout) managed with uv, with a lockfile.
- A `smugback` command (argparse, no extra dependency) supporting `--version`
  and `--help`.
- Dev tools: pytest, and ruff for lint and format.
- One "run everything" command for tests, lint and format check, run by CI on
  every PR.
- Sandbox allowlist: the package hosts uv needs, and nothing else.
- First sections of `docs/architecture.md` (system context), `docs/test-plan.md`
  and `docs/dependencies.md`.

**Out:** SmugMug sign-in and album listing (CR-0003); threat model details for
the token (CR-0003); any SmugMug host on the sandbox allowlist (real runs happen
in the owner's own terminal, never in the sandbox).

## Design notes

- uv for Python and packages: one tool, a lockfile, and fast. pytest and ruff are
  common practice and dev-only.
- argparse rather than a CLI library: enough for a few subcommands, no dependency.
- The plan confirms which hosts uv needs (PyPI, and possibly GitHub's release
  download host if uv installs Python itself) and the form of the single command
  (for example `make check`).
- CI actions are pinned by commit SHA, as the existing pinning check requires.

## Acceptance criteria

- [ ] AC1: `uv run smugback --version` prints the version from `pyproject.toml`.
  *Verified by:* `test_cr0002_ac1_prints_version`.
- [ ] AC2: `uv run smugback --help` lists usage and exits 0.
  *Verified by:* `test_cr0002_ac2_help_exits_cleanly`.
- [ ] AC3: One command runs tests, lint and format check, and fails if any of
  them fails. *Verified by:* manual check in `docs/test-plan.md`.
- [ ] AC4: CI runs that command on every PR, and this PR passes it.
  *Verified by:* the new CI job.
- [ ] AC5: The sandbox allowlist adds only the package hosts uv needs, and no
  SmugMug host. *Verified by:* manual check of `.claude/settings.json`.
- [ ] AC6: No template placeholders remain in `CLAUDE.md`, `README.md`,
  `CODEOWNERS`, `SECURITY.md` or `LICENSE`. *Verified by:* manual check.
- [ ] AC7: Every new dependency is in `docs/dependencies.md`, and `uv.lock` is
  committed. *Verified by:* manual check.

## Constraints and risks

- Touches protected paths: `.claude/settings.json` (allowlist) and
  `.github/workflows/ci.yml` (new job). This CR explicitly covers both.
- No real credentials of any kind.

## Approval log

| Gate | Date | By | Notes |
|------|------|----|-------|
| CR approved | 2026-11-23 | sam-tmts | |
| Plan approved | 2026-11-24 | sam-tmts | Plan in the PR description |
| PR merged | | | |
| Released | | | |
