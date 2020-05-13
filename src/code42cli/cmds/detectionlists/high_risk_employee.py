from code42cli.cmds.detectionlists import (
    DetectionList,
    DetectionListHandlers,
    load_user_descriptions,
    load_username_description,
    get_user_id,
    update_user,
    try_handle_user_already_added_error,
    try_add_risk_tags,
    try_remove_risk_tags,
)
from code42cli.cmds.detectionlists.enums import DetectionLists, DetectionListUserKeys, RiskTags
from code42cli.commands import Command

from py42.exceptions import Py42BadRequestError


def load_subcommands():
    handlers = _create_handlers()
    detection_list = DetectionList.create_high_risk_employee_list(handlers)
    cmd_list = detection_list.load_subcommands()
    cmd_list.extend(
        [
            Command(
                u"add-risk-tags",
                u"Associates risk tags with a user.",
                handler=add_risk_tags,
                arg_customizer=_load_risk_tag_mgmt_descriptions,
            ),
            Command(
                u"remove-risk-tags",
                u"Disassociates risk tags from a user.",
                handler=remove_risk_tags,
                arg_customizer=_load_risk_tag_mgmt_descriptions,
            ),
        ]
    )
    return cmd_list


def _create_handlers():
    return DetectionListHandlers(
        add=add_high_risk_employee, remove=remove_high_risk_employee, load_add=_load_add_description
    )


def add_risk_tags(sdk, profile, username, risk_tag):
    risk_tag = _handle_list_args(risk_tag)
    user_id = get_user_id(sdk, username)
    try_add_risk_tags(sdk, user_id, risk_tag)


def remove_risk_tags(sdk, profile, username, risk_tag):
    risk_tag = _handle_list_args(risk_tag)
    user_id = get_user_id(sdk, username)
    try_remove_risk_tags(sdk, user_id, risk_tag)


def add_high_risk_employee(sdk, profile, username, cloud_alias=None, risk_tag=None, notes=None):
    """Adds an employee to the high risk employee detection list.
    
    Args:
        sdk (py42.sdk.SDKClient): py42.
        profile (C42Profile): Your code42 profile.
        username (str): The username of the employee to add.
        cloud_alias (str): An alternative email address for another cloud service.
        risk_tag (iter[str]): Risk tags associated with the employee.
        notes: (str): Notes about the employee.
    """
    risk_tag = _handle_list_args(risk_tag)
    user_id = get_user_id(sdk, username)

    try:
        sdk.detectionlists.high_risk_employee.add(user_id)
        update_user(sdk, user_id, cloud_alias, risk_tag, notes)
    except Py42BadRequestError as err:
        list_name = DetectionLists.HIGH_RISK_EMPLOYEE
        try_handle_user_already_added_error(err, username, list_name)
        raise


def remove_high_risk_employee(sdk, profile, username):
    """Removes an employee from the high risk employee detection list.
    
    Args:
        sdk (py42.sdk.SDKClient): py42.
        profile (C42Profile): Your code42 profile.
        username (str): The username of the employee to remove.
    """
    user_id = get_user_id(sdk, username)
    sdk.detectionlists.high_risk_employee.remove(user_id)


def _load_risk_tag_description(argument_collection):
    risk_tag = argument_collection.arg_configs[DetectionListUserKeys.RISK_TAG]
    risk_tag.as_multi_val_param()
    tags = u", ".join(list(RiskTags()))
    risk_tag.set_help(
        u"Risk tags associated with the employee. Options include: [{}].".format(tags)
    )


def _load_add_description(argument_collection):
    load_user_descriptions(argument_collection)
    _load_risk_tag_description(argument_collection)


def _load_risk_tag_mgmt_descriptions(argument_collection):
    load_username_description(argument_collection)
    _load_risk_tag_description(argument_collection)


def _handle_list_args(list_arg):
    """Converts str args to a list. Useful for `bulk` commands which don't use `argparse` but 
    instead pass in values from files, such as in the form "item1 item2"."""
    if list_arg and type(list_arg) != list:
        return list_arg.split()
    return list_arg
