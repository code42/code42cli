import os

from code42cli.args import ArgConfig
from code42cli.commands import Command, SubcommandLoader
from code42cli.bulk import generate_template, BulkCommandType
from code42cli.cmds.legal_hold import (
    add_user,
    remove_user,
    get_matters,
    add_bulk_users,
    remove_bulk_users,
    show_matter,
)


class LegalHoldSubcommandLoader(SubcommandLoader):
    ADD_USER = "add-user"
    REMOVE_USER = "remove-user"
    LIST = "list"
    SHOW = "show"
    BULK = "bulk"

    def __init__(self, root_command_name):
        super(LegalHoldSubcommandLoader, self).__init__(root_command_name)
        self._bulk_subcommand_loader = LegalHoldBulkSubcommandLoader(self.BULK)

    def load_commands(self):
        """Sets up the `legal-hold` subcommand with all of its subcommands."""
        usage_prefix = u"code42 legal-hold"

        add = Command(
            self.ADD_USER,
            u"Add a user to a legal hold matter.",
            u"{} add-user --matter-id <id> --username <username>".format(usage_prefix),
            handler=add_user,
            arg_customizer=_customize_add_arguments,
        )

        remove = Command(
            self.REMOVE_USER,
            u"Remove a user from a legal hold matter.",
            u"{} remove-user --matter-id <id> --username <username>".format(usage_prefix),
            handler=remove_user,
            arg_customizer=_customize_remove_arguments,
        )

        list_matters = Command(
            self.LIST,
            u"Fetch existing legal hold matters.",
            u"{} list".format(usage_prefix),
            handler=get_matters,
        )

        show = Command(
            self.SHOW,
            u"Fetch all legal hold custodians for a given matter.",
            u"{} show <matter-id>".format(usage_prefix),
            handler=show_matter,
            arg_customizer=_customize_show_arguments,
        )

        bulk = Command(
            self.BULK,
            u"Tools for executing bulk commands.",
            subcommand_loader=self._bulk_subcommand_loader,
        )

        return [add, remove, list_matters, show, bulk]


class LegalHoldBulkSubcommandLoader(SubcommandLoader):
    GENERATE_TEMPLATE = u"generate-template"
    ADD = u"add"
    REMOVE = u"remove"

    def load_commands(self):
        """Sets up the `legal-hold bulk` subcommands."""
        usage_prefix = u"code42 legal-hold bulk"

        bulk_add = Command(
            u"add-user",
            u"Bulk add users to legal hold matters from a csv file. CSV file format: matter_id,username",
            u"{} add-user <filename>".format(usage_prefix),
            handler=add_bulk_users,
            arg_customizer=_customize_bulk_arguments,
        )

        bulk_remove = Command(
            u"remove-user",
            u"Bulk remove users from legal hold matters from a csv file. CSV file format: matter_id,username",
            u"{} remove-user <filename>".format(usage_prefix),
            handler=remove_bulk_users,
            arg_customizer=_customize_bulk_arguments,
        )

        generate_template_cmd = Command(
            u"generate-template",
            u"Generate the necessary csv template needed for bulk adding users.",
            u"{} generate-template <cmd> <optional args>".format(usage_prefix),
            handler=_generate_template_file,
            arg_customizer=_load_bulk_generate_template_description,
        )

        return [bulk_add, bulk_remove, generate_template_cmd]


def _customize_add_arguments(argument_collection):
    matter = argument_collection.arg_configs["matter_id"]
    matter.add_short_option_name("-m")
    matter.set_help("ID of the legal hold matter user will be added to. Required.")
    username = argument_collection.arg_configs["username"]
    username.add_short_option_name("-u")
    username.set_help("The username of the user to add to the matter. Required.")


def _customize_remove_arguments(argument_collection):
    matter = argument_collection.arg_configs["matter_id"]
    matter.add_short_option_name("-m")
    matter.set_help("ID of the legal hold matter user will be removed from. Required.")
    username = argument_collection.arg_configs["username"]
    username.add_short_option_name("-u")
    username.set_help("The username of the user to remove from the matter. Required.")


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
    handler = None
    filename = u"legal_hold.csv"
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
