from __future__ import print_function, with_statement

import sys
from os import path, makedirs
from code42cli.compat import open


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


def print_error(error_text):
    """Prints red text."""
    print(u"\033[91mERROR: {}\033[0m".format(error_text))


def print_bold(bold_text):
    print(u"\033[1m{}\033[0m".format(bold_text))


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
