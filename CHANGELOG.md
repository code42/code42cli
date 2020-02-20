# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

The intended audience of this file is for py42 consumers -- as such, changes that don't affect
how a consumer would use the library (e.g. adding unit tests, updating documentation, etc) are not captured here.

## Unreleased

### Removed
- Removed config file settings and `-c` CLI arg. Use `c42sec profile set`.
- Removed `--clear-password` CLI argument. Use `c42sec profile set -p`. You will be prompted.
- Removed top-level destination args. Use subcommands `write-to`. `send-to`, `print`.

### Added
- Added ability to view your profile: `c42sec profile show`.
- Added `write-to` subcommand that outputs to a file.
- Added `send-to` subcommand that outputs to a server.
- Added `print` subcommand that outputs to STDOUT.
- Added `clear-cursor` subcommand that removes the stored cursor for 'incremental' mode.

### Changed
- Renamed `c42aed` to `c42sec`.
- Moved CLI arguments `-s`, `-u`, and `--ignore-ssl-errors` to `c42sec profile set` command.
- Renamed and moved top-level `-r` flag. Use `-i` on one of these subcommands: `write-to`. `send-to`, `print`.
- Moved query arguments to individual subcommands `write-to`. `send-to`, `print`.

## 0.1.1 - 2019-10-29

### Fixed
- Issue where IOError message was inaccurate when using the wrong port for server destinations.

### Added
- Error handling for all socket errors.
- Error handling for IOError 'connection refused'.
