import click

from code42cli.cmds.detectionlists import (
    DetectionListHandlers,
    load_user_descriptions,
    try_handle_user_already_added_error,
)
from code42cli.cmds.detectionlists_shared import update_user
from code42cli.cmds.detectionlists_shared.options import (
    username_arg,
    cloud_alias_option,
    notes_option,
)
from code42cli.bulk import run_bulk_process, template_args, write_template_file
from code42cli.util import get_user_id
from code42cli.cmds.detectionlists.enums import DetectionLists
from code42cli.options import global_options, OrderedGroup

from py42.exceptions import Py42BadRequestError


@click.group(cls=OrderedGroup)
@global_options
def departing_employee(state):
    pass


@departing_employee.command()
@username_arg
@click.option("--departure-date", help="The date the employee is departing in format yyyy-MM-dd.")
@cloud_alias_option
@notes_option
@global_options
def add(state, username, cloud_alias, departure_date, notes):
    user_id = get_user_id(state.sdk, username)
    try:
        state.sdk.detectionlists.departing_employee.add(user_id, departure_date)
        update_user(state.sdk, user_id, cloud_alias, notes=notes)
    except Py42BadRequestError as err:
        list_name = u"{} list".format(DetectionLists.DEPARTING_EMPLOYEE)
        try_handle_user_already_added_error(err, username, list_name)
        raise


@departing_employee.command()
@username_arg
@global_options
def remove(state, username):
    user_id = get_user_id(state.sdk, username)
    state.sdk.detectionlists.departing_employee.remove(user_id)


@departing_employee.group(cls=OrderedGroup)
@global_options
def bulk(state):
    pass


DEPARTING_EMPLOYEE_CSV_HEADERS = []


@bulk.command()
@template_args
def generate_template(cmd, path):
    """\b
    Generate the csv template needed for bulk adding/removing users.

    Optional PATH argument can be provided to write to a specific file path/name.
    """
    if not path:
        filename = "departing_employee_bulk_{}_users.csv".format(cmd)
        path = os.path.join(os.getcwd(), filename)
    write_template_file(path, columns=["matter_id", "username"])
