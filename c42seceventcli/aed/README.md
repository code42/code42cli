# c42seceventcli - AED

The c42seceventcli AED module contains a CLI for extracting AED events as well as a state manager
for recording and retrieving insertion timestamps. An insertion timestamp is used a cursor so that only new events are
extracted on subsequent runs.

## Requirements
- python 2.7
- c42secevents
- py42
- Code42 Server 6.8.x+

## Usage

A simple usage only requires the code42 authority url and your username:

        python aed_event_extraction_cli.py -s https://example.authority.com -u security.admin@example.com
        
If this is the first execution, the program will prompt for your password.

To use a config file, rename `config.default.cfg` to `config.cfg` and edit the fields to be your
authority server URL and your Code42 logon username. Then, do not provide those command line arguments:

        python aed_event_extraction_cli.py

If you get a keychain error when running this script, you may have to add a code signature to the script:

        codesign -f -s - $(which python)

Full usage:

        aed_event_extraction_cli.py -s C42_AUTHORITY_URL -u C42_USERNAME
                                           [-e C42_END_DATE | -r] [-h]
                                           [-b C42_BEGIN_DATE] [-i] [-o {CEF,JSON}]
                                           [-t [{created,modified,deleted,read_by_app} [{created,modified,deleted,read_by_app} ...]]]
                                           [-d--debug]
        
        optional arguments:
          -e C42_END_DATE, --end C42_END_DATE
                                The beginning of the date range in which to look for
                                events, in YYYY-MM-DD format OR a number (number of
                                minutes ago).
          -r, --record-cursor   Used to only get new events on subsequent runs.
        
        required arguments:
          -s C42_AUTHORITY_URL, --server C42_AUTHORITY_URL
                                The full scheme, url and port of the Code42 server.
          -u C42_USERNAME, --username C42_USERNAME
                                The username of the Code42 API user.
        
        optional arguments:
          -h, --help            Show this help message and exit
          -b C42_BEGIN_DATE, --begin C42_BEGIN_DATE
                                The end of the date range in which to look for events,
                                in YYYY-MM-DD format OR a number (number of minutes
                                ago).
          -i, --ignore-ssl-errors
                                Set to ignore ssl errors.
          -o {CEF,JSON}, --output-format {CEF,JSON}
                                The format used for outputting events.
          -t [{created,modified,deleted,read_by_app} [{created,modified,deleted,read_by_app} ...]], --types [{created,modified,deleted,read_by_app} [{created,modified,deleted,read_by_app} ...]]
                                The types of events to extract.
          -d--debug             Set to turn on debug logging.