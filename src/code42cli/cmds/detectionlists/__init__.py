from py42.exceptions import Py42BadRequestError

from code42cli.compat import str
from code42cli.cmds.detectionlists.commands import DetectionListCommandFactory
from code42cli.bulk import generate_template, run_bulk_process, CSVReader, FlatFileReader
from code42cli.logger import get_main_cli_logger
from code42cli.bulk import BulkCommandType
from code42cli.cmds.detectionlists.enums import DetectionLists, DetectionListUserKeys, RiskTags


class UserAlreadyAddedError(Exception):
    def __init__(self, username, list_name):
        msg = u"'{}' is already on the {} list.".format(username, list_name)
        super(UserAlreadyAddedError, self).__init__(msg)


class UnknownRiskTagError(Exception):
    def __init__(self, bad_tags):
        tags = u", ".join(bad_tags)
        super(UnknownRiskTagError, self).__init__(
            u"The following risk tags are unknown: '{}'.".format(tags)
        )


def try_handle_user_already_added_error(bad_request_err, username_tried_adding, list_name):
    if _error_is_user_already_added(bad_request_err.response.text):
        raise UserAlreadyAddedError(username_tried_adding, list_name)
    return False


def _error_is_user_already_added(bad_request_error_text):
    return u"User already on list" in bad_request_error_text


class UserDoesNotExistError(Exception):
    """An error to represent a username that is not in our system. The CLI shows this error when 
    the user tries to add or remove a user that does not exist. This error is not shown during 
    bulk add or remove."""

    def __init__(self, username):
        super(UserDoesNotExistError, self).__init__(u"User '{}' does not exist.".format(username))


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


class DetectionList(object):
    """An object representing a Code42 detection list. Use this class by passing in handlers for 
    adding and removing employees. This class will handle the bulk-related commands and some 
    search_shared help texts.
    
    Args:
        list_name (str or unicode): An option from the DetectionLists enum. For convenience, use one of the 
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
    def create_high_risk_employee_list(cls, handlers):
        """Creates a high risk employee detection list.
        
        Args:
            handlers (DetectionListHandlers): A DTO containing implementations for adding / 
                removing users from specific lists.
        
        Returns:
            DetectionList: A high risk employee detection list.
        """
        return cls(DetectionLists.HIGH_RISK_EMPLOYEE, handlers)

    @classmethod
    def create_departing_employee_list(cls, handlers):
        """Creates a departing employee detection list.
        
        Args:
            handlers (DetectionListHandlers): A DTO containing implementations for adding /
                removing users from specific lists.
        
        Returns:
            DetectionList: A departing employee detection list.
        """
        return cls(DetectionLists.DEPARTING_EMPLOYEE, handlers)

    def load_subcommands(self):
        """Loads high risk employee related subcommands"""
        bulk = self.factory.create_bulk_command(lambda: self._load_bulk_subcommands())
        add = self.factory.create_add_command(
            self.handlers.add_employee, self.handlers.load_add_description
        )
        remove = self.factory.create_remove_command(
            self.handlers.remove_employee, load_username_description
        )
        return [bulk, add, remove]

    def _load_bulk_subcommands(self):
        generate_template_cmd = self.factory.create_bulk_generate_template_command(
            self.generate_template_file
        )
        add = self.factory.create_bulk_add_command(self.bulk_add_employees)
        remove = self.factory.create_bulk_remove_command(self.bulk_remove_employees)
        return [generate_template_cmd, add, remove]

    def generate_template_file(self, cmd, path=None):
        """Generates a template file a user would need to fill-in for bulk operating on the 
        detection list.
        
        Args:
            cmd (str or unicode): An option from the `BulkCommandType` enum specifying which type of file to 
                generate.
            path (str or unicode, optional): A path to put the file after it's generated. If None, will use 
                the current working directory. Defaults to None.
        """
        handler = None
        if cmd == BulkCommandType.ADD:
            handler = self.handlers.add_employee
        elif cmd == BulkCommandType.REMOVE:
            handler = self.handlers.remove_employee

        generate_template(handler, path)

    def bulk_add_employees(self, sdk, profile, csv_file):
        """Takes a csv file with each row representing an employee and adds them all to a 
        detection list in a bulk fashion.

        Args:
            sdk (py42.sdk.SDKClient): The py42 sdk.
            profile (Code42Profile): The profile under which to execute this command.
            csv_file (str or unicode): The path to the csv file containing rows of users.
        """
        run_bulk_process(
            csv_file, lambda **kwargs: self._add_employee(sdk, profile, **kwargs), CSVReader()
        )

    def bulk_remove_employees(self, sdk, profile, users_file):
        """Takes a flat file with each row containing a username and removes them all from the 
        detection list in a bulk fashion.
        
        Args:
            sdk (py42.sdk.SDKClient): The py42 sdk.
            profile (Code42Profile): The profile under which to execute this command.
            users_file (str or unicode): The path to the file containing rows of user names.
        """
        run_bulk_process(
            users_file,
            lambda *args, **kwargs: self._remove_employee(sdk, profile, *args, **kwargs),
            FlatFileReader(),
        )

    def _add_employee(self, sdk, profile, **kwargs):
        self.handlers.add_employee(sdk, profile, **kwargs)

    def _remove_employee(self, sdk, profile, *args, **kwargs):
        self.handlers.remove_employee(sdk, profile, *args, **kwargs)


def load_username_description(argument_collection):
    """Loads the arg descriptions for the `username` CLI parameter."""
    username = argument_collection.arg_configs[DetectionListUserKeys.USERNAME]
    username.set_help(u"A code42 username for an employee.")


def load_user_descriptions(argument_collection):
    """Loads the arg descriptions related to updating fields about a detection list user, such as 
    notes or a cloud alias.
    
    Args:
        argument_collection (ArgConfigCollection): The arg configs off the command that needs its 
            user descriptions loaded.
    """
    load_username_description(argument_collection)
    cloud_alias = argument_collection.arg_configs[DetectionListUserKeys.CLOUD_ALIAS]
    notes = argument_collection.arg_configs[DetectionListUserKeys.NOTES]
    cloud_alias.set_help(u"An alternative email address for another cloud service.")
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
        ex = UserDoesNotExistError(username)
        get_main_cli_logger().print_and_log_error(str(ex))
        raise ex
    return users[0][u"userUid"]


def update_user(sdk, user_id, cloud_alias=None, risk_tag=None, notes=None):
    """Updates a detection list user.
    
    Args:
        sdk (py42.sdk.SDKClient): py42 sdk.
        user_id (str or unicode): The ID of the user to update. This is their `userUid` found from 
            `sdk.users.get_by_username()`.
        cloud_alias (str or unicode): A cloud alias to add to the user.
        risk_tag (iter[str or unicode]): A list of risk tags associated with user.
        notes (str or unicode): Notes about the user.
    """
    if cloud_alias:
        sdk.detectionlists.add_user_cloud_alias(user_id, cloud_alias)
    if risk_tag:
        try_add_risk_tags(sdk, user_id, risk_tag)
    if notes:
        sdk.detectionlists.update_user_notes(user_id, notes)


def try_add_risk_tags(sdk, user_id, risk_tag):
    _try_add_or_remove_risk_tags(user_id, risk_tag, sdk.detectionlists.add_user_risk_tags)


def try_remove_risk_tags(sdk, user_id, risk_tag):
    _try_add_or_remove_risk_tags(user_id, risk_tag, sdk.detectionlists.remove_user_risk_tags)


def _try_add_or_remove_risk_tags(user_id, risk_tag, func):
    try:
        func(user_id, risk_tag)
    except Py42BadRequestError:
        _try_handle_bad_risk_tag(risk_tag)
        raise


def _try_handle_bad_risk_tag(tags):
    options = list(RiskTags())
    unknowns = [tag for tag in tags if tag not in options] if tags else None
    if unknowns:
        raise UnknownRiskTagError(unknowns)
