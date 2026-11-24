"""The `smugback` command."""

import argparse
import getpass
import sys
import webbrowser
from importlib.metadata import version

from keyring.errors import KeyringError

from smugback import credentials, smugmug
from smugback.credentials import Credentials, InsecureStoreError
from smugback.smugmug import SmugMug, SmugMugError


def login(args: argparse.Namespace) -> int:
    # Check before asking for anything, so the owner isn't asked for a secret
    # that can't be stored
    credentials.check_secure_store()
    api_key = input("SmugMug API key: ").strip()
    api_secret = getpass.getpass("SmugMug API secret: ").strip()
    request_token, request_secret = smugmug.get_request_token(api_key, api_secret)
    url = smugmug.authorize_url(request_token)
    print(f"Sign in to SmugMug and approve SmugBack at:\n  {url}")
    webbrowser.open(url)
    pin = input("Six-digit code from SmugMug: ").strip()
    token, token_secret = smugmug.get_access_token(
        api_key, api_secret, request_token, request_secret, pin
    )
    credentials.save(Credentials(api_key, api_secret, token, token_secret))
    print("Signed in. Your credentials are in the macOS Keychain.")
    return 0


def logout(args: argparse.Namespace) -> int:
    credentials.delete()
    print("Signed out: SmugBack's credentials are removed from the Keychain.")
    return 0


def albums(args: argparse.Namespace) -> int:
    stored = credentials.load()
    if stored is None:
        print("Not signed in. Run `smugback login` first.", file=sys.stderr)
        return 1
    for album in SmugMug(stored).albums():
        print(f"{album['Name']} ({item_count(album.get('ImageCount', 0))})")
    return 0


def item_count(count: int) -> str:
    return f"{count} item" if count == 1 else f"{count} items"


def build_parser() -> argparse.ArgumentParser:
    # prog is fixed so usage reads "smugback" however the command is started
    parser = argparse.ArgumentParser(
        prog="smugback",
        description="Back up a SmugMug account's photos and videos to a local folder.",
    )
    # The installed package's metadata comes from pyproject.toml, so the version
    # lives in one place
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {version('smugback')}"
    )
    commands = parser.add_subparsers(title="commands", metavar="<command>")
    for name, handler, help_text in [
        (
            "login",
            login,
            "sign in to SmugMug and store the credentials in the Keychain",
        ),
        ("logout", logout, "remove SmugBack's credentials from the Keychain"),
        ("albums", albums, "list every album in your SmugMug account"),
    ]:
        commands.add_parser(name, help=help_text).set_defaults(handler=handler)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not hasattr(args, "handler"):
        parser.print_help()
        return 0
    try:
        return args.handler(args)
    except (SmugMugError, InsecureStoreError) as error:
        print(f"smugback: {error}", file=sys.stderr)
    except KeyringError:
        # The Keychain refused (for example, access was denied at its prompt)
        print("smugback: the Keychain refused the request.", file=sys.stderr)
    return 1
