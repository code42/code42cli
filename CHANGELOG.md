# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

The intended audience of this file is for py42 consumers -- as such, changes that don't affect
how a consumer would use the library (e.g. adding unit tests, updating documentation, etc) are not captured here.

## Unreleased

- Renamed `c42aed` to `c42sec`.
- Broke up arguments for setting username, password, authority URL, and whether to ignore SSL errors into subcommand.
- Removed config file settings. Use `c42sec profile set`.
- Added ability to view your profile: `c4sec profile show`.

## 0.1.1 - 2019-10-29

### Fixed
- Issue where IOError message was inaccurate when using the wrong port for server destinations.

### Added
- Error handling for all socket errors.
- Error handling for IOError 'connection refused'.
