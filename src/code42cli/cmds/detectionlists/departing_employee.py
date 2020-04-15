from code42cli.cmds.detectionlists.enums import BulkCommandType, DetectionLists
from code42cli.cmds.detectionlists.commands import (
    DetectionListCommandFactory,
    create_usage_prefix,
    load_username_description,
)
from code42cli.bulk import generate_template, run_bulk_process

_NAME = DetectionLists.DEPARTING_EMPLOYEE
_USAGE_PREFIX = create_usage_prefix(_NAME)


def load_subcommands():
    factory = DetectionListCommandFactory(_NAME)
    bulk = factory.create_bulk_command(lambda: load_bulk_subcommands(factory))
    add = factory.create_add_command(add_departing_employee, _load_add_description)
    return [bulk, add]


def load_bulk_subcommands(factory):
    generate_template_cmd = factory.create_bulk_generate_template_command(generate_csv_file)
    add = factory.create_bulk_add_command(bulk_add_departing_employees)
    return [generate_template_cmd, add]


def generate_csv_file(cmd, path=None):
    """Generates a csv template a user would need to fill-in for bulk adding users to the 
    departing employee detection list."""
    handler = None
    if cmd == BulkCommandType.ADD:
        handler = add_departing_employee
    generate_template(handler, path)


def bulk_add_departing_employees(sdk, profile, csv_file):
    """Takes a csv file in the form `username,cloud_aliases,departure_date,notes` with each row 
    representing an employee and adds each employee to the departing employee detection list in a 
    bulk fashion.

    Args:
        sdk (py42.sdk.SDKClient): The py42 sdk.
        profile (Code42Profile): The profile under which to execute this command.
        csv_file (str): The path to the csv file containing rows of users.
    """
    run_bulk_process(csv_file, lambda **kwargs: add_departing_employee(sdk, profile, **kwargs))


def add_departing_employee(
    sdk, profile, username, cloud_aliases=None, departure_date=None, notes=None
):
    """Adds the user with the given username to the departing employee detection list.

    Args:
        sdk (py42.sdk.SDKClient): The py42 sdk.
        profile (Code42Profile): The profile under which to execute this command.
        username (str): The username for the user.
        cloud_aliases (iter[str]): A list of cloud aliases associated with the user.
        departure_date (str): The date the employee is departing.
        notes (str): Notes about the user.
    """


def _load_add_description(argument_collection):
    load_username_description(argument_collection)
    departure_date = argument_collection.arg_configs[u"departure_date"]
    departure_date.set_help(u"The date the employee is departing.")
