# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

The intended audience of this file is for py42 consumers -- as such, changes that don't affect
how a consumer would use the library (e.g. adding unit tests, updating documentation, etc) are not captured here.

## 0.4.1 - 2020-03-12

### Fixed

- Bug where `profile reset-pw` would create a bad entry in keychain when using the default profile.
- Bug where `profile show` indicated a password was set for a different profile.
- We now validate credentials when setting a password.

## 0.4.0 - 2020-03-12

### Added

- Support for multiple profiles:
    - Optional `--profile` flag for:
        - `securitydata write-to`, `print`, and `send-to`,
        - `profile show`, `set`, and `reset-pw`.
    - `code42 profile use` command for changing the default profile.
    - `code42 profile list` command for listing all the available profiles.
- The following search args can now take multiple values:
    - `--c42username`,
    - `--actor`,
    - `--md5`,
    - `--sha256`,
    - `--filename`,
    - `--filepath`,
    - `--processOwner`,
    - `--tabURL`

### Fixed

- Fixed bug where port attached to `securitydata send-to` command was not properly applied.

### Changed

- Begin dates are no longer required for subsequent interactive `securitydata` commands.
- When provided, begin dates are now ignored on subsequent interactive `securitydata` commands.
- `--profile` arg is now required the first time setting up a profile.

## 0.3.0 - 2020-03-04

### Added

- Begin and end date now support specifying time: `code42 securitydata print -b 2020-02-02 12:00:00`.
- If running interactively and errors occur, you will be told them at the end of `code42 securitydata` commands.
- New search arguments for `print`, `write-to`, and `send-to`:
    - `--c42username`
    - `--actor`
    - `--md5`
    - `--sha256`
    - `--source`
    - `--filename`
    - `--filepath`
    - `--processOwner`
    - `--tabURL`
    - `--include-non-exposure`

### Changed

- It is no longer required to store your password in your profile,
    and you will be prompted to enter your password at runtime if you don't.
- You will be asked if you would like to set a password after using `code42cli profile set`.
- Begin date is now required for `securitydata` `print`, `write-to`, and `send-to` commands.

### Removed

- Removed `--show` flag from `code42 profile set` command. Just use `code42 profile show`.

## 0.2.0 - 2020-02-25

### Removed

- Removed config file settings and `-c` CLI arg. Use `code42 profile set`.
- Removed `--clear-password` CLI argument. Use `code42 profile set -p`. You will be prompted.
- Removed top-level destination args. Use subcommands `write-to`. `send-to`, `print` off of `code42 security data`.

### Added

- Added ability to view your profile: `code42 profile show`.
- Added `securitydata` subcommands:
    - Use `code42 securitydata write-to` to output to a file.
    - Use `code42 securitydata send-to` to output to a server.
    - Use `code42 securitydata print` to outputs to stdout.
    - Use `code42 securitydata clear-cursor` to remove the stored cursor for 'incremental' mode.
- Added support for raw JSON queries via `code42 securitydata [subcommand] --advanced-query [JSON]`.

### Changed

- Renamed base command `c42aed` to `code42`.
- Moved CLI arguments `-s`, `-u`, and `--ignore-ssl-errors` to `code42 profile set` command.
- Renamed and moved top-level `-r` flag.
    - Use `-i` on one of these `securitydata` subcommands `write-to`. `send-to`, `print`.
- Moved search arguments to individual `securitydata` subcommands `write-to`. `send-to`, `print`.

## 0.1.1 - 2019-10-29

### Fixed

- Issue where IOError message was inaccurate when using the wrong port for server destinations.

### Added

- Error handling for all socket errors.
- Error handling for IOError 'connection refused'.
