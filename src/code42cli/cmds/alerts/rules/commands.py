from code42cli.commands import Command
from code42cli.bulk import generate_template, BulkCommandType
from code42cli.cmds.alerts.rules.user_rule import (
    add_user, 
    remove_user,
    get_rules,
    add_bulk_users,
    remove_bulk_users,
    show_rules,
)


def _customize_add_arguments(argument_collection):
    rule_id = argument_collection.arg_configs[u"rule_id"]
    rule_id.set_help(u"Observer Id of the rule to be updated.")
    user_name = argument_collection.arg_configs[u"user_name"]
    user_name.set_help(u"The username of the user to add to the alert, email id.")


def _customize_remove_arguments(argument_collection):

    rule_id = argument_collection.arg_configs[u"rule_id"]
    rule_id.set_help(u"Observer rule id of the rule to be updated.")
    user_name = argument_collection.arg_configs[u"user_name"]
    user_name.set_help(u"The username of the user to remove from the alert, email id.")


def _customize_list_arguments(argument_collection):
    rule_id = argument_collection.arg_configs[u"rule_id"]
    rule_id.set_help(u"Observer rule id of the rule")


def _customize_bulk_arguments(argument_collection):
    file_name = argument_collection.arg_configs[u"file_name"]
    file_name.set_help(u"CSV file name with relative path."
                       u"Format rule_id,user_id to update rule for specific user, "
                       u"or rule_id, when all users need to be removed from a rule.")


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
        handler = add_bulk_users
    elif cmd == BulkCommandType.REMOVE:
        handler = remove_bulk_users

    generate_template(handler, path)


def _load_bulk_generate_template_description(argument_collection):
    cmd_type = argument_collection.arg_configs[u"cmd"]
    cmd_type.set_help(u"The type of command the template with be used for.")
    cmd_type.set_choices(BulkCommandType())


class BulkCommand(object):

    @staticmethod
    def bulk_command():
        usage_prefix = u"code42 alert-rules bulk"

        generate_template_cmd = Command(
            u"generate-template",
            u"Generate the necessary csv template needed for bulk adding users.",
            u"{} {}".format(usage_prefix, u"generate-template <cmd> <optional args>"),
            handler=_generate_template_file,
            arg_customizer=_load_bulk_generate_template_description,
        )

        bulk_add = Command(
            u"add",
            u"Update multiple alert rules to monitor user aliases against the Code42 userUid "
            u"and given rule id. CSV file format: rule_id, user_name",
            u"{} {}".format(usage_prefix, u"add <filename>"),
            handler=add_bulk_users,
            arg_customizer=_customize_bulk_arguments
        )

        bulk_remove = Command(
            u"remove",
            u"Update multiple alert rules to monitor user aliases against the Code42 userUid "
            u"and given rule id. CSV file format: rule_id, user_name",
            u"{} {}".format(usage_prefix, u"remove <filename>"),
            handler=remove_bulk_users,
            arg_customizer=_customize_bulk_arguments
        )

        return [generate_template_cmd, bulk_add, bulk_remove]


class AlertRulesCommands(object):

    @staticmethod
    def load_subcommands():
        usage_prefix = u"code42 alert-rules"

        add = Command(
                u"add-user",
                u"Update alert rule to monitor user aliases against the Uid for the given rule id.",
                u"{} {}".format(usage_prefix, u"add-user <rule_id>  <user-name>"),
                handler=add_user,
                arg_customizer=_customize_add_arguments
            )

        remove = Command(
                u"remove-user",
                u"Update alert rule criteria to remove a user and all its aliases.",
                u"{} {}".format(usage_prefix, u"remove-user <rule_id> --user-name [email-id]"),
                handler=remove_user,
                arg_customizer=_customize_remove_arguments
            )

        list_rules = Command(
                u"list",
                u"Fetch existing alert rules, optionally fetch by by rule-id",
                u"{} {}".format(usage_prefix, u"list --rule-id [UX]"),
                handler=get_rules,
                arg_customizer=_customize_list_arguments
            )

        show = Command(
            u"show",
            u"Fetch configured alert-rules against the rule-id",
            u"{} {}".format(usage_prefix, u"show --rule-id"),
            handler=show_rules,
            arg_customizer=_customize_list_arguments
        )

        bulk = Command(
            u"bulk",
            u"Tools for executing bulk commands.",
            subcommand_loader=BulkCommand.bulk_command,
        )

        return [add, remove, list_rules, show, bulk]
