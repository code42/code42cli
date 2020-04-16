from code42cli.cmds.detectionlists.commands import DetectionListCommandFactory
from code42cli.bulk import generate_template, run_bulk_process
from code42cli.cmds.detectionlists.enums import BulkCommandType


class DetectionListHandlers(object):
    def __init__(self, add=None, remove=None, load_add=None):
        self.add_employee = add
        self.remove_employee = remove
        self.load_add_description = load_add


class DetectionList(object):
    def __init__(self, list_name, handlers, cmd_factory=None):
        self.name = list_name
        self.handlers = handlers
        self.factory = cmd_factory or DetectionListCommandFactory(list_name)

    def load_subcommands(self):
        bulk = self.factory.create_bulk_command(lambda: self._load_bulk_subcommands())
        add = self.factory.create_add_command(
            self.handlers.add_employee, self.handlers.load_add_description
        )
        return [bulk, add]

    def _load_bulk_subcommands(self):
        generate_template_cmd = self.factory.create_bulk_generate_template_command(
            self.generate_csv_file
        )
        add = self.factory.create_bulk_add_command(self.bulk_add_employees)
        return [generate_template_cmd, add]

    def generate_csv_file(self, cmd, path=None):
        """Generates a csv template a user would need to fill-in for bulk adding users to the 
        detection list."""
        handler = None
        if cmd == BulkCommandType.ADD:
            handler = self.handlers.add_employee
        generate_template(handler, path)

    def bulk_add_employees(self, sdk, profile, csv_file):
        """Takes a csv file with each row representing an employee and adds each them all to a 
        detection list in a bulk fashion.

        Args:
            sdk (py42.sdk.SDKClient): The py42 sdk.
            profile (Code42Profile): The profile under which to execute this command.
            csv_file (str): The path to the csv file containing rows of users.
        """
        run_bulk_process(
            csv_file, lambda **kwargs: self.handlers.add_employee(sdk, profile, **kwargs)
        )


def load_username_description(argument_collection):
    username = argument_collection.arg_configs[u"username"]
    username.set_help(u"The code42 username of the user you want to add.")


def get_user_id(sdk, username):
    return sdk.users.get_by_username(username)[u"users"][0][u"userUid"]


def update_user(sdk, user_id, cloud_aliases=None, risk_factors=None, notes=None):
    if cloud_aliases:
        sdk.detectionlists.add_cloud_aliases(user_id, cloud_aliases)
    if risk_factors:
        sdk.detectionlists.add_risk_tags(user_id, risk_factors)
    if notes:
        sdk.detectionlists.update_notes(user_id, notes)
