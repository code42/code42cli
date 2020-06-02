from py42.exceptions import Py42BadRequestError

from code42cli.cmds.detectionlists.commands import DetectionListSubcommandLoader
from code42cli.bulk import generate_template, run_bulk_process
from code42cli.file_readers import create_csv_reader, create_flat_file_reader
from code42cli.errors import UserAlreadyAddedError, UnknownRiskTagError
from code42cli.cmds.detectionlists.enums import DetectionLists, DetectionListUserKeys, RiskTags
from code42cli.cmds.detectionlists.bulk import BulkDetectionList, BulkHighRiskEmployee
from code42cli.util import get_user_id


def try_handle_user_already_added_error(bad_request_err, username_tried_adding, list_name):
    if _error_is_user_already_added(bad_request_err.response.text):
        raise UserAlreadyAddedError(username_tried_adding, list_name)
    return False


def _error_is_user_already_added(bad_request_error_text):
    return u"User already on list" in bad_request_error_text


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

    def add_handler(self, attr_name, handler):
        self.__setattr__(attr_name, handler)


class DetectionList(object):
    """An object representing a Code42 detection list. Use this class by passing in handlers for 
    adding and removing employees. This class will handle the bulk-related commands and some 
    search_shared help texts.
    
    Args:
        list_name (str or unicode): An option from the DetectionLists enum. For convenience, use one of the 
            given `classmethods`.
        handlers (DetectionListHandlers): A DTO containing implementations for adding / removing 
            users from specific lists.
        cmd_factory (DetectionListSubcommandLoader): A factory that creates detection list commands.
    """

    def __init__(self, list_name, handlers, subcommand_loader=None):
        self.name = list_name
        self.handlers = handlers
        self.subcommand_loader = subcommand_loader or DetectionListSubcommandLoader(list_name)
        self.bulk_subcommand_loader = self.subcommand_loader.bulk_subcommand_loader
        self.bulk_subcommand_loader.load_commands = lambda: self._load_bulk_subcommands

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
        bulk = self.subcommand_loader.create_bulk_command()
        bulk.subcommand_loader.load_commands = lambda: self._load_bulk_subcommands()
        add = self.subcommand_loader.create_add_command(
            self.handlers.add_employee, self.handlers.load_add_description
        )
        remove = self.subcommand_loader.create_remove_command(
            self.handlers.remove_employee, load_username_description
        )
        return [bulk, add, remove]

    def _load_bulk_subcommands(self):
        add = self.bulk_subcommand_loader.create_bulk_add_command(
            self.bulk_add_employees, self.handlers.add_employee
        )
        remove = self.bulk_subcommand_loader.create_bulk_remove_command(self.bulk_remove_employees)
        commands = [add, remove]

        if self.name == DetectionLists.HIGH_RISK_EMPLOYEE:
            commands.extend(self._get_risk_tags_bulk_subcommands())
        else:
            generate_template_cmd = self.bulk_subcommand_loader.create_bulk_generate_template_command(
                self.generate_template_file
            )
            commands.append(generate_template_cmd)
        return commands

    def _get_risk_tags_bulk_subcommands(self):
        bulk_add_risk_tags = self.bulk_subcommand_loader.create_bulk_add_risk_tags_command(
            self.bulk_add_risk_tags, add_risk_tags
        )
        bulk_remove_risk_tags = self.bulk_subcommand_loader.create_bulk_remove_risk_tags_command(
            self.bulk_remove_risk_tags, remove_risk_tags
        )

        self.handlers.add_handler(u"add_risk_tags", add_risk_tags)
        self.handlers.add_handler(u"remove_risk_tags", remove_risk_tags)
        generate_template_cmd = self.bulk_subcommand_loader.create_hre_bulk_generate_template_command(
            self.generate_template_file
        )
        return [bulk_add_risk_tags, bulk_remove_risk_tags, generate_template_cmd]

    def generate_template_file(self, cmd, path=None):
        """Generates a template file a user would need to fill-in for bulk operating on the 
        detection list.

        Args:
            cmd (str or unicode): An option from the `BulkCommandType` enum specifying which type of file to 
                generate.
            path (str or unicode, optional): A path to put the file after it's generated. If None, will use 
                the current working directory. Defaults to None.
        """

        if self.name == DetectionLists.HIGH_RISK_EMPLOYEE:
            detection_list = BulkHighRiskEmployee()
        else:
            detection_list = BulkDetectionList()
        handler = detection_list.get_handler(self.handlers, cmd)
        generate_template(handler, path)

    def bulk_add_employees(self, sdk, profile, csv_file):
        """Takes a csv file with each row representing an employee and adds them all to a 
        detection list in a bulk fashion.

        Args:
            sdk (py42.sdk.SDKClient): The py42 sdk.
            profile (Code42Profile): The profile under which to execute this command.
            csv_file (str or unicode): The path to the csv file containing rows of users.
        """
        reader = create_csv_reader(csv_file)
        run_bulk_process(lambda **kwargs: self._add_employee(sdk, profile, **kwargs), reader)

    def bulk_remove_employees(self, sdk, profile, users_file):
        """Takes a flat file with each row containing a username and removes them all from the 
        detection list in a bulk fashion.
        
        Args:
            sdk (py42.sdk.SDKClient): The py42 sdk.
            profile (Code42Profile): The profile under which to execute this command.
            users_file (str or unicode): The path to the file containing rows of user names.
        """
        reader = create_flat_file_reader(users_file)
        run_bulk_process(
            lambda *args, **kwargs: self._remove_employee(sdk, profile, *args, **kwargs), reader
        )

    def _add_employee(self, sdk, profile, **kwargs):
        self.handlers.add_employee(sdk, profile, **kwargs)

    def _remove_employee(self, sdk, profile, *args, **kwargs):
        self.handlers.remove_employee(sdk, profile, *args, **kwargs)

    def bulk_add_risk_tags(self, sdk, profile, csv_file):
        reader = create_csv_reader(csv_file)
        run_bulk_process(lambda **kwargs: add_risk_tags(sdk, profile, **kwargs), reader)

    def bulk_remove_risk_tags(self, sdk, profile, csv_file):
        reader = create_csv_reader(csv_file)
        run_bulk_process(lambda **kwargs: remove_risk_tags(sdk, profile, **kwargs), reader)


def load_username_description(argument_collection):
    """Loads the arg descriptions for the `username` CLI parameter."""
    username = argument_collection.arg_configs[DetectionListUserKeys.USERNAME]
    username.set_help(u"A Code42 username for an employee.")


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


def handle_list_args(list_arg):
    """Converts str args to a list. Useful for `bulk` commands which don't use `argparse` but
    instead pass in values from files, such as in the form "item1 item2"."""
    if list_arg and not isinstance(list_arg, list):
        return list_arg.split()
    return list_arg


def add_risk_tags(sdk, profile, username, tag):
    risk_tag = handle_list_args(tag)
    user_id = get_user_id(sdk, username)
    try_add_risk_tags(sdk, user_id, risk_tag)


def remove_risk_tags(sdk, profile, username, tag):
    risk_tag = handle_list_args(tag)
    user_id = get_user_id(sdk, username)
    try_remove_risk_tags(sdk, user_id, risk_tag)
