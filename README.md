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
After running `code42 profile set`, you will be prompted about storing a password.
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

You can add multiple profiles with different names and the change the default profile with the `use` command:
```bash
code42 profile use MY_SECOND_PROFILE
```

To see all your profiles, do:
```bash
code42 profile list
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
Begin date will be ignored if provided on subsequent queries using `-i`.

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

You can also use wildcard for queries, but note, they must be in quotes:
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
To learn more about acceptable arguments, add the `-h` flag to `code42` or and of the destination-type subcommands.


# Known Issues

Only the first 10,000 of each set of events containing the exact same insertion timestamp is reported.
