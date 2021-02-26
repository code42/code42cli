# Clean up your environment by deactivating devices

Your Code42 environment may contain many old devices that are no
longer active computers and that have not connected to Code42 in
quite some time. In order to clean up your environment, you can
use the CLI to deactivate these devices in bulk.

## Generate a list of devices

You can generate a list of devices using `code42 devices list`. By
default, it will display the list of devices at the command line,
but you can also output it in a number of file formats. For
example, to generate a CSV of devices in your environment, use
this command:

```
code42 devices list -f CSV
```

To save to a file, redirect the output to a file in your shell:

```
code42 devices list -f CSV > output.csv
```

### Filter the list

You can filter or edit the list of devices in your spreadsheet or
text editor of choice, but the CLI has some parameters built in
that can help you to filter the list of devices to just the ones
you want to deactivate. To see a full list of available
parameters, run `code42 devices list -h`.

Here are some useful parameters you may wish to leverage when
curating a list of devices to deactivate:

* `--last-connected-before DATE|TIMESTAMP|SHORT_TIME` - allows you to only see devices that have not connected since a particular date. You can also use a timestamp or short time format, for example `30d`.
* `--exclude-most-recently-connected INTEGER` - allows you to exclude the most recently connected device (per user) from the results. This allows you to ensure that every user is left with at least N device(s), regardless of how recently they have connected.
* `--created-before DATE|TIMESTAMP|SHORT_TIME` - allows you to only see devices created before a particular date.

## Deactivate devices

Once you have a list of devices that you want to remove, you can
run the `code42 devices bulk deactivate` command:

```
code42 devices bulk deactivate list_of_devices.csv
```

The device list must be a file in CSV format containing a `guid`
column with the unique identifier of the devices to be
deactivated. The deactivate command can also accept some optional
parameters:

* `--change-device-name` - prepends `deactivated_<current_date>` to the beginning of the device name, allowing you to have a record of which devices were deactivated by the CLI and when.
* `--purge-date yyyy-MM-dd` - allows you to change the date on which the deactivated devices' archives will be purged from cold storage.

To see a full list of available options, run `code42 devices bulk deactivate -h`.

The `code42 devices bulk deactivate` command will output the guid
of the device to be deactivated, plus a column indicating the
success or failure of the deactivation. To change the format of
this output, use the `-f` or `--format` option.

You can also redirect the output to a file, for example:

```
code42 devices bulk deactivate devices_to_deactivate.csv -f CSV > deactivation_results.csv
```

Deactivation will fail if the user running the command does not
have permission to deactivate the device, or if the user owning
the device is on legal hold.


### Generate the list and deactivate in a single command

You can also pipe the output of `code42 devices list` directly to
`code42 devices bulk deactivate`. When using a pipe, make sure to
use `-` as the input argument for `code42 devices bulk deactivate`
to indicate that it should read from standard input.

Here is an example:

```
code42 devices list \
--last-connected-before 365d \
--exclude-most-recently-connected 1 \
-f CSV \
| code42 devices bulk deactivate - \
-f CSV \
> deactivation_results.csv
```

This lists all devices that have not connected within a year _and_
are not a user's most-recently-connected device, and then attempts
to deactivate them.
