import click
from py42.exceptions import Py42BadRequestError

from code42cli.bulk import run_bulk_process, generate_template_cmd_factory
from code42cli.cmds.detectionlists import (
    update_user,
    add_risk_tags as _add_risk_tags,
    remove_risk_tags as _remove_risk_tags,
    try_handle_user_already_added_error,
    handle_list_args,
)
from code42cli.cmds.detectionlists.enums import RiskTags
from code42cli.cmds.detectionlists.options import (
    cloud_alias_option,
    notes_option,
    username_arg,
)
from code42cli.cmds.shared import get_user_id
from code42cli.file_readers import read_csv_arg, read_flat_file_arg
from code42cli.options import sdk_options, OrderedGroup

risk_tag_option = click.option(
    "-t",
    "--risk-tag",
    multiple=True,
    type=click.Choice(RiskTags()),
    help="Risk tags associated with the employee.",
)


@click.group(cls=OrderedGroup)
@sdk_options
def high_risk_employee(state):
    """For adding and removing employees from the high risk employee detection list."""
    pass


@high_risk_employee.command()
@cloud_alias_option
@notes_option
@risk_tag_option
@username_arg
@sdk_options
def add(state, username, cloud_alias, risk_tag, notes):
    """Add a user to the high-risk-employee detection list."""
    _add_high_risk_employee(state.sdk, username, cloud_alias, risk_tag, notes)


@high_risk_employee.command()
@username_arg
@sdk_options
def remove(state, username):
    """Remove a user from the high-risk-employee detection list."""
    _remove_high_risk_employee(state.sdk, username)


@high_risk_employee.command()
@username_arg
@risk_tag_option
@sdk_options
def add_risk_tags(state, username, risk_tag):
    """Associates risk tags with a user."""
    _add_risk_tags(state.sdk, username, risk_tag)


@high_risk_employee.command()
@username_arg
@risk_tag_option
@sdk_options
def remove_risk_tags(state, username, risk_tag):
    """Disassociates risk tags from a user."""
    _remove_risk_tags(state.sdk, username, risk_tag)


@high_risk_employee.group(cls=OrderedGroup)
@sdk_options
def bulk(state):
    """Tools for executing bulk high risk employee actions."""
    pass


HIGH_RISK_EMPLOYEE_CSV_HEADERS = ["username", "cloud_alias", "risk_tag", "notes"]
RISK_TAG_CSV_HEADERS = ["username", "tag"]

high_risk_employee_generate_template = generate_template_cmd_factory(
    group_name="high_risk_employee",
    commands_dict={
        "add": HIGH_RISK_EMPLOYEE_CSV_HEADERS,
        "remove": "username",
        "add-risk-tags": RISK_TAG_CSV_HEADERS,
        "remove-risk-tags": RISK_TAG_CSV_HEADERS,
    },
)
bulk.add_command(high_risk_employee_generate_template)


@bulk.command(
    help="Bulk add users to the high-risk-employee detection list using a csv file with "
    "format: {}".format(",".join(HIGH_RISK_EMPLOYEE_CSV_HEADERS))
)
@read_csv_arg(headers=HIGH_RISK_EMPLOYEE_CSV_HEADERS)
@sdk_options
def add(state, csv_rows):
    sdk = state.sdk
    row_handler = lambda username, cloud_alias, risk_tag, notes: _add_high_risk_employee(
        sdk, username, cloud_alias, risk_tag, notes
    )
    run_bulk_process(
        row_handler, csv_rows, progress_label="Adding users to high risk employee detection list:"
    )


@bulk.command(
    help="Bulk remove users from the high-risk-employee detection list using a newline separated "
    "file of usernames."
)
@read_flat_file_arg
@sdk_options
def remove(state, file_rows):
    sdk = state.sdk
    row_handler = lambda username: _remove_high_risk_employee(sdk, username)
    run_bulk_process(
        row_handler,
        file_rows,
        progress_label="Removing users from high risk employee detection list:",
    )


@bulk.command(
    help="Adds risk tags to users in bulk using a csv file with format: {}".format(
        ",".join(RISK_TAG_CSV_HEADERS)
    )
)
@read_csv_arg(headers=RISK_TAG_CSV_HEADERS)
@sdk_options
def add_risk_tags(state, csv_rows):
    sdk = state.sdk
    row_handler = lambda username, tag: _add_risk_tags(sdk, username, tag)
    run_bulk_process(
        row_handler, csv_rows, progress_label="Adding risk tags to users:",
    )


@bulk.command(
    help="Removes risk tags from users in bulk using a csv file with format: {}".format(
        ",".join(RISK_TAG_CSV_HEADERS)
    )
)
@read_csv_arg(headers=RISK_TAG_CSV_HEADERS)
@sdk_options
def remove_risk_tags(state, csv_rows):
    sdk = state.sdk
    row_handler = lambda username, tag: _remove_risk_tags(sdk, username, tag)
    run_bulk_process(
        row_handler, csv_rows, progress_label="Removing risk tags from users:",
    )


def _add_high_risk_employee(sdk, username, cloud_alias, risk_tag, notes):
    risk_tag = handle_list_args(risk_tag)
    user_id = get_user_id(sdk, username)

    try:
        sdk.detectionlists.high_risk_employee.add(user_id)
        update_user(sdk, username, cloud_alias=cloud_alias, risk_tag=risk_tag, notes=notes)
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
