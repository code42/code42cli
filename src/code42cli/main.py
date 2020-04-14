import sys

import platform

from code42cli.cmds import profile
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


def main():
    top = Command("", "", subcommand_loader=_load_top_commands)
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
    ]


if __name__ == "__main__":
    main()
