# Retrospectives

A short look back before each release (see the release criteria in
[test-plan.md](test-plan.md)): what worked, what to change, and what changed as a
result. A lesson that keeps coming up becomes an update to `CLAUDE.md`.

## SmugBack 0.1.0 — 2026-11-24

Covers CR-0002 (project setup) and CR-0003 (sign-in and album listing). The 0.2.0
entry below is the template's, kept as history.

### What worked

- Probing before trusting: a two-minute Keychain test during planning showed sandboxed
  commands could read Keychain secrets, almost certainly including git's GitHub token.
  The deny rule closed it before any real token existed.
- Independent review earned its place again: it caught an unpinned build backend, a
  signed header that redirects would carry to other hosts, and a clean install that
  ignored the lockfile.
- Checking the test-writer's tests before the gate caught an AC5 test that no correct
  OAuth client could pass.
- A private checklist page with a results form made the real-account test (M14) easy
  to run from the everyday account, and its results came straight back to Claude.
- Small, honest decisions by the owner kept scope tight: Keychain only, release after
  CR-0003, real runs from the everyday account.

### What to change

- Test the setup instructions against real changes earlier: the README's token
  lacked the Workflows permission, found only on the first push that touched CI.
- Remember that the sandbox makes some ordinary git commands fail in confusing ways:
  `git pull` across a change to `.claude/settings.json`, and pushes once the token
  can't be read (seen after switching macOS accounts). When that happens, the owner
  runs the command in their own terminal; Claude doesn't retry.
- Don't name an unwritten CR in living docs; refer to future work by GitHub issue.
- Name every value that a protocol sends in the clear when writing security tests
  (OAuth 1.0a sends the access token in a header).

### What changed as a result

- `.claude/settings.json` denies the login Keychain to the sandbox and Claude's file
  tools; the README's token setup lists the Workflows permission.
- `CLAUDE.md` has the future-work convention.
- SmugBack runs for real only from a clean install in the owner's everyday account.

## 0.2.0 — 2026-11-22

### What worked

- The gates caught real problems before they reached `main`: independent reviews found
  a firewall that failed open and a check that could pass falsely.
- Testing on the real Mac found two bugs no review could (the `.git` rule blocking
  commits, and pushes needing credentials outside the sandbox).
- Pushing back on complexity, once we started doing it, quickly led to simpler designs.

### What to change

- Try the simplest well-trodden option before building anything bespoke: we built and
  reviewed a dev container before testing Claude Code's own sandbox.
- Weigh review findings against the risk instead of fixing every one.
- Test on the real machine earlier, and phrase manual checks plainly.

### What changed as a result

- Principles at the top of `CLAUDE.md`, a challenge-before-building rule, and reviewer
  checks that follow the principles.
- CRs hold intent and acceptance criteria; the plan lives in the pull request.
- The container parked in favour of the sandbox in a dedicated developer account.
- A lighter path for trivial changes, and a retrospective before each release.
