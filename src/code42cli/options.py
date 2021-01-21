import click

from code42cli.click_ext.types import MagicDate
from code42cli.cmds.search.enums import ServerProtocol
from code42cli.cmds.search.options import AdvancedQueryAndSavedSearchIncompatible
from code42cli.cmds.search.options import BeginOption
from code42cli.date_helper import convert_datetime_to_timestamp
from code42cli.date_helper import round_datetime_to_day_end
from code42cli.date_helper import round_datetime_to_day_start
from code42cli.errors import Code42CLIError
from code42cli.output_formats import OutputFormat
from code42cli.output_formats import SendToFileEventsOutputFormat
from code42cli.profile import get_profile
from code42cli.sdk_client import create_sdk


yes_option = click.option(
    "-y",
    "--assume-yes",
    is_flag=True,
    expose_value=False,
    callback=lambda ctx, param, value: ctx.obj.set_assume_yes(value),
    help='Assume "yes" as the answer to all prompts and run non-interactively.',
)

format_option = click.option(
    "-f",
    "--format",
    type=click.Choice(OutputFormat(), case_sensitive=False),
    help="The output format of the result. Defaults to table format.",
    default=OutputFormat.TABLE,
)


class CLIState:
    def __init__(self):
        try:
            self._profile = get_profile()
        except Code42CLIError:
            self._profile = None
        self.debug = False
        self._sdk = None
        self.search_filters = []
        self.assume_yes = False

    @property
    def profile(self):
        if self._profile is None:
            self._profile = get_profile()
        return self._profile

    @profile.setter
    def profile(self, value):
        self._profile = value

    @property
    def sdk(self):
        if self._sdk is None:
            self._sdk = create_sdk(self.profile, self.debug)
        return self._sdk

    def set_assume_yes(self, param):
        self.assume_yes = param


def set_profile(ctx, param, value):
    """Sets the profile on the global state object when --profile <name> is passed to commands
    decorated with @global_options."""
    if value:
        ctx.ensure_object(CLIState).profile = get_profile(value)


def set_debug(ctx, param, value):
    """Sets debug to True on global state object when --debug/-d is passed to commands decorated
    with @global_options.
    """
    if value:
        ctx.ensure_object(CLIState).debug = value


def profile_option(hidden=False):
    opt = click.option(
        "--profile",
        expose_value=False,
        callback=set_profile,
        hidden=hidden,
        help="The name of the Code42 CLI profile to use when executing this command.",
    )
    return opt


def debug_option(hidden=False):
    opt = click.option(
        "-d",
        "--debug",
        is_flag=True,
        expose_value=False,
        callback=set_debug,
        hidden=hidden,
        help="Turn on debug logging.",
    )
    return opt


pass_state = click.make_pass_decorator(CLIState, ensure=True)


def sdk_options(hidden=False):
    def decorator(f):
        f = profile_option(hidden)(f)
        f = debug_option(hidden)(f)
        f = pass_state(f)
        return f

    return decorator


def server_options(f):
    hostname_arg = click.argument("hostname")
    protocol_option = click.option(
        "-p",
        "--protocol",
        type=click.Choice(ServerProtocol(), case_sensitive=False),
        default=ServerProtocol.UDP,
        help="Protocol used to send logs to server. Defaults to UDP.",
    )
    f = hostname_arg(f)
    f = protocol_option(f)
    return f


send_to_format_options = click.option(
    "-f",
    "--format",
    type=click.Choice(SendToFileEventsOutputFormat(), case_sensitive=False),
    help="The output format of the result. Defaults to json format.",
    default=SendToFileEventsOutputFormat.RAW,
)


def begin_option(term, **kwargs):
    defaults = dict(
        type=MagicDate(rounding_func=round_datetime_to_day_start),
        help=f"The beginning of the date range in which to look for {term}. {MagicDate.HELP_TEXT}",
        cls=BeginOption,
        callback=lambda ctx, param, arg: convert_datetime_to_timestamp(arg),
    )
    defaults.update(kwargs)
    return click.option("-b", "--begin", **defaults)


def end_option(term, **kwargs):
    defaults = dict(
        type=MagicDate(rounding_func=round_datetime_to_day_end),
        cls=AdvancedQueryAndSavedSearchIncompatible,
        help=f"The end of the date range in which to look for {term}, argument format options are "
        "the same as `--begin`.",
        callback=lambda ctx, param, arg: convert_datetime_to_timestamp(arg),
    )
    defaults.update(kwargs)
    return click.option("-e", "--end", **defaults)


def checkpoint_option(term, **kwargs):
    defaults = dict(help=f"Only get {term} that were not previously retrieved.")
    defaults.update(kwargs)
    return click.option("-c", "--use-checkpoint", **defaults)


def set_begin_default_dict(term):
    return dict(
        type=MagicDate(rounding_func=round_datetime_to_day_start),
        help=f"The beginning of the date range in which to look for {term}. {MagicDate.HELP_TEXT}",
        callback=lambda ctx, param, arg: convert_datetime_to_timestamp(arg),
    )


def set_end_default_dict(term):
    return dict(
        type=MagicDate(rounding_func=round_datetime_to_day_end),
        help=f"The end of the date range in which to look for {term}, argument format options are "
        "the same as `--begin`.",
        callback=lambda ctx, param, arg: convert_datetime_to_timestamp(arg),
    )
