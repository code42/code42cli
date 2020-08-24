import csv
import io
import json

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


class OutputFormatter:
    def __init__(self, output_format, header=None):
        output_format = output_format.upper() if output_format else OutputFormat.TABLE
        self.output_format = output_format
        self._format_func = to_table
        self.header = header
        if output_format is None:
            return

        if output_format == OutputFormat.CSV:
            self._format_func = to_csv
        elif output_format == OutputFormat.RAW:
            self._format_func = to_json
        elif output_format == OutputFormat.TABLE:
            self._format_func = to_table
        elif output_format == OutputFormat.JSON:
            self._format_func = to_formatted_json

    def _format_output(self, output):
        return self._format_func(output, self.header)

    def get_formatted_output(self, output):
        if self._requires_list_output:
            yield self._format_output(output)
        else:
            for item in output:
                yield self._format_output(item)

    @property
    def _requires_list_output(self):
        return (
            self.output_format == OutputFormat.TABLE
            or self.output_format == OutputFormat.CSV
        )


def to_csv(output, header=None):
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
    header = header or get_dynamic_header(output)
    rows, column_size = find_format_width(output, header)
    return format_to_table(rows, column_size)


def _filter(output, header):
    return [{header[key]: row[key] for key in header.keys()} for row in output]


def to_json(output, header=None):
    """Output is a single record"""
    return json.dumps(output)


def to_formatted_json(output, header):
    """Output is a single record"""
    json_str = json.dumps(output, indent=4)
    return json_str


def get_dynamic_header(header_items):
    if not header_items:
        return

    return {
        key: key.capitalize()
        for key in header_items[0].keys()
        if type(header_items[0][key]) == str
    }
