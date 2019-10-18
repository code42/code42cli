# c42seceventcli - AED

The c42seceventcli AED module contains a CLI for extracting AED events as well as an optional state manager
for only getting events you did not previously get.

## Requirements

- Python 2.7.x or 3.5.0+
- Code42 Server 6.8.x+

## Installation
Until `py42` and `c42secevents` are available on PyPI, you will need to first install them manually.

`py42` is available for download [here](https://confluence.corp.code42.com/pages/viewpage.action?pageId=61767969#py42%E2%80%93Code42PythonSDK-Downloads).
For py42 installation instructions, see its [README](https://stash.corp.code42.com/projects/SH/repos/lib_c42_python_sdk/browse/README.md).

`c42secevents` is available [here](https://confluence.corp.code42.com/display/LS/Security+Event+Extractor+-+Python).
For `c42secevents` installation instructions, see its [README](https://stash.corp.code42.com/projects/INT/repos/security-event-extractor/browse/README.md).

Once you've done that, install `c42seceventscli` using:

```bash
$ python setup.py install
```

## Usage

A simple usage requires you to pass in your Code42 authority URL and username as arguments:

```bash
c42aed -s https://example.authority.com -u security.admin@example.com
```
        
Another option is to put your Code42 authority URL and username in a file named `config.cfg`. 
Rename `config.default.cfg` to `config.cfg` and edit the fields to be your
authority server URL and username.
There are also other optional arguments in `config.default.cfg` that mirror CLI args.

```buildoutcfg
[Code42]
c42_username=user@code42.com
c42_authority_url=https://example.authority.com
```

Then, run the script as follows:

```bash
c42aed -c path/to/config
```

To use a the state management service, simply provide the `-r` to the command line:

```bash
c42aed -s https://example.authority.com -u security.admin@example.com -r
```

Alternatively, set the `c42_record_cursor` arg in the config file to True:

```buildoutcfg
[Code42]
c42_username=user@code42.com
c42_authority_url=https://example.authority.com
c42_record_cursor=True
```

To reset the cursor:

```bash
c42aed -s https://example.authority.com -u security.admin@example.com -r --reset-cursor
```

By not using `-r`, the following runs will have no knowledge of previous extracted events, and 
you will get all the events in the given time range (or default time range of 60 days back). 
`-r` is particularly useful if you wish to run this script on a recurring job.


You can also use CLI args with config-file args, but the program will favor the CLI args.

If this is the first run, you will be prompted for your password.

If you get a keychain error when running this script, you may have to add a code signature:

```bash
codesign -f -s - $(which python)
```

If you get an `OperationError: unable to open database file`, trying running again with `sudo`:

```bash
sudo c42aed -s https://example.authority.com -u security.admin@example.com
``` 

All errors are sent to an error log file named `c42seceventcli_errors.log`.


Full usage:

```
usage: main.py [-e C42_END_DATE | -r] [-c C42_CONFIG_FILE]
               [-s C42_AUTHORITY_URL] [-u C42_USERNAME] [-h]
               [-b C42_BEGIN_DATE] [-i] [-o {CEF,JSON}]
               [-t [{SharedViaLink,SharedToDomain,ApplicationRead,CloudStorage,RemovableMedia,IsPublic} [{SharedViaLink,SharedToDomain,ApplicationRead,CloudStorage,RemovableMedia,IsPublic} ...]]]
               [-d--debug] [--dest-type {stdout,file,syslog}]
               [--dest C42_DESTINATION] [--dest-port C42_SYSLOG_PORT]
               [--dest-protocol {TCP,UDP}]

optional arguments:
  -e C42_END_DATE, --end C42_END_DATE
                        The beginning of the date range in which to look for
                        events, in YYYY-MM-DD UTC format OR a number (number
                        of minutes ago).
  -r, --record-cursor   To only get events that were not previously retrieved.

main:
  -c C42_CONFIG_FILE, --config-file C42_CONFIG_FILE
                        The path to the config file to use for the rest of the
                        arguments.
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
                        if destination type is not SysLog.
```

# Known Issues

Only the first 10,000 of each set of events containing the exact same insertion timestamp will be reported.
