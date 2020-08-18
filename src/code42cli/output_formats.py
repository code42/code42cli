import csv
import io
import json

import click

from code42cli.util import find_format_width
from code42cli.util import format_to_table


CEF_DEFAULT_PRODUCT_NAME = "Advanced Exfiltration Detection"
CEF_DEFAULT_SEVERITY_LEVEL = "5"


class OutputFormat:
    TABLE = "TABLE"
    CSV = "CSV"
    JSON = "JSON"
    RAW = "RAW-JSON"

    def __iter__(self):
        return iter([self.TABLE, self.CSV, self.JSON, self.RAW])


def output_format(_, __, value):
    if value is not None:
        value = value.upper()
        if value == OutputFormat.CSV:
            return to_csv
        if value == OutputFormat.RAW:
            return to_json
        if value == OutputFormat.TABLE:
            return to_table
        if value == OutputFormat.JSON:
            return to_formatted_json
    # default option
    return to_table


format_option = click.option(
    "-f",
    "--format",
    type=click.Choice(OutputFormat(), case_sensitive=False),
    help="The output format of the result. Defaults to table format.",
    callback=output_format,
)


def to_csv(output, header):
    if not output:
        return
    string_io = io.StringIO()
    writer = csv.DictWriter(string_io, fieldnames=output[0].keys())
    writer.writeheader()
    writer.writerows(output)
    return string_io.getvalue()


def to_table(output, header):
    if not output:
        return
    header = header or get_dynamic_header(output[0])
    rows, column_size = find_format_width(output, header)
    return format_to_table(rows, column_size)


def _filter(output, header):
    return [{header[key]: row[key] for key in header.keys()} for row in output]


def to_json(output, header=None):
    return json.dumps(output)


def to_formatted_json(output, header=None):
    return json.dumps(_filter(output, header), indent=4)


def get_dynamic_header(header_items):
    print(header_items)
    return {
        key: key.capitalize()
        for key in header_items.keys()
        if type(header_items[key]) == str
    }
