import csv
import click
from pandas import DataFrame

from code42cli.click_ext.groups import OrderedGroup
from code42cli.click_ext.options import incompatible_with
from code42cli.click_ext.types import AutoDecodedFile
from code42cli.bulk import run_bulk_process
from code42cli.errors import Code42CLIError
from code42cli.file_readers import read_csv_arg
from code42cli.options import format_option
from code42cli.options import sdk_options
from code42cli.output_formats import DataFrameOutputFormatter

from py42.constants import WatchlistType


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
    help="Type of watchlist to remove user from. For CUSTOM watchlists, --watchlist-id is required.",
    cls=incompatible_with("watchlist_id"),
)
@format_option
@sdk_options()
def list_users(state, watchlist_type, watchlist_id, format):
    """List all users on a given watchlist."""
    if watchlist_type:
        watchlist_id = state.sdk.watchlists._watchlists_service.watchlist_type_id_map[watchlist_type]
    pages = state.sdk.watchlists.get_all_included_users(watchlist_id)
    dfs = (DataFrame(page["includedUsers"]) for page in pages)
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
    help="Type of watchlist to remove user from. For CUSTOM watchlists, --watchlist-id is required.",
    cls=incompatible_with("watchlist_id"),
)
@click.argument("user", metavar="USER_ID|USERNAME")
@sdk_options()
def add(state, watchlist_id, user):
    try:
        user = int(user)
    except ValueError:
        # assume username if `user` is not an int
        user = state.sdk.userriskprofile.get_by_username(user)["userId"]
    state.sdk.watchlists.add_included_users_by_watchlist_id(user, watchlist_id)


@watchlists.command()
@click.option("--watchlist-id", help="ID of the watchlist.")
@click.option(
    "--watchlist-type",
    type=click.Choice(WatchlistType.choices()),
    help="Type of watchlist to remove user from. For CUSTOM watchlists, --watchlist-id is required.",
    cls=incompatible_with("watchlist_id"),
)
@click.argument("user", metavar="USER_ID|USERNAME")
@sdk_options()
def remove(state, watchlist_id, watchlist_type, user):
    try:
        user = int(user)
    except ValueError:
        # assume username if `user` is not an int
        user = state.sdk.userriskprofile.get_by_username(user)["userId"]
    state.sdk.watchlists.remove_included_users_by_watchlist_id(user, watchlist_id)


@watchlists.group(cls=OrderedGroup)
@sdk_options(hidden=True)
def bulk(state):
    """Tools for executing bulk watchlist actions."""
    pass


@bulk.command(
    name="add",
    help="Bulk add users to watchlists using a CSV file. Requires either a `watchlist_id` or "
         "`watchlist_type` column header to identify the watchlist, and either a `user_id` or "
         "`username` column header to identify the user to add."
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
    if "userId" not in headers and "username" not in headers:
        raise Code42CLIError(
            "CSV requires either a `username` or `userId` "
            "column to identify which users to add to watchlist."
        )
    if "watchlistId" not in headers and "watchlistType" not in headers:
        raise Code42CLIError(
            "CSV requires either a `watchlistId` or `watchlistType` "
            "column to identify which watchlist to add user to."
        )

    sdk = state.sdk

    def handle_row(
        watchlist_id=None,
        watchlist_type=None,
        user_id=None,
        username=None
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
                "missing value for `watchlistId` and `watchlistType` columns."
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
         "`username` header to identify the user to remove."
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
    if "userId" not in headers and "username" not in headers:
        raise Code42CLIError(
            "CSV requires either a `username` or `userId` "
            "column to identify which users to remove from watchlist."
        )
    if "watchlistId" not in headers and "watchlistType" not in headers:
        raise Code42CLIError(
            "CSV requires either a `watchlistId` or `watchlistType` "
            "column to identify which watchlist to remove user from."
        )

    sdk = state.sdk

    def handle_row(watchlistId=None, watchlistType=None, userId=None, username=None):
        if username and not userId:
            userId = sdk.userriskprofile.get_by_username(username)["userId"]
        if watchlistId:
            sdk.watchlists.remove_included_users_by_watchlist_id(userId, watchlistId)
        elif watchlistType:
            sdk.watchlists.remove_included_users_by_watchlist_type(
                userId, watchlistType
            )
        else:
            raise Code42CLIError(
                f"Row for username={username}, userId={userId} "
                "missing value for `watchlistId` and `watchlistType` columns."
            )

    run_bulk_process(
        handle_row,
        list(csv_rows),
        progress_label="Adding users to Watchlists:",
    )
