# SmugBack

A command-line tool that backs up a SmugMug account's photos and videos to a folder on
your computer.

> **Status:** early. The `smugback` command installs and runs, but can't back anything
> up yet. Signing in to SmugMug and listing albums come next (CR-0003).

## Scope

**SmugBack does:** download every photo and video in your SmugMug account, keeping the
album structure, and pick up where it left off if a backup is interrupted.

**SmugBack doesn't:** upload, edit or delete anything on SmugMug, or sync changes back.
It only ever reads from your account.

## Quick start

You need [uv](https://docs.astral.sh/uv/). From a clone of this repository:

```sh
uv run smugback --help
```

## Working on SmugBack

SmugBack is built with coding agents, and every change follows a change request.
[`CLAUDE.md`](CLAUDE.md) has the principles, workflow and commands. In short:

- **Change requests drive every change**
  ([ADR-0001](docs/adr/ADR-0001-change-requests-in-repo.md)).
- **Tests come first**, and every criterion is traceable to a test or a manual check
  ([test plan](docs/test-plan.md)). `make check` runs every automated check.
- **Releases follow semver**, with a hand-written changelog
  ([ADR-0002](docs/adr/ADR-0002-semver-and-changelog.md)).
- **Real secrets never enter the repository**
  ([ADR-0003](docs/adr/ADR-0003-secrets-outside-repository.md)).
- **Agents work in Claude Code's sandbox**, in a dedicated developer account
  ([ADR-0004](docs/adr/ADR-0004-sandboxed-development.md)).
- **Python with uv, pytest and ruff**
  ([ADR-0005](docs/adr/ADR-0005-python-toolchain.md)).

### One-time setup on your computer

1. **Use a dedicated developer account**, with no access to your personal files, for
   all development.
2. **Install [Claude Code](https://code.claude.com/docs/en/overview)** in that account.
   Claude's commands run in a sandbox; `git push` is the only exception, and Claude asks
   before every push ([details](docs/adr/ADR-0004-sandboxed-development.md)).
3. **Install git** (on macOS: `xcode-select --install`), and create a
   [fine-grained personal access token](https://github.com/settings/personal-access-tokens)
   limited to this repository, with a short expiry and only Contents and Workflows
   (read and write; GitHub needs Workflows for any push that changes CI).
   Push once from an ordinary terminal and paste the token when asked for a password;
   git stores it for later pushes, including Claude's.
4. **Install [uv](https://docs.astral.sh/uv/getting-started/installation/)**.
5. **Clone over HTTPS**, and in an ordinary terminal run `uv python install` in the
   folder: the sandbox can reach PyPI but not uv's Python downloads. Then start
   `claude` there, and run `/sandbox` to confirm the sandbox is on.

### Repository settings

GitHub doesn't copy settings, so these are applied by hand:

- **Rules → Rulesets:** protect `main`: require a pull request, block force pushes,
  restrict deletions, and require these status checks: `Secret scan (gitleaks)`,
  `Markdown lint`, `Actions pinned and token read-only`, `PR references a CR` and
  `Tests, lint and format (make check)`.
- **Security → Advanced Security:** Dependabot alerts, **Secret Protection** with
  **Push protection**, and private vulnerability reporting (which `SECURITY.md` points
  to).
- **Actions → General:** require approval for fork pull request workflows from all
  external contributors, and set workflow permissions to read-only.

Dependabot's pull requests don't need a CR: they are routine updates of already
approved dependencies, so the CI check for a CR reference skips them. The owner still
reviews and merges each one.

## Licence

[MIT](LICENSE). Copyright (c) 2026 Samuel Taylor (sam-tmts).
