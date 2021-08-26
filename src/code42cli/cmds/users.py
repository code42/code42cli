import click
from pandas import DataFrame

from code42cli.bulk import generate_template_cmd_factory
from code42cli.bulk import run_bulk_process
from code42cli.click_ext.groups import OrderedGroup
from code42cli.click_ext.options import incompatible_with
from code42cli.errors import Code42CLIError
from code42cli.errors import UserDoesNotExistError
from code42cli.file_readers import read_csv_arg
from code42cli.options import format_option
from code42cli.options import sdk_options
from code42cli.output_formats import DataFrameOutputFormatter
from code42cli.output_formats import OutputFormat
from code42cli.output_formats import OutputFormatter
from code42cli.worker import create_worker_stats


@click.group(cls=OrderedGroup)
@sdk_options(hidden=True)
def users(state):
    """Manage users within your Code42 environment."""
    pass


org_uid_option = click.option(
    "--org-uid",
    help="Limit users to only those in the organization you specify. Note that child orgs are included.",
)
active_option = click.option(
    "--active", is_flag=True, help="Limits results to only active users.", default=None,
)
inactive_option = click.option(
    "--inactive",
    is_flag=True,
    help="Limits results to only deactivated users.",
    cls=incompatible_with("active"),
)


user_uid_option = click.option(
    "--user-id", help="The unique identifier of the user to be modified.", required=True
)

org_id_option = click.option(
    "--org-id",
    help="The identifier for the organization to which the user will be moved.",
    required=True,
)


def role_name_option(help):
    return click.option("--role-name", help=help)


def username_option(help, required=False):
    return click.option("--username", help=help, required=required)


@users.command(name="list")
@org_uid_option
@role_name_option("Limit results to only users having the specified role.")
@active_option
@inactive_option
@format_option
@sdk_options()
def list_users(state, org_uid, role_name, active, inactive, format):
    """List users in your Code42 environment."""
    if inactive:
        active = False
    role_id = _get_role_id(state.sdk, role_name) if role_name else None
    columns = (
        ["userUid", "status", "username", "orgUid"]
        if format == OutputFormat.TABLE
        else None
    )
    df = _get_users_dataframe(state.sdk, columns, org_uid, role_id, active)
    if df.empty:
        click.echo("No results found.")
    else:
        formatter = DataFrameOutputFormatter(format)
        formatter.echo_formatted_dataframe(df)


@users.command()
@username_option("Username of the target user.")
@role_name_option("Name of role to add.")
@sdk_options()
def add_role(state, username, role_name):
    """Add the specified role to the user with the specified username."""
    _add_user_role(state.sdk, username, role_name)


@users.command()
@role_name_option("Name of role to remove.")
@username_option("Username of the target user.")
@sdk_options()
def remove_role(state, username, role_name):
    """Remove the specified role to the user with the specified username."""
    _remove_user_role(state.sdk, role_name, username)


@users.command(name="update")
@user_uid_option
@click.option("--username", help="The new username for the user.")
@click.option("--password", help="The new password for the user.")
@click.option("--email", help="The new email for the user.")
@click.option("--first-name", help="The new first name for the user.")
@click.option("--last-name", help="The new last name for the user.")
@click.option("--notes", help="Notes about this user.")
@click.option(
    "--archive-size-quota", help="The total size (in bytes) allowed for this user."
)
@sdk_options()
def update_user(
    state,
    user_id,
    username,
    email,
    password,
    first_name,
    last_name,
    notes,
    archive_size_quota,
):
    """Update a user with the specified unique identifier."""
    _update_user(
        state.sdk,
        user_id,
        username,
        email,
        password,
        first_name,
        last_name,
        notes,
        archive_size_quota,
    )


_bulk_user_update_headers = [
    "user_id",
    "username",
    "email",
    "password",
    "first_name",
    "last_name",
    "notes",
    "archive_size_quota",
]

_bulk_user_move_headers = ["username", "org_id"]


@users.command(name="move")
@username_option("The username of the user to move.", required=True)
@org_id_option
@sdk_options()
def change_organization(state, username, org_id):
    """Change the organization of the user with the given username
    to the org with the given org ID."""
    _change_organization(state.sdk, username, org_id)


@users.group(cls=OrderedGroup)
@sdk_options(hidden=True)
def bulk(state):
    """Tools for managing users in bulk."""
    pass


users_generate_template = generate_template_cmd_factory(
    group_name="users",
    commands_dict={
        "update": _bulk_user_update_headers,
        "move": _bulk_user_move_headers,
    },
    help_message="Generate the CSV template needed for bulk user commands.",
)
bulk.add_command(users_generate_template)


@bulk.command(
    name="update",
    help="Update a list of users from the provided CSV in format: "
    f"{','.join(_bulk_user_update_headers)}",
)
@read_csv_arg(headers=_bulk_user_update_headers)
@format_option
@sdk_options()
def bulk_update(state, csv_rows, format):
    """Update a list of users from the provided CSV."""

    # Initialize the SDK before starting any bulk processes
    # to prevent multiple instances and having to enter 2fa multiple times.
    sdk = state.sdk

    csv_rows[0]["updated"] = "False"
    formatter = OutputFormatter(format, {key: key for key in csv_rows[0].keys()})
    stats = create_worker_stats(len(csv_rows))

    def handle_row(**row):
        try:
            _update_user(
                sdk, **{key: row[key] for key in row.keys() if key != "updated"}
            )
            row["updated"] = "True"
        except Exception as err:
            row["updated"] = f"False: {err}"
            stats.increment_total_errors()
        return row

    result_rows = run_bulk_process(
        handle_row,
        csv_rows,
        progress_label="Updating users:",
        stats=stats,
        raise_global_error=False,
    )
    formatter.echo_formatted_list(result_rows)


@bulk.command(
    name="move",
    help="Change the organization of the list of users from the provided CSV in format: "
    f"{','.join(_bulk_user_move_headers)}",
)
@read_csv_arg(headers=_bulk_user_move_headers)
@format_option
@sdk_options()
def bulk_move(state, csv_rows, format):
    """Change the organization of the list of users from the provided CSV."""

    # Initialize the SDK before starting any bulk processes
    # to prevent multiple instances and having to enter 2fa multiple times.
    sdk = state.sdk

    csv_rows[0]["moved"] = "False"
    formatter = OutputFormatter(format, {key: key for key in csv_rows[0].keys()})
    stats = create_worker_stats(len(csv_rows))

    def handle_row(**row):
        try:
            _change_organization(
                sdk, **{key: row[key] for key in row.keys() if key != "moved"}
            )
            row["moved"] = "True"
        except Exception as err:
            row["moved"] = f"False: {err}"
            stats.increment_total_errors()
        return row

    result_rows = run_bulk_process(
        handle_row,
        csv_rows,
        progress_label="Moving users:",
        stats=stats,
        raise_global_error=False,
    )
    formatter.echo_formatted_list(result_rows)


def _add_user_role(sdk, username, role_name):
    user_id = _get_user_id(sdk, username)
    _get_role_id(sdk, role_name)  # function provides role name validation
    sdk.users.add_role(user_id, role_name)


def _remove_user_role(sdk, role_name, username):
    user_id = _get_user_id(sdk, username)
    _get_role_id(sdk, role_name)  # function provides role name validation
    sdk.users.remove_role(user_id, role_name)


def _get_user_id(sdk, username):
    if not username:
        # py42 returns all users when passing `None` to `get_by_username()`.
        raise click.BadParameter("Username is required.")
    user = sdk.users.get_by_username(username)["users"]
    if len(user) == 0:
        raise UserDoesNotExistError(username)
    user_id = user[0]["userId"]
    return user_id


def _get_role_id(sdk, role_name):
    try:
        roles_dataframe = DataFrame.from_records(
            sdk.users.get_available_roles().data, index="roleName"
        )
        role_result = roles_dataframe.at[role_name, "roleId"]
        return str(role_result)  # extract the role ID from the series
    except KeyError:
        raise Code42CLIError(f"Role with name '{role_name}' not found.")


def _get_users_dataframe(sdk, columns, org_uid, role_id, active):
    users_generator = sdk.users.get_all(active=active, org_uid=org_uid, role_id=role_id)
    users_list = []
    for page in users_generator:
        users_list.extend(page["users"])

    return DataFrame.from_records(users_list, columns=columns)


def _update_user(
    sdk,
    user_id,
    username,
    email,
    password,
    first_name,
    last_name,
    notes,
    archive_size_quota,
):
    return sdk.users.update_user(
        user_id,
        username=username,
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name,
        notes=notes,
        archive_size_quota_bytes=archive_size_quota,
    )


def _change_organization(sdk, username, org_id):
    user_id = _get_user_id(sdk, username)
    org_id = _get_org_id(sdk, org_id)
    return sdk.users.change_org_assignment(user_id=int(user_id), org_id=int(org_id))


def _get_org_id(sdk, org_id):
    org = sdk.orgs.get_by_uid(org_id)
    return org["orgId"]
