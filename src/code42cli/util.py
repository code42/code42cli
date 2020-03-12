from __future__ import print_function, with_statement

import sys
from os import path, makedirs


def get_input(prompt):
    """Uses correct input function based on Python version."""
    # pylint: disable=undefined-variable
    if sys.version_info >= (3, 0):
        return input(prompt)
    else:
        return raw_input(prompt)


def get_user_project_path(subdir=""):
    """The path on your user dir to /.code42cli/[subdir]."""
    package_name = __name__.split(".")[0]
    home = path.expanduser("~")
    user_project_path = path.join(home, ".{0}".format(package_name), subdir)

    if not path.exists(user_project_path):
        makedirs(user_project_path)

    return user_project_path


def open_file(file_path, mode, action):
    """Wrapper for opening files, useful for testing purposes."""
    with open(file_path, mode) as f:
        action(f)


def print_error(error_text):
    """Prints red text."""
    print("\033[91mUSAGE ERROR: {}\033[0m".format(error_text))


def print_bold(bold_text):
    print("\033[1m{}\033[0m".format(bold_text))


def is_interactive():
    return sys.stdin.isatty()


def print_no_existing_profile_message():
    print_error(u"No existing profile.")
    print_set_profile_help()


def print_set_profile_help():
    print(u"")
    print(u"To add a profile, use: ")
    print_bold(u"\tcode42 profile set --profile <profile-name> -s <authority-URL> -u <username>")
    print(u"")


def get_url_parts(url_str):
    parts = url_str.split(u":")
    port = None
    if len(parts) > 1 and parts[1] != u"":
        port = int(parts[1])
    return parts[0], port
