import os, inspect

from code42cli.compat import open, str
from code42cli.worker import Worker
from code42cli.logger import get_main_cli_logger
from code42cli.args import SDK_ARG_NAME, PROFILE_ARG_NAME
from code42cli.progress_bar import ProgressBar


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
    path = path or os.path.join(os.getcwd(), u"{}.csv".format(str(handler.__name__)))
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

    def __init__(self, row_handler, reader, worker=None, progress_bar=None):
        total = reader.get_rows_count()
        self.file_path = reader.file_path
        self._row_handler = row_handler
        self._reader = reader
        self.__worker = worker or Worker(5, total)
        self._stats = self.__worker.stats
        self._progress_bar = progress_bar or ProgressBar(total)

    def run(self):
        """Processes the csv file specified in the ctor, calling `self.row_handler` on each row."""
        with open(self.file_path, newline=u"", encoding=u"utf8") as bulk_file:
            for row in self._reader(bulk_file=bulk_file):
                self._process_row(row)
            self.__worker.wait()
        self._print_results()

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
        message = str(self._stats)
        self._progress_bar.update(self._stats.total_processed, message)
        self._row_handler(*args, **kwargs)

    def _print_results(self):
        self._progress_bar.clear_bar_and_print_final(str(self._stats))
        if self._stats.total_errors:
            logger = get_main_cli_logger()
            logger.print_errors_occurred_message()
