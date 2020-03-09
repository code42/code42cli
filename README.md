# The Code42 CLI

Use the `code42` command to interact with your Code42 environment.
`code42 securitydata` is a CLI tool for extracting AED events.
Additionally, `code42 securitydata` can record a checkpoint so that you only get events you have not previously gotten
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
code42 profile set -s https://example.authority.com -u security.admin@example.com
```
Your profile contains the necessary properties for logging into Code42 servers.
After running this `code42 profile set`, you will be prompted about storing a password.
If you agree, you will be securely prompted to input your password.
Your password is not stored in plain-text, and is not shown when you do `code42 profile show`.
However, `code42 profile show` will confirm that there is a password set for your profile.
If you do not set a password, you will be securely prompted to enter a password each time you run a command.

To ignore SSL errors, do:
```bash
code42 profile set --disable-ssl-errors
```

To re-enable SSL errors, do:
```bash
code42 profile set --enable-ssl-errors
```

Next, you can query for events and send them to three possible destination types
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

To write events to a file, do:
```bash
code42 securitydata write-to filename.txt -b 2020-02-02
```

To send events to a server, do:
```bash
code42 securitydata send-to syslog.company.com -p TCP -b 2020-02-02
```

To only get events you did not get previously for the same query, use incremental mode with the `-i` flag:
```bash
code42 securitydata send-to syslog.company.com -i
```

Note that begin date will be ignored if provided on subsequent queries using `-i`.


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

Note that you cannot use other query parameters if you use `--advanced-query`.

To learn more about acceptable arguments, add the `-h` flag to `code42` or and of the destination-type subcommands.


# Known Issues

Only the first 10,000 of each set of events containing the exact same insertion timestamp is reported.
