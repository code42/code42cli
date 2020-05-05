from code42cli.cmds.alerts.rules.user_rule import (
    add_user, 
    remove_user, 
    remove_all_users, 
    get_by_rule_type,
    get_all,
    add_bulk_users,
    remove_bulk_users,
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


def _customize_remove_all_arguments(argument_collection):
    rule_id = argument_collection.arg_configs[u"rule_id"]
    rule_id.set_help(u"Update alert rule criteria to remove all users the from the alert rule.")


def _customize_list_arguments(argument_collection):
    rule_type = argument_collection.arg_configs[u"rule_type"]
    rule_type.set_help(u"Type of rule, either of 'exfiltration', 'cloudshare', 'filetypemismatch'")
    rule_type.set_choices([u"exfiltration", u"cloudshare", u"filetypemismatch"])
    rule_id = argument_collection.arg_configs[u"rule_id"]
    rule_id.set_help(u"Rule id of th rule")


def bulk_arguments(argument_collection):
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

    add_bulk = Command(
        u"add-bulk",
        u"Update multiple alert rules to monitor user aliases against the Uid for the given rule id."
        u"csv file format: rule_id, user_id",
        u"{} {}".format(usage_prefix, u"add-bulk <filenamce>"),
        handler=add_bulk_users,
        arg_customizer=bulk_arguments
    )

    remove_one = Command(
            u"remove-user",
            u"Update alert rule criteria to remove a user and all its aliases.",
            u"{} {}".format(usage_prefix, u"remove-user <rule_id>  <user_id>"),
            handler=remove_user,
            arg_customizer=_customize_remove_arguments
        )

    remove_all = Command(
        u"remove-all",
        u"Update alert rule criteria to remove all users and all its aliases from a rule.",
        u"{} {}".format(usage_prefix, u"remove-all <rule_id>"),
        handler=remove_all_users,
        arg_customizer=_customize_remove_all_arguments
    )
    
    remove_bulk = Command(
        u"remove-bulk",
        u"Update multiple alert rule criteria to remove all users and all its aliases from a rule."
        u"csv file format: rule_id",
        u"{} {}".format(usage_prefix, u"remove-bulk <filename>"),
        handler=remove_bulk_users,
        arg_customizer=bulk_arguments
    )

    list_rules = Command(
            u"list",
            u"Fetch existing alert rules by rule -id",
            u"{} {}".format(usage_prefix, u"list <rule_type>  <rule_id>"),
            handler=get_by_rule_type,
            arg_customizer=_customize_list_arguments
        )

    list_all_rules = Command(
        u"list-all",
        u"Fetch all existing alert rules.",
        u"{} {}".format(usage_prefix, u"list-all"),
        handler=get_all,
    )

    return [add, add_bulk, remove_one, remove_all, remove_bulk, list_rules, list_all_rules]
