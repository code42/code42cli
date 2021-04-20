import csv
import io
import json

import click

from code42cli.logger.formatters import CEF_TEMPLATE
from code42cli.logger.formatters import map_event_to_cef
from code42cli.util import find_format_width
from code42cli.util import format_to_table


CEF_DEFAULT_PRODUCT_NAME = "Advanced Exfiltration Detection"
CEF_DEFAULT_SEVERITY_LEVEL = "5"
OUTPUT_VIA_PAGER_THRESHOLD = 10


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

    def echo_formatted_list(self, output_list, force_pager=False):
        formatted_output = self.get_formatted_output(output_list)
        if len(output_list) > OUTPUT_VIA_PAGER_THRESHOLD or force_pager:
            click.echo_via_pager(formatted_output)
        else:
            for output in formatted_output:
                click.echo(output, nl=False)
            if self.output_format in [OutputFormat.TABLE]:
                click.echo()

    @property
    def _requires_list_output(self):
        return self.output_format in (OutputFormat.TABLE, OutputFormat.CSV)


class DataFrameOutputFormatter:
    def __init__(self, output_format):
        self.output_format = (
            output_format.upper() if output_format else OutputFormat.TABLE
        )

    def get_formatted_output(self, df, **kwargs):
        if self.output_format == OutputFormat.JSON:
            defaults = {
                "orient": "records",
                "lines": True,
                "index": True,
                "default_handler": str,
            }
            defaults.update(kwargs)
            return df.to_json(**defaults)

        elif self.output_format == OutputFormat.RAW:
            defaults = {
                "orient": "records",
                "lines": False,
                "index": True,
                "default_handler": str,
            }
            defaults.update(kwargs)
            return df.to_json(**defaults)

        elif self.output_format == OutputFormat.CSV:
            defaults = {"index": False}
            defaults.update(kwargs)
            df = df.fillna("")
            return df.to_csv(**defaults)

        elif self.output_format == OutputFormat.TABLE:
            defaults = {"index": False}
            defaults.update(kwargs)
            df = df.fillna("")
            return df.to_string(**defaults)

        else:
            raise ValueError(
                f"DataFrameOutputFormatter received an invalid format: {self.output_format}"
            )

    def echo_formatted_dataframe(self, df, **kwargs):
        str_output = self.get_formatted_output(df, **kwargs)
        if len(df) <= OUTPUT_VIA_PAGER_THRESHOLD:
            click.echo(str_output)
        else:
            click.echo_via_pager(str_output)


def to_csv(output):
    """Output is a list of records"""

    if not output:
        return
    string_io = io.StringIO(newline=None)
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


class FileEventsOutputFormat(OutputFormat):
    CEF = "CEF"

    def __iter__(self):
        return iter([self.TABLE, self.CSV, self.JSON, self.RAW, self.CEF])


class FileEventsOutputFormatter(OutputFormatter):
    def __init__(self, output_format, header=None):
        output_format = (
            output_format.upper() if output_format else FileEventsOutputFormat.TABLE
        )
        super().__init__(output_format, header)
        if output_format == FileEventsOutputFormat.CEF:
            self._format_func = to_cef


def to_cef(output):
    """Output is a single record"""
    return "{}\n".format(_convert_event_to_cef(output))


def _convert_event_to_cef(event):
    ext, evt, sig_id = map_event_to_cef(event)
    cef_log = CEF_TEMPLATE.format(
        productName=CEF_DEFAULT_PRODUCT_NAME,
        signatureID=sig_id,
        eventName=evt,
        severity=CEF_DEFAULT_SEVERITY_LEVEL,
        extension=ext,
    )
    return cef_log
