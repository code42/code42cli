import click
from pandas import DataFrame

from code42cli.click_ext.groups import OrderedGroup
from code42cli.click_ext.options import incompatible_with
from code42cli.errors import Code42CLIError
from code42cli.errors import UserDoesNotExistError
from code42cli.options import format_option
from code42cli.options import sdk_options
from code42cli.output_formats import DataFrameOutputFormatter
from code42cli.output_formats import OutputFormat


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


def role_name_option(help):
    return click.option("--role-name", help=help)


def username_option(help):
    return click.option("--username", help=help)


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


def _add_user_role(sdk, username, role_name):
    user_id = _get_user_id(sdk, username)
    _get_role_id(sdk, role_name)  # function provides role name validation
    sdk.users.add_role(user_id, role_name)


def _remove_user_role(sdk, role_name, username):
    user_id = _get_user_id(sdk, username)
    _get_role_id(sdk, role_name)  # function provides role name validation
    sdk.users.remove_role(user_id, role_name)


def _get_user_id(sdk, username):
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
