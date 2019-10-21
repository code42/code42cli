# c42seceventcli - AED

The c42seceventcli AED module contains a CLI for extracting AED events as well as an optional state manager
for only getting events you did not previously get.

## Requirements

- Python 2.7.x or 3.5.0+
- Code42 Server 6.8.x+

## Installation
Until we are able to put `py42` and `c42secevents` on PyPI, you will need to first install them manually.

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
c42_authority_url=https://example.authority.com
c42_username=user@code42.com
```

Then, run the script as follows:

```bash
c42aed -c path/to/config
```

To use a the state management service, simply provide the `-r` to the command line.
`-r` is particularly useful if you wish to run this script on a recurring job:

```bash
c42aed -s https://example.authority.com -u security.admin@example.com -r
```

If you are using a config file with `-c`, set the `c42_record_cursor` arg in the config file to True:

```buildoutcfg
[Code42]
c42_authority_url=https://example.authority.com
c42_username=user@code42.com
c42_record_cursor=True
```
By excluding `-r`, future runs will not know about previous events you got, and 
you will get all the events in the given time range (or default time range of 60 days back). 

To clear the cursor:

```bash
c42aed -s https://example.authority.com -u security.admin@example.com -r --clear-cursor
```
There are two possible output formats.

* CEF
* JSON

JSON is the default. To use CEF, use `-o CEF`:

```bash
c42aed -s https://example.authority.com -u security.admin@example.com -o CEF
```

Or if you are using a config file with `-c`:

```buildoutcfg
[Code42]
c42_authority_url=https://example.authority.com
c42_username=user@code42.com
c42_output_format=CEF
```

There are three possible destination types to use:

* stdout - printing to console
* file - writing to a file
* syslog - transmitting to a syslog server

The program defaults to `stdout`. To use a file, use `--dest-type` and `--dest` this way:

```bash
c42aed -s https://example.authority.com -u security.admin@example.com --dest-type file --dest name-of-file.txt
```

To use syslog:

```bash
c42aed -s https://example.authority.com -u security.admin@example.com --dest-type syslog --dest https://syslog.example.com
```

Both `c42_destination_type` and `c42_destination` are possible fields in the config file as well.

You can also use CLI args with config-file args, but the program will favor the CLI args.

If this is your first time running, you will be prompted for your Code42 password.

If you get a keychain error when running this script, you may have to add a code signature:

```bash
codesign -f -s - $(which python)
```

If you get an `OperationError: unable to open database file`, trying running again with `sudo` and entering you device password:

```bash
sudo c42aed -s https://example.authority.com -u security.admin@example.com
``` 

All errors are sent to an error log file named `c42seceventcli_errors.log` located in your python's site-packages/c42seceventcli/aed.
To find the location of c42seceventcli:

```bash
pip show c42seceventcli
```


Full usage:

```
usage: c42aed [-e C42_END_DATE | -r] [--clear-cursor] [--reset-password]
              [-c C42_CONFIG_FILE] [-s C42_AUTHORITY_URL] [-u C42_USERNAME]
              [-h] [-b C42_BEGIN_DATE] [-i] [-o {CEF,JSON}]
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
  --clear-cursor        Resets the stored cursor.
  --reset-password      Clears stored password and prompts user for password.
  -c C42_CONFIG_FILE, --config-file C42_CONFIG_FILE
                        The path to the config file to use for the rest of the
                        arguments.
  -s C42_AUTHORITY_URL, --server C42_AUTHORITY_URL
                        The full scheme, url and port of the Code42 server.
  -u C42_USERNAME, --username C42_USERNAME
                        The username of the Code42 API user.
  -h, --help            Show this help message and exit.
  -b C42_BEGIN_DATE, --begin C42_BEGIN_DATE
                        The end of the date range in which to look for events,
                        in YYYY-MM-DD UTC format OR a number (number of
                        minutes ago).
  -i, --ignore-ssl-errors
                        Set to ignore ssl errors.
  -o {CEF,JSON}, --output-format {CEF,JSON}
                        The format used for outputting events.
  -t [{SharedViaLink,SharedToDomain,ApplicationRead,CloudStorage,RemovableMedia,IsPublic} [{SharedViaLink,SharedToDomain,ApplicationRead,CloudStorage,RemovableMedia,IsPublic} ...]], --types [{SharedViaLink,SharedToDomain,ApplicationRead,CloudStorage,RemovableMedia,IsPublic} [{SharedViaLink,SharedToDomain,ApplicationRead,CloudStorage,RemovableMedia,IsPublic} ...]]
                        To limit extracted events to those with given exposure
                        types.
  -d--debug             Set to turn on debug logging.
  --dest-type {stdout,file,syslog}
                        The type of destination to send output to.
  --dest C42_DESTINATION
                        Either a name of a local file or syslog host address.
                        Ignored if destination type is stdout.
  --dest-port C42_SYSLOG_PORT
                        Port used on syslog destination. Ignored if
                        destination type is not syslog.
  --dest-protocol {TCP,UDP}
                        Protocol used to send logs to syslog server. Ignored
                        if destination type is not syslog.
```

# Known Issues

Only the first 10,000 of each set of events containing the exact same insertion timestamp will be reported.
