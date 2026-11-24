# One command for every automated check, locally and in CI (CR-0002 AC3).
# Make stops at the first failing command, so `make check` fails if any check fails.
.PHONY: check
check:
	uv run --locked pytest
	uv run --locked ruff check
	uv run --locked ruff format --check
