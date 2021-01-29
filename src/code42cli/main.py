import signal
import sys

import click
from py42.__version__ import __version__ as py42version
from py42.settings import set_user_agent_suffix

from code42cli import PRODUCT_NAME
from code42cli.__version__ import __version__ as cliversion
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
from code42cli.options import sdk_options

BANNER = """\b
 dP""b8  dP"Yb  8888b. 888888  dP88  oP"Yb.
dP   `" dP   Yb 8I  Yb 88__   dP 88  "' dP'
Yb      Yb   dP 8I  dY 88""  d888888   dP'
 YboodP  YbodP  8888Y" 888888    88  .d8888

code42cli version {}, by Code42 Software.
powered by py42 version {}.""".format(
    cliversion, py42version
)


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


@click.group(cls=ExceptionHandlingGroup, context_settings=CONTEXT_SETTINGS, help=BANNER)
@sdk_options(hidden=True)
def cli(state):
    pass


cli.add_command(alerts)
cli.add_command(alert_rules)
cli.add_command(security_data)
cli.add_command(departing_employee)
cli.add_command(high_risk_employee)
cli.add_command(legal_hold)
cli.add_command(profile)
cli.add_command(devices)
cli.add_command(audit_logs)
cli.add_command(cases)
