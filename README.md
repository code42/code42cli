# The Code42 CLI

Use the `code42` command to interact with your Code42 environment.
`code42 securitydata` is a CLI tool for extracting AED events.
Additionally, you can choose to only get events that Code42 previously did not observe since you last recorded a checkpoint
(provided you do not change your query).

## Requirements

- Python 2.7.x or 3.5.0+
- Code42 Server 6.8.x+

## Installation
Install the `code42` CLI using:

```bash
$ python setup.py install
```

## Usage

First, set your profile:
```bash
code42 profile set --profile MY_FIRST_PROFILE -s https://example.authority.com -u security.admin@example.com
```
The `--profile` flag is required the first time and it takes a name.
On subsequent uses of `set`, not specifying the profile will set the default profile.

Your profile contains the necessary properties for logging into Code42 servers.
After running `code42 profile set`, the program prompts you about storing a password.
If you agree, you are then prompted to input your password.

Your password is not stored in plain-text and is not shown when you do `code42 profile show`.
However, `code42 profile show` will confirm that a password exists for your profile.
If you do not set a password, you will be securely prompted to enter a password each time you run a command.

For development purposes, you may need to ignore ssl errors. If you need to do this, do:
```bash
code42 profile set --disable-ssl-errors
```

To re-enable SSL errors, do:
```bash
code42 profile set --enable-ssl-errors
```

You can add multiple profiles with different names and the change the default profile with the `use` command:
```bash
code42 profile use MY_SECOND_PROFILE
```
When the `--profile` flag is available on other commands, such as those in `securitydata`,
it will use that profile instead of the default one.

To see all your profiles, do:
```bash
code42 profile list
```

Using the CLI, you can query for events and send them to three possible destination types:
* stdout
* A file
* A server, such as SysLog

To print events to stdout, do:
```bash
code42 securitydata print -b 2020-02-02
```

Note that `-b` or `--begin` is usually required.
To specify a time, do:

```bash
code42 securitydata print -b 2020-02-02 12:51
```
Begin date will be ignored if provided on subsequent queries using `-i`.

Use different format with `-f`:
```bash
code42 securitydata print -b 2020-02-02 -f CEF
```
The available formats are CEF, JSON, and RAW-JSON.

To write events to a file, do:
```bash
code42 securitydata write-to filename.txt -b 2020-02-02
```

To send events to a server, do:
```bash
code42 securitydata send-to syslog.company.com -p TCP -b 2020-02-02
```

To only get events that Code42 previously did not observe since you last recorded a checkpoint, use the `-i` flag.
```bash
code42 securitydata send-to syslog.company.com -i
```
This is only guaranteed if you did not change your query.

To send events to a server using a specific profile, do:
```bash
code42 securitydata send-to --profile PROFILE_FOR_RECURRING_JOB syslog.company.com -b 2020-02-02 -f CEF -i
```

You can also use wildcard for queries, but note, if they are not in quotes, you may get unexpected behavior.
```bash
code42 securitydata print --actor "*"
```


Each destination-type subcommand shares query parameters
* `-t` (exposure types)
* `-b` (begin date)
* `-e` (end date)
* `--c42username`
* `--actor`
* `--md5`
* `--sha256`
* `--source`
* `--filename`
* `--filepath`
* `--processOwner`
* `--tabURL`
* `--include-non-exposure` (does not work with `-t`)
* `--advanced-query` (raw JSON query)

You cannot use other query parameters if you use `--advanced-query`.
To learn more about acceptable arguments, add the `-h` flag to `code42` or any of the destination-type subcommands.


# Known Issues

Only the first 10,000 of each set of events containing the exact same insertion timestamp is reported.


# Troubleshooting

If you keep getting prompted for your password, try resetting with `code42 profile reset-pw`.
If that doesn't work, delete your credentials file located at ~/.code42cli or the entry in keychain.
