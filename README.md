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

`-p` will prompt for your password securely.

To ignore SSL errors, do:

```bash
c42sec profile set --ignore-ssl-errors true
```

# Known Issues

Only the first 10,000 of each set of events containing the exact same insertion timestamp is reported.
