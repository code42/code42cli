from code42cli.cmds.detectionlists.enums import DetectionLists
from code42cli.cmds.detectionlists import (
    DetectionList,
    DetectionListHandlers,
    load_username_description,
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
    pass


def _load_add_description(argument_collection):
    load_username_description(argument_collection)
    risk_factors = argument_collection.arg_configs[u"risk_factors"]
    risk_factors.set_help(u"Risk factors associated with the employee.")
