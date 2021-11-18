import csv
import io
import json
from itertools import chain
from typing import Generator

import click
from pandas import concat
from pandas import notnull

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
        if not isinstance(dfs, (Generator, list, tuple)):
            return [dfs]
        return dfs

    def _iter_table(self, dfs, columns=None, **kwargs):
        dfs = self._ensure_iterable(dfs)
        df = concat(dfs)
        if df.empty:
            return
        # convert everything to strings so we can left-justify format
        df = df.fillna("").applymap(str)
        # set overrideable default kwargs
        kwargs = {
            "index": False,
            "justify": "left",
            "formatters": make_left_aligned_formatter(df),
            **kwargs,
        }
        if columns:
            filtered = self._select_columns(df, columns)
            formatted_rows = filtered.to_string(**kwargs).splitlines(keepends=True)
        else:
            formatted_rows = df.to_string(**kwargs).splitlines(keepends=True)
        # don't checkpoint the header row
        if kwargs.get("header") is not False:
            yield formatted_rows.pop(0)

        yield from self._checkpoint_and_iter_formatted_events(df, formatted_rows)

    def _iter_csv(self, dfs, columns=None, **kwargs):
        dfs = self._ensure_iterable(dfs)
        no_header = kwargs.get("header") is False

        for i, df in enumerate(dfs):
            if df.empty:
                continue
            # convert null values to empty string
            df.fillna("", inplace=True)
            # only add header on first df and if header=False was not passed in kwargs
            header = False if no_header else (i == 0)
            kwargs = {"index": False, "header": header, **kwargs}
            if columns:
                filtered = self._select_columns(df, columns)
                formatted_rows = filtered.to_csv(**kwargs).splitlines(keepends=True)
            else:
                formatted_rows = df.to_csv(**kwargs).splitlines(keepends=True)
            if header:
                yield formatted_rows.pop(0)

            yield from self._checkpoint_and_iter_formatted_events(df, formatted_rows)

    def _iter_json(self, dfs, columns=None, **kwargs):
        kwargs = {"ensure_ascii": False, **kwargs}
        for event in self.iter_rows(dfs, columns=columns):
            json_string = json.dumps(event, **kwargs)
            yield f"{json_string}\n"

    def _checkpoint_and_iter_formatted_events(self, df, formatted_rows):
        for event, row in zip(df.to_dict("records"), formatted_rows):
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

    def _select_columns(self, df, columns):
        if df.empty:
            return df
        if not isinstance(columns, (list, tuple)):
            raise Code42CLIError(
                "'columns' parameter must be a list or tuple of column names."
            )
        # enable case-insensitive column selection
        normalized_map = {c.lower(): c for c in df.columns}
        try:
            columns = [normalized_map[c.lower()] for c in columns]
            return df[columns]
        except KeyError as e:
            key = e.args[0]
            raise click.BadArgumentUsage(
                f"'{key}' is not a valid column. Valid columns are: {list(df.columns)}"
            )

    def iter_rows(self, dfs, columns=None):
        """
        Accepts a pandas DataFrame or list/generator of DataFrames and yields each
        'row' of the DataFrame as a dict, calling the `checkpoint_func` on each row
        after it has been yielded.

        Accepts an optional list of column names that filter
        columns in the yielded results.
        """
        dfs = self._ensure_iterable(dfs)
        for df in dfs:
            # convert pandas' default null (numpy.NaN) to None
            df = df.astype(object).where(notnull, None)
            if columns:
                filtered = self._select_columns(df, columns)
            else:
                filtered = df
            for full_event, filtered_event in zip(
                df.to_dict("records"), filtered.to_dict("records")
            ):
                yield filtered_event
                self.checkpoint_func(full_event)

    def get_formatted_output(self, dfs, columns=None, **kwargs):
        """
        Accepts a pandas DataFrame or list/generator of DataFrames and formats and yields
        the results line by line to the caller as a generator.

        Accepts an optional list of column names that filter columns in the yielded
        results.

        Any additional kwargs provided will be passed to the underlying format method
        if customizations are required.
        """
        if self.output_format == OutputFormat.TABLE:
            yield from self._iter_table(dfs, columns=columns, **kwargs)

        elif self.output_format == OutputFormat.CSV:
            yield from self._iter_csv(dfs, columns=columns, **kwargs)

        elif self.output_format == OutputFormat.JSON:
            kwargs = {"indent": 4, **kwargs}
            yield from self._iter_json(dfs, columns=columns, **kwargs)

        elif self.output_format == OutputFormat.RAW:
            yield from self._iter_json(dfs, columns=columns, **kwargs)

        else:
            raise Code42CLIError(
                f"DataFrameOutputFormatter received an invalid format: {self.output_format}"
            )

    def echo_formatted_dataframes(
        self, dfs, columns=None, force_pager=False, force_no_pager=False, **kwargs
    ):
        """
        Accepts a pandas DataFrame or list/generator of DataFrames and formats and echos the
        result to stdout. If total lines > 10, results will be sent to pager. `force_pager`
        and `force_no_pager` can be set to override the pager logic based on line count.

        Accepts an optional list of column names that filter
        columns in the echoed results.

        Any additional kwargs provided will be passed to the underlying format method
        if customizations are required.
        """
        lines = self.get_formatted_output(dfs, columns=columns, **kwargs)
        try:
            # check for empty generator
            first = next(lines)
            lines = chain([first], lines)
        except StopIteration:
            click.echo("No results found.")
            return
        if force_pager and force_no_pager:
            raise Code42CLIError("force_pager cannot be used with force_no_pager.")
        if force_pager:
            click.echo_via_pager(lines)
        elif force_no_pager:
            for line in lines:
                click.echo(line)
        else:
            self._echo_via_pager_if_over_threshold(lines)


class FileEventsOutputFormatter(DataFrameOutputFormatter):
    """Class that adds CEF format output option to base DataFrameOutputFormatter."""

    def __init__(self, output_format, checkpoint_func=None):
        self.output_format = (
            output_format.upper() if output_format else OutputFormat.RAW
        )
        if self.output_format not in FileEventsOutputFormat.choices():
            raise Code42CLIError(
                f"FileEventsOutputFormatter received an invalid format: {self.output_format}"
            )
        self.checkpoint_func = checkpoint_func or (lambda x: None)

    def _iter_cef(self, dfs, **kwargs):
        dfs = self._ensure_iterable(dfs)
        for df in dfs:
            df = df.mask(df.isna(), other=None)
            for _i, row in df.iterrows():
                event = dict(row)
                yield f"{_convert_event_to_cef(event)}\n"
                self.checkpoint_func(event)

    def get_formatted_output(self, dfs, columns=None, **kwargs):
        if self.output_format == FileEventsOutputFormat.CEF:
            yield from self._iter_cef(dfs, **kwargs)
        else:
            yield from super().get_formatted_output(dfs, columns=columns, **kwargs)


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


def make_left_aligned_formatter(df):
    return {c: f"{{:<{df[c].str.len().max()}s}}".format for c in df.columns}
