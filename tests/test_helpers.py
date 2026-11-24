import io
import urllib.error
import urllib.request

import pytest
from keyring.backend import KeyringBackend

from smugback.cli import item_count
from smugback.credentials import Credentials, is_secure
from smugback.smugmug import (
    NoRedirect,
    SmugMug,
    SmugMugError,
    authorize_url,
    fetch,
)

CREDS = Credentials("key", "api-secret-value", "token-value", "token-secret-value")
URL = "https://api.smugmug.com/api/v2!authuser"


class FakeOpener:
    """Stands in for urllib's opener: records the request, then answers or raises."""

    def __init__(self, outcome):
        self.outcome = outcome
        self.request = None

    def open(self, request, timeout):
        self.request = request
        if isinstance(self.outcome, BaseException):
            raise self.outcome
        return self.outcome


class FakeResponse(io.BytesIO):
    status = 200


def test_item_count_uses_singular_for_one():
    assert item_count(1) == "1 item"
    assert item_count(0) == "0 items"
    assert item_count(2) == "2 items"


def test_item_count_shows_unknown_when_smugmug_gives_none():
    assert item_count(None) == "? items"


def test_fetch_sends_post_with_an_empty_body(monkeypatch):
    opener = FakeOpener(FakeResponse(b"ok"))
    monkeypatch.setattr("smugback.smugmug.opener", opener)

    assert fetch("POST", URL, {}) == (200, b"ok")
    assert opener.request.get_method() == "POST"
    assert opener.request.data == b""


def test_fetch_returns_status_and_body_of_http_errors(monkeypatch):
    error = urllib.error.HTTPError(URL, 500, "Server Error", {}, io.BytesIO(b"oops"))
    monkeypatch.setattr("smugback.smugmug.opener", FakeOpener(error))

    assert fetch("GET", URL, {}) == (500, b"oops")


@pytest.mark.parametrize(
    "failure", [urllib.error.URLError("unreachable"), TimeoutError(), OSError()]
)
def test_fetch_reports_network_failures_as_smugmug_errors(monkeypatch, failure):
    monkeypatch.setattr("smugback.smugmug.opener", FakeOpener(failure))

    with pytest.raises(SmugMugError):
        fetch("GET", URL, {})


def test_redirects_are_refused_so_the_signed_header_stays_with_smugmug():
    request = urllib.request.Request(URL, headers={"Authorization": "OAuth ..."})

    redirected = NoRedirect().redirect_request(
        request, None, 302, "Found", {}, "https://elsewhere.example/"
    )

    assert redirected is None


def test_unreadable_reply_is_reported_as_a_smugmug_error(monkeypatch):
    monkeypatch.setattr("smugback.smugmug.fetch", lambda *args: (200, b"<html>"))

    with pytest.raises(SmugMugError):
        SmugMug(CREDS).get("/api/v2!authuser")


def test_plain_text_keyring_backends_are_not_secure():
    class PlainTextKeyring(KeyringBackend):
        priority = 1

        def get_password(self, service, username): ...
        def set_password(self, service, username, password): ...
        def delete_password(self, service, username): ...

    PlainTextKeyring.__module__ = "keyrings.alt.file"

    assert not is_secure(PlainTextKeyring())


def test_credentials_repr_hides_secrets():
    shown = repr(CREDS)

    for secret in ("api-secret-value", "token-value", "token-secret-value"):
        assert secret not in shown


def test_authorize_url_asks_for_full_access_with_read_permission():
    url = authorize_url("request-token")

    assert "oauth_token=request-token" in url
    assert "Access=Full" in url
    assert "Permissions=Read" in url


def test_client_refuses_links_off_the_api_host(monkeypatch):
    sent = []
    monkeypatch.setattr("smugback.smugmug.fetch", lambda *args: sent.append(args))

    with pytest.raises(SmugMugError):
        SmugMug(CREDS).get("https://elsewhere.example/steal")

    assert sent == []
