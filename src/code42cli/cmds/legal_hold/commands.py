from code42cli.args import ArgConfig
from code42cli.commands import Command
from code42cli.bulk import generate_template, BulkCommandType
from code42cli.cmds.legal_hold import (
    add_user,
    remove_user,
    get_matters,
    add_bulk_users,
    remove_bulk_users,
    show_matter,
)


def _customize_add_arguments(argument_collection):
    args = {
        u"matter_id": ArgConfig(
            u"-m",
            u"--matter-id",
            help=u"ID of the legal hold matter user will be added to. Required.",
            required=True,
        ),
        u"username": ArgConfig(
            u"-u",
            u"--username",
            help=u"The username of the user to add to the matter. Required.",
            required=True,
        ),
    }
    argument_collection.extend(args)


def _customize_remove_arguments(argument_collection):
    args = {
        u"matter_id": ArgConfig(
            u"-m",
            u"--matter-id",
            help=u"ID of the legal hold matter user will be removed from. Required.",
            required=True,
        ),
        u"username": ArgConfig(
            u"-u",
            u"--username",
            help=u"The username of the user to remove from the matter. Required.",
            required=True,
        ),
    }
    argument_collection.extend(args)


def _customize_show_arguments(argument_collection):
    matter_id = argument_collection.arg_configs[u"matter_id"]
    matter_id.set_help(u"ID of the legal hold matter.")
    args = {
        u"include_inactive": ArgConfig(
            u"--include-inactive",
            action=u"store_true",
            help=u"Include list of users who are no longer actively on this matter.",
        ),
        u"include_policy": ArgConfig(
            u"--include-policy",
            action=u"store_true",
            help=u"Include the preservation policy (in json format) for this matter.",
        ),
    }
    argument_collection.extend(args)


def _customize_bulk_arguments(argument_collection):
    file_name = argument_collection.arg_configs[u"file_name"]
    file_name.set_help(
        u"The path to the csv file with columns 'matter_id,username' "
        u"for bulk adding users to legal hold."
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


class LegalHoldBulkCommands(object):
    @staticmethod
    def load_commands():
        usage_prefix = u"code42 legal-hold bulk"

        generate_template_cmd = Command(
            u"generate-template",
            u"Generate the necessary csv template needed for bulk adding users.",
            u"{} generate-template <cmd> <optional args>".format(usage_prefix),
            handler=_generate_template_file,
            arg_customizer=_load_bulk_generate_template_description,
        )

        bulk_add = Command(
            u"add",
            u"Bulk add users to legal hold matters from a csv file. CSV file format: matter_id,username",
            u"{} add <filename>".format(usage_prefix),
            handler=add_bulk_users,
            arg_customizer=_customize_bulk_arguments,
        )

        bulk_remove = Command(
            u"remove",
            u"Bulk remove users from legal hold matters from a csv file. CSV file format: matter_id,username",
            u"{} remove <filename>".format(usage_prefix),
            handler=remove_bulk_users,
            arg_customizer=_customize_bulk_arguments,
        )

        return [generate_template_cmd, bulk_add, bulk_remove]


class LegalHoldCommands(object):
    @staticmethod
    def load_subcommands():
        usage_prefix = u"code42 legal-hold"

        add = Command(
            u"add-user",
            u"Add a user to a legal hold matter.",
            u"{} add-user --matter-id <id>  --username <username>".format(usage_prefix),
            handler=add_user,
            arg_customizer=_customize_add_arguments,
        )

        remove = Command(
            u"remove-user",
            u"Remove a user from a legal hold matter.",
            u"{} remove-user --matter-id <id> --username <username>".format(usage_prefix),
            handler=remove_user,
            arg_customizer=_customize_remove_arguments,
        )

        list_matters = Command(
            u"list",
            u"Fetch existing legal hold matters.",
            u"{} list".format(usage_prefix),
            handler=get_matters,
        )

        show = Command(
            u"show",
            u"Fetch all legal hold custodians for a given matter.",
            u"{} show <matter-id>".format(usage_prefix),
            handler=show_matter,
            arg_customizer=_customize_show_arguments,
        )

        bulk = Command(
            u"bulk",
            u"Tools for executing bulk commands.",
            subcommand_loader=LegalHoldBulkCommands.load_commands,
        )

        return [add, remove, list_matters, show, bulk]
