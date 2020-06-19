import os

import click

from py42.exceptions import Py42BadRequestError

from code42cli.cmds.detectionlists_shared import (
    update_user,
    add_risk_tags as _add_risk_tags,
    remove_risk_tags as _remove_risk_tags,
    try_handle_user_already_added_error,
    handle_list_args,
)
from code42cli.cmds.detectionlists_shared.options import (
    cloud_alias_option,
    notes_option,
    username_arg,
)
from code42cli.options import global_options, OrderedGroup
from code42cli.util import get_user_id
from code42cli.cmds.detectionlists_shared.enums import RiskTags
from code42cli.bulk import run_bulk_process, write_template_file, template_args
from code42cli.file_readers import read_csv_arg, read_flat_file_arg


risk_tag_option = click.option(
    "-t",
    "--risk-tag",
    multiple=True,
    type=click.Choice(RiskTags()),
    help="Risk tags associated with the employee.",
)


@click.group(cls=OrderedGroup)
@global_options
def high_risk_employee(state):
    pass


@high_risk_employee.command()
@cloud_alias_option
@notes_option
@risk_tag_option
@username_arg
@global_options
def add(state, username, cloud_alias, risk_tag, notes):
    _add_high_risk_employee(state.sdk, username, cloud_alias, risk_tag, notes)


@high_risk_employee.command()
@username_arg
@global_options
def remove(state, username):
    _remove_high_risk_employee(state.sdk, username)


@high_risk_employee.command()
@username_arg
@risk_tag_option
@global_options
def add_risk_tags(state, username, risk_tag):
    _add_risk_tags(state.sdk, username, risk_tag)


@high_risk_employee.command()
@username_arg
@risk_tag_option
@global_options
def remove_risk_tags(state, username, risk_tag):
    _remove_risk_tags(state.sdk, username, risk_tag)


@high_risk_employee.group()
@global_options
def bulk(state):
    pass


HIGH_RISK_EMPLOYEE_CSV_HEADERS = ["username", "cloud_alias", "risk_tag", "notes"]


@bulk.command()
@template_args
def generate_template(cmd, path):
    """\b
    Generate the csv template needed for bulk adding/removing users.

    Optional PATH argument can be provided to write to a specific file path/name.
    """
    if not path:
        filename = "high_risk_employee_bulk_{}_users.csv".format(cmd)
        path = os.path.join(os.getcwd(), filename)
    write_template_file(path, columns=HIGH_RISK_EMPLOYEE_CSV_HEADERS)


@bulk.command()
@read_csv_arg(headers=HIGH_RISK_EMPLOYEE_CSV_HEADERS)
@global_options
def add(state, csv_rows):
    row_handler = lambda username, cloud_alias, risk_tag, notes: _add_high_risk_employee(
        state.sdk, username, cloud_alias, risk_tag, notes
    )
    run_bulk_process(row_handler, csv_rows)


@bulk.command()
@read_flat_file_arg
@global_options
def remove(state, file_rows):
    row_handler = lambda username: _remove_high_risk_employee(state.sdk, username)
    run_bulk_process(row_handler, file_rows)


def _add_high_risk_employee(sdk, username, cloud_alias, risk_tag, notes):
    risk_tag = handle_list_args(risk_tag)
    user_id = get_user_id(sdk, username)

    try:
        sdk.detectionlists.high_risk_employee.add(user_id)
        update_user(sdk, user_id, cloud_alias=cloud_alias, risk_tag=risk_tag, notes=notes)
    except Py42BadRequestError as err:
        try_handle_user_already_added_error(err, username, "high-risk-employee list")
        raise


def _remove_high_risk_employee(sdk, username):
    """Removes an employee from the high risk employee detection list.

    Args:
        sdk (py42.sdk.SDKClient): py42.
        profile (C42Profile): Your code42 profile.
        username (str): The username of the employee to remove.
    """
    user_id = get_user_id(sdk, username)
    sdk.detectionlists.high_risk_employee.remove(user_id)
