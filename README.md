# The Code42 CLI

![Build status](https://github.com/code42/code42cli/workflows/build/badge.svg)
[![codecov.io](https://codecov.io/github/code42/code42cli/coverage.svg?branch=master)](https://codecov.io/github/code42/code42cli?branch=master)
[![versions](https://img.shields.io/pypi/pyversions/code42cli.svg)](https://pypi.org/project/code42cli/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Documentation Status](https://readthedocs.org/projects/code42cli/badge/?version=latest)](https://clidocs.code42.com/en/latest/?badge=latest)

Use the `code42` command to interact with your Code42 environment.

* `code42 security-data` is a CLI tool for extracting AED events.
    Additionally, you can choose to only get events that Code42 previously did not observe since you last recorded a
    checkpoint (provided you do not change your query).
* `code42 high-risk-employee` is a collection of tools for managing the high risk employee detection list. Similarly,
    there is `code42 departing-employee`.

## Requirements

- Python 3.6.0+
- Code42 Server 6.8.x+

## Installation

Install the `code42` CLI using:

```bash
$ python3 -m pip install code42cli
```

## Usage

First, create your profile:
```bash
code42 profile create --name MY_FIRST_PROFILE --server example.authority.com --username security.admin@example.com
```

Your profile contains the necessary properties for logging into Code42 servers. After running `code42 profile create`,
the program prompts you about storing a password. If you agree, you are then prompted to input your password.

Your password is not shown when you do `code42 profile show`. However, `code42 profile show` will confirm that a
password exists for your profile. If you do not set a password, you will be securely prompted to enter a password each
time you run a command.

For development purposes, you may need to ignore ssl errors. If you need to do this, use the `--disable-ssl-errors`
option when creating your profile:

```bash
code42 profile create -n MY_FIRST_PROFILE -s https://example.authority.com -u security.admin@example.com --disable-ssl-errors
```

You can add multiple profiles with different names and the change the default profile with the `use` command:

```bash
code42 profile use MY_SECOND_PROFILE
```

When the `--profile` flag is available on other commands, such as those in `security-data`, it will use that profile
instead of the default one. For example,

```bash
code42 security-data search -b 2020-02-02 --profile MY_SECOND_PROFILE
```

To see all your profiles, do:

```bash
code42 profile list
```

## Security Data and Alerts

Using the CLI, you can query for security events and alerts just like in the admin console, but the results are output
to stdout so they can be written to a file or piped out to another process (for sending to an external syslog server, for
example).


The following examples pertain to security events, but can also be used for alerts by replacing `security-data` with
`alerts`:

To print events to stdout, do:

```bash
code42 security-data search -b <begin_date>
```

Note that `-b` or `--begin` is usually required.

And end date can also be given with `-e` or `--end` to query for a specific date range (if end is not passed, it will get all events up to the present time).

To specify a begin/end time, you can pass a date or a date w/ time as a string:

```bash
code42 security-data search -b '2020-02-02 12:51:00'
```

```bash
code42 security-data search -b '2020-02-02 12:30'
```

```bash
code42 security-data search -b '2020-02-02 12'
```

```bash
code42 security-data search -b 2020-02-02
```

or a shorthand string specifying either days, hours, or minutes back from the current time:

```bash
code42 security-data search -b 30d
```

```bash
code42 security-data search -b 10d -e 12h
```

Begin date will be ignored if provided on subsequent queries using `-c/--use-checkpoint`.

Use other formats with `-f`:

```bash
code42 security-data search -b 2020-02-02 -f CEF
```

The available formats are CEF, JSON, and RAW-JSON.
Currently, CEF format is only supported for security events.

To write events to a file, just redirect your output:

```bash
code42 security-data search -b 2020-02-02 > filename.txt
```

To send events to an external server, use the `send-to` command, which behaves the same as `search` except for defaulting
to `RAW-JSON` output and sending results to an external server instead of to stdout:

The default port (if none is specified on the address) is the standard syslog port 514, and default protocol is UDP:

```bash
code42 security-data send-to 10.10.10.42 -b 1d
```

Results can also be sent over TCP to any port by using the `-p/--protocol` flag and adding a port to the address argument:

```bash
code42 security-data send-to 10.10.10.42:8080 -p TCP -b 1d
```

Note: For more complex requirements when sending to an external server (SSL, special formatting, etc.), use a dedicated
syslog forwarding tool like `rsyslog` or connection tunneling tool like `stunnel`.

If you want to periodically run the same query, but only retrieve the new events each time, use the
`-c/--use-checkpoint` option with a name for your checkpoint. This stores the timestamp of the query's last event to a
file on disk and uses that as the "begin date" timestamp filter on the next query that uses the same checkpoint name.
Checkpoints are stored per profile.

Initial run requires a begin date:
```bash
code42 security-data search -b 30d --use-checkpoint my_checkpoint
```

Subsequent runs do not:
```bash
code42 security-data search --use-checkpoint my_checkpoint
```

You can also use wildcard for queries, but note, if they are not in quotes, you may get unexpected behavior.

```bash
code42 security-data search --actor "*"
```

The search query parameters are as follows:

- `-t/--type` (exposure types)
- `-b/--begin` (begin date)
- `-e/--end` (end date)
- `--c42-username`
- `--actor`
- `--md5`
- `--sha256`
- `--source`
- `--file-name`
- `--file-path`
- `--process-owner`
- `--tab-url`
- `--include-non-exposure` (does not work with `-t`)
- `--advanced-query` (raw JSON query)

You cannot use other query parameters if you use `--advanced-query`.
To learn more about acceptable arguments, add the `-h` flag to `code42 security-data`

Saved Searches:

The CLI can also access "saved searches" that are stored in the admin console, and run them via their saved search ID.

Use the `saved-search list` subcommand to list existing searches with their IDs:

```bash
code42 security-data saved-search list
```

The `show` subcommand will give details about the search with the provided ID:

```bash
code42 security-data saved-search show <ID>
```

To get the results of a saved search, use the `--saved-search` option with your search ID on the `search` subcommand:

```bash
code42 security-data search --saved-search <ID>
```

## Detection Lists

You can both add and remove employees from detection lists using the CLI. This example uses `high-risk-employee`.

```bash
code42 high-risk-employee add user@example.com --notes "These are notes"
code42 high-risk-employee remove user@example.com
```

Detection lists include a `bulk` command. To add employees to a list, you can pass in a csv file. First, generate the
csv file for the desired command by executing the `generate-template` command:

```bash
code42 high-risk-employee bulk generate-template add
```

Notice that `generate-template` takes a `cmd` parameter for determining what type of template to generate. In the
example above, we give it the value `add` to generate a file for bulk adding users to the high risk employee list.

Next, fill out the csv file with all the users and then pass it in as a parameter to `bulk add`:

```bash
code42 high-risk-employee bulk add users_to_add.csv
```

Note that for `bulk remove`, the file only has to be an end-line delimited list of users with one line per user.

## Known Issues

In `security-data`, only the first 10,000 of each set of events containing the exact same insertion timestamp is
reported.

## Troubleshooting

If you keep getting prompted for your password, try resetting with `code42 profile reset-pw`.
If that doesn't work, delete your credentials file located at ~/.code42cli or the entry in keychain.

## Shell tab completion

To enable shell autocomplete when you hit `tab` after the first few characters of a command name, do the following:

For Bash, add this to ~/.bashrc:

```
eval "$(_CODE42_COMPLETE=source_bash code42)"
```

For Zsh, add this to ~/.zshrc:

```
eval "$(_CODE42_COMPLETE=source_zsh code42)"
```

For Fish, add this to ~/.config/fish/completions/code42.fish:

```
eval (env _CODE42_COMPLETE=source_fish code42)
```

Open a new shell to enable completion. Or run the eval command directly in your current shell to enable it temporarily.


## Writing Extensions

The CLI exposes a few helpers for writing custom extension scripts powered by the CLI. Read the user-guide [here](https://clidocs.code42.com/en/feature-extension_scripts/userguides/extensions.html).
