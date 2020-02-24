# code42

`code42` is a CLI tool for extracting AED events. 
Additionally, `code42` can record a checkpoint so that you only get events you have not previously gotten.

## Requirements

- Python 2.7.x or 3.5.0+
- Code42 Server 6.8.x+

## Installation
Install `code42` using:

```bash
$ python setup.py install
```

## Usage

First, set your profile:
```bash
code42 profile set -s https://example.authority.com -u security.admin@example.com
```
Your profile contains the necessary properties for logging into Code42 servers.
You will prompted for a password if there is not one saved for your current username/authority URL combination.

To explicitly set your password, use `-p`:
```bash
code42 profile set -p
```
You will be securely prompted to input your password.
Your password is not stored in plain-text, and is not shown when you do `code42 profile show`.
However, `code42 profile show` will confirm that there is a password set for your profile.

To ignore SSL errors, do:
```bash
code42 profile set --disable-ssl-errors
```

To re-enable SSL errors, do:
```bash
code42 profile set --enable-ssl-errors
```

Next, you can query for events and send them to three possible destination types
* STDOUT
* A file
* A server, such as SysLog

To print events to STDOUT, do:
```bash
code42 print
```

To write events to a file, do:
```bash
code42 write-to filename.txt
```

To send events to a server, do:
```bash
code42 send-to https://syslog.company.com -p TCP
```

Each destination-type subcommand shares query parameters
* `-t` (exposure types)
* `-b` (begin date)
* `-e` (end date)
* `--advanced-query` (raw JSON query)

Note that you cannot use other query parameters if you use `--advanced-query`.

To learn more about acceptable arguments, add the `-h` flag to `code42` or and of the destination-type subcommands.


# Known Issues

Only the first 10,000 of each set of events containing the exact same insertion timestamp is reported.
