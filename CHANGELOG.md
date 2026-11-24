# Changelog

All notable changes to this project are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the
project uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html). Every pull
request adds its entries under `Unreleased`; a release moves them under a version
heading and is tagged `vX.Y.Z`.

## [Unreleased]

### Added

- The `smugback` command, with `--version` and `--help` (CR-0002).
- Python toolchain: uv with a lockfile, pytest and ruff, and `make check` to run
  every check, locally and in CI (CR-0002).
- `smugback login` and `smugback logout`: sign in to SmugMug with your own API key,
  keeping the credentials only in the macOS Keychain (CR-0003).
- `smugback albums`: list every album in your SmugMug account (CR-0003).
- `smugback` with no arguments prints the help (CR-0003).

### Security

- Coding agents' sandbox can no longer read the login Keychain (CR-0003).

[Unreleased]: https://github.com/sam-tmts/smugback/commits/main
