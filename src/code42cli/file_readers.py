import csv
import click


def read_csv_arg(headers):
    """Helper for defining arguments that read from a csv file. Automatically converts 
    the file name provided on command line to a list of csv rows (passed to command 
    function as `csv_rows` param).
    """
    return click.argument(
        "csv_rows",
        metavar="CSV_FILE",
        type=click.File("r"),
        callback=lambda ctx, arg: read_csv(arg, headers=headers),
    )


def read_csv(file, headers=None):
    """Helper to read a csv file object into dict rows, automatically removing header row
    if it exists, and errors if column count doesn't match header list length.
    """
    reader = csv.DictReader(file, fieldnames=headers)
    first_row = next(reader)
    if None in first_row or None in first_row.values():
        raise click.BadParameter(
            "Column count in {} doesn't match expected headers: {}".format(file.name, headers)
        )
    # skip first row if it's the header values
    if tuple(first_row.keys()) == tuple(first_row.values()):
        return list(reader)
    else:
        return [first_row, *list(reader)]


def read_flat_file(file):
    return [row.strip() for row in file]


read_flat_file_arg = click.argument(
    "file_rows", metavar="FILE", type=click.File("r"), callback=read_flat_file
)
