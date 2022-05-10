import click
from py42.clients.detectionlists import RiskTags
from py42.services.detectionlists.high_risk_employee import HighRiskEmployeeFilters

from code42cli.bulk import generate_template_cmd_factory
from code42cli.bulk import run_bulk_process
from code42cli.click_ext.groups import OrderedGroup
from code42cli.cmds.detectionlists import add_risk_tags as _add_risk_tags
from code42cli.cmds.detectionlists import ALL_FILTER
from code42cli.cmds.detectionlists import get_choices
from code42cli.cmds.detectionlists import handle_filter_choice
from code42cli.cmds.detectionlists import handle_list_args
from code42cli.cmds.detectionlists import list_employees
from code42cli.cmds.detectionlists import remove_risk_tags as _remove_risk_tags
from code42cli.cmds.detectionlists import update_user
from code42cli.cmds.detectionlists.options import cloud_alias_option
from code42cli.cmds.detectionlists.options import notes_option
from code42cli.cmds.detectionlists.options import username_arg
from code42cli.cmds.shared import get_user_id
from code42cli.file_readers import read_csv_arg
from code42cli.options import format_option
from code42cli.options import sdk_options
from code42cli.util import deprecation_warning

DEPRECATION_TEXT = "(DEPRECATED): Use `code42 watchlists` commands instead."


def _get_filter_choices():
    filters = HighRiskEmployeeFilters.choices()
    return get_choices(filters)


filter_option = click.option(
    "--filter",
    help=f"High risk employee filter options. Defaults to {ALL_FILTER}.",
    type=click.Choice(_get_filter_choices()),
    default=ALL_FILTER,
    callback=lambda ctx, param, arg: handle_filter_choice(arg),
)


risk_tag_option = click.option(
    "-t",
    "--risk-tag",
    multiple=True,
    type=click.Choice(RiskTags.choices()),
    help="Risk tags associated with the employee.",
)


@click.group(
    cls=OrderedGroup,
    help=f"{DEPRECATION_TEXT}\n\nAdd and remove employees from the High Risk Employees detection list.",
)
@sdk_options(hidden=True)
def high_risk_employee(state):
    pass


@high_risk_employee.command(
    "list",
    help=f"{DEPRECATION_TEXT}\n\nLists the employees on the High Risk Employee list.",
)
@sdk_options()
@format_option
@filter_option
def _list(state, format, filter):
    deprecation_warning(DEPRECATION_TEXT)
    employee_generator = _get_high_risk_employees(state.sdk, filter)
    list_employees(employee_generator, format)


@high_risk_employee.command(
    help=f"{DEPRECATION_TEXT}\n\nAdd a user to the high risk employees detection list."
)
@cloud_alias_option
@notes_option
@risk_tag_option
@username_arg
@sdk_options()
def add(state, username, cloud_alias, risk_tag, notes):
    deprecation_warning(DEPRECATION_TEXT)
    _add_high_risk_employee(state.sdk, username, cloud_alias, risk_tag, notes)


@high_risk_employee.command(
    help=f"{DEPRECATION_TEXT}\n\nRemove a user from the high risk employees detection list."
)
@username_arg
@sdk_options()
def remove(state, username):
    deprecation_warning(DEPRECATION_TEXT)
    _remove_high_risk_employee(state.sdk, username)


@high_risk_employee.command(
    help=f"{DEPRECATION_TEXT}\n\nAssociates risk tags with a user."
)
@username_arg
@risk_tag_option
@sdk_options()
def add_risk_tags(state, username, risk_tag):
    deprecation_warning(DEPRECATION_TEXT)
    _add_risk_tags(state.sdk, username, risk_tag)


@high_risk_employee.command(
    help=f"{DEPRECATION_TEXT}\n\nDisassociates risk tags from a user."
)
@username_arg
@risk_tag_option
@sdk_options()
def remove_risk_tags(state, username, risk_tag):
    deprecation_warning(DEPRECATION_TEXT)
    _remove_risk_tags(state.sdk, username, risk_tag)


@high_risk_employee.group(
    cls=OrderedGroup,
    help=f"{DEPRECATION_TEXT}\n\nTools for executing high risk employee actions in bulk.",
)
@sdk_options(hidden=True)
def bulk(state):
    pass


HIGH_RISK_EMPLOYEE_CSV_HEADERS = ["username", "cloud_alias", "risk_tag", "notes"]
RISK_TAG_CSV_HEADERS = ["username", "tag"]
REMOVE_EMPLOYEE_HEADERS = ["username"]

high_risk_employee_generate_template = generate_template_cmd_factory(
    group_name="high_risk_employee",
    commands_dict={
        "add": HIGH_RISK_EMPLOYEE_CSV_HEADERS,
        "remove": REMOVE_EMPLOYEE_HEADERS,
        "add-risk-tags": RISK_TAG_CSV_HEADERS,
        "remove-risk-tags": RISK_TAG_CSV_HEADERS,
    },
)
bulk.add_command(high_risk_employee_generate_template)


@bulk.command(
    name="add",
    help=f"{DEPRECATION_TEXT}\n\nBulk add users to the high risk employees detection list using a "
    f"CSV file with format: {','.join(HIGH_RISK_EMPLOYEE_CSV_HEADERS)}.",
)
@read_csv_arg(headers=HIGH_RISK_EMPLOYEE_CSV_HEADERS)
@sdk_options()
def bulk_add(state, csv_rows):
    deprecation_warning(DEPRECATION_TEXT)
    sdk = state.sdk

    def handle_row(username, cloud_alias, risk_tag, notes):
        _add_high_risk_employee(sdk, username, cloud_alias, risk_tag, notes)

    run_bulk_process(
        handle_row,
        csv_rows,
        progress_label="Adding users to high risk employee detection list:",
    )


@bulk.command(
    name="remove",
    help=f"{DEPRECATION_TEXT}\n\nBulk remove users from the high risk employees detection list "
    f"using a CSV file with format {','.join(REMOVE_EMPLOYEE_HEADERS)}.",
)
@read_csv_arg(headers=REMOVE_EMPLOYEE_HEADERS)
@sdk_options()
def bulk_remove(state, csv_rows):
    deprecation_warning(DEPRECATION_TEXT)
    sdk = state.sdk

    def handle_row(username):
        _remove_high_risk_employee(sdk, username)

    run_bulk_process(
        handle_row,
        csv_rows,
        progress_label="Removing users from high risk employee detection list:",
    )


@bulk.command(
    name="add-risk-tags",
    help=f"{DEPRECATION_TEXT}\n\nAdds risk tags to users in bulk using a CSV file with format: "
    f"{','.join(RISK_TAG_CSV_HEADERS)}.",
)
@read_csv_arg(headers=RISK_TAG_CSV_HEADERS)
@sdk_options()
def bulk_add_risk_tags(state, csv_rows):
    deprecation_warning(DEPRECATION_TEXT)
    sdk = state.sdk

    def handle_row(username, tag):
        _add_risk_tags(sdk, username, tag)

    run_bulk_process(
        handle_row,
        csv_rows,
        progress_label="Adding risk tags to users:",
    )


@bulk.command(
    name="remove-risk-tags",
    help=f"{DEPRECATION_TEXT}\n\nRemoves risk tags from users in bulk using a CSV file with "
    f"format: {','.join(RISK_TAG_CSV_HEADERS)}.",
)
@read_csv_arg(headers=RISK_TAG_CSV_HEADERS)
@sdk_options()
def bulk_remove_risk_tags(state, csv_rows):
    deprecation_warning(DEPRECATION_TEXT)
    sdk = state.sdk

    def handle_row(username, tag):
        _remove_risk_tags(sdk, username, tag)

    run_bulk_process(
        handle_row,
        csv_rows,
        progress_label="Removing risk tags from users:",
    )


def _get_high_risk_employees(sdk, filter):
    return sdk.detectionlists.high_risk_employee.get_all(filter)


def _add_high_risk_employee(sdk, username, cloud_alias, risk_tag, notes):
    risk_tag = handle_list_args(risk_tag)
    user_id = get_user_id(sdk, username)
    sdk.detectionlists.high_risk_employee.add(user_id)
    update_user(sdk, username, cloud_alias=cloud_alias, risk_tag=risk_tag, notes=notes)


def _remove_high_risk_employee(sdk, username):
    user_id = get_user_id(sdk, username)
    sdk.detectionlists.high_risk_employee.remove(user_id)
