# c42seceventcli - AED

The c42seceventcli AED module contains a CLI for extracting AED events as well as a state manager
for recording and retrieving insertion timestamps. This project uses the insertion timestamp of the 
most recently extracted event as a cursor so that only new events come through on subsequent runs.


## Usage

A simple usage requires you to pass in your Code42 authority URL and username as arguments:

```bash
c42aed -s https://example.authority.com -u security.admin@example.com
```
        
Another option is to put your Code42 authority URL and username in a file named `config.cfg`. 
Rename `config.default.cfg` to `config.cfg` and edit the fields to be your
authority server URL and username.

```buildoutcfg
[Code42]
username=user@code42.com
server=https://example.authority.com
```

Then, run the script as follows:

```bash
c42aed
```

If this is the first run, it will prompt you for your password.

If you get a keychain error when running this script, you may have to add a code signature:

```bash
codesign -f -s - $(which python)
```

Full usage:

```
usage: event_extraction_cli.py [-e C42_END_DATE | -r] [-s C42_AUTHORITY_URL]
                               [-u C42_USERNAME] [-h] [-b C42_BEGIN_DATE] [-i]
                               [-o {CEF,JSON}]
                               [-t [{SharedViaLink,SharedToDomain,ApplicationRead,CloudStorage,RemovableMedia,IsPublic} [{SharedViaLink,SharedToDomain,ApplicationRead,CloudStorage,RemovableMedia,IsPublic} ...]]]
                               [-d--debug] [--dest-type {stdout,file,syslog}]
                               [--dest C42_DESTINATION]
                               [--dest-port C42_SYSLOG_PORT]
                               [--dest-protocol {TCP,UDP}]

optional arguments:
  -e C42_END_DATE, --end C42_END_DATE
                        The beginning of the date range in which to look for
                        events, in YYYY-``MM-DD UTC format OR a number (number
                        of minutes ago).
  -r, --record-cursor   Used to only get new events on subsequent runs.

main:
  -s C42_AUTHORITY_URL, --server C42_AUTHORITY_URL
                        The full scheme, url and port of the Code42 server.
  -u C42_USERNAME, --username C42_USERNAME
                        The username of the Code42 API user.
  -h, --help            Show this help message and exit
  -b C42_BEGIN_DATE, --begin C42_BEGIN_DATE
                        The end of the date range in which to look for events,
                        in YYYY-MM-DD UTC format OR a number (number of
                        minutes ago).
  -i, --ignore-ssl-errors
                        Set to ignore ssl errors.
  -o {CEF,JSON}, --output-format {CEF,JSON}
                        The format used for outputting events.
  -t [{SharedViaLink,SharedToDomain,ApplicationRead,CloudStorage,RemovableMedia,IsPublic} [{SharedViaLink,SharedToDomain,ApplicationRead,CloudStorage,RemovableMedia,IsPublic} ...]], --types [{SharedViaLink,SharedToDomain,ApplicationRead,CloudStorage,RemovableMedia,IsPublic} [{SharedViaLink,SharedToDomain,ApplicationRead,CloudStorage,RemovableMedia,IsPublic} ...]]
                        The events with given exposure types to extract.
  -d--debug             Set to turn on debug logging.
  --dest-type {stdout,file,syslog}
                        The type of destination to send output to.
  --dest C42_DESTINATION
                        Either a name of a local file or SysLog host address.
                        Ignored if destination type is stdout.
  --dest-port C42_SYSLOG_PORT
                        Port used on SysLog destination. Ignored if
                        destination type is not SysLog.
  --dest-protocol {TCP,UDP}
                        Protocol used to send logs to SysLog server. Ignored
                        if destination type is not SysLog.             Set to turn on debug logging.
```

# Known Issues

If your client inserted more than 10,000 events at the same time, you will only get 10,000 of them.
