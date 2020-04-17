from code42cli.cmds.detectionlists.commands import DetectionListCommandFactory
from code42cli.bulk import generate_template, run_bulk_process
from code42cli.cmds.detectionlists.enums import (
    BulkCommandType,
    DetectionLists,
    DetectionListUserKeys,
)
from code42cli.util import print_error


class DetectionListHandlers(object):
    """Handlers DTO for passing in specific detection list functions.
    
    Args:
        add (callable): A function that adds an employee to the list.
        remove (callable): A function that removes an employee from the list.
        load_add (callable): A function that loads the add-related `ArgConfig`s.
    """

    def __init__(self, add=None, remove=None, load_add=None):
        self.add_employee = add
        self.remove_employee = remove
        self.load_add_description = load_add


class UserDoesNotExistError(Exception):
    """An error to represent a username that is not in our system."""

    def __init__(self, username):
        super(UserDoesNotExistError, self).__init__(u"User '{}' does not exist.".format(username))


class DetectionList(object):
    """An object representing a Code42 detection list. Use this class by passing in handlers for 
    adding and removing employees. This class will handle the bulk-related commands and some 
    shared help texts.
    
    Args:
        list_name (str): An option from the DetectionLists enum. For convenience, use one of the 
            given `classmethods`.
        handlers (DetectionListHandlers): A DTO containing implementations for adding / removing 
            users from specific lists.
        cmd_factory (DetectionListCommandFactory): A factory that creates detection list commands.
    """

    def __init__(self, list_name, handlers, cmd_factory=None):
        self.name = list_name
        self.handlers = handlers
        self.factory = cmd_factory or DetectionListCommandFactory(list_name)

    @classmethod
    def create_high_risk_list(cls, handlers):
        """Creates a high risk detection list.
        
        Args:
            handlers (DetectionListHandlers): A DTO containing implementations for adding / 
                removing users from specific lists.
        
        Returns:
            DetectionList: A high-risk employee detection list.
        """
        return cls(DetectionLists.HIGH_RISK_EMPLOYEE, handlers)

    def load_subcommands(self):
        """Loads high risk employee related subcommands"""
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
        detection list.
        
        Args:
            cmd (str): An option from the `BulkCommandType` enum specifying which type of csv to 
                generate.
            path (str, optional): A path to put the file after it's generated. If None, will use 
                the current working directory. Defaults to None.
        """
        handler = None
        if cmd == BulkCommandType.ADD:
            handler = self.handlers.add_employee
        generate_template(handler, path)

    def bulk_add_employees(self, sdk, profile, csv_file):
        """Takes a csv file with each row representing an employee and adds them all to a 
        detection list in a bulk fashion.

        Args:
            sdk (py42.sdk.SDKClient): The py42 sdk.
            profile (Code42Profile): The profile under which to execute this command.
            csv_file (str): The path to the csv file containing rows of users.
        """
        run_bulk_process(csv_file, lambda **kwargs: self._add_employee(sdk, profile, **kwargs))

    def _add_employee(self, sdk, profile, **kwargs):
        if (
            kwargs.has_key(DetectionListUserKeys.CLOUD_ALIAS)
            and type(kwargs[DetectionListUserKeys.CLOUD_ALIAS]) != list
        ):
            kwargs[DetectionListUserKeys.CLOUD_ALIAS] = kwargs[
                DetectionListUserKeys.CLOUD_ALIAS
            ].split()

        self.handlers.add_employee(sdk, profile, **kwargs)


def load_user_descriptions(argument_collection):
    """Loads the arg descriptions related to updating fields about a detection list user, such as 
    notes or cloud aliases.
    
    Args:
        argument_collection (ArgConfigCollection): The arg configs off the command that needs its 
            user descriptions loaded.
    """
    username = argument_collection.arg_configs[DetectionListUserKeys.USERNAME]
    cloud_alias = argument_collection.arg_configs[DetectionListUserKeys.CLOUD_ALIAS]
    notes = argument_collection.arg_configs[DetectionListUserKeys.NOTES]

    username.set_help(u"The code42 username of the user you want to add.")
    cloud_alias.set_help(u"Alternative emails addresses for other cloud services.")
    cloud_alias.as_multi_val_param()
    notes.set_help(u"Notes about the employee.")


def get_user_id(sdk, username):
    """Returns the user's UID (referred to by `user_id` in detection lists). If the user does not 
    exist, it prints an error and exits.
    
    Args:
        sdk (py42.sdk.SDKClient): The py42 sdk.
        username (str or unicode): The username of the user to get an ID for.
    
    Returns:
         str: The user ID for the user with the given username.
    """
    users = sdk.users.get_by_username(username)[u"users"]
    if not users:
        print_error(str(UserDoesNotExistError(username)))
        exit(1)
    return users[0][u"userUid"]


def update_user(sdk, user_id, cloud_alias=None, risk_tag=None, notes=None):
    """Updates a detection list user.
    
    Args:
        user_id (str): The ID of the user to update. This is their `userUid` found from 
            `sdk.users.get_by_username()`.
        cloud_alias (iter[str]): A list of cloud aliases to add to the user.
        risk_tag (iter[str]): A list of risk tags associated with user.
        notes (str): Notes about the user.
    """
    if cloud_alias:
        sdk.detectionlists.add_user_cloud_aliases(user_id, cloud_alias)
    if risk_tag:
        sdk.detectionlists.add_user_risk_tags(user_id, risk_tag)
    if notes:
        sdk.detectionlists.update_user_notes(user_id, notes)
