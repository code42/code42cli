import click

from code42cli.options import global_options


@click.group()
@global_options
@click.pass_context
def cli(ctx, sdk):
    ctx.max_content_width = 200
