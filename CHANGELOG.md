# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

The intended audience of this file is for py42 consumers -- as such, changes that don't affect
how a consumer would use the library (e.g. adding unit tests, updating documentation, etc) are not captured here.

## 1.4.2 - 2021-04-22

### Fixed

- Bug where some CSV outputs on Windows would have an extra newline between the rows.

- Issue where outputting or sending an alert or file-event with a timestamp without
  decimals would error.

- A performance issue with the `code42 departing-employee bulk add` command.

### Changed

- `code42 alert-rules list` now outputs via a pager when results contain more than 10 rules.

- `code42 cases list` now outputs via a pager when results contain more than 10 cases.

## 1.4.1 - 2021-04-15

### Added

- `code42 legal-hold search-events` command:
    - `--matter-id` filters based on a legal hold uid.
    - `--begin` filters based on a beginning timestamp.
    - `--end` filters based on an end timestamp.
    - `--event-type` filters based on a list of event types.

### Fixed

- Arguments/options that read data from files now attempt to autodetect file encodings.
  Resolving a bug where CSVs written on Windows with Powershell would fail to be read properly.

## 1.4.0 - 2021-03-09

### Added

- `code42cli.extensions` module exposes `sdk_options` decorator and `script` group for writing custom extension scripts
    using the Code42 CLI.

- `code42 devices list` options:
    - `--include-legal-hold-membership` prints the legal hold matter name and ID for any active device on legal hold
    - `--include-total-storage` prints the backup archive count and total storage

## 1.3.1 - 2021-02-25

### Changed

- Command options for `profile update`:
    - `-n` `--name` is not required, and if omitted will use the default profile.
    - `-s` `--server` and `-u` `--username` are not required and can be updated independently now.
    - Example: `code42 profile update -s 1.2.3.4:1234`

## 1.3.0 - 2021-02-11

### Fixed

- Issue where `code42 alert-rules bulk add` would show as successful when adding users to a non-existent alert rule.

### Added

- New choice `TLS-TCP` for `--protocol` option used by `send-to` commands:
    - `code42 security-data send-to`
    - `code42 alerts send-to`
    - `code42 audit-logs send-to`
  for more securely transporting data. Included are new flags:
    - `--certs`
    - `--ignore-cert-validation`

### Changed

- The error text in cases command when:
    - `cases create` sets a name that already exists in the system.
    - `cases create` sets a description that has more than 250 characters.
    - `cases update` sets a description that has more than 250 characters.
    - `cases file-events add` is performed on an already closed case.
    - `cases file-events add` sets an event id that is already added to the case.
    - `cases file-events remove` is performed on an already closed case.

## 1.2.0 - 2021-01-25

### Added

- The `devices` command is added. Included are:
    - `devices deactivate` to deactivate a single device.
    - `devices reactivate` to reactivate a single device.
    - `devices show` to retrieve detailed information about a device.
    - `devices list` to retrieve info about many devices, including device settings.
    - `devices list-backup-sets` to retrieve detailed info about device backup sets.
    - `devices bulk deactivate` to deactivate a list of devices.
    - `devices bulk reactivate` to reactivate a list of devices.
    - `devices bulk generate-template` to create a blank CSV file for bulk commands.

- `code42 departing-employee list` command.

- `code42 high-risk-employee list` command.

- `code42 cases` commands:
    - `create` to create a new case.
    - `update` to update case details.
    - `export` to download a case summary as a PDF file.
    - `list` to view all cases.
    - `show` to view the details of a particular case.

- `code42 cases file-events` commands:
    - `add` to add an event to a case.
    - `remove` to remove an event from a case.
    - `list` to view all events associated with a case.

### Changed

- The error text when removing an employee from a detection list now references the employee
  by ID rather than the username.

- Improved help text for date option arguments.

## 1.1.0 - 2020-12-18

### Fixed

- Issue where `code42 profile delete` was allowed without giving a `profile_name` even
  though deleting the default profile is not allowed.

### Added

- `code42 audit-logs` commands:
    - `search` to search for audit-logs.
    - `send-to` to send audit-logs to server.

### Changed

- `profile_name` argument is now required for `code42 profile delete`, as it was meant to be.

- The `--advanced-query` option on `alerts search` and `security-data (search|send-to)` commands has been updated:
    - It can now accept the query as a JSON string or as the path to a file containing the JSON query.
    - It can be used with the `--use-checkpoint/-c` option.

- Now, when adding a cloud alias to a detection list user, such as during `departing-employee add`, it will remove the existing cloud alias if one exists.
    - Before, it would error and the cloud alias would not get added.

## 1.0.0 - 2020-08-31

### Fixed

- Bug where `code42 legal-hold show` would error when terminal was too small.

- Fixed bug in `departing_employee bulk add` command that allowed invalid dates to be passed without validation.

### Changed

- The follow commands now print a nicer error message when trying to remove a user who is not on the list:
    - `code42 departing-employee remove`
    - `code42 high-risk-employee remove`
    - `code42 alert-rules remove-user`

- `-i` (`--incremental`) has been removed, use `-c` (`--use-checkpoint`) with a string name for the checkpoint instead.

- The code42cli has been migrated to the [click](https://click.palletsprojects.com) framework. This brings:
    - BREAKING CHANGE: Commands that accept multiple values for the same option now must have the option flag provided before each value:
        use `--option value1 --option value2` instead of `--option value1 value2` (which was previously possible).
    - Cosmetic changes to error messages, progress bars, and help message formatting.

- The `print` command on the `security-data` and `alerts` command groups has been replaced with the `search` command.
    This was a name change only, all other functionality remains the same.

- A profile created with the `--disable-ssl-errors` flag will now correctly not verify SSL certs when making requests. A warning message is printed
    each time the CLI is run with a profile configured this way, as it is not recommended.

- The `path` positional argument for bulk `generate-template` commands is now an option (`--p/-p`).

- Below `search` subcommands accept argument `--format/-f` to display result in formats `csv`, `table`, `json`, `raw-json`:
    - Default output format is changed to `table` format from `raw-json`, returns a paginated response.
    All properties would be displayed by default except when using `-f table`.
    Pass `--include-all` when using `table` to view all non-nested top-level properties.
    - `code42 alerts search`
    - `code42 security-data search`
    - `code42 security-data saved-search list`
    - `code42 legal-hold list`
    - `code42 alert-rules list`

### Added

- `--or-query` option added to `security-data search` and `alerts search` commands which combines the provided filter arguments into an 'OR' query instead of the default 'AND' query.

- `--password` option added to `profile create` and `profile update` commands, enabling creating profiles while bypassing the interactive password prompt.

- Profiles can now save multiple alert and file event checkpoints. The name of the checkpoint to be used for a given query should be passed to `-c` (`--use-checkpoint`).

- `-y/--assume-yes` option added to `profile delete` and `profile delete-all` commands to not require interactive prompt.

- Below subcommands accept argument `--format/-f` to display result in formats `csv`, `table`, `json`, `formatted-json`:
    - `code42 alert-rules list`
    - `code42 legal-hold list`
    - `code42 legal-hold show`
    - `code42 security-data saved-search list`

### Removed

- The `write-to` command for `security-data` and `alerts` command groups.

## 0.7.3 - 2020-06-23

### Fixed

- Fixed bug that caused the last few entries in csv files to sometimes not be processed when performing bulk processing actions.

## 0.7.2 - 2020-06-11

### Fixed

- Fixed bug that caused `alert-rules list` to error due to page size restrictions on backing service.

## 0.7.1 - 2020-06-10

### Fixed

- Issue that prevented alerts from being retrieved successfully via `code42 alerts` commands due to a change in its backing API.

## 0.7.0 - 2020-06-08

### Changed

- `code42cli` no longer supports python 2.7.

- `code42 profile create` now uses required `--name`, `--server` and `--username` flags instead of positional arguments.

- `code42 high-risk-employee add-risk-tags` now uses required `--username` and `--tag` flags instead of positional arguments.

- `code42 high-risk-employee remove-risk-tags` now uses required `--username` and `--tag` flags instead of positional arguments.

### Added

- Extraction subcommands of `code42 security-data`, `print/write-to/send-to` accepts argument `--saved-search` to
   return saved search results.

- `code42 security-data saved-search` commands:
    - `list` prints out existing saved searches' id and name
    - `show` takes a search id

- `code42 high-risk-employee bulk` supports `add-risk-tags` and `remove-risk-tags`.
    - `code42 high-risk-employee bulk generate-template <cmd>` options `add-risk-tags` and `remove-risk-tags`.
        - `add-risk-tags` that takes a csv file with username and space separated risk tags.
        - `remove-risk-tags` that takes a csv file with username and space separated risk tags.

- Display, `Fuzzy suggestions`, valid keywords matching mistyped commands or arguments.

- `code42 alerts`:
    - Ability to search/poll for alerts with checkpointing using one of the following commands:
      - `print` to output to stdout.
      - `write-to` to output to a file.
      - `send-to` to output to server via UDP or TCP.

- `code42 alert-rules` commands:
    - `add-user` with parameters `--rule-id` and `--username`.
    - `remove-user` that takes a rule ID and optionally `--username`.
    - `list`.
    - `show` takes a rule ID.
    - `bulk` with subcommands:
        - `add`: that takes a csv file with rule IDs and usernames.
        - `generate-template`: that creates the file template. And parameters:
            - `cmd`: with options `add` and `remove`.
            - `path`
        - `remove`: that takes a csv file with rule IDs and usernames.

- `code42 legal-hold` commands:
    - `add-user` with parameters `--matter-id/-m` and `--username/-u`.
    - `remove-user` with parameters `--matter-id/-m` and `--username/-u`.
    - `list` prints out existing active legal hold matters.
    - `show` takes a `matter_id` and prints details of the matter.
        - optional argument `--include-inactive` additionally prints matter memberships that are no longer active.
        - optional argument `--include-policy` additionally prints out the matter's backup preservation policy in json form.
    - `bulk` with subcommands:
        - `add-user`: that takes a csv file with matter IDs and usernames.
        - `remove-user`: that takes a csv file with matter IDs and usernames.
        - `generate-template`: that creates the file templates.
            - `cmd`: with options `add` and `remove`.
            - `path`

- Success messages for `profile delete` and `profile update`.

- Additional information in the error log file:
    - The full command path for the command that errored.
    - User-facing error messages you see during adhoc sessions.

- A custom error in the error log when you try adding unknown risk tags to user.

- A custom error in the error log when you try adding a user to a detection list who is already added.
- Graceful handling of keyboard interrupts (ctrl-c) so stack traces aren't printed to console.
- Warning message printed when ctrl-c is encountered in the middle of an operation that could cause incorrect checkpoint
    state, a second ctrl-c is required to quit while that operation is ongoing.

- A progress bar that displays during bulk commands.

- Short option `-u` added for `code42 high-risk-employee add-risk-tags` and `remove-risk-tags`.

- Tab completion for bash and zsh for Unix based machines.

### Fixed

- Fixed bug in bulk commands where value-less fields in csv files were treated as empty strings instead of None.
- Fixed anomaly where the path to the error log on Windows contained mixed slashes.

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
