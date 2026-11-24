# ADR-0006: A read-only SmugMug client on the standard library and oauthlib

| Field      | Value                    |
|------------|--------------------------|
| Status     | Accepted                 |
| Date       | 2026-11-24               |
| Deciders   | Samuel Taylor (sam-tmts) |
| Related CR | CR-0003                  |

## Context

SmugBack must sign in to SmugMug's API v2, which uses OAuth 1.0a, and read the owner's
account. It must never change anything there, must keep the owner's secrets out of
URLs, logs and messages, and should add as few dependencies as possible (ADR-0005).

## Decision

- **HTTP** uses the standard library (`urllib.request`), through one `fetch` function
  that tests replace, so no test reaches SmugMug.
- **Request signing** uses `oauthlib` (HMAC-SHA1). Signatures go in the
  `Authorization` header, never in URLs. We don't write our own signing code.
- **Sign-in** uses the out-of-band PIN flow, asking for `Access=Full` (private albums
  included) and `Permissions=Read`. The token requests are the only POSTs.
- **After sign-in, the client offers only `get`.** Every later feature, including
  downloading, reads through it; nothing may add a method that writes to SmugMug.
- **The signed header goes only to `api.smugmug.com`:** the client follows only paths
  on that host, and refuses HTTP redirects (urllib would otherwise copy the header to
  the redirect's host; an OAuth 1.0a signature doesn't survive a redirect anyway).

## Consequences

- One small dependency (`oauthlib`, no dependencies of its own) for signing.
- Read-only is enforced by the client's shape and checked by a test, on top of the
  read-only API key.
- Downloading large files will need streaming through `fetch`; that is a later
  change to this module, not a reason for a different HTTP library.

## Alternatives considered

- **`requests` with `requests-oauthlib`:** friendlier, but five or more extra
  dependencies for a few GET requests.
- **Our own OAuth 1.0a signing:** no dependency, but security-sensitive code that an
  established library already gets right.
- **SmugMug's own SDKs:** none maintained for Python.
