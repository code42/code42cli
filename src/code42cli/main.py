import os
import signal
import site
import sys
import warnings

import click
from click_plugins import with_plugins
from pkg_resources import iter_entry_points
from py42.settings import set_user_agent_suffix

from code42cli import BANNER
from code42cli import PRODUCT_NAME
from code42cli.click_ext.groups import ExceptionHandlingGroup
from code42cli.cmds.alert_rules import alert_rules
from code42cli.cmds.alerts import alerts
from code42cli.cmds.auditlogs import audit_logs
from code42cli.cmds.cases import cases
from code42cli.cmds.departing_employee import departing_employee
from code42cli.cmds.devices import devices
from code42cli.cmds.high_risk_employee import high_risk_employee
from code42cli.cmds.legal_hold import legal_hold
from code42cli.cmds.profile import profile
from code42cli.cmds.securitydata import security_data
from code42cli.cmds.shell import shell
from code42cli.cmds.trustedactivities import trusted_activities
from code42cli.cmds.users import users
from code42cli.cmds.watchlists import watchlists
from code42cli.options import sdk_options

warnings.simplefilter("ignore", DeprecationWarning)


# Handle KeyboardInterrupts by just exiting instead of printing out a stack
def exit_on_interrupt(signal, frame):
    click.echo(err=True)
    sys.exit(1)


signal.signal(signal.SIGINT, exit_on_interrupt)

# Sets part of the user agent string that py42 attaches to requests for the purposes of
# identifying CLI users.
set_user_agent_suffix(PRODUCT_NAME)

CONTEXT_SETTINGS = {
    "help_option_names": ["-h", "--help"],
    "max_content_width": 200,
}


@with_plugins(iter_entry_points("code42cli.plugins"))
@click.group(
    cls=ExceptionHandlingGroup,
    context_settings=CONTEXT_SETTINGS,
    help=BANNER,
    invoke_without_command=True,
    no_args_is_help=True,
)
@click.option(
    "--python",
    is_flag=True,
    help="Print path to the python interpreter env that `code42cli` is installed in.",
)
@click.option(
    "--script-dir",
    is_flag=True,
    help="Print the directory the `code42` script was installed in (for adding to your PATH if needed).",
)
@sdk_options(hidden=True)
def cli(state, python, script_dir):
    if python:
        click.echo(sys.executable)
        sys.exit(0)
    if script_dir:
        for root, _dirs, files in os.walk(site.PREFIXES[0]):
            if "code42" in files or "code42.exe" in files:
                print(root)
                sys.exit(0)

        for root, _dirs, files in os.walk(site.USER_BASE):
            if "code42" in files or "code42.exe" in files:
                print(root)
                sys.exit(0)


cli.add_command(alerts)
cli.add_command(alert_rules)
cli.add_command(audit_logs)
cli.add_command(cases)
cli.add_command(departing_employee)
cli.add_command(devices)
cli.add_command(high_risk_employee)
cli.add_command(legal_hold)
cli.add_command(profile)
cli.add_command(security_data)
cli.add_command(shell)
cli.add_command(users)
cli.add_command(trusted_activities)
cli.add_command(watchlists)
