import click
from pandas import DataFrame

from code42cli.click_ext.groups import OrderedGroup
from code42cli.click_ext.options import incompatible_with
from code42cli.errors import Code42CLIError
from code42cli.options import format_option
from code42cli.options import sdk_options
from code42cli.output_formats import DataFrameOutputFormatter


@click.group(cls=OrderedGroup)
@sdk_options(hidden=True)
def users(state):
    """Manage users within your Code42 environment"""
    pass


org_uid_option = click.option(
    "--org-uid",
    required=False,
    type=str,
    default=None,
    help="Limit users to only those in the organization you specify. ",
)
role_name_option = click.option(
    "--role-name",
    required=False,
    type=str,
    default=None,
    help="Limit results to only users having the specified role.",
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


@users.command(name="list")
@org_uid_option
@role_name_option
@active_option
@inactive_option
@format_option
@sdk_options()
def list_users(state, org_uid, role_name, active, inactive, format):
    """List users in your Code42 environment."""
    if inactive:
        active = False
    if role_name:
        role_id = _get_role_id(state.sdk, role_name)
    else:
        role_id = None
    df = _get_users_dataframe(state.sdk, org_uid, role_id, active)
    if df.empty:
        click.echo("No results found.")
    else:
        formatter = DataFrameOutputFormatter(format)
        formatter.echo_formatted_dataframe(df)


def _get_role_id(sdk, role_name):
    try:
        roles_dataframe = DataFrame.from_records(sdk.users.get_available_roles().data)
        return str(
            roles_dataframe.loc[
                roles_dataframe["roleName"] == role_name, "roleId"
            ].array[0]
        )
    except KeyError:
        raise Code42CLIError("Role with name {} not found.".format(role_name))


def _get_users_dataframe(sdk, org_uid, role_id, active):
    users_generator = sdk.users.get_all(active=active, org_uid=org_uid, role_id=role_id)
    users_list = []
    for page in users_generator:
        users_list.extend(page["users"])
    return DataFrame.from_records(users_list)
