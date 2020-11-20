import json
from _collections import OrderedDict

import click

from code42cli.click_ext.groups import OrderedGroup
from code42cli.cmds.search.extraction import create_simple_send_to_handler
from code42cli.date_helper import parse_max_timestamp
from code42cli.date_helper import parse_min_timestamp
from code42cli.logger import get_logger_for_server
from code42cli.options import begin_option
from code42cli.options import end_option
from code42cli.options import format_option
from code42cli.options import sdk_options
from code42cli.options import send_to_format_options
from code42cli.options import server_options
from code42cli.output_formats import OutputFormatter


EVENT_KEY = "events"
AUDIT_LOGS_KEYWORD = "audit-logs"

AUDIT_LOGS_DEFAULT_HEADER = OrderedDict()
AUDIT_LOGS_DEFAULT_HEADER["timestamp"] = "Timestamp"
AUDIT_LOGS_DEFAULT_HEADER["type"] = "Type"
AUDIT_LOGS_DEFAULT_HEADER["actorName"] = "ActorName"
AUDIT_LOGS_DEFAULT_HEADER["actorIpAddress"] = "ActorIpAddress"
AUDIT_LOGS_DEFAULT_HEADER["success"] = "Success"
AUDIT_LOGS_DEFAULT_HEADER["resultCount"] = "ResultCount"

filter_option_usernames = click.option(
    "--username", required=False, help="Filter results by usernames.", multiple=True,
)
filter_option_user_ids = click.option(
    "--user-id", required=False, help="Filter results by user ids.", multiple=True,
)

filter_option_user_ip_addresses = click.option(
    "--user-ip",
    required=False,
    help="Filter results by user ip addresses.",
    multiple=True,
)
filter_option_affected_user_ids = click.option(
    "--affected-user-id",
    required=False,
    help="Filter results by affected user ids.",
    multiple=True,
)
filter_option_affected_usernames = click.option(
    "--affected-username",
    required=False,
    help="Filter results by affected usernames.",
    multiple=True,
)
filter_option_event_types = click.option(
    "--event-type",
    required=False,
    help="Filter results by event types.",
    multiple=True,
)


def filter_options(f):
    f = begin_option(
        f,
        AUDIT_LOGS_KEYWORD,
        callback=lambda ctx, param, arg: parse_min_timestamp(arg),
        required=True,
    )
    f = end_option(
        f, AUDIT_LOGS_KEYWORD, callback=lambda ctx, param, arg: parse_max_timestamp(arg)
    )
    f = filter_option_event_types(f)
    f = filter_option_usernames(f)
    f = filter_option_user_ids(f)
    f = filter_option_user_ip_addresses(f)
    f = filter_option_affected_user_ids(f)
    f = filter_option_affected_usernames(f)
    return f


@click.group(cls=OrderedGroup)
@sdk_options(hidden=True)
def audit_logs(state):
    """Retrieve audit logs."""
    pass


@audit_logs.command()
@filter_options
@format_option
@sdk_options()
def search(
    state,
    begin,
    end,
    event_type,
    username,
    user_id,
    user_ip,
    affected_user_id,
    affected_username,
    format,
):
    """Search audit logs."""
    _search(
        state.sdk,
        format,
        begin_time=begin,
        end_time=end,
        event_types=event_type,
        usernames=username,
        user_ids=user_id,
        user_ip_addresses=user_ip,
        affected_user_ids=affected_user_id,
        affected_usernames=affected_username,
    )


@audit_logs.command()
@filter_options
@server_options
@send_to_format_options
@sdk_options()
def send_to(
    state,
    hostname,
    protocol,
    format,
    begin,
    end,
    event_type,
    username,
    user_id,
    user_ip,
    affected_user_id,
    affected_username,
):
    """Send audit logs to given server address."""
    _send_to(
        state.sdk,
        hostname,
        protocol,
        format,
        begin_time=begin,
        end_time=end,
        event_types=event_type,
        usernames=username,
        user_ids=user_id,
        user_ip_addresses=user_ip,
        affected_user_ids=affected_user_id,
        affected_usernames=affected_username,
    )


def _search(sdk, format, **filter_args):

    formatter = OutputFormatter(format, AUDIT_LOGS_DEFAULT_HEADER)
    response_gen = sdk.auditlogs.get_all(**filter_args)

    events = []
    try:
        for response in response_gen:
            response_dict = json.loads(response.text)
            if EVENT_KEY in response_dict:
                events.extend(response_dict.get(EVENT_KEY))
    except KeyError:
        # API endpoint (get_page) returns a response without events key when no records are found
        # e.g {"paginationRangeStartIndex": 10000, "paginationRangeEndIndex": 10000, "totalResultCount": 1593}
        pass

    event_count = len(events)
    if not event_count:
        click.echo("No results found.")
    elif event_count > 10:
        click.echo_via_pager(formatter.get_formatted_output(events))
    else:
        formatter.echo_formatted_list(events)


def _send_to(sdk, hostname, protocol, format, **filter_args):
    logger = get_logger_for_server(hostname, protocol, format)
    response_handler = create_simple_send_to_handler(
        logger, sdk.auditlogs.get_all, EVENT_KEY, **filter_args
    )
    response_handler()
