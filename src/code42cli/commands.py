import click

from code42cli.options import global_options

from code42cli.cmds.alerts import import alerts

@click.group()
@global_options
@click.pass_context
def cli(ctx, sdk):
    ctx.max_content_width = 200

cli.add_command(profile_command)
cli.add_command(legal_hold_command)
cli.add_command(sec_data_command)
cli.add_command(alerts_command)
