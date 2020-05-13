# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

The intended audience of this file is for py42 consumers -- as such, changes that don't affect
how a consumer would use the library (e.g. adding unit tests, updating documentation, etc) are not captured here.

## Unreleased

### Added

- Success messages for `profile delete` and `profile update`.
- Additional information in the error log file:
    - The full command path for the command that errored.
    - User-facing error messages you see during adhoc sessions.
- When you trying adding risk tags that are unknown, you will now get custom errors in the logs.
- When you try to add a user to a detection list who is already added, you will now get a custom error in the logs.

### 0.5.3 - 2020-05-04

### Fixed

- Issue introduced in py42 v1.1.0 that prevented `high-risk-employee` and `departing-employee` commands from working properly.

## 0.5.2 - 2020-04-29

### Fixed

- Issue that prevented bulk csv loading. 

## 0.5.1 - 2020-04-27

### Fixed

- Issue that prevented version 0.5.0 from updating its dependencies properly.

- Issue that prevented the `add` and `bulk add` functionality of `departing-employee` and `high-risk-employee` from successfully adding users to lists when specifying optional fields.

## 0.5.0 - 2020-04-24

### Changed

- `securitydata` renamed to `security-data`.
- From `security-data` related subcommands (such as `print`):
    - `--c42username` flag renamed to `--c42-username`.
    - `--filename` flag renamed to `--file-name`.
    - `--filepath` flag renamed to `--file-path`.
    - `--processOwner` flag renamed to `--process-owner`.
- `-b|--begin` and `-e|--end` arguments now accept shorthand date-range strings for days, hours, and minute intervals going back from the current time (e.g. `30d`, `24h`, `15m`).
- Default profile validation logic added to prevent confusing error states.

### Added

- `code42 profile update` command.
- `code42 profile create` command.
- `code42 profile delete` command.
- `code42 profile delete-all` command.
- `code42 high-risk-employee` commands:
    - `bulk` with subcommands:
        - `add`: that takes a csv file of users.
        - `generate-template`: that creates the file template. And parameters:
            - `cmd`: with options `add` and `remove`.
            - `path`
        - `remove`: that takes a list of users in a file.
    - `add` that takes parameters: `--username`, `--cloud-alias`, `--risk-factor`, and `--notes`.
    - `remove` that takes a username.
    - `add-risk-tags` that takes a username and risk tags.
    - `remove-risk-tags` that takes a username and risk tags.
- `code42 departing-employee` commands:
    - `bulk` with subcommands:
        - `add`: that takes a csv file of users.
        - `generate-template`: that creates the file template. And parameters:
            - `cmd`: with options `add` and `remove`.
            - `path`
        - `remove`: that takes a list of users in a file.
    - `add` that takes parameters: `--username`, `--cloud-alias`, `--departure-date`, and `--notes`.
    - `remove` that takes a username.

### Removed

- `code42 profile set` command. Use `code42 profile create` instead.

## 0.4.4 - 2020-04-01

### Added

- Added message to STDERR when no results are found

### Fixed

- Add milliseconds to end timestamp, to represent end of day with milliseconds precision.

## 0.4.3 - 2020-03-17

### Added

- Support for storing passwords when keying is not available.

### Fixed

- Bug where keyring caused errors on certain operating systems when not supported.

### Changed

- Updated help texts to be more descriptive.

## 0.4.2 - 2020-03-13

### Fixed

- Bug where encoding would cause an error when opening files on python2.

## 0.4.1 - 2020-03-13

### Fixed

- Bug where `profile reset-pw` did not work with the default profile.
- Bug where `profile show` indicated a password was set for a different profile.
- We now validate credentials when setting a password.

### Changed

- Date inputs are now required to be in quotes when they include a time.

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
