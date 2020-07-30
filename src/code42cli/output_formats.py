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


output_option = click.option(
    "-f",
    "--format",
    type=click.Choice(OutputFormat(), case_sensitive=False),
    help="The output format of the result.",
    callback=output_format,
)


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
    return json.dumps(_filter(output, header))


def to_formatted_json(output, header=None):
    return json.dumps(_filter(output, header), indent=4)
