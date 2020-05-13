import sys
from functools import wraps
from os import makedirs, path
from signal import signal, getsignal, SIGINT

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


def is_interactive():
    return sys.stdin.isatty()


def get_url_parts(url_str):
    parts = url_str.split(u":")
    port = None
    if len(parts) > 1 and parts[1] != u"":
        port = int(parts[1])
    return parts[0], port


class warn_interrupt(object):
    def __init__(self, warning="The code42 cli is working... "):
        self.warning = warning
        self.old_handler = None
        self.interrupted = False
        self.exit_instructions = "Hit CTRL-C again to quit anyway."

    def __enter__(self):
        self.old_handler = getsignal(SIGINT)
        signal(SIGINT, self._handle_interrupts)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        signal(SIGINT, self.old_handler)
        return False

    def _handle_interrupts(self, sig, frame):
        if not self.interrupted:
            self.interrupted = True
            print("\n{}\n{}".format(self.warning, self.exit_instructions), file=sys.stderr)
        else:
            exit()

    def __call__(self, func):
        @wraps(func)
        def inner(*args, **kwds):
            with self:
                return func(*args, **kwds)

        return inner
