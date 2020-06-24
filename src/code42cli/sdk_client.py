import py42.sdk
import py42.settings.debug as debug
import py42.settings

from code42cli.errors import UserDoesNotExistError
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


def get_user_id(sdk, username):
    """Returns the user's UID (referred to by `user_id` in detection lists). Raises 
    `UserDoesNotExistError` if the user doesn't exist in the Code42 server.
    
    Args:
        sdk (py42.sdk.SDKClient): The py42 sdk.
        username (str or unicode): The username of the user to get an ID for.
    
    Returns:
         str: The user ID for the user with the given username.
    """
    users = sdk.users.get_by_username(username)[u"users"]
    if not users:
        raise UserDoesNotExistError(username)
    return users[0][u"userUid"]
