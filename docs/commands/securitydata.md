# Security Data


## search

Search for file events and print them to stdout.

Arguments:
* `--advanced-query` (optional | cannot be used with other query options): A raw JSON file events query. Useful for when the provided query parameters do not 
    satisfy your requirements. WARNING: Using advanced queries is incompatible with other query-building args.
* `--saved-search` (optional | cannot be used with other query options): Get events from a saved search filter (created in the Code42 admin console) with the given ID.
* `-b`, `--begin` (required except for non-first runs in checkpoint mode): The beginning of the date range in which to 
    look for file events, can be a date/time in yyyy-MM-dd (UTC) or yyyy-MM-dd HH:MM:SS (UTC+24-hr time) format where 
    the 'time' portion of the string can be partial (e.g. '2020-01-01 12' or '2020-01-01 01:15') or a short value 
    representing days (30d), hours (24h) or minutes (15m) from current time.
* `-e`, `--end` (optional): The end of the date range in which to look for file events, argument format options are the 
    same as `--begin`.
* `-t`, `--type` (optional): Limits events to those with given exposure types. Available choices=
    ['SharedViaLink', 'SharedToDomain', 'ApplicationRead', 'CloudStorage', 'RemovableMedia', 'IsPublic']
* `--c42-username` (optional): Limits events to endpoint events for these users.
* `--actor` (optional): Limits events to only those enacted by the cloud service user of the person who caused the event.
* `--md5` (optional): Limits events to file events where the file has one of these MD5 hashes.
* `--sha256` (optional): Limits events to file events where the file has one of these SHA256 hashes.
* `--source` (optional): Limits events to only those from one of these sources. Example=Gmail.
* `--file-name` (optional): Limits events to file events where the file has one of these names.
* `--file-path` (optional): Limits events to file events where the file is located at one of these paths.
* `--process-owner` (optional): Limits events to exposure events where one of these users owns the process behind the 
    exposure.
* `--tab-url` (optional): Limits events to be exposure events with one of these destination tab URLs.
* `--include-non-exposure` (optional): Get all events including non-exposure events.
* `-f`, `--format` (optional): The format used for outputting file events. Available choices= [CEF,JSON,RAW-JSON]. 
* `-c`, `--use-checkpoint` (optional): Get only file events that were not previously retrieved by writing the timestamp of the last event retrieved to a named checkpoint.

Usage:
```bash
code42 security-data search -b <begin-date> <options>
```


## clear-checkpoint

Arguments:
* `name`: The name to save this checkpoint as for later reuse.

Remove the saved file event checkpoint from 'use-checkpoint' (-c) mode.

Usage:
```bash
code42 security-data clear-checkpoint <name>
```
