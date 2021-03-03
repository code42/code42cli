from code42cli.click_ext.groups import ExtensionGroup
from code42cli.main import CONTEXT_SETTINGS
from code42cli.options import debug_option
from code42cli.options import pass_state
from code42cli.options import profile_option


def sdk_options(f):
    """Decorator that adds two `click.option`s (--profile, --debug) to wrapped command, as well as
    passing the `code42cli.options.CLIState` object using the [click.make_pass_decorator](https://click.palletsprojects.com/en/7.x/api/#click.make_pass_decorator),
    which automatically instantiates the `py42` sdk using the Code42 profile provided from the `--profile`
    option. The `py42` sdk can be accessed from the `state.sdk` attribute.

    Example:

        @click.command()
        @sdk_options
        def get_current_user_command(state):
            my_user = state.sdk.users.get_current()
            print(my_user)
    """
    f = profile_option()(f)
    f = debug_option()(f)
    f = pass_state(f)
    return f


script = ExtensionGroup(context_settings=CONTEXT_SETTINGS)
"""A `click.Group` subclass that enables the Code42 CLI's custom error handling/logging to be used
in extension scripts. If only a single command is added to the `script` group it also uses that
command as the default, so the command name doesn't need to be called explicitly.

Example:

    @click.command()
    @click.argument("guid")
    @sdk_options
    def get_device_info(state, guid)
        device = state.sdk.devices.get_by_guid(guid)
        print(device)

    if __name__ == "__main__":
        script.add_command(my_command)
        script()

The script can then be invoked directly without needing to call the `get-device-info` subcommand:

    python script.py --profile my_profile <guid>
"""
