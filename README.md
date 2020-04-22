# The Code42 CLI

Use the `code42` command to interact with your Code42 environment.

* `code42 security-data` is a CLI tool for extracting AED events.
    Additionally, you can choose to only get events that Code42 previously did not observe since you last recorded a 
    checkpoint (provided you do not change your query).
* `code42 high-risk-employee` is a collection of tools for managing the high risk employee detection list. Similarly, 
    there is `code42 departing-employee`.

## Requirements

- Python 2.7.x or 3.5.0+
- Code42 Server 6.8.x+

## Installation

Install the `code42` CLI using:

```bash
$ python setup.py install
```

## Usage

First, create your profile:
```bash
code42 profile create MY_FIRST_PROFILE https://example.authority.com security.admin@example.com
```

Your profile contains the necessary properties for logging into Code42 servers.
After running `code42 profile create`, the program prompts you about storing a password.
If you agree, you are then prompted to input your password.

Your password is not shown when you do `code42 profile show`.
However, `code42 profile show` will confirm that a password exists for your profile.
If you do not set a password, you will be securely prompted to enter a password each time you run a command.

For development purposes, you may need to ignore ssl errors. If you need to do this, use the `--disable-ssl-errors` option when creating your profile:

```bash
code42 profile create MY_FIRST_PROFILE https://example.authority.com security.admin@example.com --disable-ssl-errors
```

You can add multiple profiles with different names and the change the default profile with the `use` command:

```bash
code42 profile use MY_SECOND_PROFILE
```

When the `--profile` flag is available on other commands, such as those in `security-data`, it will use that profile instead of the default one.

To see all your profiles, do:

```bash
code42 profile list
```

## Security Data

Using the CLI, you can query for events and send them to three possible destination types:
* stdout
* A file
* A server, such as SysLog

To print events to stdout, do:

```bash
code42 security-data print -b <begin_date>
```

Note that `-b` or `--begin` is usually required.

And end date can also be given with `-e` or `--end` to query for a specific date range (if end is not passed, it will get all events up to the present time).

To specify a begin/end time, you can pass a date or a date w/ time as a string:

```bash
code42 security-data print -b '2020-02-02 12:51:00'
```

```bash
code42 security-data print -b '2020-02-02 12:30'
```

```bash
code42 security-data print -b '2020-02-02 12'
```

```bash
code42 security-data print -b 2020-02-02
```

or a shorthand string specifying either days, hours, or minutes back from the current time:

```bash
code42 security-data print -b 30d
```

```bash
code42 security-data print -b 10d -e 12h
```

Begin date will be ignored if provided on subsequent queries using `-i`.

Use different format with `-f`:

```bash
code42 security-data print -b 2020-02-02 -f CEF
```

The available formats are CEF, JSON, and RAW-JSON.

To write events to a file, do:

```bash
code42 security-data write-to filename.txt -b 2020-02-02
```

To send events to a server, do:

```bash
code42 security-data send-to syslog.company.com -p TCP -b 2020-02-02
```

To only get events that Code42 previously did not observe since you last recorded a checkpoint, use the `-i` flag.

```bash
code42 security-data send-to syslog.company.com -i
```

This is only guaranteed if you did not change your query.

To send events to a server using a specific profile, do:

```bash
code42 security-data send-to --profile PROFILE_FOR_RECURRING_JOB syslog.company.com -b 2020-02-02 -f CEF -i
```

You can also use wildcard for queries, but note, if they are not in quotes, you may get unexpected behavior.

```bash
code42 security-data print --actor "*"
```

Each destination-type subcommand shares query parameters

- `-t` (exposure types)
- `-b` (begin date)
- `-e` (end date)
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
To learn more about acceptable arguments, add the `-h` flag to `code42` or any of the destination-type subcommands.

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
