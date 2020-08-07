import csv
import io
import json

import click

from code42cli.cmds.enums import OutputFormat
from code42cli.util import find_format_width
from code42cli.util import format_to_table


def output_format(_, __, value):
    if value is not None:
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


def extraction_output_format(_, __, value):
    if value is not None:
        if value == OutputFormat.CSV:
            return to_dynamic_csv
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


extraction_format_option = click.option(
    "-f",
    "--format",
    type=click.Choice(OutputFormat(), case_sensitive=False),
    help="The output format of the result. Defaults to table format.",
    callback=extraction_output_format,
)


def to_dynamic_csv(output, header):
    string_io = io.StringIO()
    writer = csv.DictWriter(string_io, fieldnames=header)
    filtered_output = [{key: row[key] for key in header} for row in output]
    writer.writeheader()
    writer.writerows(filtered_output)
    return string_io.getvalue()


def to_csv(output, header):
    columns = ",".join(header.values())
    lines = []
    lines.append(columns)
    for row in output:
        items = [str(row[key]) for key in header.keys()]
        line = ",".join(items)
        lines.append(line)

    return "\n".join(lines)


def to_table(output, header):
    rows, column_size = find_format_width(output, header)
    return format_to_table(rows, column_size)


def _filter(output, header):
    return [{header[key]: row[key] for key in header.keys()} for row in output]


def to_json(output, header=None):
    return json.dumps(output)


def to_formatted_json(output, header=None):
    return json.dumps(_filter(output, header), indent=4)
