import click

import py42.sdk
import py42.settings.debug as debug
import py42.settings

from code42cli.logger import get_main_cli_logger

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


class SDK(object):
    def __init__(self):
        ctx = click.get_current_context()
        self._sdk = create_sdk(ctx.obj['profile'], ctx.obj['debug'])

    def __getattr__(self, item):
        return getattr(self._sdk, item)


pass_sdk = click.make_pass_decorator(SDK, ensure=True)
