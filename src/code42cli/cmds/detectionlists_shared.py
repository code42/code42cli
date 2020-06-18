from py42.exceptions import Py42BadRequestError

from code42cli.cmds.detectionlists import RiskTags, handle_list_args
from code42cli.errors import UnknownRiskTagError
from code42cli.util import get_user_id


def update_user(sdk, user_id, cloud_alias=None, risk_tag=None, notes=None):
    """Updates a detection list user.
    
    Args:
        sdk (py42.sdk.SDKClient): py42 sdk.
        user_id (str or unicode): The ID of the user to update. This is their `userUid` found from 
            `sdk.users.get_by_username()`.
        cloud_alias (str or unicode): A cloud alias to add to the user.
        risk_tag (iter[str or unicode]): A list of risk tags associated with user.
        notes (str or unicode): Notes about the user.
    """
    if cloud_alias:
        sdk.detectionlists.add_user_cloud_alias(user_id, cloud_alias)
    if risk_tag:
        try_add_risk_tags(sdk, user_id, risk_tag)
    if notes:
        sdk.detectionlists.update_user_notes(user_id, notes)


def try_add_risk_tags(sdk, user_id, risk_tag):
    _try_add_or_remove_risk_tags(user_id, risk_tag, sdk.detectionlists.add_user_risk_tags)


def try_remove_risk_tags(sdk, user_id, risk_tag):
    _try_add_or_remove_risk_tags(user_id, risk_tag, sdk.detectionlists.remove_user_risk_tags)


def _try_add_or_remove_risk_tags(user_id, risk_tag, func):
    try:
        func(user_id, risk_tag)
    except Py42BadRequestError:
        _try_handle_bad_risk_tag(risk_tag)
        raise


def _try_handle_bad_risk_tag(tags):
    options = list(RiskTags())
    unknowns = [tag for tag in tags if tag not in options] if tags else None
    if unknowns:
        raise UnknownRiskTagError(unknowns)


def add_risk_tags(sdk, profile, username, tag):
    risk_tag = handle_list_args(tag)
    user_id = get_user_id(sdk, username)
    try_add_risk_tags(sdk, user_id, risk_tag)


def remove_risk_tags(sdk, profile, username, tag):
    risk_tag = handle_list_args(tag)
    user_id = get_user_id(sdk, username)
    try_remove_risk_tags(sdk, user_id, risk_tag)
