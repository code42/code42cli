import click

from code42cli.profile import get_profile
from code42cli.sdk_client import create_sdk


class CLIState(object):
    def __init__(self):
        self.profile = get_profile()
        self.debug = False
        self._sdk = None
        self.search_filters = []
        self.cursor = None

    @property
    def sdk(self):
        if self._sdk is None:
            self._sdk = create_sdk(self.profile, self.debug)
        return self._sdk


def set_profile(ctx, value):
    """Sets the profile on the global state object when --profile <name> is passed to commands 
    decorated with @global_options."""
    if value:
        ctx.ensure_object(CLIState).profile = get_profile(value)


def set_debug(ctx, value):
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


def global_options(f):
    f = profile_option(f)
    f = debug_option(f)
    f = pass_state(f)
    return f


def incompatible_with(incompatible_opts):
    """Returns a custom click.Option subclass that is incompatible with the option names 
    provided.
    """
    if isinstance(incompatible_opts, str):
        incompatible_opts = [incompatible_opts]

    class IncompatibleOption(click.Option):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

        def handle_parse_result(self, ctx, opts, args):
            found_incompatible = ", ".join(
                ["--{}".format(opt) for opt in opts if opt in incompatible_opts]
            )
            if self.name in opts and found_incompatible:
                raise click.BadOptionUsage(
                    option_name=self.name,
                    message="--{} can't be used with: {}".format(self.name, found_incompatible),
                )
            return super().handle_parse_result(ctx, opts, args)

    return IncompatibleOption
