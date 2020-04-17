from code42cli.cmds.detectionlists import (
    DetectionList,
    DetectionListHandlers,
    load_user_descriptions,
    get_user_id,
    update_user,
)


def load_subcommands():
    handlers = _get_handlers()
    detection_list = DetectionList.create_high_risk_list(handlers)
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
    if risk_factors and type(risk_factors) != list:
        risk_factors = risk_factors.split()

    if cloud_aliases and type(cloud_aliases) != list:
        cloud_aliases = cloud_aliases.split()

    user_id = get_user_id(sdk, username)
    update_user(sdk, user_id, cloud_aliases, risk_factors, notes)
    sdk.detectionlists.high_risk_employee.add(user_id)


def _load_add_description(argument_collection):
    load_user_descriptions(argument_collection)
    risk_factors = argument_collection.arg_configs[u"risk_factors"]
    risk_factors.as_multi_val_param()
    risk_factors.set_help(u"Risk factors associated with the employee.")
