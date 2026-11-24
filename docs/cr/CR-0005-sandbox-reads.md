# CR-0005: Keep the sandbox's reads inside the project

| Field         | Value                                                         |
|---------------|---------------------------------------------------------------|
| Status        | Approved                                                      |
| Author        | Claude, for sam-tmts                                          |
| Created       | 2026-11-24                                                    |
| Semver impact | none: changes development settings only, not SmugBack itself  |

## Why

The owner runs several projects at once in the developer account. A shell command
Claude runs for SmugBack can read every one of them, and every other file in the home
folder, because the sandbox only blocks reads of a short list of credential locations.
On 2026-11-24 Claude listed `~/Downloads` while looking for a file, without asking,
and nothing stopped it.

That falls short of CR-0001, whose scope said sandboxed commands "can't read the rest
of the account"; only the credential locations were blocked. A habit of staying in the
project isn't enough: if text in a file or dependency got Claude to act on hidden
instructions, only the sandbox would stop it reading another project's code or
secrets. This CR makes the sandbox enforce the wall between projects.

## Scope

**In:**

- `.claude/settings.json`: sandboxed commands can't read anything in the home folder
  except this project and the few paths the project's tools need to work (for example
  the Python that uv installs, and git's own settings). Every path allowed back is
  listed, with the reason, in ADR-0004.
- The existing credential denies stay, so they still apply if a parent folder is ever
  allowed back.
- Claude's file tools (Read, Grep, Glob), which run outside the sandbox: the plan
  checks whether they can read other projects without asking. If they can, a
  permission rule stops them; if no simple rule does, the gap is recorded as a known
  limitation for the owner to accept.
- ADR-0004, the threat model (a threat for one project reaching another, and the
  "Agent reaches personal data" row) and the test plan updated.
- A GitHub issue to carry the same change to the template repository.

**Out:**

- Locations outside the home folder, such as `/Volumes` (external drives) and shared
  temporary folders: the plan lists what else is readable, and anything worth closing
  becomes a GitHub issue. The developer account holding no personal data stays the
  main protection.
- Network rules: unchanged.
- Hooks and MCP servers, which also run outside the sandbox: unchanged, as recorded in
  the threat model's known limitations.

## Design notes

- **Deny broadly, allow back narrowly.** Block reads of `~`, then allow back this
  project and the paths tools need. The alternative, listing each folder to block
  (`~/Projects`, `~/Downloads`, …), is simpler to write but misses every folder added
  later. The plan confirms the sandbox supports allowing a path back inside a denied
  one, and the exact setting names.
- **Find the allow list by probing, not guessing.** The plan runs `make check`, git
  commands and `uv` with the broad deny in place, and adds back only what fails. Fewer
  allowed paths is better; each one must earn its place.
- **The project path:** settings can't assume where each developer keeps the project.
  The plan finds how to name "this project" in the shared settings (for example a path
  relative to the project), so it works for any developer.
- **Claude's own session state** (`~/.claude`) is handled by Claude Code outside the
  sandbox; the plan checks that blocking it from shell commands breaks nothing.

Relies on and amends: ADR-0004 (sandboxed development). Relies on: ADR-0005 (uv's
cache inside the project, which this keeps working).

## Acceptance criteria

- [x] AC1: A shell command Claude runs can't read or list a file in another folder of
  the home directory, such as a sibling project or `~/Downloads`.
  *Verified by:* manual check in `docs/test-plan.md` (the owner creates a dummy file
  in another project folder in their own terminal; Claude's sandboxed `cat` and `ls`
  of it fail with a sandbox denial, while the owner's terminal reads it).
- [x] AC2: Claude's file tools can't read a file in another project folder without the
  owner's approval, or, if no simple rule achieves that, the threat model records it
  as a known limitation the owner has accepted.
  *Verified by:* manual check in `docs/test-plan.md`.
- [x] AC3: Day-to-day work still flows from inside the sandbox: `make check`, `uv run
  smugback --help`, `git status`, `git commit`, and a push through the normal approval.
  *Verified by:* manual check in `docs/test-plan.md` (re-running M9 and M10).
- [x] AC4: The credential reads blocked before this CR are still blocked.
  *Verified by:* re-running manual checks M6 and M16.
- [x] AC5: ADR-0004 lists every path allowed back, with the reason; the threat model
  covers one project reaching another; a GitHub issue tracks the template change.
  *Verified by:* the reviewer's documentation check.

## Constraints and risks

- **Protected path:** `.claude/settings.json`, for the sandbox's read rules and any
  permission rule from AC2. This CR covers it.
- **Breaking the workflow:** too broad a deny stops uv, git or Python working in the
  sandbox. Probing during planning keeps this small, and AC3 is the backstop.
- **`git pull` and settings changes:** the retrospective found the sandbox makes `git
  pull` fail across a change to `.claude/settings.json`; the owner may need to pull
  this change in their own terminal.
- **Personal overrides:** a developer can still loosen this in
  `.claude/settings.local.json` (already a known limitation).
- **Not a complete boundary:** hooks and MCP servers still run outside the sandbox.

## Approval log

| Gate | Date | By | Notes |
|------|------|----|-------|
| CR approved | 2026-11-24 | sam-tmts | Raised after Claude listed `~/Downloads` unasked |
| Plan approved | 2026-11-24 | sam-tmts | Plan in the PR description |
| PR merged | 2026-11-24 | sam-tmts | PR #9. AC1 by M17, AC2 by M18 (fresh session), AC3 by M19, AC4 by M6 and M16 (M6's `~/.ssh` read stopped first by the permission rule), AC5 by the review and template-claude-project#15 |
| Released | | | |
