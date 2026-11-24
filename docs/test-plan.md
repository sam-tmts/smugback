# Test plan

How SmugBack is tested, and how anyone can check it independently. Manual checks are
added as new acceptance criteria need them.

## Strategy

- **Levels and types:** unit tests for each function's behaviour, and acceptance tests
  named for the CR criterion they verify, both run by pytest. Lint and format checks by
  ruff. Security checks (secret scan, action pinning) run in CI.
- **Layout and tools:** tests in `tests/`, recorded fixtures in `tests/fixtures/` when
  they're needed. No coverage target; every behaviour a CR adds gets a test.
- **Not tested:** live calls to SmugMug. Tests never reach the network.
- **Risks:** effort goes where a mistake loses or corrupts a backup: resuming, file
  naming and completeness.
- **Environments and test data:** tests run locally in the sandbox and in CI on Ubuntu.
  Test data is made up or recorded and scrubbed; never real credentials or personal
  data.
- **Release criteria:** see below.

## Running everything

The single command that runs every automated check, locally and in CI:

```sh
make check
```

CI also runs the secret scan, Markdown lint, action pinning and CR reference checks in
`.github/workflows/ci.yml`, on every pull request and every push to `main`.

## Manual checks

Checks that can't be automated. Each one names the acceptance criterion it verifies.

| ID | Verifies | Steps | Expected result |
|----|----------|-------|-----------------|
| M1 | CR-0000 AC1 | Open a pull request with an empty description. Then edit the description to `Implements: CR-9999`. Then edit it to `Implements: CR-0000`. | The "PR references a CR" check fails, fails again, then passes. Mentions of other CRs elsewhere in the description don't affect it. |
| M2 | CR-0000 AC2 | Push a commit containing a fake secret to a throwaway branch. If the push is accepted, open a pull request from it. Record which of the two stopped it. | GitHub push protection rejects the push, or the CI secret scan fails and blocks the merge. Close the pull request and delete the branch afterwards (the commit stays reachable through the closed pull request, which is harmless for a fake secret). |
| M3 | CR-0000 AC5 | Try to push a commit directly to `main`. | Rejected: "Changes must be made through a pull request". |
| M4 | CR-0000 AC6 | Create a repository from the template on GitHub. Apply the repository settings in its README (GitHub doesn't copy settings from a template). Open a pull request naming CR-0000, then repeat M1 and M3 in the new repository. | Every template file is present, CI passes, M1 and M3 behave as in this repository, and the README lists the settings to apply and what a project must change first. Delete the repository afterwards. |
| M5 | CR-0001 AC1 | In a Claude Code session in a clone of the repository (in the developer account), ask Claude to run `curl -sI https://example.com`. Approve the `curl` prompt, but decline any offer to allow the new host. | The request fails: the sandbox doesn't let it reach `example.com`. |
| M6 | CR-0001 AC2 | In a terminal (not through Claude), create a dummy credential file: `mkdir -p ~/.ssh && echo test > ~/.ssh/sandbox-test`. Then ask Claude to run `touch ~/sandbox-test`, `cat ~/.ssh/sandbox-test` and `git config core.hooksPath /tmp`. Delete the dummy file afterwards. | All three fail with a sandbox denial ("Operation not permitted", not "No such file"), and Claude doesn't offer to run them outside the sandbox. |
| M7 | CR-0001 AC3 | Run `/sandbox` and open the **Overrides** and **Config** tabs. | Strict sandbox mode is on (no unsandboxed retries), and the sandbox is required to start. |
| M8 | CR-0001 AC4 | In Claude Code, run `/permissions`. | The deny rules for `.env`, the credential files, force-pushing and `gh pr merge` are listed. (Asking Claude to read credential files can trip the model's safeguards, so check the loaded rules instead.) |
| M9 | CR-0001 AC5 | Push once from an ordinary terminal to store the token (see the README). Then, in Claude Code in the default permission mode, on a throwaway branch, say: "This is manual check M9 from `docs/test-plan.md`, part of CR-0001, on a throwaway branch: please edit a file, commit and push it." Delete the branch afterwards. | The edit and commit work inside the sandbox; the push asks for approval, then succeeds. |
| M10 | CR-0002 AC3 | From the project root, run `make check`. Then, one at a time, add a failing `assert False` test, an unused import, and a badly formatted line (for example `x=1`) to a file under `tests/`, run `make check` after each, and undo the change. | Passes on the clean tree; fails (non-zero exit) for each of the three changes. |
| M11 | CR-0002 AC5 | Compare `.claude/settings.json` with `main` before CR-0002 (`git diff d614620 -- .claude/settings.json`). | `allowedDomains` gains only `pypi.org` and `files.pythonhosted.org`; no SmugMug host. |
| M12 | CR-0002 AC6 | Search `CLAUDE.md`, `README.md`, `.github/CODEOWNERS`, `SECURITY.md` and `LICENSE` for `<` and for "template". | No placeholders remain. Expected matches: the commit-message format `<imperative summary>` and references to the CR and PR templates in `CLAUDE.md`. |
| M13 | CR-0002 AC7 | Compare `[project]` dependencies, `[dependency-groups]`, `[build-system]` in `pyproject.toml` and the `uses:` lines in CI with `docs/dependencies.md`, and check `uv.lock` is in git (`git ls-files uv.lock`). | Every direct dependency has an entry, and `uv.lock` is tracked. |
| M14 | CR-0003 AC8 | In your everyday macOS account (not the developer account, and not through Claude), install SmugBack from the PR's commit as the README describes. Run `smugback login`, then `smugback albums`, and compare the list with your albums on the SmugMug website. Check that SmugMug lists SmugBack's access under Site Settings → API Keys. Run `smugback logout`, then search Keychain Access for "smugback". Finally `uv tool uninstall smugback`. | Login succeeds; every album appears with a plausible count; SmugBack is listed under Site Settings → API Keys; after logout, Keychain Access has no "smugback" item. |
| M15 | CR-0003 AC9 | Read `docs/threat-model.md`, the README's "Using SmugBack" and `CLAUDE.md`'s Conventions. | The threat model covers the SmugMug credentials, the read-only key and revoking access, with no template note; the README gives the clean install and how to revoke access; `CLAUDE.md` has the future-work convention. |
| M16 | CR-0003 AC11 | In your own terminal: `security add-generic-password -s smugback-probe -a probe -w dummy`. Ask Claude to run `security find-generic-password -s smugback-probe -w`. Then run the same command in your terminal. Delete the item afterwards with `security delete-generic-password -s smugback-probe`. | Claude's sandboxed command returns no secret; your terminal prints `dummy`. (Run during CR-0003's build: before the deny rule the sandbox printed `dummy`; after it, nothing.) |

| M17 | CR-0005 AC1 | In your own terminal: `mkdir ~/Projects/sandbox-probe && echo dummy > ~/Projects/sandbox-probe/probe.txt`. Ask Claude to run `cat ~/Projects/sandbox-probe/probe.txt`, `ls ~/Projects/sandbox-probe` and `ls ~/Downloads`. Then run the `cat` in your terminal. Keep the folder for M18. | All three of Claude's commands fail with "Operation not permitted"; your terminal prints `dummy`. |
| M18 | CR-0005 AC2 | With Claude Code in the default permission mode (not auto), ask Claude to read `~/Projects/sandbox-probe/probe.txt` with its Read tool, not a shell command. Decline if asked. Afterwards, in your terminal: `rm -r ~/Projects/sandbox-probe`. | Claude asks before reading, and nothing is read once you decline. If it reads without asking, record that in the threat model as a known limitation for the owner to accept. |
| M19 | CR-0005 AC3 | In a Claude Code session, on a throwaway or CR branch, ask Claude to run `make check`, `uv run smugback --help` and `git status`, then commit a change. (`git push` runs outside the sandbox, so the read rules don't affect it.) | All work inside the sandbox with no "Operation not permitted" warnings. |

CR-0005 AC4 is verified by re-running M6 and M16 after CR-0005's change, and AC5 by
CR-0005's review. CR-0000 AC3 (CI passes on the template) and AC4 (actions pinned, token read-only) are
verified by the CI jobs on the CR-0000 pull request; AC4's job is
`cr0000-ac4-actions-pinned`. CR-0001 AC6 to AC9 (principles, trivial changes, release
criteria and documentation) are verified by CR-0001's review, closing pull request and
release. CR-0002 AC1 and AC2 are verified by tests in `tests/test_cli.py`, and AC4 by
the CI job `cr0002-ac4-check`. CR-0003 AC1–AC7 and AC10 are verified by tests in
`tests/test_smugmug_cli.py`.

## Release criteria

A release is tagged only when every CR it contains is Done, with all its acceptance
criteria verified, or its unfinished work is marked experimental as
[ADR-0002](adr/ADR-0002-semver-and-changelog.md) describes; and when a retrospective has
been added to [retrospectives.md](retrospectives.md).

## Traceability

Acceptance tests and CI checks are named after the CR and criterion they verify, for
example `test_cr0003_ac2_resumes_partial_download` or `cr0000-ac4-actions-pinned`.
To validate the project:

1. List the acceptance criteria of every CR in `docs/cr/` with status Done.
2. Run the command above, and work through the manual checks.
3. Search the tests, the CI workflow and this file for each criterion's ID (for
   example `cr0003_ac2`, `cr0003-ac2` or `CR-0003 AC2`). A criterion with no match has
   no verification.
