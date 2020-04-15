import platform
import sys

from py42.sdk.settings import set_user_agent_suffix

from code42cli import PRODUCT_NAME
from code42cli.cmds import profile
from code42cli.cmds.detectionlists import main as dlmain
from code42cli.cmds.securitydata import main as secmain
from code42cli.commands import Command
from code42cli.invoker import CommandInvoker

# If on Windows, configure console session to handle ANSI escape sequences correctly
# source: https://bugs.python.org/issue29059
if platform.system().lower() == u"windows":
    from ctypes import windll, c_int, byref

    stdout_handle = windll.kernel32.GetStdHandle(c_int(-11))
    mode = c_int(0)
    windll.kernel32.GetConsoleMode(c_int(stdout_handle), byref(mode))
    mode = c_int(mode.value | 4)
    windll.kernel32.SetConsoleMode(c_int(stdout_handle), mode)


# Sets part of the user agent string that py42 attaches to requests for the purposes of
# identifying CLI users.
set_user_agent_suffix(PRODUCT_NAME)


def main():
    top = Command(u"", u"", subcommand_loader=_load_top_commands)
    invoker = CommandInvoker(top)
    invoker.run(sys.argv[1:])


def _load_top_commands():
    return [
        Command(
            u"profile", u"For managing Code42 settings.", subcommand_loader=profile.load_subcommands
        ),
        Command(
            u"security-data",
            u"Tools for getting security related data, such as file events.",
            subcommand_loader=secmain.load_subcommands,
        ),
        Command(
            u"detection-lists",
            u"For adding and removing employees from detection lists.",
            subcommand_loader=dlmain.load_subcommands,
        ),
    ]


if __name__ == "__main__":
    main()
