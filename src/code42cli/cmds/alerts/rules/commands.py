import os

from code42cli.commands import Command
from code42cli import MAIN_COMMAND
from code42cli.commands import Command, SubcommandLoader
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
    rule_id.set_help(u"Observer ID of the rule to be updated.")
    username = argument_collection.arg_configs[u"username"]
    username.add_short_option_name("-u")
    username.set_help(u"The username of the user to add to the alert rule.")


def _customize_remove_arguments(argument_collection):
    rule_id = argument_collection.arg_configs[u"rule_id"]
    rule_id.set_help(u"Observer ID of the rule to be updated.")
    username = argument_collection.arg_configs[u"username"]
    username.add_short_option_name("-u")
    username.set_help(u"The username of the user to remove from the alert rule.")


def _customize_list_arguments(argument_collection):
    rule_id = argument_collection.arg_configs[u"rule_id"]
    rule_id.set_help(u"Observer ID of the rule.")


def _customize_bulk_add_arguments(argument_collection):
    _customize_bulk_arguments(argument_collection, u"adding")


def _customize_bulk_remove_arguments(argument_collection):
    _customize_bulk_arguments(argument_collection, u"removing")


def _customize_bulk_arguments(argument_collection, action):
    file_name = argument_collection.arg_configs[u"file_name"]
    file_name.set_help(
        u"The path to the csv file with columns 'rule_id,username' "
        u"for bulk {} users to the alert rule.".format(action)
    )


def _generate_template_file(cmd, path=None):
    """Generates a template file a user would need to fill-in for bulk operating.

    Args:
        cmd (str or unicode): An option from the `BulkCommandType` enum specifying which type of 
            file to generate.
        path (str or unicode, optional): A path to put the file after it's generated. If None, will 
            use the current working directory. Defaults to None.
    """
    handler = None
    filename = u"alert_rule.csv"
    if cmd == BulkCommandType.ADD:
        handler = add_user
        filename = u"add_users_to_{}".format(filename)
    elif cmd == BulkCommandType.REMOVE:
        handler = remove_user
        filename = u"remove_users_from_{}".format(filename)
    if not path:
        path = os.path.join(os.getcwd(), filename)
    generate_template(handler, path)


def _load_bulk_generate_template_description(argument_collection):
    cmd_type = argument_collection.arg_configs[u"cmd"]
    cmd_type.set_help(u"The type of command the template will be used for.")
    cmd_type.set_choices(BulkCommandType())


class AlertRulesBulkSubcommandLoader(SubcommandLoader):
    GENERATE_TEMPLATE = u"generate-template"
    ADD = u"add"
    REMOVE = u"remove"

    def load_commands(self):
        usage_prefix = u"{} alert-rules bulk".format(MAIN_COMMAND)

        generate_template_cmd = Command(
            self.GENERATE_TEMPLATE,
            u"Generate the necessary csv template for bulk actions.",
            u"{} generate-template <cmd> <optional args>".format(usage_prefix),
            handler=_generate_template_file,
            arg_customizer=_load_bulk_generate_template_description,
        )

        bulk_add = Command(
            self.ADD,
            u"Add users to alert rules. " u"CSV file format: `rule_id,username`.",
            u"{} add <filename>".format(usage_prefix),
            handler=add_bulk_users,
            arg_customizer=_customize_bulk_add_arguments,
        )

        bulk_remove = Command(
            self.REMOVE,
            u"Remove users from alert rules. " u"CSV file format: `rule_id,username`.",
            u"{} remove <filename>".format(usage_prefix),
            handler=remove_bulk_users,
            arg_customizer=_customize_bulk_remove_arguments,
        )

        return [generate_template_cmd, bulk_add, bulk_remove]


class AlertRulesSubcommandLoader(SubcommandLoader):
    ADD_USER = u"add-user"
    REMOVE_USER = u"remove-user"
    LIST = u"list"
    SHOW = u"show"
    BULK = u"bulk"

    def __init__(self, root_command_name):
        super(AlertRulesSubcommandLoader, self).__init__(root_command_name)
        self._bulk_subcommand_loader = AlertRulesBulkSubcommandLoader(self.BULK)

    def load_commands(self):
        usage_prefix = u"code42 alert-rules"

        add = Command(
            self.ADD_USER,
            u"Add a user to an alert rule.",
            u"{} add-user --rule-id <id>  --username <username>".format(usage_prefix),
            handler=add_user,
            arg_customizer=_customize_add_arguments,
        )

        remove = Command(
            self.REMOVE_USER,
            u"Remove a user from an alert rule.",
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
            u"Print out detailed alert rule criteria.",
            u"{} show <rule-id>".format(usage_prefix),
            handler=show_rule,
            arg_customizer=_customize_list_arguments,
        )

        bulk = Command(
            self.BULK,
            u"Tools for executing bulk commands.",
            subcommand_loader=self._bulk_subcommand_loader,
        )

        return [add, remove, list_rules, show, bulk]
