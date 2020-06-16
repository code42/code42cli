import click

from code42cli.sdk_client import sdk_options


@click.group()
@sdk_options
@click.pass_context
def cli(ctx, sdk):
    ctx.max_content_width = 200
