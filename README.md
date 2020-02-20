# c42sec

The c42seceventcli AED module contains a CLI tool for extracting AED events as well as an optional state manager 
for recording timestamps. The state manager records timestamps so that on future runs,
you only extract events you did not previously extract.

## Requirements

- Python 2.7.x or 3.5.0+
- Code42 Server 6.8.x+

## Installation
Install `c42sec` using:

```bash
$ python setup.py install
```

## Usage

First, set your profile

```bash
c42sec profile set -s https://example.authority.com -u security.admin@example.com -p
```

`-p` will prompt for your password securely. If your username does not have a password stored, you will be prompted anyway.

To ignore SSL errors, do:

```bash
c42sec profile set --ignore-ssl-errors true
```

To print events to STDOUT, do:
```bash
c42sec print
```

Configure your output format with the `-f` flag:

```bash
c42sec print -f CEF
```

To write events to a file, do:
```bash
c42sec write-to -f filename
```

To send events to a server, such as syslog, do:
```bash
c42sec send-to https://syslog.company.com
```

To only get events that you have not previously gotten, use the `-i` flag:
```bash
c42sec send-to https://syslog.company.com -i
```

To use an advanced query (raw JSON), use the `--advanced-query` flag:
```bash
c42sec send-to https://syslog.company.com --advanced-query 
```

Note: You cannot use begin date (`-b`), end date (`-e`), or any other query parameters when using an advanced query.

To learn more about any of the subcommands and their accepted arguments, add the `-h` flag.


# Known Issues

Only the first 10,000 of each set of events containing the exact same insertion timestamp is reported.
