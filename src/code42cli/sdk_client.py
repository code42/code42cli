import click

import py42.sdk
import py42.settings.debug as debug
import py42.settings

from code42cli.logger import get_main_cli_logger
from code42cli.profile import get_profile

py42.settings.items_per_page = 500


def create_sdk(profile, is_debug_mode):
    if is_debug_mode:
        py42.settings.debug.level = debug.DEBUG
    try:
        password = profile.get_password()
        return py42.sdk.from_local_account(profile.authority_url, profile.username, password)
    except Exception:
        logger = get_main_cli_logger()
        logger.print_and_log_error(
            u"Invalid credentials or host address. "
            u"Verify your profile is set up correctly and that you are supplying the correct password."
        )
        exit(1)


def validate_connection(authority_url, username, password):
    try:
        py42.sdk.from_local_account(authority_url, username, password)
        return True
    except:
        return False


class CLIContext(object):
    def __init__(self):
        self.profile = get_profile()
        self.debug = False
        self._sdk = None
        self.search_filters = []

    def __getattr__(self, item):
        if self._sdk is None:
            self._sdk = create_sdk(self.profile, self.debug)
        return getattr(self._sdk, item)


def set_profile(ctx, value):
    if not value:
        return
    ctx.ensure_object(CLIContext).profile = get_profile(value)


def set_debug(ctx, value):
    if not value:
        return
    ctx.ensure_object(CLIContext).debug = value


profile_option = click.option("--profile", expose_value=False, callback=set_profile)
debug_option = click.option("-d", "--debug", is_flag=True, expose_value=False, callback=set_debug)
pass_sdk = click.make_pass_decorator(CLIContext, ensure=True)


def sdk_options(f):
    f = profile_option(f)
    f = debug_option(f)
    f = pass_sdk(f)
    return f
