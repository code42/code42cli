from code42cli.cmds.detectionlists.enums import DetectionLists
from code42cli.cmds.detectionlists import (
    DetectionList,
    DetectionListHandlers,
    load_username_description,
    get_user_id,
    update_user,
)


def load_subcommands():
    handlers = DetectionListHandlers(add=add_high_risk_employee, load_add=_load_add_description)
    detection_list = DetectionList(DetectionLists.HIGH_RISK_EMPLOYEE, handlers)
    return detection_list.load_subcommands()


def _get_handlers():
    return DetectionListHandlers(add=add_high_risk_employee, load_add=_load_add_description)


def add_high_risk_employee(
    sdk, profile, username, cloud_aliases=None, risk_factors=None, notes=None
):
    """Adds an employee to the high risk detection list.
    
    Args:
        sdk (py42.sdk.SDKClient): py42
        profile (C42Profile): Your code42 profile
        username (str): The username of the employee to add.
        cloud_aliases (iter[str]): Alternative emails addresses for other cloud services.
        risk_factors (iter[str]): Risk factors associated with the employee.
        notes: (str): Notes about the employee.
    """
    user_id = get_user_id(sdk, username)
    update_user(sdk, user_id, cloud_aliases, risk_factors, notes)
    sdk.detectionlists.high_risk_employee.add(user_id)


def _load_add_description(argument_collection):
    load_username_description(argument_collection)
    risk_factors = argument_collection.arg_configs[u"risk_factors"]
    risk_factors.set_help(u"Risk factors associated with the employee.")
