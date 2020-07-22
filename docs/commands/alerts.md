# Alerts

## search

Search for alerts and print them to stdout.

Arguments:
* `advanced-query`: A raw JSON alerts query. Useful for when the provided query parameters do not satisfy your
    requirements. WARNING: Using advanced queries is incompatible with other query-building args.
* `-b`, `--begin`: The beginning of the date range in which to look for alerts, can be a date/time in yyyy-MM-dd (UTC)
    or yyyy-MM-dd HH:MM:SS (UTC+24-hr time) format where the 'time' portion of the string can be partial
    (e.g. '2020-01-01 12' or '2020-01-01 01:15') or a short value representing days (30d), hours (24h) or minutes (15m)
    from current time.
* `-e`, `--end`: The end of the date range in which to look for alerts, argument format options are the same as --begin.
* `--severity`: Filter alerts by severity. Defaults to returning all severities.
    Available choices=['HIGH', 'MEDIUM', 'LOW']
* `--state`: Filter alerts by state. Defaults to returning all states. Available choices=['OPEN', 'RESOLVED'].
* `--actor`: Filter alerts by including the given actor(s) who triggered the alert. Args must match actor username
    exactly.
* `--actor-contains`: Filter alerts by including actor(s) whose username contains the given string.
* `--exclude-actor`: Filter alerts by excluding the given actor(s) who triggered the alert. Args must match actor
    username exactly.
* `--exclude-actor-contains`: Filter alerts by excluding actor(s) whose username contains the given string.
* `--rule-name`: Filter alerts by including the given rule name(s).
* `--exclude-rule-name`: Filter alerts by excluding the given rule name(s).
* `--rule-id`: Filter alerts by including the given rule id(s).
* `--exclude-rule-id`: Filter alerts by excluding the given rule id(s).
* `--rule-type`: Filter alerts by including the given rule type(s).
    Available choices=['FedEndpointExfiltration', 'FedCloudSharePermissions', 'FedFileTypeMismatch'].
* `--exclude-rule-type`: Filter alerts by excluding the given rule type(s).
    Available choices=['FedEndpointExfiltration', 'FedCloudSharePermissions', 'FedFileTypeMismatch'].
* `--description`: Filter alerts by description. Does fuzzy search by default.
* `-f`, `--format` (optional): The format used for outputting file events. Available choices= [CEF,JSON,RAW-JSON].
* `-c`, `--use-checkpoint` (optional): Get only file events that were not previously retrieved by writing the timestamp of the last event retrieved to a named checkpoint.

Usage:
```bash
code42 alerts search -b <begin-date> <options>
```

## clear-checkpoint

Arguments:
* `name`: The name to save this checkpoint as for later reuse.

Remove the saved file event checkpoint from 'use-checkpoint' (-c) mode.

Usage:
```bash
code42 alerts clear-checkpoint <name>
```
