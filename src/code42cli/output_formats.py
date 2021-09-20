import csv
import io
import json
from itertools import chain
from typing import Generator

import click
import pandas

from code42cli.enums import FileEventsOutputFormat
from code42cli.enums import OutputFormat
from code42cli.errors import Code42CLIError
from code42cli.logger.formatters import CEF_TEMPLATE
from code42cli.logger.formatters import map_event_to_cef
from code42cli.util import find_format_width
from code42cli.util import format_to_table


CEF_DEFAULT_PRODUCT_NAME = "Advanced Exfiltration Detection"
CEF_DEFAULT_SEVERITY_LEVEL = "5"

# Uses method `echo_via_pager()` when 10 or more records.
OUTPUT_VIA_PAGER_THRESHOLD = 10


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

    def _format_output(self, output, *args, **kwargs):
        return self._format_func(output, *args, **kwargs)

    def _to_table(self, output, include_header=True):
        return to_table(output, self.header, include_header=include_header)

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
    def __init__(self, output_format, checkpoint_func=None):
        self.output_format = (
            output_format.upper() if output_format else OutputFormat.TABLE
        )
        if self.output_format not in OutputFormat.choices():
            raise Code42CLIError(
                f"DataFrameOutputFormatter received an invalid format: {self.output_format}"
            )
        self.checkpoint_func = checkpoint_func or (lambda x: None)

    def _ensure_iterable(self, dfs):
        if not isinstance(dfs, (Generator, list)):
            return [dfs]
        return dfs

    def _iter_table(self, dfs, **kwargs):
        df = pandas.concat(self._ensure_iterable(dfs)).fillna("")
        # set overrideable default kwargs
        kwargs = {"index": False, **kwargs}
        formatted_rows = df.to_string(**kwargs).splitlines(keepends=True)
        # don't checkpoint the header row
        if kwargs.get("header") is not False:
            yield formatted_rows.pop(0)

        yield from self._checkpoint_and_iter_formatted_events(df, formatted_rows)

    def _iter_csv(self, dfs, **kwargs):
        dfs = self._ensure_iterable(dfs)
        no_header = kwargs.get("header") is False

        for i, df in enumerate(dfs):
            # convert null values to empty string
            df.fillna("", inplace=True)
            # only add header on first df and if header=False was not passed in kwargs
            header = False if no_header else (i == 0)
            kwargs = {"index": False, "header": header, **kwargs}
            formatted_rows = df.to_csv(**kwargs).splitlines(keepends=True)
            if header:
                yield formatted_rows.pop(0)

            yield from self._checkpoint_and_iter_formatted_events(df, formatted_rows)

    def _iter_json(self, dfs, **kwargs):
        dfs = self._ensure_iterable(dfs)
        for df in dfs:
            # converts np.NaN nulls to None
            df = df.mask(df.isna(), other=None)
            row_count = len(df)
            for i, row in enumerate(df.iterrows(), start=1):
                event = dict(row[1])
                self.checkpoint_func(event)
                json_string = json.dumps(event, **kwargs)
                if i == row_count:
                    yield json_string
                else:
                    yield f"{json_string}\n"

    def _checkpoint_and_iter_formatted_events(self, df, formatted_rows):
        events = (dict(row[1]) for row in df.iterrows())
        for event, row in zip(events, formatted_rows):
            yield row
            self.checkpoint_func(event)

    def _echo_via_pager_if_over_threshold(self, gen):
        first_rows = []
        try:
            for _ in range(OUTPUT_VIA_PAGER_THRESHOLD):
                first_rows.append(next(gen))
        except StopIteration:
            click.echo("".join(first_rows))
            return

        click.echo_via_pager(chain(first_rows, gen))

    def get_formatted_output(self, dfs, **kwargs):
        if self.output_format == OutputFormat.TABLE:
            yield from self._iter_table(dfs, **kwargs)

        elif self.output_format == OutputFormat.CSV:
            yield from self._iter_csv(dfs, **kwargs)

        elif self.output_format == OutputFormat.JSON:
            kwargs = {"indent": 4, **kwargs}
            yield from self._iter_json(dfs, **kwargs)

        elif self.output_format == OutputFormat.RAW:
            yield from self._iter_json(dfs, **kwargs)

        else:
            raise Code42CLIError(
                f"DataFrameOutputFormatter received an invalid format: {self.output_format}"
            )

    def echo_formatted_dataframes(
        self, dfs, force_pager=False, force_no_pager=False, **kwargs
    ):
        """
        Accepts a dataframe or list/generator of dataframes and formats and echos the
        result to stdout. If total lines > 10, results will be sent to pager.
        """
        lines = self.get_formatted_output(dfs, **kwargs)
        if force_pager and force_no_pager:
            raise Code42CLIError("force_pager cannot be used with force_no_pager.")
        if force_pager:
            click.echo_via_pager(lines)
        elif force_no_pager:
            for line in lines:
                click.echo(line)
        else:
            self._echo_via_pager_if_over_threshold(lines)


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


def to_table(output, header, include_header=True):
    """Output is a list of records"""
    if not output:
        return

    rows, column_size = find_format_width(output, header, include_header=include_header)
    return format_to_table(rows, column_size)


def to_json(output):
    """Output is a single record"""
    return f"{json.dumps(output)}\n"


def to_formatted_json(output):
    """Output is a single record"""
    return f"{json.dumps(output, indent=4)}\n"


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
    return f"{_convert_event_to_cef(output)}\n"


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
