# Using Bulk Commands

Bulk functionality is available for many Code42 CLI methods, more details on which commands have bulk capabilities can be found in the [Commands Documentation](../commands.md).

All bulk methods take a CSV file as input.

The `generate-template` command can be used to create a CSV file with the necessary headers for a particular command.

For instance, the following command will create a file named `devices_bulk_deactivate.csv` with a single column header row of `guid`.
```bash
code42 devices bulk generate-template deactivate
```

The CSV file can contain more columns than are necessary for the command, however then the header row is **required**.

If the CSV file contains the *exact* number of columns that are necessary for the command then the header row is **optional**, but columns are expected to be in the same order as the template.

To run a bulk method, simply pass the CSV file path to the desired command.  For example, you would use to following command to deactivate multiple devices within your organization at once:


```bash
code42 devices bulk deactivate devices_bulk_deactivate.csv
```
