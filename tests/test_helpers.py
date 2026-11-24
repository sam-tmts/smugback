import pytest
from keyring.backend import KeyringBackend

from smugback.cli import item_count
from smugback.credentials import Credentials, is_secure
from smugback.smugmug import SmugMug, SmugMugError, authorize_url

CREDS = Credentials("key", "api-secret-value", "token-value", "token-secret-value")


def test_item_count_uses_singular_for_one():
    assert item_count(1) == "1 item"
    assert item_count(0) == "0 items"
    assert item_count(2) == "2 items"


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
