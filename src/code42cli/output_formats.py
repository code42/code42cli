import json

import click
from texttable import Texttable

from code42cli.cmds.enums import OutputFormat


def output_format(_, __, value):
    if value is not None:
        if value is OutputFormat.CSV:
            return to_csv
        if value is OutputFormat.RAW:
            return to_json
        if value is OutputFormat.ASCII:
            return to_ascii_table
        if value is OutputFormat.JSON:
            return to_formatted_json


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
    for row in output:
        items = [str(row[key]) for key in header.keys()]
        line = ",".join(items)
        lines.append(line)
    click.echo(columns)
    click.echo("\n".join(lines))


def to_ascii_table(output, header):
    table = Texttable()
    table.set_cols_align(["c" for _ in header.keys()])
    table.set_cols_valign(["m" for _ in header.keys()])
    table.set_max_width(0)

    rows = []
    columns = header.values()
    rows.append(columns)

    for row in output:
        rows.append([str(row[key]) for key in header.keys()])
    table.add_rows(rows)
    click.echo(table.draw() + "\n")


def to_json(output, header=None):
    # Todo Whether to filter results by header, and verify default output is json
    click.echo(output)


def to_formatted_json(output, header=None):
    # Todo Whether to filter results by header
    click.echo(json.dumps(output, indent=4))
