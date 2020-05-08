import sys
from os import makedirs, path

from code42cli.compat import open
PADDING_SIZE = 3


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


def process_rules_for_formatting(rules, header):
    column_size = {key: len(column_name) for key, column_name in header.items()}
    rows = []
    rows.append(header)
    for rule in rules:
        row = {}
        for key in header.keys():
            row[key] = rule[key]
            if type(rule[key]) is bool:
                continue
            if column_size[key] < len(rule[key]):
                column_size[key] = len(rule[key])
        rows.append(row)
    return rows, column_size


def format_to_table(rows, column_size):
    for row in rows:
        for key in row.keys():
            print(repr(row[key]).ljust(column_size[key] + PADDING_SIZE), end=' ')
        print("")
