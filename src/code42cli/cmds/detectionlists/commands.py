from code42cli.commands import Command


def create_usage_prefix(detection_list_name):
    return u"code42 detection-list {}".format(detection_list_name)


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

    def create_bulk_generate_template_command(self, handler, arg_customizer):
        return Command(
            u"generate-template",
            u"Generates the necessary csv template needed for bulk adding users.",
            u"{} gen-template <cmd> <optional args>".format(self._bulk_usage_prefix),
            handler=handler,
            arg_customizer=arg_customizer,
        )

    def create_bulk_add_command(self, handler, arg_customizer):
        return Command(
            u"add",
            u"Bulk add users to the high risk detection list using a csv file.",
            u"{} add <csv-file>".format(self._bulk_usage_prefix),
            handler=handler,
            arg_customizer=arg_customizer,
        )
