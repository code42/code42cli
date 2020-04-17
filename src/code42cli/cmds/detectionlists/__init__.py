from code42cli.cmds.detectionlists.commands import DetectionListCommandFactory
from code42cli.bulk import generate_template, run_bulk_process
from code42cli.cmds.detectionlists.enums import BulkCommandType
from code42cli.util import print_error


class DetectionListHandlers(object):
    def __init__(self, add=None, remove=None, load_add=None):
        self.add_employee = add
        self.remove_employee = remove
        self.load_add_description = load_add


class UserDoesNotExistError(Exception):
    def __init__(self, username):
        super(UserDoesNotExistError, self).__init__(u"User '{}' does not exist.".format(username))


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
        run_bulk_process(csv_file, lambda **kwargs: self._add_employee(sdk, profile, **kwargs))

    def _add_employee(self, sdk, profile, **kwargs):
        if kwargs.has_key(u"cloud_aliases") and type(kwargs[u"cloud_aliases"]) != list:
            kwargs[u"cloud_aliases"] = kwargs[u"cloud_aliases"].split()

        self.handlers.add_employee(sdk, profile, **kwargs)


def load_user_descriptions(argument_collection):
    username = argument_collection.arg_configs[u"username"]
    cloud_aliases = argument_collection.arg_configs[u"cloud_aliases"]
    notes = argument_collection.arg_configs[u"notes"]

    username.set_help(u"The code42 username of the user you want to add.")
    cloud_aliases.set_help(u"Alternative emails addresses for other cloud services.")
    cloud_aliases.as_multi_val_param()
    notes.set_help(u"Notes about the employee.")


def get_user_id(sdk, username):
    users = sdk.users.get_by_username(username)[u"users"]
    if not users:
        print_error(str(UserDoesNotExistError(username)))
        exit(1)
    return users[0][u"userUid"]


def update_user(sdk, user_id, cloud_aliases=None, risk_factors=None, notes=None):
    if cloud_aliases:
        sdk.detectionlists.add_user_cloud_aliases(user_id, cloud_aliases)
    if risk_factors:
        sdk.detectionlists.add_user_risk_tags(user_id, risk_factors)
    if notes:
        sdk.detectionlists.update_user_notes(user_id, notes)
