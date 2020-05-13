from __future__ import print_function
import sys
from os import makedirs, path

from code42cli.compat import open

_PADDING_SIZE = 3


def get_input(prompt):
    """Uses correct input function based on Python version."""
    # pylint: disable=undefined-variable
    if sys.version_info >= (3, 0):
        return input(prompt)
    else:
        return raw_input(prompt)


def does_user_agree(prompt):
    """Prompts the user and checks if they said yes."""
    ans = get_input(prompt)
    ans = ans.strip().lower()
    return ans == u"y"


def get_user_project_path(subdir=u""):
    """The path on your user dir to /.code42cli/[subdir]."""
    package_name = __name__.split(u".")[0]
    home = path.expanduser(u"~")
    hidden_package_name = u".{0}".format(package_name)
    user_project_path = path.join(home, hidden_package_name, subdir)
    if not path.exists(user_project_path):
        makedirs(user_project_path)
    return user_project_path


def open_file(file_path, mode, action):
    """Wrapper for opening files, useful for testing purposes."""
    with open(file_path, mode, encoding=u"utf-8") as f:
        return action(f)


def is_interactive():
    return sys.stdin.isatty()


def get_url_parts(url_str):
    parts = url_str.split(u":")
    port = None
    if len(parts) > 1 and parts[1] != u"":
        port = int(parts[1])
    return parts[0], port


def find_format_width(record, header):
    """Fetches needed keys/items to be displayed based on header keys.
    
    Finds the largest string against each column so as to decide the padding size for the column.
    
    Args:
        record (list of dict), data to be formatted.  
        header (dict), key-value where keys should map to keys of record dict and
          value is the corresponding column name to be displayed on the cli.
    
    Returns:
        tuple (list of dict, dict), i.e Filtered records, padding size of columns.
    """
    rows = [header]

    # Set default max width items to column names
    max_width_item = dict(header.items())
    for record_row in record:
        row = {}
        for header_key in header.keys():
            row[header_key] = record_row[header_key]
            max_width_item[header_key] = max(
                max_width_item[header_key], str(record_row[header_key]), key=len
            )
        rows.append(row)
    column_size = {key: len(value) for key, value in max_width_item.items()}
    return rows, column_size


def format_to_table(rows, column_size):
    """Prints result in left justified format in a tabular form.
    """
    for row in rows:
        for key in row.keys():
            print(repr(row[key]).ljust(column_size[key] + _PADDING_SIZE), end=u" ")
        print(u"")
