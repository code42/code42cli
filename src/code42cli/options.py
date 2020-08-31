from collections import OrderedDict

import click

from code42cli.cmds.search.enums import ServerProtocol
from code42cli.errors import Code42CLIError
from code42cli.output_formats import OutputFormat
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


def incompatible_with(incompatible_opts):

    if isinstance(incompatible_opts, str):
        incompatible_opts = [incompatible_opts]

    class IncompatibleOption(click.Option):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

        def handle_parse_result(self, ctx, opts, args):
            # if None it means we're in autocomplete mode and don't want to validate
            if ctx.obj is not None:
                found_incompatible = ", ".join(
                    [
                        "--{}".format(opt.replace("_", "-"))
                        for opt in opts
                        if opt in incompatible_opts
                    ]
                )
                if self.name in opts and found_incompatible:
                    name = self.name.replace("_", "-")
                    raise click.BadOptionUsage(
                        option_name=self.name,
                        message="--{} can't be used with: {}".format(
                            name, found_incompatible
                        ),
                    )
            return super().handle_parse_result(ctx, opts, args)

    return IncompatibleOption


class OrderedGroup(click.Group):
    """A click.Group subclass that uses OrderedDict to store commands so the help text lists them
    in the order they were defined/added to the group.
    """

    def __init__(self, name=None, commands=None, **attrs):
        super().__init__(name, commands, **attrs)
        # the registered subcommands by their exported names.
        self.commands = commands or OrderedDict()

    def list_commands(self, ctx):
        return self.commands


def server_options(f):
    hostname_arg = click.argument("hostname")
    protocol_option = click.option(
        "-p",
        "--protocol",
        type=click.Choice(ServerProtocol(), case_sensitive=False),
        default=ServerProtocol.UDP,
        help="Protocol used to send logs to server. Defaults to UDP",
    )
    f = hostname_arg(f)
    f = protocol_option(f)
    return f
