from code42cli.cmds.shared import get_user_id
from code42cli.errors import UserAlreadyAddedError


def update_user(sdk, username, cloud_alias=None, risk_tag=None, notes=None):
    """Updates a detection list user.

    Args:
        sdk (py42.sdk.SDKClient): py42 sdk.
        user_id (str or unicode): The ID of the user to update. This is their `userUid` found from 
            `sdk.users.get_by_username()`.
        cloud_alias (str or unicode): A cloud alias to add to the user.
        risk_tag (iter[str or unicode]): A list of risk tags associated with user.
        notes (str or unicode): Notes about the user.
    """
    user_id = get_user_id(sdk, username)
    if cloud_alias:
        sdk.detectionlists.add_user_cloud_alias(user_id, cloud_alias)
    if risk_tag:
        add_risk_tags(sdk, username, risk_tag)
    if notes:
        sdk.detectionlists.update_user_notes(user_id, notes)


def add_risk_tags(sdk, username, risk_tag):
    risk_tag = handle_list_args(risk_tag)
    user_id = get_user_id(sdk, username)
    sdk.detectionlists.add_user_risk_tags(user_id, risk_tag)


def remove_risk_tags(sdk, username, risk_tag):
    risk_tag = handle_list_args(risk_tag)
    user_id = get_user_id(sdk, username)
    sdk.detectionlists.remove_user_risk_tags(user_id, risk_tag)


def try_handle_user_already_added_error(bad_request_err, username_tried_adding, list_name):
    if _error_is_user_already_added(bad_request_err.response.text):
        raise UserAlreadyAddedError(username_tried_adding, list_name)
    return False


def _error_is_user_already_added(bad_request_error_text):
    return "User already on list" in bad_request_error_text


def handle_list_args(list_arg):
    """Converts str args to a list. Useful for `bulk` commands which don't use click's argument 
    parsing but instead pass in values from files, such as in the form "item1 item2"."""
    if isinstance(list_arg, str):
        return list_arg.split()
    return list_arg
