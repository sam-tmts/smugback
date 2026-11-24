"""Shared test setup: no test may touch the real Keychain or the network."""

import json
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import keyring
import pytest
from keyring.backend import KeyringBackend
from keyring.errors import PasswordDeleteError

FIXTURES = Path(__file__).parent / "fixtures"

API_KEY = "test-api-key"
API_SECRET = "test-api-secret"
PIN = "123456"
ACCESS_TOKEN = "test-access-token"
TOKEN_SECRET = "test-token-secret"
SECRETS = [API_SECRET, ACCESS_TOKEN, TOKEN_SECRET]


class MemoryKeyring(KeyringBackend):
    """In-memory credential store, so tests never reach the macOS Keychain."""

    priority = 1

    def __init__(self):
        super().__init__()
        self.items: dict[tuple[str, str], str] = {}

    def get_password(self, service, username):
        return self.items.get((service, username))

    def set_password(self, service, username, password):
        self.items[(service, username)] = password

    def delete_password(self, service, username):
        if (service, username) not in self.items:
            raise PasswordDeleteError("not found")
        del self.items[(service, username)]


@pytest.fixture(autouse=True)
def memory_keyring():
    backend = MemoryKeyring()
    keyring.set_keyring(backend)
    return backend


class FakeSmugMug:
    """Stands in for SmugMug: records requests and serves canned responses."""

    def __init__(self):
        self.requests: list[tuple[str, str, dict]] = []
        # URL fragment -> HTTP status to answer with instead of the canned reply
        self.fail: dict[str, int] = {}

    def __call__(self, method, url, headers=None, *args, **kwargs):
        self.requests.append((method, url, dict(headers or {})))
        for fragment, status in self.fail.items():
            if fragment in url:
                return status, b'{"Code": %d, "Message": "failed"}' % status
        return 200, self._body(url)

    def _body(self, url):
        parsed = urlparse(url)
        path = parsed.path
        if path.endswith("/getRequestToken"):
            return b"oauth_token=test-request-token&oauth_token_secret=test-request-secret&oauth_callback_confirmed=true"
        if path.endswith("/getAccessToken"):
            return (
                f"oauth_token={ACCESS_TOKEN}&oauth_token_secret={TOKEN_SECRET}".encode()
            )
        if path.endswith("!authuser"):
            return (FIXTURES / "authuser.json").read_bytes()
        if path.endswith("/demo!albums"):
            start = int(parse_qs(parsed.query).get("start", ["1"])[0])
            name = "albums_page1.json" if start < 3 else "albums_page2.json"
            return (FIXTURES / name).read_bytes()
        raise AssertionError(f"unexpected request to {url}")

    @property
    def urls(self):
        return [url for _, url, _ in self.requests]


@pytest.fixture
def smugmug(monkeypatch):
    fake = FakeSmugMug()
    monkeypatch.setattr("smugback.smugmug.fetch", fake)
    return fake


@pytest.fixture
def prompts(monkeypatch):
    """Answers login's prompts: API key and PIN via input, secret via getpass."""
    answers = [API_KEY, PIN]
    monkeypatch.setattr("builtins.input", lambda *a, **k: answers.pop(0))
    monkeypatch.setattr("getpass.getpass", lambda *a, **k: API_SECRET)
    monkeypatch.setattr("webbrowser.open", lambda *a, **k: True)


def stored_json(backend):
    """The decoded JSON of the single stored keyring item."""
    assert len(backend.items) == 1
    ((service, _), password), *_ = backend.items.items()
    assert service == "smugback"
    return json.loads(password)
