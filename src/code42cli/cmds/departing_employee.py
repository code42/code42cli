import click
from py42.services.detectionlists.departing_employee import DepartingEmployeeFilters

from code42cli.bulk import generate_template_cmd_factory
from code42cli.bulk import run_bulk_process
from code42cli.click_ext.groups import OrderedGroup
from code42cli.cmds.detectionlists import ALL_FILTER
from code42cli.cmds.detectionlists import get_choices
from code42cli.cmds.detectionlists import handle_filter_choice
from code42cli.cmds.detectionlists import list_employees
from code42cli.cmds.detectionlists import update_user
from code42cli.cmds.detectionlists.options import cloud_alias_option
from code42cli.cmds.detectionlists.options import notes_option
from code42cli.cmds.detectionlists.options import username_arg
from code42cli.cmds.shared import get_user_id
from code42cli.errors import Code42CLIError
from code42cli.file_readers import read_csv_arg
from code42cli.file_readers import read_flat_file_arg
from code42cli.options import format_option
from code42cli.options import sdk_options


def _get_filter_choices():
    filters = DepartingEmployeeFilters.choices()
    return get_choices(filters)


DATE_FORMAT = "%Y-%m-%d"
filter_option = click.option(
    "--filter",
    help="Departing employee filter options. Defaults to {}.".format(ALL_FILTER),
    type=click.Choice(_get_filter_choices()),
    default=ALL_FILTER,
    callback=lambda ctx, param, arg: handle_filter_choice(arg),
)


@click.group(cls=OrderedGroup)
@sdk_options(hidden=True)
def departing_employee(state):
    """Add and remove employees from the Departing Employees detection list."""
    pass


@departing_employee.command("list")
@sdk_options()
@format_option
@filter_option
def _list(state, format, filter):
    """Lists the users on the Departing Employees list."""
    employee_generator = _get_departing_employees(state.sdk, filter)
    list_employees(
        employee_generator, format, {"departureDate": "Departure Date"},
    )


@departing_employee.command()
@username_arg
@click.option(
    "--departure-date",
    help="The date the employee is departing. Format: yyyy-MM-dd.",
    type=click.DateTime(formats=[DATE_FORMAT]),
)
@cloud_alias_option
@notes_option
@sdk_options()
def add(state, username, cloud_alias, departure_date, notes):
    """Add a user to the Departing Employees detection list."""
    _add_departing_employee(state.sdk, username, cloud_alias, departure_date, notes)


@departing_employee.command()
@username_arg
@sdk_options()
def remove(state, username):
    """Remove a user from the Departing Employees detection list."""
    _remove_departing_employee(state.sdk, username)


@departing_employee.group(cls=OrderedGroup)
@sdk_options(hidden=True)
def bulk(state):
    """Tools for executing bulk departing employee actions."""
    pass


DEPARTING_EMPLOYEE_CSV_HEADERS = ["username", "cloud_alias", "departure_date", "notes"]

departing_employee_generate_template = generate_template_cmd_factory(
    group_name="departing_employee",
    commands_dict={"add": DEPARTING_EMPLOYEE_CSV_HEADERS, "remove": "username"},
)
bulk.add_command(departing_employee_generate_template)


@bulk.command(
    name="add",
    help="Bulk add users to the Departing Employees detection list using a CSV file with "
    "format: {}.".format(",".join(DEPARTING_EMPLOYEE_CSV_HEADERS)),
)
@read_csv_arg(headers=DEPARTING_EMPLOYEE_CSV_HEADERS)
@sdk_options()
def bulk_add(state, csv_rows):
    sdk = state.sdk  # Force initialization of py42 to only happen once.

    def handle_row(username, cloud_alias, departure_date, notes):
        if departure_date:
            try:
                departure_date = click.DateTime(formats=[DATE_FORMAT]).convert(
                    departure_date, None, None
                )
            except click.exceptions.BadParameter:
                message = (
                    f"Invalid date {departure_date}, valid date format {DATE_FORMAT}."
                )
                raise Code42CLIError(message)
        _add_departing_employee(sdk, username, cloud_alias, departure_date, notes)

    run_bulk_process(
        handle_row,
        csv_rows,
        progress_label="Adding users to the Departing Employees detection list:",
    )


@bulk.command(
    name="remove",
    help="Bulk remove users from the Departing Employees detection list using a line-separated "
    "file of usernames.",
)
@read_flat_file_arg
@sdk_options()
def bulk_remove(state, file_rows):
    sdk = state.sdk

    def handle_row(username):
        _remove_departing_employee(sdk, username)

    run_bulk_process(
        handle_row,
        file_rows,
        progress_label="Removing users from the Departing Employees detection list:",
    )


def _get_departing_employees(sdk, filter):
    return sdk.detectionlists.departing_employee.get_all(filter)


def _add_departing_employee(sdk, username, cloud_alias, departure_date, notes):
    if departure_date:
        departure_date = departure_date.strftime(DATE_FORMAT)
    user_id = get_user_id(sdk, username)
    sdk.detectionlists.departing_employee.add(user_id, departure_date)
    update_user(sdk, username, cloud_alias=cloud_alias, notes=notes)


def _remove_departing_employee(sdk, username):
    user_id = get_user_id(sdk, username)
    sdk.detectionlists.departing_employee.remove(user_id)
