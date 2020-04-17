from code42cli.cmds.detectionlists.enums import DetectionLists
from code42cli.cmds.detectionlists import (
    DetectionList,
    DetectionListHandlers,
    load_user_descriptions,
    get_user_id,
    update_user,
)


def load_subcommands():
    handlers = _get_handlers()
    detection_list = DetectionList(DetectionLists.HIGH_RISK_EMPLOYEE, handlers)
    return detection_list.load_subcommands()


def _get_handlers():
    return DetectionListHandlers(add=add_departing_employee, load_add=_load_add_description)


def add_departing_employee(
    sdk, profile, username, cloud_aliases=None, departure_date=None, notes=None
):
    """Adds an employee to the high risk detection list.

    Args:
        sdk (py42.sdk.SDKClient): py42
        profile (C42Profile): Your code42 profile
        username (str): The username of the employee to add.
        cloud_aliases (iter[str]): Alternative emails addresses for other cloud services.
        departure_date (str): The date the employee is departing.
        notes: (str): Notes about the employee.
    """
    if cloud_aliases and type(cloud_aliases) != list:
        cloud_aliases = cloud_aliases.split()

    user_id = get_user_id(sdk, username)
    update_user(sdk, user_id, cloud_aliases, departure_date, notes)
    sdk.detectionlists.high_risk_employee.add(user_id)


def remove_high_risk_employee(sdk, profile, username):
    user_id = get_user_id(sdk, username)
    sdk.detectionlists.departing_employee.remove(user_id)


def _load_add_description(argument_collection):
    load_user_descriptions(argument_collection)
    risk_factors = argument_collection.arg_configs[u"departure_date"]
    risk_factors.as_multi_val_param()
    risk_factors.set_hdelp(u"The date the employee is departing.")
