import click

from code42cli.date_helper import parse_max_timestamp
from code42cli.date_helper import parse_min_timestamp
from code42cli.options import OrderedGroup
from code42cli.options import sdk_options


filter_option_usernames = click.option(
    "--usernames", required=False, help="Filter results by usernames.", multiple=True,
)
filter_option_user_ids = click.option(
    "--user-ids", required=False, help="Filter results by user ids.", multiple=True,
)

filter_option_user_ip_addresses = click.option(
    "--user-ips",
    required=False,
    help="Filter results by user ip addresses.",
    multiple=True,
)
filter_option_affected_user_ids = click.option(
    "--affected-user-ids",
    required=False,
    help="Filter results by affected user ids.",
    multiple=True,
)
filter_option_affected_usernames = click.option(
    "--affected-usernames",
    required=False,
    help="Filter results by affected usernames.",
    multiple=True,
)
filter_option_event_types = click.option(
    "--event-types",
    required=False,
    help="Filter results by event types.",
    multiple=True,
)

filter_option_begin_time = click.option(
    "-b",
    "--begin",
    required=False,
    callback=lambda ctx, param, arg: parse_min_timestamp(arg),
    help="The beginning of the date range in which to look for audit-logs, can be a date/time in "
    "yyyy-MM-dd (UTC) or yyyy-MM-dd HH:MM:SS (UTC+24-hr time) format where the 'time' "
    "portion of the string can be partial (e.g. '2020-01-01 12' or '2020-01-01 01:15') "
    "or a short value representing days (30d), hours (24h) or minutes (15m) from current "
    "time.",
    default=None,
)

filter_option_end_time = click.option(
    "-e",
    "--end",
    callback=lambda ctx, param, arg: parse_max_timestamp(arg),
    required=False,
    help="The end of the date range in which to look for audit-logs, argument format options are "
    "the same as `--begin`.",
    default=None,
)
format_option = click.option(
    "-f",
    "--format",
    type=click.Choice(["CSV", "CEF", "JSON"]),
    default="JSON",
    help="The output format of the result. Defaults to JSON.",
)


@click.group(cls=OrderedGroup)
@sdk_options(hidden=True)
def audit_logs(state):
    """Retrieve audit logs."""
    pass


@audit_logs.command()
@format_option
@filter_option_begin_time
@filter_option_end_time
@filter_option_event_types
@filter_option_usernames
@filter_option_user_ids
@filter_option_user_ip_addresses
@filter_option_affected_user_ids
@filter_option_affected_usernames
@sdk_options()
def search(
    state,
    format,
    begin,
    end,
    event_types,
    usernames,
    user_ids,
    user_ips,
    affected_user_ids,
    affected_usernames,
):
    _search(
        state.sdk,
        format,
        begin_time=begin,
        end_time=end,
        event_types=event_types,
        usernames=usernames,
        user_ids=user_ids,
        user_ip_addresses=user_ips,
        affected_user_ids=affected_user_ids,
        affected_usernames=affected_usernames,
    )


def _search(sdk, format, **filter_args):

    if format.upper() != "JSON":
        click.echo(sdk.auditlogs.export(format=format, **filter_args))
    else:
        print("here")
        for page in sdk.auditlogs.get_all(**filter_args):
            click.echo(page)
