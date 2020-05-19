# -*- coding: utf-8 -*-

import os, sys, inspect, csv

from code42cli.compat import open, str
from code42cli.worker import Worker
from code42cli.logger import get_main_cli_logger
from code42cli.args import SDK_ARG_NAME, PROFILE_ARG_NAME
from code42cli.errors import BadFileError


_logger = get_main_cli_logger()


class BulkCommandType(object):
    ADD = u"add"
    REMOVE = u"remove"

    def __iter__(self):
        return iter([self.ADD, self.REMOVE])


def generate_template(handler, path=None):
    """Looks at the parameter names of `handler` and creates a file with the same column names. If 
    `handler` only has one parameter that is not `sdk` or `profile`, it will create a blank file. 
    This is useful for commands such as `remove` which only require a list of users.
    """
    path = path or u"{0}/{1}.csv".format(os.getcwd(), str(handler.__name__))
    args = [
        arg
        for arg in inspect.getargspec(handler).args
        if arg != SDK_ARG_NAME and arg != PROFILE_ARG_NAME
    ]

    if len(args) <= 1:
        _logger.print_info(
            u"A blank file was generated because there are no csv headers needed for this command. "
            u"Simply enter one {} per line.".format(args[0])
        )
        # Set args to None so that we don't make a header out of the single arg.
        args = None

    _write_template_file(path, args)


def _write_template_file(path, columns=None):
    with open(path, u"w", encoding=u"utf8") as new_file:
        if columns:
            new_file.write(u",".join(columns))


def run_bulk_process(row_handler, reader):
    """Runs a bulk process.
    
    Args: 
        row_handler (callable): A callable that you define to process values from the row as 
            either *args or **kwargs.
        reader: (CSVReader or FlatFileReader, optional): A generator that reads rows and yields data into 
            `row_handler`. If None, it will use a CSVReader. Defaults to None.
    """
    processor = _create_bulk_processor(row_handler, reader)
    processor.run()


def _create_bulk_processor(row_handler, reader):
    """A factory method to create the bulk processor, useful for testing purposes."""
    return BulkProcessor(row_handler, reader)


class BulkProcessor(object):
    """A class for bulk processing a file. 
    
    Args:
        row_handler (callable): A callable that you define to process values from the row as 
            either *args or **kwargs. For example, if it's a csv file with header `prop_a,prop_b` 
            and first row `1,test`, then `row_handler` should receive kwargs 
            `prop_a: '1', prop_b: 'test'` when processing the first row. If it's a flat file, then 
            `row_handler` only needs to take an extra arg.
        reader (CSVReader or FlatFileReader): A generator that reads rows and yields data into `row_handler`.
    """

    def __init__(self, row_handler, reader):
        self.file_path = reader.file_path
        self._row_handler = row_handler
        self._reader = reader
        self.__worker = Worker(5, reader.get_rows_count())
        self._stats = self.__worker.stats
        self._progress_bar = ProgressBar(self._stats)

    def run(self):
        """Processes the csv file specified in the ctor, calling `self.row_handler` on each row."""
        self._progress_bar.update()  # init progress bar
        with open(self.file_path, newline=u"", encoding=u"utf8") as bulk_file:
            for row in self._reader(bulk_file=bulk_file):
                self._process_row(row)
            self.__worker.wait()
        self._progress_bar.clear_bar_and_print_results()

    def _process_row(self, row):
        if isinstance(row, dict):
            self._process_csv_row(row)
        elif row:
            self._process_flat_file_row(row.strip())

    def _process_csv_row(self, row):
        # Removes problems from including extra comments. Error messages from out of order args
        # are more indicative this way too.
        row.pop(None, None)
        row_values = {key: val if val != u"" else None for key, val in row.items()}
        self.__worker.do_async(
            lambda *args, **kwargs: self._handle_row(*args, **kwargs), **row_values
        )

    def _process_flat_file_row(self, row):
        if row:
            self.__worker.do_async(lambda *args, **kwargs: self._handle_row(*args, **kwargs), row)

    def _handle_row(self, *args, **kwargs):
        self._progress_bar.update()
        self._row_handler(*args, **kwargs)


class BulkFileReader(object):
    _ROWS_COUNT = -1

    def __init__(self, file_path):
        self.file_path = file_path

    def __call__(self, *args, **kwargs):
        pass

    def get_rows_count(self):
        if self._ROWS_COUNT == -1:
            self._ROWS_COUNT = sum(1 for _ in open(self.file_path))
        if self._ROWS_COUNT == 0:
            raise BadFileError(u"Given empty file {}.".format(self.file_path))
        return self._ROWS_COUNT


class CSVReader(BulkFileReader):
    """A generator that yields header keys mapped to row values from a csv file."""

    def __init__(self, file_path):
        with open(file_path) as f:
            try:
                self.has_header = csv.Sniffer().has_header(next(f))
            except StopIteration:
                raise BadFileError(u"Given empty file {}.".format(file_path))
        super(CSVReader, self).__init__(file_path)

    def __call__(self, *args, **kwargs):
        for row in csv.DictReader(kwargs.get(u"bulk_file")):
            yield row

    def get_rows_count(self):
        rows_count = super(CSVReader, self).get_rows_count()
        return rows_count - 1 if self.has_header else rows_count


class FlatFileReader(BulkFileReader):
    """A generator that yields a single-value per row from a file."""

    def __call__(self, *args, **kwargs):
        for row in kwargs[u"bulk_file"]:
            yield row


def create_csv_reader(file_path):
    return CSVReader(file_path)


def create_flat_file_reader(file_path):
    return FlatFileReader(file_path)


class ProgressBar(object):
    _FILL = u"█"
    _LENGTH = 100
    _LATENCY = _LENGTH / 10

    def __init__(self, stats):
        self._stats = stats

    def update(self):
        iteration = self._stats.total_processed + 1
        bar = self._create_bar(iteration)
        stats_msg = self._create_stats_text()

        sys.stdout.write(u"\r{} {}".format(bar, stats_msg))
        sys.stdout.flush()

    def _create_bar(self, iteration):
        fill_length = self._calculate_fill_length(iteration)
        return self._FILL * fill_length + u"-" * (self._LENGTH - fill_length)

    def _calculate_fill_length(self, idx):
        filled_length = self._LENGTH * idx // self._stats.total
        if filled_length + self._LATENCY < self._LENGTH:
            filled_length += self._LATENCY
        return int(filled_length)

    def _create_stats_text(self):
        return u"{0} succeeded, {1} failed out of {2}.".format(
            self._stats.total_successes, self._stats.total_errors, self._stats.total
        )

    def clear_bar_and_print_results(self):
        clear = self._LENGTH * u" "
        sys.stdout.write(u"\r{}{}\n".format(self._create_stats_text(), clear))
        sys.stdout.flush()
        if self._stats.total_errors:
            _logger.print_errors_occurred_message()
