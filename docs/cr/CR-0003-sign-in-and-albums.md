# CR-0003: Sign in to SmugMug and list albums

| Field         | Value                                                        |
|---------------|--------------------------------------------------------------|
| Status        | Approved                                                     |
| Author        | Claude, for sam-tmts                                         |
| Created       | 2026-11-24                                                   |
| Semver impact | minor: first commands that talk to SmugMug                   |

## Why

Before SmugBack can back anything up, it must sign in to the owner's SmugMug account
and see what's there. This CR delivers sign-in, sign-out and an album listing, so the
owner can confirm SmugBack sees exactly what the SmugMug website shows. Downloading
builds on this in a later CR.

It also closes the risks CR-0002 left open before SmugBack handles credentials.

## Scope

**In:**

- `smugback login`: signs in with SmugMug's OAuth 1.0a flow, using the owner's own
  SmugMug API key and secret (entered at the prompt) and a PIN SmugMug shows in the
  browser. The API key, secret and access token are stored in the macOS Keychain
  (ADR-0003), never in a file. If no secure credential store is available, `login`
  stops with a clear message and stores nothing: it never falls back to plain text.
- `smugback logout`: removes everything `login` stored.
- `smugback albums`: lists every album in the signed-in account, with its name and the
  number of photos and videos in it.
- `smugback` with no arguments prints the help.
- Threat model: SmugBack's own assets and threats (the API secret and access token),
  replacing the template note. It records that:
  - the API key is read-only, so a leaked token exposes photos but can't change
    anything: a privacy risk, not a destruction risk;
  - SmugMug tokens don't expire, so revoking access in SmugMug's account settings is
    the remedy if one is exposed (the README says how);
  - on macOS, Keychain access is granted to the Python interpreter, so any script run
    by the same interpreter can read SmugBack's items without a prompt.
- A documented way for the owner to run SmugBack from a clean install of a reviewed
  commit, not from the project's `.venv/` that sandboxed commands can write to. This
  closes the residual risk recorded in CR-0002.
- A convention in `CLAUDE.md`: refer to future work by its GitHub issue, never by an
  unwritten CR number.

**Out:**

- Downloading photos and videos, resuming, and incremental backups: later CRs, tracked
  as GitHub issues.
- Any change on SmugMug: SmugBack stays read-only.
- Other operating systems' credential stores: macOS only for now (the library chosen
  should not rule them out).
- Headless and scheduled use, on machines with no credential store (for example a
  NAS): a later CR with an ADR refining ADR-0003, tracked as a GitHub issue.
- Any SmugMug host on the sandbox allowlist: real runs stay in the owner's terminal.

## Design notes

- **Credential store:** ADR-0003 already decides the OS credential store, read
  through a library. The plan confirms the library (likely `keyring`), and checks
  whether sandboxed commands can reach the Keychain at all (expected: no). Tests never
  touch the real Keychain. macOS may ask again for Keychain access after the tool's
  Python is upgraded; the README says that's expected.
- **OAuth 1.0a and HTTP:** the plan compares the simplest options and their dependency
  cost, for example the standard library's `urllib` with `oauthlib` for request
  signing (one small dependency), against `requests` with `requests-oauthlib` (several).
  Request signing is security-sensitive, so it uses an established library rather
  than our own code.
- **Read-only by construction:** after sign-in, the client offers only GET requests.
- **Tests never reach SmugMug:** they use mocks and fixtures based on SmugMug's API
  documentation, free of secrets and personal data. Real use is checked by hand in the
  owner's terminal.
- **Clean install:** for example `uv tool install` of a reviewed commit, which installs
  outside the project folder, where the sandbox can't write.
- The plan says whether the SmugMug client approach needs an ADR.

Relies on: ADR-0003 (secrets outside the repository), ADR-0004 (sandbox),
ADR-0005 (Python toolchain).

## Acceptance criteria

- [ ] AC1: `smugback login` takes the API key, secret and PIN, completes the OAuth
  exchange, and stores the credentials only in the credential store.
  *Verified by:* `test_cr0003_ac1_login_stores_credentials_in_keychain` (mocked
  OAuth and credential store).
- [ ] AC2: `smugback albums` lists every album, with name and photo and video count,
  across all pages of results.
  *Verified by:* `test_cr0003_ac2_lists_all_albums_across_pages`.
- [ ] AC3: Without stored credentials, `smugback albums` exits non-zero and tells the
  user to run `smugback login`, without contacting SmugMug.
  *Verified by:* `test_cr0003_ac3_albums_without_login_explains`.
- [ ] AC4: After sign-in, SmugBack only reads from SmugMug: every API request is a GET.
  *Verified by:* `test_cr0003_ac4_api_requests_are_read_only`.
- [ ] AC5: The API secret and access token never appear in output or error messages,
  including when a request fails.
  *Verified by:* `test_cr0003_ac5_secrets_not_in_output_or_errors`.
- [ ] AC6: `smugback logout` removes every stored credential, and succeeds when
  there is nothing to remove.
  *Verified by:* `test_cr0003_ac6_logout_removes_credentials`.
- [ ] AC7: `smugback` with no arguments prints the help.
  *Verified by:* `test_cr0003_ac7_no_arguments_prints_help`.
- [ ] AC8: With a real account, in the owner's terminal, from a clean install: login
  works, `albums` matches the albums on the SmugMug website, and after `logout` no
  SmugBack entry remains in Keychain Access.
  *Verified by:* manual check in `docs/test-plan.md`.
- [ ] AC9: The threat model covers SmugBack's credentials, including the read-only
  key and revoking access on SmugMug, with no template note left; the README documents
  the clean-install way to run SmugBack and how to revoke access; `CLAUDE.md` has the
  future-work convention.
  *Verified by:* manual check in `docs/test-plan.md`.
- [ ] AC10: When no secure credential store is available, `smugback login` exits
  non-zero with a clear message and writes no credentials anywhere.
  *Verified by:* `test_cr0003_ac10_login_without_secure_store_stores_nothing`.

## Constraints and risks

- **Real credentials:** the agent never sees, requests or stores them (ADR-0003).
  Only the owner runs `login`, in their own terminal.
- **New dependencies:** each needs the owner's approval and an entry in
  `docs/dependencies.md`; the plan names them.
- **SmugMug API access:** the owner has a read-only API key from SmugMug. If
  SmugMug's terms for personal keys turn out to have changed, stop and raise it.
- **Keychain prompts:** macOS may ask the owner to allow SmugBack access to its
  Keychain items on first use; that is expected.
- **API details:** fixtures are written from SmugMug's documentation, so the real
  responses may differ; AC8's manual check is the backstop.

## Approval log

| Gate | Date | By | Notes |
|------|------|----|-------|
| CR approved | 2026-11-24 | sam-tmts | Keychain only; headless use deferred |
| Plan approved | | | |
| PR merged | | | |
| Released | | | |
