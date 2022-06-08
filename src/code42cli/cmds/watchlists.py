import csv

import click
from pandas import DataFrame
from py42.constants import WatchlistType
from py42.exceptions import Py42NotFoundError
from py42.exceptions import Py42WatchlistNotFound

from code42cli.bulk import generate_template_cmd_factory
from code42cli.bulk import run_bulk_process
from code42cli.click_ext.groups import OrderedGroup
from code42cli.click_ext.options import incompatible_with
from code42cli.click_ext.types import AutoDecodedFile
from code42cli.errors import Code42CLIError
from code42cli.options import format_option
from code42cli.options import sdk_options
from code42cli.output_formats import DataFrameOutputFormatter


@click.group(cls=OrderedGroup)
@sdk_options(hidden=True)
def watchlists(state):
    """Manage watchlist user memberships."""
    pass


@watchlists.command("list")
@format_option
@sdk_options()
def _list(state, format):
    """List all watchlists."""
    pages = state.sdk.watchlists.get_all()
    dfs = (DataFrame(page["watchlists"]) for page in pages)
    formatter = DataFrameOutputFormatter(format)
    formatter.echo_formatted_dataframes(dfs)


@watchlists.command()
@click.option(
    "--watchlist-id",
    help="ID of the watchlist.",
)
@click.option(
    "--watchlist-type",
    type=click.Choice(WatchlistType.choices()),
    help="Type of watchlist to list.",
    cls=incompatible_with("watchlist_id"),
)
@click.option(
    "--only-included-users",
    help="Restrict results to users explicitly added to watchlist via API or Console. "
    "Users added implicitly via group membership or other dynamic rule will not be listed.",
    is_flag=True,
)
@format_option
@sdk_options()
def list_members(state, watchlist_type, watchlist_id, only_included_users, format):
    """List all members on a given watchlist."""
    if not watchlist_id and not watchlist_type:
        raise click.ClickException("--watchlist-id OR --watchlist-type is required.")
    if watchlist_type:
        watchlist_id = state.sdk.watchlists._watchlists_service.watchlist_type_id_map[
            watchlist_type
        ]
    if only_included_users:
        pages = state.sdk.watchlists.get_all_included_users(watchlist_id)
        dfs = (DataFrame(page["includedUsers"]) for page in pages)
    else:
        pages = state.sdk.watchlists.get_all_watchlist_members(watchlist_id)
        dfs = (DataFrame(page["watchlistMembers"]) for page in pages)
    formatter = DataFrameOutputFormatter(format)
    formatter.echo_formatted_dataframes(dfs)


@watchlists.command()
@click.option(
    "--watchlist-id",
    help="ID of the watchlist.",
)
@click.option(
    "--watchlist-type",
    type=click.Choice(WatchlistType.choices()),
    help="Type of watchlist to add user to.",
    cls=incompatible_with("watchlist_id"),
)
@click.argument("user", metavar="[USER_ID|USERNAME]")
@sdk_options()
def add(state, watchlist_id, watchlist_type, user):
    """Add a user to a watchlist."""
    if not watchlist_id and not watchlist_type:
        raise click.ClickException("--watchlist-id OR --watchlist-type is required.")
    try:
        user = int(user)
    except ValueError:
        # assume username if `user` is not an int
        user = state.sdk.userriskprofile.get_by_username(user)["userId"]
    try:
        if watchlist_id:
            state.sdk.watchlists.add_included_users_by_watchlist_id(user, watchlist_id)
        elif watchlist_type:
            state.sdk.watchlists.add_included_users_by_watchlist_type(
                user, watchlist_type
            )
    except Py42WatchlistNotFound:
        raise
    except Py42NotFoundError:
        raise Code42CLIError(f"User ID {user} not found.")


@watchlists.command()
@click.option("--watchlist-id", help="ID of the watchlist.")
@click.option(
    "--watchlist-type",
    type=click.Choice(WatchlistType.choices()),
    help="Type of watchlist to remove user from.",
    cls=incompatible_with("watchlist_id"),
)
@click.argument("user", metavar="[USER_ID|USERNAME]")
@sdk_options()
def remove(state, watchlist_id, watchlist_type, user):
    """Remove a user from a watchlist."""
    if not watchlist_id and not watchlist_type:
        raise click.ClickException("--watchlist-id OR --watchlist-type is required.")
    try:
        user = int(user)
    except ValueError:
        # assume username if `user` is not an int
        user = state.sdk.userriskprofile.get_by_username(user)["userId"]
    try:
        if watchlist_id:
            state.sdk.watchlists.remove_included_users_by_watchlist_id(
                user, watchlist_id
            )
        elif watchlist_type:
            state.sdk.watchlists.remove_included_users_by_watchlist_type(
                user, watchlist_type
            )
    except Py42WatchlistNotFound:
        raise
    except Py42NotFoundError:
        raise Code42CLIError(f"User ID {user} not found.")


@watchlists.group(cls=OrderedGroup)
@sdk_options(hidden=True)
def bulk(state):
    """Tools for executing bulk watchlist actions."""
    pass


watchlists_generate_template = generate_template_cmd_factory(
    group_name="watchlists",
    commands_dict={
        "add": ["watchlist_id", "watchlist_type", "user_id", "username"],
        "remove": ["watchlist_id", "watchlist_type", "user_id", "username"],
    },
)
bulk.add_command(watchlists_generate_template)


@bulk.command(
    name="add",
    help="Bulk add users to watchlists using a CSV file. Requires either a `watchlist_id` or "
    "`watchlist_type` column header to identify the watchlist, and either a `user_id` or "
    "`username` column header to identify the user to add.",
)
@click.argument(
    "csv_rows",
    metavar="CSV_FILE",
    type=AutoDecodedFile("r"),
    callback=lambda ctx, param, arg: csv.DictReader(arg),
)
@sdk_options()
def bulk_add(state, csv_rows):
    headers = csv_rows.fieldnames
    if "user_id" not in headers and "username" not in headers:
        raise Code42CLIError(
            "CSV requires either a `username` or `user_id` "
            "column to identify which users to add to watchlist."
        )
    if "watchlist_id" not in headers and "watchlist_type" not in headers:
        raise Code42CLIError(
            "CSV requires either a `watchlist_id` or `watchlist_type` "
            "column to identify which watchlist to add user to."
        )

    sdk = state.sdk

    def handle_row(
        watchlist_id=None, watchlist_type=None, user_id=None, username=None, **kwargs
    ):
        if username and not user_id:
            user_id = sdk.userriskprofile.get_by_username(username)["userId"]
        if watchlist_id:
            sdk.watchlists.add_included_users_by_watchlist_id(user_id, watchlist_id)
        elif watchlist_type:
            choices = WatchlistType.choices()
            if watchlist_type not in choices:
                raise Code42CLIError(
                    f"Provided watchlist_type `{watchlist_type}` for username={username}, "
                    f"user_id={user_id} row is invalid. Must be one of: {','.join(choices)}"
                )
            sdk.watchlists.add_included_users_by_watchlist_type(user_id, watchlist_type)
        else:
            raise Code42CLIError(
                f"Row for username={username}, user_id={user_id} "
                "missing value for `watchlist_id` or `watchlist_type` columns."
            )

    run_bulk_process(
        handle_row,
        list(csv_rows),
        progress_label="Adding users to Watchlists:",
    )


@bulk.command(
    name="remove",
    help="Bulk remove users from watchlists using a CSV file. Requires either a `watchlist_id` or "
    "`watchlist_type` column header to identify the watchlist, and either a `user_id` or "
    "`username` header to identify the user to remove.",
)
@click.argument(
    "csv_rows",
    metavar="CSV_FILE",
    type=AutoDecodedFile("r"),
    callback=lambda ctx, param, arg: csv.DictReader(arg),
)
@sdk_options()
def bulk_remove(state, csv_rows):
    headers = csv_rows.fieldnames
    if "user_id" not in headers and "username" not in headers:
        raise Code42CLIError(
            "CSV requires either a `username` or `user_id` "
            "column to identify which users to remove from watchlist."
        )
    if "watchlist_id" not in headers and "watchlist_type" not in headers:
        raise Code42CLIError(
            "CSV requires either a `watchlist_id` or `watchlist_type` "
            "column to identify which watchlist to remove user from."
        )

    sdk = state.sdk

    def handle_row(
        watchlist_id=None, watchlist_type=None, user_id=None, username=None, **kwargs
    ):
        if username and not user_id:
            user_id = sdk.userriskprofile.get_by_username(username)["userId"]
        if watchlist_id:
            sdk.watchlists.remove_included_users_by_watchlist_id(user_id, watchlist_id)
        elif watchlist_type:
            sdk.watchlists.remove_included_users_by_watchlist_type(
                user_id, watchlist_type
            )
        else:
            raise Code42CLIError(
                f"Row for username={username}, user_id={user_id} "
                "missing value for `watchlist_id` or `watchlist_type` columns."
            )

    run_bulk_process(
        handle_row,
        list(csv_rows),
        progress_label="Adding users to Watchlists:",
    )
