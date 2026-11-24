import os

import keyring
import pytest
from conftest import (
    ACCESS_TOKEN,
    API_KEY,
    API_SECRET,
    PIN,
    SECRETS,
    TOKEN_SECRET,
    stored_json,
)
from keyring.backends import fail, null

from smugback.cli import main

EXPECTED_ALBUMS = [
    "Holiday 2024 (12 items)",
    "Empty Album (0 items)",
    "Garden Videos (340 items)",
    "Family Portraits (57 items)",
]


def run(argv):
    """Run the CLI and return its exit code, whether it returns or exits."""
    try:
        result = main(argv)
    except SystemExit as exit_info:
        result = exit_info.code
    return result or 0


@pytest.fixture
def signed_in(smugmug, prompts):
    assert run(["login"]) == 0
    smugmug.requests.clear()


def test_cr0003_ac1_login_stores_credentials_in_keychain(
    smugmug, prompts, memory_keyring, tmp_path, monkeypatch
):
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.chdir(tmp_path)

    assert run(["login"]) == 0

    # One item, under the service name "smugback", holding all four values
    stored = stored_json(memory_keyring)
    assert {API_KEY, API_SECRET, ACCESS_TOKEN, TOKEN_SECRET} <= set(stored.values())
    # The PIN was used in the exchange, and nothing was written to disk
    access_calls = [r for r in smugmug.requests if r[1].endswith("/getAccessToken")]
    assert len(access_calls) == 1
    assert f'oauth_verifier="{PIN}"' in access_calls[0][2]["Authorization"]
    assert list(tmp_path.iterdir()) == []


def test_cr0003_ac2_lists_all_albums_across_pages(smugmug, signed_in, capsys):
    assert run(["albums"]) == 0

    lines = [ln for ln in capsys.readouterr().out.splitlines() if ln.strip()]
    assert lines == EXPECTED_ALBUMS


def test_cr0003_ac3_albums_without_login_explains(smugmug, capsys):
    assert run(["albums"]) != 0

    captured = capsys.readouterr()
    assert "smugback login" in captured.out + captured.err
    assert smugmug.requests == []


def test_cr0003_ac4_api_requests_are_read_only(smugmug, signed_in):
    assert run(["albums"]) == 0

    assert len(smugmug.requests) >= 3  # authuser plus both album pages
    assert {method for method, _, _ in smugmug.requests} == {"GET"}


@pytest.mark.parametrize(
    "failing_stage",
    [None, "getRequestToken", "getAccessToken", "!authuser", "demo!albums"],
)
@pytest.mark.parametrize("status", [401, 500])
def test_cr0003_ac5_secrets_not_in_output_or_errors(
    smugmug, prompts, capsys, failing_stage, status
):
    if failing_stage:
        smugmug.fail[failing_stage] = status

    login_code = run(["login"])
    albums_code = run(["albums"])

    if failing_stage:
        assert login_code != 0 or albums_code != 0
    output = capsys.readouterr()
    for secret in SECRETS:
        assert secret not in output.out
        assert secret not in output.err
    # Signatures travel in the Authorization header, never in the URL
    for url in smugmug.urls:
        assert "oauth_signature" not in url
        for secret in SECRETS:
            assert secret not in url
    # OAuth 1.0a sends the access token itself in the Authorization header
    # (oauth_token="..."); only the two secrets used for signing never travel
    for _, _, headers in smugmug.requests:
        for value in headers.values():
            for secret in (API_SECRET, TOKEN_SECRET):
                assert secret not in value


def test_cr0003_ac6_logout_removes_credentials(smugmug, signed_in, memory_keyring):
    assert memory_keyring.items

    assert run(["logout"]) == 0

    assert memory_keyring.items == {}


def test_cr0003_ac6_logout_with_nothing_stored_succeeds(memory_keyring):
    assert run(["logout"]) == 0

    assert memory_keyring.items == {}


def test_cr0003_ac7_no_arguments_prints_help(capsys):
    assert run([]) == 0

    out = capsys.readouterr().out
    assert "usage: smugback" in out
    for command in ("login", "logout", "albums"):
        assert command in out


@pytest.mark.parametrize("backend", [fail.Keyring, null.Keyring])
def test_cr0003_ac10_login_without_secure_store_stores_nothing(
    smugmug, prompts, memory_keyring, capsys, tmp_path, monkeypatch, backend
):
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.chdir(tmp_path)
    keyring.set_keyring(backend())

    assert run(["login"]) != 0

    captured = capsys.readouterr()
    assert captured.err.strip() != ""  # a message, not a bare failure
    for secret in SECRETS:
        assert secret not in captured.out + captured.err
    assert memory_keyring.items == {}
    assert os.listdir(tmp_path) == []
