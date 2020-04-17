from code42cli.cmds.detectionlists.enums import BulkCommandType
from code42cli.commands import Command


def create_usage_prefix(detection_list_name):
    return u"code42 {}".format(detection_list_name)


def create_bulk_usage_prefix(detection_list_name):
    return u"{} bulk".format(create_usage_prefix(detection_list_name))


class DetectionListCommandFactory:
    def __init__(self, detection_list_name):
        self._name = detection_list_name
        self._usage_prefix = create_usage_prefix(detection_list_name)
        self._bulk_usage_prefix = create_bulk_usage_prefix(detection_list_name)

    def create_bulk_command(self, subcommand_loader):
        return Command(
            u"bulk",
            u"Tools for executing bulk {} commands.".format(self._name),
            subcommand_loader=subcommand_loader,
        )

    def create_add_command(self, handler, arg_customizer):
        return Command(
            u"add",
            u"Add a user to the {} detection list.".format(self._name),
            u"{} add <username> <optional args>".format(self._usage_prefix),
            handler=handler,
            arg_customizer=arg_customizer,
        )

    def create_bulk_generate_template_command(self, handler):
        return Command(
            u"generate-template",
            u"Generate the necessary csv template needed for bulk adding users.",
            u"{} generate-template <cmd> <optional args>".format(self._bulk_usage_prefix),
            handler=handler,
            arg_customizer=DetectionListCommandFactory._load_bulk_generate_template_description,
        )

    def create_bulk_add_command(self, handler):
        return Command(
            u"add",
            u"Bulk add users to the {} detection list using a csv file.".format(self._name),
            u"{} add <csv-file>".format(self._bulk_usage_prefix),
            handler=handler,
            arg_customizer=self._load_bulk_add_description,
        )

    @staticmethod
    def _load_bulk_generate_template_description(argument_collection):
        cmd_type = argument_collection.arg_configs[u"cmd"]
        cmd_type.set_help(u"The type of command the template with be used for.")
        cmd_type.set_choices(BulkCommandType())

    def _load_bulk_add_description(self, argument_collection):
        csv_file = argument_collection.arg_configs[u"csv_file"]
        csv_file.set_help(
            u"The path to the csv file for bulk adding users to the {} detection list.".format(
                self._name
            )
        )
