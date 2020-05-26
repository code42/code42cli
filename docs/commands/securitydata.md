# Security Data

## Shared arguments

Search args are shared between `print`, `write-to`, and `send-to` commands.

* `--advanced-query` (optional): A raw JSON file events query. Useful for when the provided query parameters do not 
    satisfy your requirements. WARNING: Using advanced queries is incompatible with other query-building args.
* `-b`, `--begin` (required except for non-first runs in incremental mode): The beginning of the date range in which to 
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
* `-i`, `--incremental` (optional): Only get file events that were not previously retrieved.


## print

Print file events to stdout.

Arguments:
* search args (note that begin date is often required).

Usage:
```bash
code42 security-data print -b <begin-date> <args>
```

## write-to

Write file events to the file with the given name. 

Arguments:
* `output_file`: The name of the local file to send output to.
* search args (note that begin date is often required).

Usage:
```bash
code42 security-data write-to -b 2020-03-01 <args>
```

## send-to

Send file events to the given server address. 

Arguments:
* `server`: The server address to send output to.
* `protocol` (optional): Protocol used to send logs to server. Available choices= [TCP, UDP].
* search args (note that begin date is often required).

Usage:
```bash
code42 security-data send-to <server> <optional-server-args> <args>
```

## clear-checkpoint

Remove the saved file event checkpoint from 'incremental' (-i) mode.

Usage:
```bash
code42 security-data clear-checkpoint
```
