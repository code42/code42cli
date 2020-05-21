from code42cli.cmds.detectionlists import (
    DetectionList,
    DetectionListHandlers,
    load_user_descriptions,
    get_user_id,
    update_user,
    try_handle_user_already_added_error,
)
from code42cli.cmds.detectionlists.enums import DetectionLists

from py42.exceptions import Py42BadRequestError


def load_subcommands():
    handlers = _create_handlers()
    detection_list = DetectionList.create_departing_employee_list(handlers)
    return detection_list.load_subcommands()


def _create_handlers():
    return DetectionListHandlers(
        add=add_departing_employee, remove=remove_departing_employee, load_add=_load_add_description
    )


def add_departing_employee(
    sdk, profile, username, cloud_alias=None, departure_date=None, notes=None
):
    """Adds an employee to the departing employee detection list.

    Args:
        sdk (py42.sdk.SDKClient): py42.
        profile (C42Profile): Your code42 profile.
        username (str): The username of the employee to add.
        cloud_alias (str): An alternative email address for another cloud service.
        departure_date (str): The date the employee is departing in format `YYYY-MM-DD`.
        notes: (str): Notes about the employee.
    """
    user_id = get_user_id(sdk, username)

    try:
        sdk.detectionlists.departing_employee.add(user_id, departure_date)
        update_user(sdk, user_id, cloud_alias, notes=notes)
    except Py42BadRequestError as err:
        list_name = DetectionLists.DEPARTING_EMPLOYEE
        try_handle_user_already_added_error(err, username, list_name)
        raise


def remove_departing_employee(sdk, profile, username):
    user_id = get_user_id(sdk, username)
    sdk.detectionlists.departing_employee.remove(user_id)


def _load_add_description(argument_collection):
    load_user_descriptions(argument_collection)
    departure_date = argument_collection.arg_configs[u"departure_date"]
    departure_date.set_help(u"The date the employee is departing in format YYYY-MM-DD.")
