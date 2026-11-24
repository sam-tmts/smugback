# CR-0004: Faster, clearer album listing

| Field         | Value                                                         |
|---------------|---------------------------------------------------------------|
| Status        | Draft                                                         |
| Author        | Claude, for sam-tmts                                          |
| Created       | 2026-11-24                                                    |
| Semver impact | minor: new options on `albums`, and a change to its output    |

## Why

On a large account, `smugback albums` is slow, with results arriving in a slow
trickle. Its output shows album names without their paths, which makes it hard to see
where anything lives. Every later feature (stats,
downloading) walks the same albums, so slow listing means slow test cycles for all
of them.

This CR makes the listing visible (`--verbose`), limits it to part of the account
(`--include`), and shows where each album lives. It also finds out whether
`--include` really is the speed-up we expect.

## Scope

**In:**

- `--verbose` on `albums`: each request's path and how long it took, then the number
  of requests and the total time. Written to standard error, so the listing on
  standard output stays clean. Built so later commands can share it.
- Find out why the listing trickles and fix it if it's ours. The likely cause is
  SmugMug returning pages of 10 albums rather than the 100 we ask for.
- `--include PATH`: list only the albums under a folder or album, given as its web
  address path (for example `/Date/2019`). It can be given more than once. A full web
  address pasted from the browser is also accepted; SmugBack uses its path.
- `--album-paths full|relative|names-only`, default `full`:
  - `full`: the album's whole path, for example `/Date/2019/January`.
  - `relative`: the path below the `--include` path it was found under, for example
    `January`. Without `--include`, the full path without its leading slash.
  - `names-only`: the album's own name only.
- `--album-name-format web-address|display-name`, default `web-address`:
  - `web-address`: names as they appear in the album's web address.
  - `display-name`: the album's display name, as shown on SmugMug. This works only
    with `--album-paths names-only`. Any other combination stops with a clear message,
    because a full path of display names needs every folder's display name, which
    album records don't carry.
- `albums` output sorted by path, so albums in the same folder appear together, each
  with its photo and video count as now.
- README: the new options, with examples.

**Out:**

- Excludes and a config file.
- Folder display names in paths.

## Design notes

- **Include prunes at the source.** `--include` looks the path up on SmugMug and
  lists only what's beneath it, rather than fetching every album and filtering. That
  is the point of the option. The API offers lookups by path (for example the user's
  `!urlpathlookup`, or `!weburilookup`); the plan confirms which one from SmugMug's
  documentation, and how to list a folder's contents beneath it.
- **Without `--include`,** the listing stays one paged list of every album: fewer
  requests than walking the folder tree.
- **Paths match on whole segments:** `/Date/2019` covers `/Date/2019/January`, not
  `/Date/2019-scans`. A trailing slash makes no difference.
- **Album fields:** each album record is expected to carry its web address path, its
  web name and its display name (`UrlPath`, `UrlName`, `Name`); the plan confirms this
  from the documentation.
- **Sorting** means nothing prints until the listing is complete; `--verbose` shows
  progress meanwhile.
- **Read-only, unchanged:** the lookups are GET requests on `api.smugmug.com` through
  the existing client, so ADR-0006 holds as it is.
- No new ADR expected; the plan says if one is needed.

## Acceptance criteria

- [ ] AC1: With `--verbose`, each request's path and duration, then the request count
  and total time, appear on standard error; standard output holds only the listing.
  *Verified by:* `test_cr0004_ac1_verbose_reports_requests_on_stderr`.
- [ ] AC2: `--verbose` output never contains the API secret, access token, token
  secret or any signature.
  *Verified by:* `test_cr0004_ac2_verbose_output_has_no_secrets`.
- [ ] AC3: Listing every album asks SmugMug for 100 albums per page on every page.
  *Verified by:* `test_cr0004_ac3_every_page_requests_100_albums`.
- [ ] AC4: `--include` lists only albums under the path, on whole segments, and
  doesn't fetch the full album list.
  *Verified by:* `test_cr0004_ac4_include_lists_only_albums_under_path`.
- [ ] AC5: With several `--include` paths, including overlapping ones, each album is
  listed once.
  *Verified by:* `test_cr0004_ac5_overlapping_includes_list_each_album_once`.
- [ ] AC6: An `--include` path that doesn't exist exits non-zero with a message naming
  the path, and lists nothing.
  *Verified by:* `test_cr0004_ac6_unknown_include_path_explains`.
- [ ] AC7: `--include` accepts a full web address and uses its path.
  *Verified by:* `test_cr0004_ac7_include_accepts_web_address`.
- [ ] AC8: By default, each line shows the album's full web address path and its
  count, sorted by path.
  *Verified by:* `test_cr0004_ac8_default_lists_full_paths_sorted`.
- [ ] AC9: `--album-paths relative` and `names-only` show the path below the include
  path, and the album's own name, as described in Scope.
  *Verified by:* `test_cr0004_ac9_album_paths_relative_and_names_only`.
- [ ] AC10: `--album-name-format display-name` with `names-only` shows display names;
  with `full` or `relative` it exits non-zero with a clear message, before contacting
  SmugMug.
  *Verified by:* `test_cr0004_ac10_display_name_only_with_names_only`.
- [ ] AC11: Every request, including the path lookups, is a GET.
  *Verified by:* `test_cr0004_ac11_include_requests_are_read_only`.
- [ ] AC12: With a real account, from a clean install: time `albums` with and without
  `--include` for one year's folder, record both timings and request counts, and
  check that folder's listing matches the SmugMug website.
  *Verified by:* manual check in `docs/test-plan.md`.
- [ ] AC13: The README documents the new options with examples; `docs/architecture.md`
  is updated if the change affects it.
  *Verified by:* manual check in `docs/test-plan.md`.

## Constraints and risks

- **No new dependencies** expected.
- **Fixtures come from SmugMug's documentation,** and the path lookup's real replies
  may differ from them; AC12 is the backstop.
- **The trickle's cause may not be ours.** If SmugMug ignores the page size or
  throttles us, the plan says so; AC12 records what we see.
- **Existing tests:** if fixing the page size touches CR-0003's tests or fixtures,
  that needs the owner's approval first.
- **Read-only on SmugMug,** as always.

## Approval log

| Gate | Date | By | Notes |
|------|------|----|-------|
| CR approved | | | |
| Plan approved | | | |
| PR merged | | | |
| Released | | | |
