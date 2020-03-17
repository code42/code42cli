import platform
from argparse import ArgumentParser, RawDescriptionHelpFormatter

import code42cli.securitydata.main as securitydata
from code42cli.compat import str
from code42cli.profile import profile

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
    description = u"""
    Groups:
        profile      - For managing Code42 settings.
        securitydata - Tools for getting security related data, such as file events.
    """
    code42_arg_parser = ArgumentParser(
        formatter_class=RawDescriptionHelpFormatter,
        description=description,
        usage=u"code42 <group> <subcommand> <optional args>",
    )
    subcommand_parser = code42_arg_parser.add_subparsers(title=u"groups")
    profile.init(subcommand_parser)
    securitydata.init_subcommand(subcommand_parser)
    _run(code42_arg_parser)


def _run(parser):
    try:
        args = parser.parse_args()
        args.func(args)
    except AttributeError as ex:
        if str(ex) == u"'Namespace' object has no attribute 'func'":
            parser.print_help()
            return
        raise ex


if __name__ == "__main__":
    main()
