import csv

import click

from code42cli.click_ext.types import AutoDecodedFile
from code42cli.errors import Code42CLIError


def read_csv_arg(headers):
    """Helper for defining arguments that read from a csv file. Automatically converts
    the file name provided on command line to a list of csv rows (passed to command
    function as `csv_rows` param).
    """
    return click.argument(
        "csv_rows",
        metavar="CSV_FILE",
        type=AutoDecodedFile("r"),
        callback=lambda ctx, param, arg: read_csv(arg, headers=headers),
    )


def read_csv(file, headers):
    """Helper to read a csv file object into a list of dict rows.
    If CSV has a header row, all items in `headers` arg must be present in CSV or an
    error is raised. Any extra columns will get filtered out from resulting dicts.

    If no header row is present in CSV, column count must match `headers` arg length or
    else error is raised.
    """
    lines = file.readlines()
    first_line = lines[0].strip().split(",")

    # handle when first row has all of our expected headers
    if all(field in first_line for field in headers):
        reader = csv.DictReader(lines[1:], fieldnames=first_line)
        csv_rows = [{key: row[key] for key in headers} for row in reader]
        if not csv_rows:
            raise Code42CLIError("CSV contains no data rows.")
        return csv_rows

    # handle when first row has no expected headers
    elif all(field not in first_line for field in headers):
        #  only process header-less CSVs if we get exact expected column count
        if len(first_line) == len(headers):
            return list(csv.DictReader(lines, fieldnames=headers))
        else:
            raise Code42CLIError(
                "CSV data is ambiguous. Column count must match expected columns exactly when no "
                f"header row is present. Expected columns: {headers}"
            )
    # handle when first row has some expected headers but not all
    else:
        missing = [field for field in headers if field not in first_line]
        raise Code42CLIError(f"Missing required columns in csv: {missing}")


def read_flat_file(file):
    """Helper to read rows of a flat file, automatically removing header comment row if
    it exists, and strips whitespace from each row automatically."""
    first_row = next(file)
    if first_row.startswith("#"):
        return [row.strip() for row in file]
    else:
        return [first_row.strip(), *[row.strip() for row in file]]


read_flat_file_arg = click.argument(
    "file_rows",
    type=AutoDecodedFile("r"),
    metavar="FILE",
    callback=lambda ctx, param, arg: read_flat_file(arg),
)
