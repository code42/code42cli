import os

import click

from code42cli.cmds.detectionlists_shared import update_user, try_handle_user_already_added_error
from code42cli.cmds.detectionlists_shared.options import (
    username_arg,
    cloud_alias_option,
    notes_option,
)
from code42cli.bulk import template_args, write_template_file, run_bulk_process
from code42cli.file_readers import read_csv_arg, read_flat_file_arg
from code42cli.util import get_user_id
from code42cli.cmds.detectionlists_shared.enums import DetectionLists
from code42cli.options import global_options, OrderedGroup

from py42.exceptions import Py42BadRequestError


@click.group(cls=OrderedGroup)
@global_options
def departing_employee(state):
    pass


@departing_employee.command()
@username_arg
@click.option("--departure-date", help="The date the employee is departing. Format: yyyy-MM-dd.")
@cloud_alias_option
@notes_option
@global_options
def add(state, username, cloud_alias, departure_date, notes):
    _add_departing_employee(state.sdk, username, cloud_alias, departure_date, notes)


@departing_employee.command()
@username_arg
@global_options
def remove(state, username):
    _remove_departing_employee(state.sdk, username)


@departing_employee.group(cls=OrderedGroup)
@global_options
def bulk(state):
    pass


DEPARTING_EMPLOYEE_CSV_HEADERS = ["username", "cloud_alias", "departure_date", "notes"]


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
    write_template_file(path, columns=DEPARTING_EMPLOYEE_CSV_HEADERS)


@bulk.command(
    help="Bulk add users to the departing-employee detection list using a csv file. "
    "CSV file format: {}".format(",".join(DEPARTING_EMPLOYEE_CSV_HEADERS))
)
@read_csv_arg(headers=DEPARTING_EMPLOYEE_CSV_HEADERS)
@global_options
def add_user(state, csv_rows):
    row_handler = lambda username, cloud_alias, departure_date, notes: _add_departing_employee(
        state.sdk, username, cloud_alias, departure_date, notes
    )
    run_bulk_process(row_handler, csv_rows)


@bulk.command(
    help="Bulk remove users from the departing-employee detection list using a newline separated "
    "file of usernames."
)
@read_flat_file_arg
@global_options
def remove_user(state, file_rows):
    row_handler = lambda username: _remove_departing_employee(state.sdk, username)
    run_bulk_process(row_handler, file_rows)


def _add_departing_employee(sdk, username, cloud_alias, departure_date, notes):
    user_id = get_user_id(sdk, username)
    try:
        sdk.detectionlists.departing_employee.add(user_id, departure_date)
        update_user(sdk, user_id, cloud_alias, notes=notes)
    except Py42BadRequestError as err:
        try_handle_user_already_added_error(err, username, "departing-employee list")
        raise


def _remove_departing_employee(sdk, username):
    user_id = get_user_id(sdk, username)
    sdk.detectionlists.departing_employee.remove(user_id)
