import os

import click

from code42cli.errors import LoggedCLIError
from code42cli.logger import get_main_cli_logger
from code42cli.worker import Worker

_logger = get_main_cli_logger()


class BulkCommandType:
    ADD = "add"
    REMOVE = "remove"

    def __iter__(self):
        return iter([self.ADD, self.REMOVE])


def write_template_file(path, columns=None, flat_item=None):
    with open(path, "w", encoding="utf8") as new_file:
        if columns:
            new_file.write(",".join(columns))
        else:
            new_file.write(
                "# This template takes a single {} to be processed on each row.".format(
                    flat_item or "item"
                )
            )


def generate_template_cmd_factory(group_name, commands_dict, help_message=None):
    """Helper function that creates a `generate-template` click command that can be added to `bulk`
    sub-command groups.

    Args:
        `group_name`: a str representing the parent command group this is generating templates for.
        `commands_dict`: a dict of the commands with their column names. Keys are the cmd
            names that will become the `cmd` argument, and values are the list of column names for
            the csv.

            If a cmd takes a flat file, value should be a string indicating what item the flat file
            rows should contain.
    """
    help_message = (
        help_message
        or "Generate the CSV template needed for bulk adding/removing users."
    )

    @click.command(help=help_message)
    @click.argument("cmd", type=click.Choice(list(commands_dict)))
    @click.option(
        "--path",
        "-p",
        type=click.Path(dir_okay=False, resolve_path=True, writable=True),
        help="Write template file to specific file path/name.",
    )
    def generate_template(cmd, path):
        columns = commands_dict[cmd]
        if not path:
            filename = "{}_bulk_{}.csv".format(group_name, cmd.replace("-", "_"))
            path = os.path.join(os.getcwd(), filename)
        if isinstance(columns, str):
            write_template_file(path, columns=None, flat_item=columns)
        else:
            write_template_file(path, columns=columns)

    return generate_template


def run_bulk_process(row_handler, rows, progress_label=None):
    """Runs a bulk process.

    Args:
        row_handler (callable): A callable that you define to process values from the row as
            either *args or **kwargs.
        rows (iterable): the rows to process.
        progress_label: a label that prints with the progress bar.
    """
    processor = _create_bulk_processor(row_handler, rows, progress_label)
    return processor.run()


def _create_bulk_processor(row_handler, rows, progress_label):
    """A factory method to create the bulk processor, useful for testing purposes."""
    return BulkProcessor(row_handler, rows, progress_label=progress_label)


class BulkProcessor:
    """A class for bulk processing a file.

    Args:
        row_handler (callable): A callable that you define to process values from the row as
            either *args or **kwargs. For example, if it's a csv file with header `prop_a,prop_b`
            and first row `1,test`, then `row_handler` should receive kwargs
            `prop_a: '1', prop_b: 'test'` when processing the first row. If it's a flat file, then
            `row_handler` only needs to take an extra arg.
    """

    def __init__(self, row_handler, rows, worker=None, progress_label=None):
        total = len(rows)
        self._rows = rows
        self._row_handler = row_handler
        self._progress_bar = click.progressbar(
            length=len(self._rows),
            item_show_func=self._show_stats,
            label=progress_label,
        )
        self.__worker = worker or Worker(5, total, bar=self._progress_bar)
        self._stats = self.__worker.stats

    def run(self):
        """Processes the csv rows specified in the ctor, calling `self.row_handler` on each row."""
        self._stats.reset_results()
        for row in self._rows:
            self._process_row(row)
        self.__worker.wait()
        self._print_results()
        return self._stats._results

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
            self.__worker.do_async(
                lambda *args, **kwargs: self._handle_row(*args, **kwargs), row
            )

    def _handle_row(self, *args, **kwargs):
        return self._row_handler(*args, **kwargs)

    def _show_stats(self, _):
        return str(self._stats)

    def _print_results(self):
        click.echo("")
        if self._stats.total_errors:
            raise LoggedCLIError("Some problems occurred during bulk processing.")
