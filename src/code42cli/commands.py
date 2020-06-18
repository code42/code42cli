import click

from code42cli.options import global_options, OrderedGroup
from code42cli.cmds.alerts import alerts
from code42cli.cmds.alert_rules import alert_rules
from code42cli.cmds.securitydata import security_data
from code42cli.cmds.legal_hold import legal_hold

CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"], "max_content_width": 200}


@click.group(cls=OrderedGroup, context_settings=CONTEXT_SETTINGS)
@global_options
def cli(state):
    pass


cli.add_command(alerts)
cli.add_command(alert_rules)
cli.add_command(security_data)
cli.add_command(legal_hold)
