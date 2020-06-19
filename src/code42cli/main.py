import platform
import signal
import sys

import click

from code42cli.options import global_options, OrderedGroup
from code42cli.cmds.alerts import alerts
from code42cli.cmds.alert_rules import alert_rules
from code42cli.cmds.securitydata import security_data

from code42cli.cmds.departing_employee import departing_employee
from code42cli.cmds.high_risk_employee import high_risk_employee
from code42cli.cmds.legal_hold import legal_hold


from py42.settings import set_user_agent_suffix

from code42cli import PRODUCT_NAME
from code42cli.util import flush_stds_out_err_without_printing_error


# Handle KeyboardInterrupts by just exiting instead of printing out a stack
def exit_on_interrupt(signal, frame):
    print()
    sys.exit(1)


signal.signal(signal.SIGINT, exit_on_interrupt)


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

CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"], "max_content_width": 200}


@click.group(cls=OrderedGroup, context_settings=CONTEXT_SETTINGS)
@global_options
def cli(state):
    pass


cli.add_command(alerts)
cli.add_command(alert_rules)
cli.add_command(security_data)
cli.add_command(departing_employee)
cli.add_command(high_risk_employee)
cli.add_command(legal_hold)


def main():
    try:
        cli()
    finally:
        flush_stds_out_err_without_printing_error()


if __name__ == u"__main__":
    main()
