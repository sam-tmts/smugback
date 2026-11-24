# Threat model

What we protect, the trust boundaries, the threats we expect, and how each is handled.
Update it in the same pull request as any change that affects these.

## Assets

| Asset | Why it matters |
|-------|----------------|
| Personal data on the developer's computer | Highly sensitive; must never be reachable by an agent |
| Credentials (API keys, tokens, SSH keys) | Misuse could expose accounts or data |
| The repository and its `main` branch | Others may build on this code |
| The owner's GitHub account | Controls all their repositories |
| SmugMug credentials (API key and secret, access token and token secret) | Give read access to every photo and video in the owner's account, including private ones |
| The owner's photos and videos | Private; SmugBack reads them and, in future, copies them to disk |

## Trust boundaries

1. **Developer account ↔ personal data.** Development uses a dedicated account with no
   access to personal data (ADR-0004).
2. **Sandbox ↔ the rest of the account.** Shell commands Claude runs are contained by
   Claude Code's sandbox, configured in `.claude/settings.json` (ADR-0004).
3. **Branch ↔ `main`.** Changes reach `main` only through a pull request whose required
   CI checks pass, merged by the owner.
4. **Owner ↔ agent.** The agent proposes; the owner approves each gate (`CLAUDE.md`).
   This applies equally to an agent working from Claude's cloud workspace with access
   to the repository.

## Threats

| Threat | Mitigations | Residual risk |
|--------|-------------|---------------|
| **Agent reaches personal data** | Dedicated developer account; sandbox | None while the account holds no personal data |
| **Prompt injection:** an agent acts on instructions hidden in something it reads | Sandbox; `CLAUDE.md` rule to treat such text as data; owner review at every gate | An injected change could reach a pull request; owner review is the backstop |
| **Credential theft** | Real secrets never enter the repository (ADR-0003); sandbox blocks reads of credential locations, and sandboxed commands can't reach the stored GitHub token (only `git push` runs outside the sandbox, with approval); permission rules block Claude's file tools from them | Credentials in the developer account outside those locations; keep tokens fine-grained and short-lived |
| **Data sent out** | Sandbox network allowlist (GitHub and PyPI only; no SmugMug host, so real runs happen only in the owner's terminal); developers decline prompts to allow new hosts unless a CR covers them | Data could be sent to an allowed service, such as a GitHub gist |
| **Secrets committed by mistake** | GitHub push protection; gitleaks in CI as a required check; GitHub secret scanning | The repository is public: a secret push protection doesn't recognise is public once pushed, even if CI stops it reaching `main` |
| **Malicious or typo-squatted dependency** | Owner approves every dependency (`docs/dependencies.md`); versions and hashes pinned in `uv.lock`; uv's cache kept inside the project, so a sandboxed command can't affect what other projects install (ADR-0005); Dependabot; sandbox limits damage | A compromised version of an approved dependency. A sandboxed command can also plant code in this project's git-ignored `.venv/` or `.uv-cache/`, which the owner's terminal would run; closed by running SmugBack with real credentials only from a clean install in the owner's everyday account, never the developer account (see the README). That install resolves dependencies afresh from PyPI rather than from `uv.lock`; `--exclude-newer` limits it to versions that existed when the commit was reviewed |
| **Compromised GitHub Action** | Actions pinned to full commit SHAs (checked in CI); read-only workflow token; fork PR workflows need approval | A compromised action at the pinned commit |
| **Unreviewed change reaches `main`** | Ruleset requires a pull request and passing checks, and blocks force-push and deletion; Claude Code can't merge and asks before pushing | With no required approval, anyone with write access can merge. Accepted while the owner reviews every change and the token is fine-grained and short-lived; a separate agent account is on the backlog |
| **SmugMug credentials stolen or leaked** | Used only from the owner's everyday account, never the developer account; stored only in that account's macOS Keychain (ADR-0003), never in a file; `login` refuses to store them if no secure store exists; the API secret and token secret never leave the machine (OAuth signatures go in the Authorization header, never in URLs); errors never print secrets; the sandbox and Claude's file tools are denied `~/Library/Keychains` | A process running as the owner with the same Python can read the Keychain item (see known limitations). The key is read-only, so a leak exposes photos but can't change or delete anything; tokens don't expire, so the remedy is revoking access in SmugMug (Site Settings → API Keys) |
| **SmugBack changes the owner's SmugMug account** | Read-only API key; sign-in asks only for Read permission; after sign-in the client can only send GET requests (ADR-0006), checked by a test | None known |
| **Signed requests sent to another host** (for example a crafted paging link) | The client accepts only paths on `api.smugmug.com` and refuses HTTP redirects, so the Authorization header goes nowhere else | None known |
| **Destructive mistake** (deleting files, rewriting history) | Sandbox limits writes to the project; permission rules block force-push, rebase, amend and branch deletion; everything is in git | Uncommitted work in the project could be lost |

## Known limitations

- The sandbox contains shell commands only. Claude's file tools, hooks and MCP servers
  run outside it, governed by permission rules, which are a guardrail rather than a
  boundary. The developer account is what protects personal data from them.
- Developers can loosen the shared settings with personal overrides
  (`.claude/settings.local.json`). The project's policy relies on each developer not
  weakening it.
- The network allowlist checks hostnames through a local proxy; an allowed host's other
  uses (such as GitHub gists) are reachable too.
- On macOS, a Keychain item is readable without a prompt by the program that created
  it. For SmugBack that program is the Python interpreter, so any script run by the
  same interpreter in the account that signed in can read SmugBack's credentials.
  That's why SmugBack runs in the owner's everyday account (see the README): the
  developer account, and any agent in it, has no route to that account's Keychain,
  and the sandbox's Keychain deny is a second layer.
- Permission rules for shell commands match command prefixes, so the same command
  written another way (for example `git -c … push --force`) can get past them. The
  sandbox and the `main` ruleset are the real backstops.
