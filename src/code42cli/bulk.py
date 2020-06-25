import os

import click

from code42cli.worker import Worker
from code42cli.logger import get_main_cli_logger
from code42cli.progress_bar import ProgressBar
from code42cli.errors import LoggedCLIError


_logger = get_main_cli_logger()


class BulkCommandType(object):
    ADD = "add"
    REMOVE = "remove"

    def __iter__(self):
        return iter([self.ADD, self.REMOVE])


def write_template_file(path, columns=None):
    with open(path, "w", encoding="utf8") as new_file:
        if columns:
            new_file.write(",".join(columns))


def generate_template_cmd_factory(csv_columns, cmd_name):
    """Helper function that creates a `generate-template` click command that can be added to `bulk`
    sub-command groups.
    """

    @click.command()
    @click.argument("cmd", type=click.Choice(BulkCommandType()))
    @click.argument(
        "path", required=False, type=click.Path(dir_okay=False, resolve_path=True, writable=True)
    )
    def generate_template(cmd, path):
        """\b
        Generate the csv template needed for bulk adding/removing users.
        
        Optional PATH argument can be provided to write to a specific file path/name.
        """
        if not path:
            filename = "{}_bulk_{}.csv".format(cmd_name, cmd)
            path = os.path.join(os.getcwd(), filename)
        write_template_file(path, columns=csv_columns)

    return generate_template


def run_bulk_process(row_handler, rows):
    """Runs a bulk process.
    
    Args: 
        row_handler (callable): A callable that you define to process values from the row as 
            either *args or **kwargs.
        rows (iterable): the rows to process.
    """
    processor = _create_bulk_processor(row_handler, rows)
    processor.run()


def _create_bulk_processor(row_handler, rows):
    """A factory method to create the bulk processor, useful for testing purposes."""
    return BulkProcessor(row_handler, rows)


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

    def __init__(self, row_handler, rows, worker=None, progress_bar=None):
        total = len(rows)
        self._rows = rows
        self._row_handler = row_handler
        self.__worker = worker or Worker(5, total)
        self._stats = self.__worker.stats
        self._progress_bar = progress_bar or ProgressBar(total)

    def run(self):
        """Processes the csv rows specified in the ctor, calling `self.row_handler` on each row."""
        for row in self._rows:
            self._process_row(row)
        self.__worker.wait()
        self._print_results()

    def _process_row(self, row):
        if isinstance(row, dict):
            self._process_csv_row(row)
        elif row:
            self._process_flat_file_row(row.strip())

    def _process_csv_row(self, row):
        # Removes problems from including extra columns. Error messages from out of order args
        # are more indicative this way too.
        row.pop(None, None)

        row_values = {key: val if val != "" else None for key, val in row.items()}
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
            raise LoggedCLIError("Some problems occurred during bulk processing.")
