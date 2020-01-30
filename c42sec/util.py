import sys
from os import path, makedirs


SERVICE_NAME = u"c42sec"


def get_input(prompt):
    if sys.version_info >= (3, 0):
        return input(prompt)
    else:
        return raw_input(prompt)


def get_user_project_path(subdir=""):
    """The path on your user dir to /.c42sec/[subdir]"""
    package_name = __name__.split(".")[0]
    home = path.expanduser("~")
    user_project_path = path.join(home, ".{0}".format(package_name), subdir)

    if not path.exists(user_project_path):
        makedirs(user_project_path)

    return user_project_path
