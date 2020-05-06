from code42cli.cmds.alerts.rules.user_rule import (
    add_user, 
    remove_user,
    get_rules,
    bulk_update,
)
from code42cli.commands import Command


def _customize_add_arguments(argument_collection):
    rule_id = argument_collection.arg_configs[u"rule_id"]
    rule_id.set_help(u"Observer Id of a rule to be updated.")
    user_id = argument_collection.arg_configs[u"user_id"]
    user_id.set_help(u"The Code42 userUid  of the user to add to the alert")


def _customize_remove_arguments(argument_collection):

    rule_id = argument_collection.arg_configs[u"rule_id"]
    rule_id.set_help(u"Update alert rule criteria to remove users the from the alert rule.")
    user_id = argument_collection.arg_configs[u"user_id"]
    user_id.set_help(u"Update alert rule criteria to remove a user and all its aliases "
                     u"from a rule of the specified userUid")


def _customize_list_arguments(argument_collection):
    rule_type = argument_collection.arg_configs[u"rule_type"]
    rule_type.set_help(u"Type of rule, either of 'exfiltration', 'cloudshare', 'filetypemismatch'")
    rule_type.set_choices([u"exfiltration", u"cloudshare", u"filetypemismatch"])
    rule_id = argument_collection.arg_configs[u"rule_id"]
    rule_id.set_help(u"Observer rule id of the rule")


def _customize_bulk_arguments(argument_collection):
    action = argument_collection.arg_configs[u"action"]
    action.set_help("Type of update operation, either of 'add' or 'remove'")
    action.set_choices([u"add", u"remove"])
    file_name = argument_collection.arg_configs[u"file_name"]
    file_name.set_help(u"CSV file name with relative path."
                       u"Format rule_id,user_id to update rule for specific user, "
                       u"or rule_id, when all users need to be removed from a rule.")


def load_subcommands():
    usage_prefix = u"code42 alert-rules"
    
    add = Command(
            u"add-user",
            u"Update alert rule to monitor user aliases against the Uid for the given rule id.",
            u"{} {}".format(usage_prefix, u"add-user <rule_id> <user_id>"),
            handler=add_user,
            arg_customizer=_customize_add_arguments
        )

    bulk = Command(
        u"bulk",
        u"Update multiple alert rules to monitor user aliases against the Code42 userUid "
        u"and given rule id. CSV file format: rule_id, user_id",
        u"{} {}".format(usage_prefix, u"bulk <action> <filename>"),
        handler=bulk_update,
        arg_customizer=_customize_bulk_arguments
    )

    remove = Command(
            u"remove-user",
            u"Update alert rule criteria to remove a user and all its aliases.",
            u"{} {}".format(usage_prefix, u"remove-user <rule_id>  --user-id [UX]"),
            handler=remove_user,
            arg_customizer=_customize_remove_arguments
        )
    
    list_rules = Command(
            u"list",
            u"Fetch existing alert rules, optionally fetch by by rule-id",
            u"{} {}".format(usage_prefix, u"list --rule-type [type] --rule-id [UX]"),
            handler=get_rules,
            arg_customizer=_customize_list_arguments
        )

    return [add, remove, list_rules, bulk]
