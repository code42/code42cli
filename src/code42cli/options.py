from collections import OrderedDict

import click

from code42cli.errors import Code42CLIError
from code42cli.profile import get_profile
from code42cli.sdk_client import create_sdk


class CLIState(object):
    def __init__(self):
        try:
            self._profile = get_profile()
        except Code42CLIError:
            self._profile = None
        self.debug = False
        self._sdk = None
        self.search_filters = []
        self.cursor_class = None

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


profile_option = click.option(
    "--profile",
    expose_value=False,
    callback=set_profile,
    help="The name of the Code42 CLI profile to use when executing this command.",
)
debug_option = click.option(
    "-d",
    "--debug",
    is_flag=True,
    expose_value=False,
    callback=set_debug,
    help="Turn on debug logging.",
)
pass_state = click.make_pass_decorator(CLIState, ensure=True)


def sdk_options(f):
    f = profile_option(f)
    f = debug_option(f)
    f = pass_state(f)
    return f


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
                        message="--{} can't be used with: {}".format(name, found_incompatible),
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
