# c42seceventcli - AED

The c42seceventcli AED module contains a CLI for extracting AED events as well as a state manager
for recording and retrieving insertion timestamps. This project uses the insertion timestamp of the 
most recently extracted event as a cursor so that only new events come through on subsequent runs.

## Requirements
- python 2.7
- c42secevents
- py42
- Code42 Server 6.8.x+

## Usage

A simple usage requires either your code42 authority url and username passed in as arguments:

    python aed_event_extraction_cli.py -s https://example.authority.com -u security.admin@example.com
        
Or, stated in a file named `config.cfg`. Rename `config.default.cfg` to `config.cfg` and edit the fields to be your
authority server URL and username. Then, run the script as follows:

    python aed_event_extraction_cli.py

If this is the first run, it will prompt you for your password.

If you get a keychain error when running this script, you may have to add a code signature:

    codesign -f -s - $(which python)

Full usage:

     aed_event_extraction_cli.py [-e C42_END_DATE | -r]
                                       [-s C42_AUTHORITY_URL] [-u C42_USERNAME]
                                       [-h] [-b C42_BEGIN_DATE] [-i]
                                       [-o {CEF,JSON}]
                                       [-t [{created,modified,deleted,read_by_app} [{created,modified,deleted,read_by_app} ...]]]
                                       [-d--debug]
    
    optional arguments:
      -e C42_END_DATE, --end C42_END_DATE
                            The beginning of the date range in which to look for
                            events, in YYYY-MM-DD UTC format OR a number (number
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
      -t [{created,modified,deleted,read_by_app} [{created,modified,deleted,read_by_app} ...]], --types [{created,modified,deleted,read_by_app} [{created,modified,deleted,read_by_app} ...]]
                            The types of events to extract.
    -d--debug             Set to turn on debug logging.