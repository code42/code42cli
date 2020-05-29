import inspect

from code42cli.bulk import BulkCommandType
from code42cli.commands import Command, SubcommandLoader
from code42cli.cmds.detectionlists.bulk import HighRiskBulkCommandType


def create_usage_prefix(detection_list_name):
    return u"code42 {}".format(detection_list_name)


def create_bulk_usage_prefix(detection_list_name):
    return u"{} bulk".format(create_usage_prefix(detection_list_name))


def _load_bulk_generate_template_description(argument_collection):
    cmd_type = argument_collection.arg_configs[u"cmd"]
    cmd_type.set_help(u"The type of command the template with be used for.")
    cmd_type.set_choices(BulkCommandType())


class DetectionListSubcommandLoader(SubcommandLoader):
    BULK = u"bulk"
    ADD = BulkCommandType.ADD
    REMOVE = BulkCommandType.REMOVE
    _USAGE_SUFFIX = u"<username> <optional args>"

    def __init__(self, detection_list_name, bulk_subcommand_loader=None):
        super(DetectionListSubcommandLoader, self).__init__(detection_list_name)
        self._name = detection_list_name
        self._usage_prefix = create_usage_prefix(detection_list_name)
        self.bulk_subcommand_loader = bulk_subcommand_loader or DetectionListBulkSubcommandLoader(
            self.BULK, detection_list_name
        )

    def create_bulk_command(self):
        return Command(
            self.BULK,
            u"Tools for executing bulk {} commands.".format(self._name),
            subcommand_loader=self.bulk_subcommand_loader,
        )

    def create_add_command(self, handler, arg_customizer):
        return Command(
            self.ADD,
            u"Add a user to the {} detection list.".format(self._name),
            u"{} {} {}".format(self._usage_prefix, BulkCommandType.ADD, self._USAGE_SUFFIX),
            handler=handler,
            arg_customizer=arg_customizer,
        )

    def create_remove_command(self, handler, arg_customizer):
        return Command(
            self.REMOVE,
            u"Remove a user from the {} detection list.".format(self._name),
            u"{} {} {}".format(self._usage_prefix, BulkCommandType.REMOVE, self._USAGE_SUFFIX),
            handler=handler,
            arg_customizer=arg_customizer,
        )


class DetectionListBulkSubcommandLoader(SubcommandLoader):
    ADD = BulkCommandType.ADD
    REMOVE = BulkCommandType.REMOVE
    GENERATE_TEMPLATE = u"generate-template"

    def __init__(self, root_command_name, detection_list_name):
        super(DetectionListBulkSubcommandLoader, self).__init__(root_command_name)
        self._bulk_usage_prefix = create_bulk_usage_prefix(detection_list_name)
        self._name = detection_list_name

    def create_bulk_generate_template_command(self, handler):
        return Command(
            self.GENERATE_TEMPLATE,
            u"Generate the necessary csv template needed for bulk adding users.",
            u"{} generate-template <cmd> <optional args>".format(self._bulk_usage_prefix),
            handler=handler,
            arg_customizer=_load_bulk_generate_template_description,
        )

    def create_hre_bulk_generate_template_command(self, handler):
        return Command(
            u"generate-template",
            u"Generate the necessary csv template for bulk actions.",
            u"{} generate-template <cmd> <optional args>".format(self._bulk_usage_prefix),
            handler=handler,
            arg_customizer=self._load_hre_bulk_generate_template_description,
        )

    def create_bulk_add_command(self, cmd_handler, row_handler):
        file_format = _get_file_format(row_handler)
        return Command(
            self.ADD,
            u"Add users to the {} detection list. CSV file format: `{}`.".format(
                self._name, file_format
            ),
            u"{} {} <filename>".format(self._bulk_usage_prefix, BulkCommandType.ADD),
            handler=cmd_handler,
            arg_customizer=self._load_bulk_add_description,
        )

    def create_bulk_remove_command(self, cmd_handler):
        return Command(
            self.REMOVE,
            u"Remove users from the {} detection list. "
            u"The file format is an end-line-delimited list of users.".format(self._name),
            u"{} {} <file>".format(self._bulk_usage_prefix, BulkCommandType.REMOVE),
            handler=cmd_handler,
            arg_customizer=self._load_bulk_remove_description,
        )

    def create_bulk_add_risk_tags_command(self, cmd_handler, row_handler):
        file_format = _get_file_format(row_handler)
        return Command(
            u"add-risk-tags",
            u"Associates risk tags with a user in bulk. CSV file format: `{}`.".format(file_format),
            u"{} {} <file>".format(self._bulk_usage_prefix, HighRiskBulkCommandType.ADD_RISK_TAG),
            handler=cmd_handler,
            arg_customizer=self._load_bulk_add_risk_tags_description,
        )

    def create_bulk_remove_risk_tags_command(self, cmd_handler, row_handler):
        file_format = _get_file_format(row_handler)
        return Command(
            u"remove-risk-tags",
            u"Disassociates risk tags from a user in bulk. CSV file format: `{}`.".format(
                file_format
            ),
            u"{} {} <file>".format(
                self._bulk_usage_prefix, HighRiskBulkCommandType.REMOVE_RISK_TAG
            ),
            handler=cmd_handler,
            arg_customizer=self._load_bulk_remove_risk_tags_description,
        )

    @staticmethod
    def _load_bulk_generate_template_description(argument_collection):
        cmd_type = argument_collection.arg_configs[u"cmd"]
        cmd_type.set_help(u"The type of command the template will be used for.")
        cmd_type.set_choices(BulkCommandType())

    @staticmethod
    def _load_hre_bulk_generate_template_description(argument_collection):
        cmd_type = argument_collection.arg_configs[u"cmd"]
        cmd_type.set_help(u"The type of command the template will be used for.")
        cmd_type.set_choices(HighRiskBulkCommandType())

    def _load_bulk_add_description(self, argument_collection):
        csv_file = argument_collection.arg_configs[u"csv_file"]
        csv_file.set_help(
            u"The path to the csv file for bulk adding users to the {} detection list.".format(
                self._name
            )
        )

    def _load_bulk_remove_description(self, argument_collection):
        users_file = argument_collection.arg_configs[u"users_file"]
        users_file.set_help(
            u"A file containing a line-separated list of users to remove form the {} detection list.".format(
                self._name
            )
        )

    def _load_bulk_add_risk_tags_description(self, argument_collection):
        csv_file = argument_collection.arg_configs[u"csv_file"]
        csv_file.set_help(
            u"A file containing a ',' separated username with space-separated tags to add "
            u"to the {} detection list. "
            u"e.g. test@email.com,tag1 tag2 tag3".format(self._name)
        )

    def _load_bulk_remove_risk_tags_description(self, argument_collection):
        csv_file = argument_collection.arg_configs[u"csv_file"]
        csv_file.set_help(
            u"A file containing a ',' separated username with space-separated tags to remove "
            u"from the {} detection list. "
            u"e.g. test@email.com,tag1 tag2 tag3".format(self._name)
        )


def _get_file_format(row_handler):
    args = inspect.getargspec(row_handler).args
    args.remove(u"profile")
    args.remove(u"sdk")
    return u", ".join(args)
