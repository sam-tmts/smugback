"""The `smugback` command."""

import argparse
from importlib.metadata import version


def main(argv: list[str] | None = None) -> None:
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
    parser.parse_args(argv)
