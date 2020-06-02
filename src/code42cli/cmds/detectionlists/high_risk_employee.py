from py42.exceptions import Py42BadRequestError

from code42cli.cmds.detectionlists import DetectionListSubcommandLoader
from code42cli.commands import Command
from code42cli.cmds.detectionlists import (
    DetectionList,
    DetectionListHandlers,
    load_user_descriptions,
    update_user,
    try_handle_user_already_added_error,
    add_risk_tags,
    remove_risk_tags,
    load_username_description,
    handle_list_args,
)
from code42cli.util import get_user_id
from code42cli.cmds.detectionlists.enums import DetectionLists, DetectionListUserKeys, RiskTags


class HighRiskEmployeeSubcommandLoader(DetectionListSubcommandLoader):
    def __init__(self, root_command_name):
        super(HighRiskEmployeeSubcommandLoader, self).__init__(root_command_name)
        handlers = _create_handlers()
        self.detection_list = DetectionList.create_high_risk_employee_list(handlers)
        self._cmd_loader = self.detection_list.subcommand_loader

    def load_commands(self):
        cmds = self.detection_list.load_subcommands()
        cmds.extend(
            [
                Command(
                    u"add-risk-tags",
                    u"Associates risk tags with a user.",
                    u"code42 high-risk-employee add-risk-tags --username <username> --tag <risk-tags>",
                    handler=add_risk_tags,
                    arg_customizer=load_risk_tag_mgmt_descriptions,
                ),
                Command(
                    u"remove-risk-tags",
                    u"Disassociates risk tags from a user.",
                    u"code42 high-risk-employee remove-risk-tags --username <username> --tag <risk-tags>",
                    handler=remove_risk_tags,
                    arg_customizer=load_risk_tag_mgmt_descriptions,
                ),
            ]
        )
        return cmds


def _create_handlers():
    return DetectionListHandlers(
        add=add_high_risk_employee, remove=remove_high_risk_employee, load_add=_load_add_description
    )


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
    risk_tag = handle_list_args(risk_tag)
    user_id = get_user_id(sdk, username)

    try:
        sdk.detectionlists.high_risk_employee.add(user_id)
        update_user(sdk, user_id, cloud_alias, risk_tag, notes)
    except Py42BadRequestError as err:
        list_name = u"{} list".format(DetectionLists.HIGH_RISK_EMPLOYEE)
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


def _load_add_description(argument_collection):
    load_user_descriptions(argument_collection)
    load_risk_tag_description(argument_collection)


def load_risk_tag_description(argument_collection):
    risk_tag = (
        argument_collection.arg_configs.get(DetectionListUserKeys.RISK_TAG)
        or argument_collection.arg_configs[u"tag"]
    )
    risk_tag.as_multi_val_param()
    tags = u", ".join(list(RiskTags()))
    risk_tag.set_help(
        u"Risk tags associated with the employee. Options include: [{}].".format(tags)
    )


def load_risk_tag_mgmt_descriptions(argument_collection):
    load_username_description(argument_collection)
    load_risk_tag_description(argument_collection)
