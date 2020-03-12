from py42 import settings
from py42.sdk import SDK
from py42.settings import debug_level
from code42cli.util import print_error


def create_sdk(profile, is_debug_mode):
    if is_debug_mode:
        settings.debug_level = debug_level.DEBUG
    try:
        password = profile.get_stored_password()
        return SDK.create_using_local_account(profile.authority_url, profile.username, password)
    except Exception:
        print_error(
            u"Invalid credentials or host address. "
            u"Verify your profile is set up correctly and that you are supplying the correct password."
        )
        exit(1)


def test_connection(username, password, authority_url):
    try:
        SDK.create_using_local_account(authority_url, username, password)
        return True
    except:
        return False
