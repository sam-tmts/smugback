# Dependency register

Every dependency, including build tools and GitHub Actions, has an entry here. A new
dependency is part of a CR and needs the owner's approval; the entry is what gets
reviewed. Exact versions are pinned in the files named, not here.

Each entry records: **purpose**, **where it's pinned**, **alternatives considered**,
**licence** and **maintenance health**.

SmugBack's runtime dependencies are `keyring` and `oauthlib`; every other entry is a
development, build or CI tool. The toolchain choice is ADR-0005.

## keyring

- **Purpose:** reads and writes SmugBack's credentials in the OS credential store
  (ADR-0003).
- **Pinned in:** `uv.lock`, with its own dependencies on macOS: `jaraco.classes`,
  `jaraco.context`, `jaraco.functools` and `more-itertools` (and, on other platforms
  only, `SecretStorage`, `jeepney` or `pywin32-ctypes`).
- **Alternatives:** calling macOS's `security` command directly (macOS only, and
  secrets on command lines).
- **Licence:** MIT. **Health:** the standard Python credential-store library, from the
  jaraco project; active.

## oauthlib

- **Purpose:** signs SmugMug API requests with OAuth 1.0a (ADR-0006).
- **Pinned in:** `uv.lock`; no dependencies of its own.
- **Alternatives:** `requests-oauthlib` (adds `requests` and its dependencies); our own
  signing code (security-sensitive).
- **Licence:** BSD-3-Clause. **Health:** widely used (underneath `requests-oauthlib`);
  active.

## uv

- **Purpose:** installs Python and packages, manages the virtual environment and
  lockfile.
- **Pinned in:** `uv.lock` records the packages; CI pins uv itself in
  `.github/workflows/ci.yml` (`version` input), which Dependabot doesn't update, so it
  is bumped by hand. Developers install uv themselves.
- **Alternatives:** pip and venv; Poetry (see ADR-0005).
- **Licence:** MIT or Apache-2.0. **Health:** Astral; very active, widely adopted.

## pytest

- **Purpose:** runs the tests (dev only).
- **Pinned in:** `uv.lock`, with its own dependencies `iniconfig`, `packaging`,
  `pluggy`, `pygments` and, on Windows only, `colorama`.
- **Alternatives:** `unittest` in the standard library (more boilerplate, weaker
  failure output).
- **Licence:** MIT. **Health:** the standard Python test runner; active.

## ruff

- **Purpose:** lint and format checks (dev only).
- **Pinned in:** `uv.lock`.
- **Alternatives:** flake8, isort and black together (three tools for one job).
- **Licence:** MIT. **Health:** Astral; very active, widely adopted.

## `uv_build`

- **Purpose:** build backend that turns the source into an installable package.
- **Pinned in:** `[build-system]` in `pyproject.toml`, to the same minor version as uv,
  which then builds with its own copy and downloads nothing.
- **Alternatives:** hatchling or setuptools (separate downloads, unpinned by the lock).
- **Licence:** MIT or Apache-2.0. **Health:** part of uv; very active.

## `astral-sh/setup-uv`

- **Purpose:** installs uv in CI.
- **Pinned in:** `.github/workflows/ci.yml` (full commit SHA, tag in a comment).
- **Alternatives:** installing uv with a `curl` script step (no pinning by SHA).
- **Licence:** MIT. **Health:** Astral's official action; active.

## gitleaks

- **Purpose:** secret scanning in CI.
- **Pinned in:** `.github/workflows/ci.yml` (exact version and SHA-256 checksum of the
  release archive).
- **Alternatives:** GitHub secret scanning alone (covers fewer secret formats);
  `trufflehog` (heavier).
- **Licence:** MIT. **Health:** widely used; actively maintained.

## `actions/checkout`

- **Purpose:** check out the repository in CI.
- **Pinned in:** `.github/workflows/ci.yml` (full commit SHA, tag in a comment).
- **Alternatives:** none; it is GitHub's own action.
- **Licence:** MIT. **Health:** maintained by GitHub.

## `DavidAnson/markdownlint-cli2-action`

- **Purpose:** lint the Markdown documentation in CI.
- **Pinned in:** `.github/workflows/ci.yml` (full commit SHA, tag in a comment).
- **Alternatives:** running `markdownlint-cli2` through npm in a script step.
- **Licence:** MIT. **Health:** maintained by the author of markdownlint; active.
