import json
import os
import shutil
from collections import OrderedDict
from functools import wraps
from hashlib import md5
from os import path
from signal import getsignal
from signal import SIGINT
from signal import signal

from click import echo
from click import get_current_context
from click import style

_PADDING_SIZE = 3


def does_user_agree(prompt):
    """Prompts the user and checks if they said yes. If command has the `yes_option` flag, and
    `-y/--yes` is passed, this will always return `True`.
    """
    ctx = get_current_context()
    if ctx.obj.assume_yes:
        return True
    ans = input(prompt)
    ans = ans.strip().lower()
    return ans == "y"


def get_user_project_path(*subdirs):
    """The path on your user dir to /.code42cli/[subdir]."""
    package_name = __name__.split(".")[0]
    home = path.expanduser("~")
    hidden_package_name = ".{}".format(package_name)
    user_project_path = path.join(home, hidden_package_name)
    result_path = path.join(user_project_path, *subdirs)
    if not path.exists(result_path):
        os.makedirs(result_path)
    return result_path


def find_format_width(record, header, include_header=True):
    """Fetches needed keys/items to be displayed based on header keys.

    Finds the largest string against each column so as to decide the padding size for the column.

    Args:
        record (dict): data to be formatted.
        header (dict): key-value where keys should map to keys of record dict and
          value is the corresponding column name to be displayed on the CLI.
        include_header (bool): include header in output, defaults to True.

    Returns:
        tuple (list of dict, dict): i.e Filtered records, padding size of columns.
    """
    rows = []
    if include_header:
        if not header:
            header = _get_default_header(record)
        rows.append(header)
    widths = dict(header.items())  # Copy
    for record_row in record:
        row = OrderedDict()
        for header_key in header.keys():
            item = record_row.get(header_key)
            row[header_key] = item
            widths[header_key] = max(widths[header_key], str(item), key=len)
        rows.append(row)
    column_sizes = {key: len(value) for key, value in widths.items()}
    return rows, column_sizes


def format_to_table(rows, column_size):
    """Formats given rows into a string of left justified table."""
    lines = []
    for row in rows:
        line = ""
        for key in row.keys():
            line += str(row[key]).ljust(column_size[key] + _PADDING_SIZE)
        lines.append(line)
    return "\n".join(lines)


def format_string_list_to_columns(string_list, max_width=None):
    """Prints a list of strings in justified columns and fits them neatly into specified width."""
    if not string_list:
        return
    if not max_width:
        max_width, _ = shutil.get_terminal_size()
    column_width = len(max(string_list, key=len)) + _PADDING_SIZE
    num_columns = int(max_width / column_width) or 1
    format_string = "{{:<{0}}}".format(column_width) * num_columns
    batches = [
        string_list[i : i + num_columns]
        for i in range(0, len(string_list), num_columns)
    ]
    padding = ["" for _ in range(num_columns)]
    for batch in batches:
        echo(format_string.format(*batch + padding))
    echo()


class warn_interrupt:
    """A context decorator class used to wrap functions where a keyboard interrupt could potentially
    leave things in a bad state. Warns the user with provided message and exits when wrapped
    function is complete. Requires user to ctrl-c a second time to force exit.

    Usage:

    @warn_interrupt(warning="example message")
    def my_important_func():
        pass
    """

    def __init__(self, warning="Cancelling operation cleanly, one moment... "):
        self.warning = warning
        self.old_int_handler = None
        self.interrupted = False
        self.exit_instructions = style("Hit CTRL-C again to force quit.", fg="red")

    def __enter__(self):
        self.old_int_handler = getsignal(SIGINT)
        signal(SIGINT, self._handle_interrupts)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.interrupted:
            exit(1)
        signal(SIGINT, self.old_int_handler)

        return False

    def _handle_interrupts(self, sig, frame):
        if not self.interrupted:
            self.interrupted = True
            echo("\n{}\n{}".format(self.warning, self.exit_instructions), err=True)
        else:
            exit()

    def __call__(self, func):
        @wraps(func)
        def inner(*args, **kwargs):
            with self:
                return func(*args, **kwargs)

        return inner


def get_url_parts(url_str):
    parts = url_str.split(":")
    port = None
    if len(parts) > 1 and parts[1] != "":
        port = int(parts[1])
    return parts[0], port


def _get_default_header(header_items):
    if not header_items:
        return

    # Creates dict where keys and values are the same for `find_format_width()`.
    header = {}
    for item in header_items:
        keys = item.keys()
        for key in keys:
            if key not in header and isinstance(key, str):
                header[key] = key
    return header


def hash_event(event):
    if isinstance(event, dict):
        event = json.dumps(event, sort_keys=True)
    return md5(event.encode()).hexdigest()
