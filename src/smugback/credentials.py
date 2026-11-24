"""SmugBack's credentials, kept only in the operating system's credential store.

See ADR-0003: never in a file, and never a plain-text fallback.
"""

import json
from dataclasses import asdict, dataclass, field

import keyring
from keyring.backends import chainer, fail, null

SERVICE = "smugback"
# One item holds everything, so logout removes it all at once
ITEM = "credentials"


class InsecureStoreError(Exception):
    """No secure credential store is available on this machine."""


@dataclass(frozen=True)
class Credentials:
    api_key: str
    # repr=False keeps secrets out of tracebacks and debug output
    api_secret: str = field(repr=False)
    token: str = field(repr=False)
    token_secret: str = field(repr=False)


def is_secure(backend) -> bool:
    """Whether a keyring backend really stores secrets securely."""
    # keyrings.alt holds plain-text and other weak stores
    if type(backend).__module__.startswith("keyrings.alt"):
        return False
    if isinstance(backend, fail.Keyring | null.Keyring):
        return False
    if isinstance(backend, chainer.ChainerBackend):
        return bool(backend.backends) and all(is_secure(b) for b in backend.backends)
    return True


def check_secure_store() -> None:
    if not is_secure(keyring.get_keyring()):
        raise InsecureStoreError(
            "No secure credential store is available, so SmugBack won't store "
            "your SmugMug credentials. SmugBack needs the macOS Keychain."
        )


def save(credentials: Credentials) -> None:
    check_secure_store()
    keyring.set_password(SERVICE, ITEM, json.dumps(asdict(credentials)))


def load() -> Credentials | None:
    stored = keyring.get_password(SERVICE, ITEM)
    return Credentials(**json.loads(stored)) if stored else None


def delete() -> None:
    if keyring.get_password(SERVICE, ITEM) is not None:
        keyring.delete_password(SERVICE, ITEM)
