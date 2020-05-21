from code42cli import MAIN_COMMAND
from code42cli.commands import Command, CommandController
from code42cli.bulk import generate_template, BulkCommandType
from code42cli.cmds.alerts.rules.user_rule import (
    add_user,
    remove_user,
    get_rules,
    add_bulk_users,
    remove_bulk_users,
    show_rule,
)


def _customize_add_arguments(argument_collection):
    rule_id = argument_collection.arg_configs[u"rule_id"]
    rule_id.set_help(u"Observer ID of the rule to be updated. Required.")
    username = argument_collection.arg_configs[u"username"]
    username.set_help(u"The username of the user to add to the alert rule. Required.")


def _customize_remove_arguments(argument_collection):
    rule_id = argument_collection.arg_configs[u"rule_id"]
    rule_id.set_help(u"Observer ID of the rule to be updated.")
    username = argument_collection.arg_configs[u"username"]
    username.set_help(u"The username of the user to remove from the alert rule.")


def _customize_list_arguments(argument_collection):
    rule_id = argument_collection.arg_configs[u"rule_id"]
    rule_id.set_help(u"Observer ID of the rule.")


def _customize_bulk_arguments(argument_collection):
    file_name = argument_collection.arg_configs[u"file_name"]
    file_name.set_help(
        u"The path to the csv file with columns 'rule_id,username' "
        u"for bulk adding users to the alert rule."
    )


def _generate_template_file(cmd, path=None):
    """Generates a template file a user would need to fill-in for bulk operating.

    Args:
        cmd (str or unicode): An option from the `BulkCommandType` enum specifying which type of file to
            generate.
        path (str or unicode, optional): A path to put the file after it's generated. If None, will use
            the current working directory. Defaults to None.
    """
    handler = None
    if cmd == BulkCommandType.ADD:
        handler = add_user
    elif cmd == BulkCommandType.REMOVE:
        handler = remove_user

    generate_template(handler, path)


def _load_bulk_generate_template_description(argument_collection):
    cmd_type = argument_collection.arg_configs[u"cmd"]
    cmd_type.set_help(u"The type of command the template with be used for.")
    cmd_type.set_choices(BulkCommandType())


class AlertRulesBulkCommandController(CommandController):
    GENERATE_TEMPLATE = u"generate-template"
    ADD = u"add"
    REMOVE = u"remove"

    @property
    def names(self):
        return [self.ADD, self.REMOVE, self.GENERATE_TEMPLATE]

    def create_commands(self):
        usage_prefix = u"{} alert-rules bulk".format(MAIN_COMMAND)

        generate_template_cmd = Command(
            self.GENERATE_TEMPLATE,
            u"Generate the necessary csv template needed for bulk adding users.",
            u"{} generate-template <cmd> <optional args>".format(usage_prefix),
            handler=_generate_template_file,
            arg_customizer=_load_bulk_generate_template_description,
        )

        bulk_add = Command(
            self.ADD,
            u"Update alert rule criteria to add users and all their aliases. "
            u"CSV file format: rule_id,username",
            u"{} add <filename>".format(usage_prefix),
            handler=add_bulk_users,
            arg_customizer=_customize_bulk_arguments,
        )

        bulk_remove = Command(
            self.REMOVE,
            u"Update alert rule criteria to remove users and all their aliases. "
            u"CSV file format: rule_id,username",
            u"{} remove <filename>".format(usage_prefix),
            handler=remove_bulk_users,
            arg_customizer=_customize_bulk_arguments,
        )

        return [generate_template_cmd, bulk_add, bulk_remove]


class AlertRulesCommandController(CommandController):
    ADD_USER = u"add-user"
    REMOVE_USER = u"remove-user"
    LIST = u"list"
    SHOW = u"show"
    BULK = u"bulk"

    def __init__(self, root_command_name):
        super(AlertRulesCommandController, self).__init__(root_command_name)
        self._bulk_controller = AlertRulesBulkCommandController(self.BULK)

    @property
    def names(self):
        return [self.ADD_USER, self.REMOVE_USER, self.LIST, self.SHOW, self.BULK]

    @property
    def table(self):
        return {self.BULK: self._bulk_controller}

    def create_commands(self):
        usage_prefix = u"code42 alert-rules"

        add = Command(
            self.ADD_USER,
            u"Update alert rule criteria to monitor user aliases against the given username.",
            u"{} add-user --rule-id <id>  --username <username>".format(usage_prefix),
            handler=add_user,
            arg_customizer=_customize_add_arguments,
        )

        remove = Command(
            self.REMOVE_USER,
            u"Update alert rule criteria to remove a user and all their aliases.",
            u"{} remove-user --rule-id <rule-id> --username <username>".format(usage_prefix),
            handler=remove_user,
            arg_customizer=_customize_remove_arguments,
        )

        list_rules = Command(
            self.LIST,
            u"Fetch existing alert rules.",
            u"{} list".format(usage_prefix),
            handler=get_rules,
        )

        show = Command(
            self.SHOW,
            u"Fetch configured alert-rules against the rule ID.",
            u"{} show <rule-id>".format(usage_prefix),
            handler=show_rule,
            arg_customizer=_customize_list_arguments,
        )

        bulk = Command(
            self.BULK,
            u"Tools for executing bulk commands.",
            subcommand_loader=self._bulk_controller.create_commands,
        )

        return [add, remove, list_rules, show, bulk]
