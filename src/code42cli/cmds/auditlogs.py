import click

import code42cli.options as opt
from code42cli.click_ext.groups import OrderedGroup
from code42cli.cmds.search import SendToCommand
from code42cli.cmds.search.cursor_store import AuditLogCursorStore
from code42cli.cmds.search.options import server_options
from code42cli.date_helper import convert_datetime_to_timestamp
from code42cli.options import checkpoint_option
from code42cli.options import format_option
from code42cli.options import sdk_options
from code42cli.output_formats import OutputFormatter
from code42cli.util import hash_event
from code42cli.util import parse_timestamp
from code42cli.util import warn_interrupt

EVENT_KEY = "events"
AUDIT_LOGS_KEYWORD = "audit-logs"


def _get_audit_logs_default_header():
    return {
        "timestamp": "Timestamp",
        "type$": "Type",
        "actorName": "ActorName",
        "actorIpAddress": "ActorIpAddress",
        "userName": "AffectedUser",
        "userId": "AffectedUserUID",
    }


begin_option = opt.begin_option(
    AUDIT_LOGS_KEYWORD,
    callback=lambda ctx, param, arg: convert_datetime_to_timestamp(arg),
)
end_option = opt.end_option(
    AUDIT_LOGS_KEYWORD,
    callback=lambda ctx, param, arg: convert_datetime_to_timestamp(arg),
)
filter_option_usernames = click.option(
    "--actor-username",
    required=False,
    help="Filter results by actor usernames.",
    multiple=True,
)
filter_option_user_ids = click.option(
    "--actor-user-id",
    required=False,
    help="Filter results by actor user IDs.",
    multiple=True,
)
filter_option_user_ip_addresses = click.option(
    "--actor-ip",
    required=False,
    help="Filter results by user IP addresses.",
    multiple=True,
)
filter_option_affected_user_ids = click.option(
    "--affected-user-id",
    required=False,
    help="Filter results by affected user IDs.",
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
    help="Filter results by event types (e.g. search_issued, user_registered, user_deactivated).",
    multiple=True,
)


def filter_options(f):
    f = filter_option_event_types(f)
    f = filter_option_usernames(f)
    f = filter_option_user_ids(f)
    f = filter_option_user_ip_addresses(f)
    f = filter_option_affected_user_ids(f)
    f = filter_option_affected_usernames(f)
    f = end_option(f)
    f = begin_option(f)
    return f


@click.group(cls=OrderedGroup)
@sdk_options(hidden=True)
def audit_logs(state):
    """Get and send audit log event data."""
    # store cursor getter on the group state so shared --begin option can use it in validation
    state.cursor_getter = _get_audit_log_cursor_store


@audit_logs.command()
@click.argument("checkpoint-name")
@sdk_options()
def clear_checkpoint(state, checkpoint_name):
    """Remove the saved audit log checkpoint from `--use-checkpoint/-c` mode."""
    _get_audit_log_cursor_store(state.profile.name).delete(checkpoint_name)


@audit_logs.command()
@filter_options
@format_option
@checkpoint_option(AUDIT_LOGS_KEYWORD)
@sdk_options()
def search(
    state,
    begin,
    end,
    event_type,
    actor_username,
    actor_user_id,
    actor_ip,
    affected_user_id,
    affected_username,
    format,
    use_checkpoint,
):
    """Search audit log events."""
    formatter = OutputFormatter(format, _get_audit_logs_default_header())
    cursor = _get_audit_log_cursor_store(state.profile.name)
    if use_checkpoint:
        checkpoint_name = use_checkpoint
        checkpoint = cursor.get(checkpoint_name)
        if checkpoint is not None:
            begin = checkpoint

    events = _get_all_audit_log_events(
        state.sdk,
        begin_time=begin,
        end_time=end,
        event_types=event_type,
        usernames=actor_username,
        user_ids=actor_user_id,
        user_ip_addresses=actor_ip,
        affected_user_ids=affected_user_id,
        affected_usernames=affected_username,
    )

    if use_checkpoint:
        checkpoint_name = use_checkpoint
        events = list(
            _dedupe_checkpointed_events_and_store_updated_checkpoint(
                cursor, checkpoint_name, events
            )
        )

    if not events:
        click.echo("No results found.", err=True)
        return

    formatter.echo_formatted_list(events)


@audit_logs.command(cls=SendToCommand)
@filter_options
@checkpoint_option(AUDIT_LOGS_KEYWORD)
@server_options
@sdk_options()
def send_to(
    state,
    begin,
    end,
    event_type,
    actor_username,
    actor_user_id,
    actor_ip,
    affected_user_id,
    affected_username,
    use_checkpoint,
    **kwargs,
):
    """Send audit log events to the given server address in JSON format.

    HOSTNAME format: address:port where port is optional and defaults to 514.
    """
    cursor = _get_audit_log_cursor_store(state.profile.name)
    if use_checkpoint:
        checkpoint_name = use_checkpoint
        checkpoint = cursor.get(checkpoint_name)
        if checkpoint is not None:
            begin = checkpoint

    events = _get_all_audit_log_events(
        state.sdk,
        begin_time=begin,
        end_time=end,
        event_types=event_type,
        usernames=actor_username,
        user_ids=actor_user_id,
        user_ip_addresses=actor_ip,
        affected_user_ids=affected_user_id,
        affected_usernames=affected_username,
    )
    if use_checkpoint:
        checkpoint_name = use_checkpoint
        events = _dedupe_checkpointed_events_and_store_updated_checkpoint(
            cursor, checkpoint_name, events
        )
    with warn_interrupt():
        event = None
        for event in events:
            state.logger.info(event)
        if event is None:  # generator was empty
            click.echo("No results found.")


def _get_all_audit_log_events(sdk, **filter_args):
    response_gen = sdk.auditlogs.get_all(**filter_args)
    events = []
    try:
        responses = list(response_gen)
    except KeyError:
        # API endpoint (get_page) returns a response without events key when no records are found
        # e.g {"paginationRangeStartIndex": 10000, "paginationRangeEndIndex": 10000, "totalResultCount": 1593}
        # we can remove this check once PL-93211 is resolved and deployed.
        return events

    for response in responses:
        if EVENT_KEY in response.data:
            response_events = response.data.get(EVENT_KEY)
            events.extend(response_events)

    return sorted(events, key=lambda x: x.get("timestamp"))


def _dedupe_checkpointed_events_and_store_updated_checkpoint(
    cursor, checkpoint_name, events
):
    """De-duplicates events across checkpointed runs. Since using the timestamp of the last event
    processed as the `--begin` time of the next run causes the last event to show up again in the
    next results, we hash the last event(s) of each run and store those hashes in the cursor to
    filter out on the next run. It's also possible that two events have the exact same timestamp, so
    `checkpoint_events` needs to be a list of hashes so we can filter out everything that's actually
    been processed.
    """

    checkpoint_events = cursor.get_events(checkpoint_name)
    new_timestamp = None
    new_events = []
    for event in events:
        event_hash = hash_event(event)
        if event_hash not in checkpoint_events:
            if event["timestamp"] != new_timestamp:
                new_timestamp = event["timestamp"]
                new_events.clear()
            new_events.append(event_hash)
            yield event
            ts = parse_timestamp(new_timestamp)
            cursor.replace(checkpoint_name, ts)
            cursor.replace_events(checkpoint_name, new_events)


def _get_audit_log_cursor_store(profile_name):
    return AuditLogCursorStore(profile_name)
