import click
import IPython

from code42cli import BANNER
from code42cli.options import sdk_options


@click.command()
@sdk_options()
def console(state):
    """Open an IPython shell with py42 initialized as `sdk`."""
    IPython.embed(colors="Neutral", banner1=BANNER, user_ns={"sdk": state.sdk})
