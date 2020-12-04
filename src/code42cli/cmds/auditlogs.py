import json
from datetime import datetime
from datetime import timezone
from datetime import timedelta
from _collections import OrderedDict

import click

from code42cli.click_ext.groups import OrderedGroup
from code42cli.cmds.search.cursor_store import AuditLogCursorStore
from code42cli.cmds.search.options import BeginOption
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
from code42cli.util import warn_interrupt

EVENT_KEY = "events"
AUDIT_LOGS_KEYWORD = "audit-logs"
AUDIT_LOG_TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%S.%f"

AUDIT_LOGS_DEFAULT_HEADER = OrderedDict()
AUDIT_LOGS_DEFAULT_HEADER["timestamp"] = "Timestamp"
AUDIT_LOGS_DEFAULT_HEADER["type$"] = "Type"
AUDIT_LOGS_DEFAULT_HEADER["actorName"] = "ActorName"
AUDIT_LOGS_DEFAULT_HEADER["actorIpAddress"] = "ActorIpAddress"
AUDIT_LOGS_DEFAULT_HEADER["userName"] = "AffectedUser"
AUDIT_LOGS_DEFAULT_HEADER["userId"] = "AffectedUserUID"


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
        cls=BeginOption,
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


checkpoint_option = click.option(
    "-c",
    "--use-checkpoint",
    help="Only get audit-log events that were not previously retrieved."
)


@click.group(cls=OrderedGroup)
@sdk_options(hidden=True)
def audit_logs(state):
    """Retrieve audit logs."""
    # store cursor getter on the group state so shared --begin option can use it in validation
    state.cursor_getter = _get_audit_log_cursor_store


@audit_logs.command()
@click.argument("checkpoint-name")
@sdk_options()
def clear_checkpoint(state, checkpoint_name):
    """Remove the saved file event checkpoint from `--use-checkpoint/-c` mode."""
    _get_audit_log_cursor_store(state.profile.name).delete(checkpoint_name)


@audit_logs.command()
@filter_options
@format_option
@checkpoint_option
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
    use_checkpoint,
):
    """Search audit logs."""
    save_checkpoint = None
    if use_checkpoint:
        cursor = _get_audit_log_cursor_store(state.profile.name)
        save_checkpoint = lambda ts: cursor.replace(use_checkpoint, ts)
        begin = cursor.get(use_checkpoint)
    
    _search(
        state.sdk,
        format,
        save_checkpoint,
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
@checkpoint_option
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
    use_checkpoint,
):
    """Send audit logs to the given server address."""
    save_checkpoint = None
    if use_checkpoint:
        cursor = _get_audit_log_cursor_store(state.profile.name)
        save_checkpoint = lambda ts: cursor.replace(use_checkpoint, ts)
        if not begin:
            begin = cursor.get(use_checkpoint)
    
    _send_to(
        state.sdk,
        hostname,
        protocol,
        format,
        save_checkpoint,
        begin_time=begin,
        end_time=end,
        event_types=event_type,
        usernames=username,
        user_ids=user_id,
        user_ip_addresses=user_ip,
        affected_user_ids=affected_user_id,
        affected_usernames=affected_username,
    )


def _search(sdk, format, save_checkpoint, **filter_args):
    formatter = OutputFormatter(format, AUDIT_LOGS_DEFAULT_HEADER)
    response_gen = sdk.auditlogs.get_all(**filter_args)
    events = _get_all_audit_log_events(response_gen)
    event_count = len(events)
    if not event_count:
        click.echo("No results found.")
        return
    elif event_count > 10:
        click.echo_via_pager(formatter.get_formatted_output(events))
    else:
        formatter.echo_formatted_list(events)
    if save_checkpoint:
        ts = _parse_audit_log_timestamp_string_to_timestamp(events[0]["timestamp"])
        save_checkpoint(ts)


def _send_to(sdk, hostname, protocol, format, save_checkpoint, **filter_args):
    logger = get_logger_for_server(hostname, protocol, format)
    with warn_interrupt():
        response_gen = sdk.auditlogs.get_all(**filter_args)
        events = _get_all_audit_log_events(response_gen, sort_descending=False)
        if not events:
            click.echo("No results found.")
            return
        for event in events:
            logger.info(event)
            if save_checkpoint:
                ts = _parse_audit_log_timestamp_string_to_timestamp(event["timestamp"])
                save_checkpoint(ts)


def _get_all_audit_log_events(response_gen, sort_descending=True):
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
    return sorted(events, key=lambda x: x.get("timestamp"), reverse=sort_descending)
    

def _parse_audit_log_timestamp_string_to_timestamp(ts):
    # example: {"property": "bar", "timestamp": "2020-11-23T17:13:26.239647Z"}
    ts = ts[:-1]
    dt = datetime.strptime(ts, AUDIT_LOG_TIMESTAMP_FORMAT).replace(tzinfo=timezone.utc)
    # add one ms so we don't get the last retrieved event again
    dt = dt + timedelta(milliseconds=1)
    return dt.timestamp()


def _get_audit_log_cursor_store(profile_name):
    return AuditLogCursorStore(profile_name)
