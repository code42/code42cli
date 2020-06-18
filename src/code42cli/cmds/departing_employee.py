import click

from code42cli.cmds.detectionlists import (
    DetectionListHandlers,
    load_user_descriptions,
    try_handle_user_already_added_error,
)
from code42cli.cmds.detectionlists_shared import update_user
from code42cli.util import get_user_id
from code42cli.cmds.detectionlists.enums import DetectionLists
from code42cli.options import global_options, OrderedGroup

from py42.exceptions import Py42BadRequestError


@click.group(cls=OrderedGroup)
@global_options
def departing_employee(state):
    pass


@departing_employee.command()
def add(state, username, cloud_alias, departure_date, notes):
    user_id = get_user_id(state.sdk, username)
    try:
        state.sdk.detectionlists.departing_employee.add(user_id, departure_date)
        update_user(state.sdk, user_id, cloud_alias, notes=notes)
    except Py42BadRequestError as err:
        list_name = u"{} list".format(DetectionLists.DEPARTING_EMPLOYEE)
        try_handle_user_already_added_error(err, username, list_name)
        raise


def remove_departing_employee(sdk, profile, username):
    user_id = get_user_id(sdk, username)
    sdk.detectionlists.departing_employee.remove(user_id)


def _load_add_description(argument_collection):
    load_user_descriptions(argument_collection)
    departure_date = argument_collection.arg_configs[u"departure_date"]
    departure_date.set_help(u"The date the employee is departing in format yyyy-MM-dd.")
