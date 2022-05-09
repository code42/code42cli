import functools

import click
from pandas import DataFrame
from pandas import json_normalize
from py42.exceptions import Py42NotFoundError
from py42.exceptions import Py42UserRiskProfileNotFound

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


username_arg = click.argument("username")

org_uid_option = click.option(
    "--org-uid",
    help="Limit users to only those in the organization you specify. Note that child orgs are included.",
)
active_option = click.option(
    "--active",
    is_flag=True,
    help="Limits results to only active users.",
    default=None,
)
inactive_option = click.option(
    "--inactive",
    is_flag=True,
    help="Limits results to only deactivated users.",
    cls=incompatible_with("active"),
)
user_id_option = click.option(
    "--user-id", help="The unique identifier of the user to be modified.", required=True
)
org_id_option = click.option(
    "--org-id",
    help="The unique identifier (UID) for the organization to which the user will be moved.",
    required=True,
)
include_legal_hold_option = click.option(
    "--include-legal-hold-membership",
    default=False,
    is_flag=True,
    help="Include legal hold membership in output.",
)


def role_name_option(help):
    return click.option("--role-name", help=help)


def username_option(help, required=False):
    return click.option("--username", help=help, required=required)


@click.group(cls=OrderedGroup)
@sdk_options(hidden=True)
def users(state):
    """Manage users within your Code42 environment."""
    pass


@users.command(name="list")
@org_uid_option
@role_name_option("Limit results to only users having the specified role.")
@active_option
@inactive_option
@include_legal_hold_option
@click.option(
    "--include-roles", default=False, is_flag=True, help="Include user roles."
)
@format_option
@sdk_options()
def list_users(
    state,
    org_uid,
    role_name,
    active,
    inactive,
    include_legal_hold_membership,
    include_roles,
    format,
):
    """List users in your Code42 environment."""
    if inactive:
        active = False
    role_id = _get_role_id(state.sdk, role_name) if role_name else None
    columns = (
        ["userUid", "status", "username", "orgUid"]
        if format == OutputFormat.TABLE
        else None
    )
    if include_roles and columns:
        columns.append("roles")
    df = _get_users_dataframe(
        state.sdk, columns, org_uid, role_id, active, include_roles
    )
    if include_legal_hold_membership:
        df = _add_legal_hold_membership_to_user_dataframe(state.sdk, df)
    formatter = DataFrameOutputFormatter(format)
    formatter.echo_formatted_dataframes(df)


@users.command("show")
@username_arg
@include_legal_hold_option
@format_option
@sdk_options()
def show_user(state, username, include_legal_hold_membership, format):
    """Show user details."""
    columns = (
        ["userUid", "status", "username", "orgUid", "roles"]
        if format == OutputFormat.TABLE
        else None
    )
    response = state.sdk.users.get_by_username(username, incRoles=True)
    df = DataFrame.from_records(response["users"], columns=columns)
    if include_legal_hold_membership and not df.empty:
        df = _add_legal_hold_membership_to_user_dataframe(state.sdk, df)
    formatter = DataFrameOutputFormatter(format)
    formatter.echo_formatted_dataframes(df)


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
@user_id_option
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


@users.command()
@username_arg
@sdk_options()
def deactivate(state, username):
    """Deactivate a user."""
    sdk = state.sdk
    _deactivate_user(sdk, username)


@users.command()
@username_arg
@sdk_options()
def reactivate(state, username):
    """Reactivate a user."""
    sdk = state.sdk
    _reactivate_user(sdk, username)


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

_bulk_user_roles_headers = ["username", "role_name"]

_bulk_user_alias_headers = ["username", "alias"]

_bulk_user_risk_profile_headers = ["username", "start_date", "end_date", "notes"]

_bulk_user_activation_headers = ["username"]


@users.command(name="move")
@username_option("The username of the user to move.", required=True)
@org_id_option
@sdk_options()
def change_organization(state, username, org_id):
    """Change the organization of the user with the given username
    to the org with the given org UID."""
    _change_organization(state.sdk, username, org_id)


@users.command()
@click.argument("username")
@click.argument("alias")
@sdk_options()
def add_alias(state, username, alias):
    """Add a cloud alias for a given user.

    A cloud alias is the username an employee uses to access cloud services such as Google Drive or Box. Adding a cloud alias allows Incydr to link a user's cloud activity with their Code42 username. Each user has a default cloud alias of their Code42 username. You can add one additional alias."""
    _add_cloud_alias(state.sdk, username, alias)


@users.command()
@click.argument("username")
@click.argument("alias")
@sdk_options()
def remove_alias(state, username, alias):
    """Remove a cloud alias for a given user."""
    _remove_cloud_alias(state.sdk, username, alias)


@users.command()
@click.argument("username")
@click.argument(
    "date", type=click.DateTime(formats=["%Y-%m-%d"]), required=False, metavar="DATE"
)
@click.option("--clear", is_flag=True, help="Clears the current `start_date` value.")
@sdk_options()
def update_start_date(state, username, date, clear):
    """Sets the `start_date` on a User's risk profile (useful for users on the New Hire Watchlist).
    Date format: %Y-%m-%d"""
    if not date and not clear:
        raise Code42CLIError("Must supply DATE argument if --clear is not used.")
    if clear:
        date = ""
    user_id = _get_user(state.sdk, username)["userId"]
    state.sdk.userriskprofile.update(user_id, start_date=date)


@users.command()
@click.argument("username")
@click.argument("date", type=click.DateTime(formats=["%Y-%m-%d"]), required=False)
@click.option("--clear", is_flag=True, help="Clears the current `end_date` value.")
@sdk_options()
def update_departure_date(state, username, date, clear):
    """Sets the `end_date` on a User's risk profile (useful for users on the Departing Watchlist). Date format: %Y-%m-%d"""
    if not date and not clear:
        raise Code42CLIError("Must supply DATE argument if --clear is not used.")
    if clear:
        date = ""
    user_id = _get_user(state.sdk, username)["userId"]
    state.sdk.userriskprofile.update(user_id, end_date=date)


@users.command()
@click.argument("username")
@click.argument("note", required=False)
@click.option("--clear", is_flag=True, help="Clears the current `notes` value.")
@click.option(
    "--append",
    is_flag=True,
    help="Appends provided note to existing note text as a new line.",
)
@sdk_options()
def update_risk_profile_notes(state, username, note, clear, append):
    """Sets the `notes` value of a User's risk profile.

    WARNING: Overwrites any existing note value."""
    if not note and not clear:
        raise Code42CLIError("Must supply NOTE argument if --clear is not used.")
    user = _get_user(state.sdk, username)
    user_id = user["userId"]
    if append and user["notes"]:
        note = user["notes"] + f"\n\n{note}"
    if clear:
        note = ""
    state.sdk.userriskprofile.update(user_id, notes=note)


@users.command()
@click.argument("username")
@sdk_options()
def list_aliases(state, username):
    """List the cloud aliases for a given user.

    Each user has a default cloud alias of their Code42 username with up to one additional alias."""
    user = _get_user(state.sdk, username)
    aliases = user["cloudAliases"]
    if aliases:
        click.echo(aliases)
    else:
        click.echo(f"No cloud aliases for user '{username}' found.")


@users.group(cls=OrderedGroup)
@sdk_options(hidden=True)
def orgs(state):
    """Tools for viewing user orgs."""
    pass


def _get_orgs_header():
    return {
        "orgId": "ID",
        "orgUid": "UID",
        "orgName": "Name",
        "status": "Status",
        "parentOrgId": "Parent ID",
        "parentOrgUid": "Parent UID",
        "type": "Type",
        "classification": "Classification",
        "creationDate": "Creation Date",
        "settings": "Settings",
    }


@orgs.command(name="list")
@format_option
@sdk_options()
def list_orgs(
    state,
    format,
):
    """List all orgs."""
    pages = state.sdk.orgs.get_all()
    formatter = OutputFormatter(format, _get_orgs_header())
    orgs = [org for page in pages for org in page["orgs"]]
    if orgs:
        formatter.echo_formatted_list(orgs)
    else:
        click.echo("No orgs found.")


@orgs.command(name="show")
@click.argument("org-uid")
@format_option
@sdk_options()
def show_org(
    state,
    org_uid,
    format,
):
    """Show org details."""
    formatter = OutputFormatter(format)
    try:
        response = state.sdk.orgs.get_by_uid(org_uid)
        formatter.echo_formatted_list([response.data])
    except Py42NotFoundError:
        raise Code42CLIError(f"Invalid org UID {org_uid}.")


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
        "add-alias": _bulk_user_alias_headers,
        "remove-alias": _bulk_user_alias_headers,
        "update-risk-profile": _bulk_user_risk_profile_headers,
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


@bulk.command(
    name="deactivate",
    help=f"Deactivate a list of users from the provided CSV in format: {','.join(_bulk_user_activation_headers)}",
)
@read_csv_arg(headers=_bulk_user_activation_headers)
@format_option
@sdk_options()
def bulk_deactivate(state, csv_rows, format):
    """Deactivate a list of users."""

    # Initialize the SDK before starting any bulk processes
    # to prevent multiple instances and having to enter 2fa multiple times.
    sdk = state.sdk

    csv_rows[0]["deactivated"] = "False"
    formatter = OutputFormatter(format, {key: key for key in csv_rows[0].keys()})
    stats = create_worker_stats(len(csv_rows))

    def handle_row(**row):
        try:
            _deactivate_user(
                sdk, **{key: row[key] for key in row.keys() if key != "deactivated"}
            )
            row["deactivated"] = "True"
        except Exception as err:
            row["deactivated"] = f"False: {err}"
            stats.increment_total_errors()
        return row

    result_rows = run_bulk_process(
        handle_row,
        csv_rows,
        progress_label="Deactivating users:",
        stats=stats,
        raise_global_error=False,
    )
    formatter.echo_formatted_list(result_rows)


@bulk.command(
    name="reactivate",
    help=f"Reactivate a list of users from the provided CSV in format: {','.join(_bulk_user_activation_headers)}",
)
@read_csv_arg(headers=_bulk_user_activation_headers)
@format_option
@sdk_options()
def bulk_reactivate(state, csv_rows, format):
    """Reactivate a list of users."""

    # Initialize the SDK before starting any bulk processes
    # to prevent multiple instances and having to enter 2fa multiple times.
    sdk = state.sdk

    csv_rows[0]["reactivated"] = "False"
    formatter = OutputFormatter(format, {key: key for key in csv_rows[0].keys()})
    stats = create_worker_stats(len(csv_rows))

    def handle_row(**row):
        try:
            _reactivate_user(
                sdk, **{key: row[key] for key in row.keys() if key != "reactivated"}
            )
            row["reactivated"] = "True"
        except Exception as err:
            row["reactivated"] = f"False: {err}"
            stats.increment_total_errors()
        return row

    result_rows = run_bulk_process(
        handle_row,
        csv_rows,
        progress_label="Reactivating users:",
        stats=stats,
        raise_global_error=False,
    )
    formatter.echo_formatted_list(result_rows)


@bulk.command(
    name="add-roles",
    help=f"Add roles to a list of users from the provided CSV in format: {','.join(_bulk_user_roles_headers)}",
)
@read_csv_arg(headers=_bulk_user_roles_headers)
@format_option
@sdk_options()
def bulk_add_roles(state, csv_rows, format):
    """Bulk add roles to a list of users."""

    # Initialize the SDK before starting any bulk processes
    # to prevent multiple instances and having to enter 2fa multiple times.
    sdk = state.sdk
    status_header = "role added"

    csv_rows[0][status_header] = "False"
    formatter = OutputFormatter(format, {key: key for key in csv_rows[0].keys()})
    stats = create_worker_stats(len(csv_rows))

    def handle_row(**row):
        try:
            _add_user_role(
                sdk, **{key: row[key] for key in row.keys() if key != status_header}
            )
            row[status_header] = "True"
        except Exception as err:
            row[status_header] = f"False: {err}"
            stats.increment_total_errors()
        return row

    result_rows = run_bulk_process(
        handle_row,
        csv_rows,
        progress_label="Adding roles to users:",
        stats=stats,
        raise_global_error=False,
    )
    formatter.echo_formatted_list(result_rows)


@bulk.command(
    name="remove-roles",
    help=f"Remove roles from a list of users from the provided CSV in format: {','.join(_bulk_user_roles_headers)}",
)
@read_csv_arg(headers=_bulk_user_roles_headers)
@format_option
@sdk_options()
def bulk_remove_roles(state, csv_rows, format):
    """Bulk remove roles from a list of users."""

    # Initialize the SDK before starting any bulk processes
    # to prevent multiple instances and having to enter 2fa multiple times.
    sdk = state.sdk
    success_header = "role removed"

    csv_rows[0][success_header] = "False"
    formatter = OutputFormatter(format, {key: key for key in csv_rows[0].keys()})
    stats = create_worker_stats(len(csv_rows))

    def handle_row(**row):
        try:
            _remove_user_role(
                sdk, **{key: row[key] for key in row.keys() if key != success_header}
            )
            row[success_header] = "True"
        except Exception as err:
            row[success_header] = f"False: {err}"
            stats.increment_total_errors()
        return row

    result_rows = run_bulk_process(
        handle_row,
        csv_rows,
        progress_label="Removing roles from users:",
        stats=stats,
        raise_global_error=False,
    )
    formatter.echo_formatted_list(result_rows)


@bulk.command(
    name="add-alias",
    help=f"Add aliases to a list of users from the provided CSV in format: {','.join(_bulk_user_alias_headers)}.\n\nA cloud alias is the username an employee uses to access cloud services such as Google Drive or Box. Adding a cloud alias allows Incydr to link a user's cloud activity with their Code42 username. Each user has a default cloud alias of their Code42 username. You can add one additional alias.",
)
@read_csv_arg(headers=_bulk_user_alias_headers)
@format_option
@sdk_options()
def bulk_add_alias(state, csv_rows, format):
    """Bulk add aliases to users"""

    # Initialize the SDK before starting any bulk processes
    # to prevent multiple instances and having to enter 2fa multiple times.
    sdk = state.sdk
    success_header = "alias added"

    csv_rows[0][success_header] = "False"
    formatter = OutputFormatter(format, {key: key for key in csv_rows[0].keys()})
    stats = create_worker_stats(len(csv_rows))

    def handle_row(**row):
        try:
            _add_cloud_alias(
                sdk, **{key: row[key] for key in row.keys() if key != success_header}
            )
            row[success_header] = "True"
        except Exception as err:
            row[success_header] = f"False: {err}"
            stats.increment_total_errors()
        return row

    result_rows = run_bulk_process(
        handle_row,
        csv_rows,
        progress_label="Adding aliases to users:",
        stats=stats,
        raise_global_error=False,
    )
    formatter.echo_formatted_list(result_rows)


@bulk.command(
    name="remove-alias",
    help=f"Remove aliases from a list of users from the provided CSV in format: {','.join(_bulk_user_alias_headers)}",
)
@read_csv_arg(headers=_bulk_user_alias_headers)
@format_option
@sdk_options()
def bulk_remove_alias(state, csv_rows, format):
    """Bulk remove aliases from users"""

    # Initialize the SDK before starting any bulk processes
    # to prevent multiple instances and having to enter 2fa multiple times.
    sdk = state.sdk
    success_header = "alias removed"

    csv_rows[0][success_header] = "False"
    formatter = OutputFormatter(format, {key: key for key in csv_rows[0].keys()})
    stats = create_worker_stats(len(csv_rows))

    def handle_row(**row):
        try:
            _remove_cloud_alias(
                sdk, **{key: row[key] for key in row.keys() if key != success_header}
            )
            row[success_header] = "True"
        except Exception as err:
            row[success_header] = f"False: {err}"
            stats.increment_total_errors()
        return row

    result_rows = run_bulk_process(
        handle_row,
        csv_rows,
        progress_label="Removing aliases from users:",
        stats=stats,
        raise_global_error=False,
    )
    formatter.echo_formatted_list(result_rows)


@bulk.command(
    name="update-risk-profile",
    help=f"Update user risk profile data from the provided CSV in format: {','.join(_bulk_user_risk_profile_headers)}"
    "\n\nTo clear a value, set column item to the string: 'null'.",
)
@format_option
@read_csv_arg(headers=_bulk_user_risk_profile_headers)
@click.option(
    "--append-notes",
    is_flag=True,
    help="Append provided note value to already existing note on a new line. Defaults to overwrite.",
)
@sdk_options()
def bulk_update_risk_profile(state, csv_rows, format, append_notes):
    """Bulk update User Risk Profile data."""
    sdk = state.sdk

    success_header = "updated_user"
    formatter = OutputFormatter(
        format, {key: key for key in [*csv_rows[0].keys(), success_header]}
    )
    stats = create_worker_stats(len(csv_rows))

    def handle_row(**row):
        try:
            updated_user = _update_userriskprofile(
                sdk, append_notes=append_notes, **row
            )
            row[success_header] = updated_user
        except Exception as err:
            row[success_header] = f"Error: {err}"
            stats.increment_total_errors()
        return row

    result_rows = run_bulk_process(
        handle_row,
        csv_rows,
        progress_label="Updating user risk profile data:",
        stats=stats,
        raise_global_error=False,
    )
    formatter.echo_formatted_list(result_rows)


def _add_user_role(sdk, username, role_name):
    user_id = _get_legacy_user_id(sdk, username)
    _get_role_id(sdk, role_name)  # function provides role name validation
    sdk.users.add_role(user_id, role_name)


def _remove_user_role(sdk, role_name, username):
    user_id = _get_legacy_user_id(sdk, username)
    _get_role_id(sdk, role_name)  # function provides role name validation
    sdk.users.remove_role(user_id, role_name)


def _get_legacy_user_id(sdk, username):
    if not username:
        # py42 returns all users when passing `None` to `get_by_username()`.
        raise click.BadParameter("Username is required.")
    user = sdk.users.get_by_username(username)["users"]
    if len(user) == 0:
        raise UserDoesNotExistError(username)
    user_id = user[0]["userId"]
    return user_id


@functools.lru_cache()
def _get_role_id(sdk, role_name):
    try:
        roles_dataframe = DataFrame.from_records(
            sdk.users.get_available_roles().data, index="roleName"
        )
        role_result = roles_dataframe.at[role_name, "roleId"]
        return str(role_result)  # extract the role ID from the series
    except KeyError:
        raise Code42CLIError(f"Role with name '{role_name}' not found.")


def _get_users_dataframe(sdk, columns, org_uid, role_id, active, include_roles):
    users_generator = sdk.users.get_all(
        active=active, org_uid=org_uid, role_id=role_id, incRoles=include_roles
    )
    users_list = []
    for page in users_generator:
        users_list.extend(page["users"])

    return DataFrame.from_records(users_list, columns=columns)


def _add_legal_hold_membership_to_user_dataframe(sdk, df):
    columns = ["legalHold.legalHoldUid", "legalHold.name", "user.userUid"]

    custodians = list(_get_all_active_hold_memberships(sdk))

    if len(custodians) == 0:
        return df

    legal_hold_member_dataframe = (
        json_normalize(custodians)[columns]
        .groupby(["user.userUid"])
        .agg(",".join)
        .rename(
            {
                "legalHold.legalHoldUid": "legalHoldUid",
                "legalHold.name": "legalHoldName",
            },
            axis=1,
        )
    )
    df = df.merge(
        legal_hold_member_dataframe,
        how="left",
        left_on="userUid",
        right_on="user.userUid",
    )

    return df


def _get_all_active_hold_memberships(sdk):
    for page in sdk.legalhold.get_all_matters(active=True):
        for matter in page["legalHolds"]:
            for _page in sdk.legalhold.get_all_matter_custodians(
                legal_hold_uid=matter["legalHoldUid"], active=True
            ):
                yield from _page["legalHoldMemberships"]


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
    user_id = _get_legacy_user_id(sdk, username)
    org_id = _get_org_id(sdk, org_id)
    return sdk.users.change_org_assignment(user_id=int(user_id), org_id=int(org_id))


def _get_org_id(sdk, org_id):
    org = sdk.orgs.get_by_uid(org_id)
    return org["orgId"]


def _deactivate_user(sdk, username):
    user_id = _get_legacy_user_id(sdk, username)
    sdk.users.deactivate(user_id)


def _reactivate_user(sdk, username):
    user_id = _get_legacy_user_id(sdk, username)
    sdk.users.reactivate(user_id)


def _get_user(sdk, username):
    # use when retrieving the user risk profile information
    try:
        return sdk.userriskprofile.get_by_username(username)
    except Py42UserRiskProfileNotFound:
        raise UserDoesNotExistError(username)


def _add_cloud_alias(sdk, username, alias):
    user = _get_user(sdk, username)
    sdk.userriskprofile.add_cloud_aliases(user["userId"], alias)


def _remove_cloud_alias(sdk, username, alias):
    user = _get_user(sdk, username)
    sdk.userriskprofile.delete_cloud_aliases(user["userId"], alias)


def _update_userriskprofile(
    sdk, append_notes=False, username=None, start_date=None, end_date=None, notes=None
):
    user = _get_user(sdk, username)
    user_id = user["userId"]
    if append_notes and notes != "null":
        notes = user["notes"] + f"\n\n{notes}"

    # py42 interprets empty string as "clear this value" for kwarg values. Since empty CSV columns
    # get parsed as "" we want to have user provide explicit 'null' string to indicate desire to
    # clear instead of just not update value
    start_date = (
        None if start_date == "" else ("" if start_date == "null" else start_date)
    )
    end_date = None if end_date == "" else ("" if end_date == "null" else end_date)
    notes = None if notes == "" else ("" if notes == "null" else notes)

    updated_user = sdk.userriskprofile.update(
        user_id, start_date=start_date, end_date=end_date, notes=notes
    )
    return {
        k: v
        for k, v in updated_user.data.items()
        if k in ["username", "userId", "startDate", "endDate", "notes"]
    }
