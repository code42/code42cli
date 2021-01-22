import csv
import io
import json

import click
from pandas import DataFrame

from code42cli.util import find_format_width
from code42cli.util import format_to_table


CEF_DEFAULT_PRODUCT_NAME = "Advanced Exfiltration Detection"
CEF_DEFAULT_SEVERITY_LEVEL = "5"


class JsonOutputFormat:
    JSON = "JSON"
    RAW = "RAW-JSON"

    def __iter__(self):
        return iter([self.JSON, self.RAW])


class OutputFormat(JsonOutputFormat):
    TABLE = "TABLE"
    CSV = "CSV"

    def __iter__(self):
        return iter([self.TABLE, self.CSV, self.JSON, self.RAW])


class SendToFileEventsOutputFormat(JsonOutputFormat):
    CEF = "CEF"

    def __iter__(self):
        return iter([self.CEF, self.JSON, self.RAW])


class OutputFormatter:
    def __init__(self, output_format, header=None):
        output_format = output_format.upper() if output_format else OutputFormat.TABLE
        self.output_format = output_format
        self._format_func = to_table
        self.header = header

        if output_format == OutputFormat.CSV:
            self._format_func = to_csv
        elif output_format == OutputFormat.RAW:
            self._format_func = to_json
        elif output_format == OutputFormat.TABLE:
            self._format_func = self._to_table
        elif output_format == OutputFormat.JSON:
            self._format_func = to_formatted_json

    def _format_output(self, output):
        return self._format_func(output)

    def _to_table(self, output):
        return to_table(output, self.header)

    def get_formatted_output(self, output):
        if self._requires_list_output:
            yield self._format_output(output)
        else:
            for item in output:
                yield self._format_output(item)

    def echo_formatted_list(self, output_list):
        formatted_output = self.get_formatted_output(output_list)
        for output in formatted_output:
            click.echo(output, nl=False)
        if self.output_format in [OutputFormat.TABLE]:
            click.echo()

    @property
    def _requires_list_output(self):
        return self.output_format in (OutputFormat.TABLE, OutputFormat.CSV)


class DataFrameOutputFormatter:
    def __init__(self, output_format):
        output_format = output_format.upper() if output_format else OutputFormat.TABLE
        self.output_format = output_format
        self._format_func = DataFrame.to_string
        self._output_args = {"index": False}

        if output_format == OutputFormat.CSV:
            self._format_func = DataFrame.to_csv
        elif output_format == OutputFormat.RAW:
            self._format_func = DataFrame.to_json
            self._output_args.update(
                {
                    "orient": "records",
                    "lines": False,
                    "index": True,
                    "default_handler": str,
                }
            )
        elif output_format == OutputFormat.JSON:
            self._format_func = DataFrame.to_json
            self._output_args.update(
                {
                    "orient": "records",
                    "lines": True,
                    "index": True,
                    "default_handler": str,
                }
            )

    def _format_output(self, output, *args, **kwargs):
        self._output_args.update(kwargs)
        return self._format_func(output, *args, **self._output_args)

    def echo_formatted_dataframe(self, output, *args, **kwargs):
        str_output = self._format_output(output, *args, **kwargs)
        if len(output) <= 10:
            click.echo(str_output)
        else:
            click.echo_via_pager(str_output)


def to_csv(output):
    """Output is a list of records"""

    if not output:
        return
    string_io = io.StringIO()
    fieldnames = list({k for d in output for k in d.keys()})
    writer = csv.DictWriter(string_io, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(output)
    return string_io.getvalue()


def to_table(output, header):
    """Output is a list of records"""
    if not output:
        return
    rows, column_size = find_format_width(output, header)
    return format_to_table(rows, column_size)


def to_json(output):
    """Output is a single record"""
    return "{}\n".format(json.dumps(output))


def to_formatted_json(output):
    """Output is a single record"""
    json_str = "{}\n".format(json.dumps(output, indent=4))
    return json_str
