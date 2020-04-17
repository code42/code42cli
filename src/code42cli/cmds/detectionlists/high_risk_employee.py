from code42cli.cmds.detectionlists import (
    DetectionList,
    DetectionListHandlers,
    load_user_descriptions,
    get_user_id,
    update_user,
)
from code42cli.cmds.detectionlists.enums import DetectionListUserKeys


def load_subcommands():
    handlers = _get_handlers()
    detection_list = DetectionList.create_high_risk_list(handlers)
    return detection_list.load_subcommands()


def _get_handlers():
    return DetectionListHandlers(add=add_high_risk_employee, load_add=_load_add_description)


def add_high_risk_employee(sdk, profile, username, cloud_alias=None, risk_tag=None, notes=None):
    """Adds an employee to the high risk detection list.
    
    Args:
        sdk (py42.sdk.SDKClient): py42
        profile (C42Profile): Your code42 profile
        username (str): The username of the employee to add.
        cloud_alias (iter[str]): Alternative emails addresses for other cloud services.
        risk_tag (iter[str]): Risk tags associated with the employee.
        notes: (str): Notes about the employee.
    """
    if risk_tag and type(risk_tag) != list:
        risk_tag = risk_tag.split()

    if cloud_alias and type(cloud_alias) != list:
        cloud_alias = cloud_alias.split()

    user_id = get_user_id(sdk, username)
    update_user(sdk, user_id, cloud_alias, risk_tag, notes)
    sdk.detectionlists.high_risk_employee.add(user_id)


def _load_add_description(argument_collection):
    load_user_descriptions(argument_collection)
    risk_tag = argument_collection.arg_configs[DetectionListUserKeys.RISK_TAG]
    risk_tag.as_multi_val_param()
    risk_tag.set_help(
        u"Risk tags associated with the employee. "
        u"Options include "
        u"[HIGH_IMPACT_EMPLOYEE, "
        u"ELEVATED_ACCESS_PRIVILEGES, "
        u"PERFORMANCE_CONCERNS, "
        u"FLIGHT_RISK, "
        u"SUSPICIOUS_SYSTEM_ACTIVITY, "
        u"POOR_SECURITY_PRACTICES, "
        u"CONTRACT_EMPLOYEE]"
    )
