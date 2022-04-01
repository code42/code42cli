import click
import py42.sdk.queries.alerts.filters as f
from py42.exceptions import Py42NotFoundError
from py42.sdk.queries.alerts.alert_query import AlertQuery
from py42.sdk.queries.alerts.filters import AlertState
from py42.sdk.queries.alerts.filters import RuleType
from py42.sdk.queries.alerts.filters import Severity
from py42.util import format_dict

import code42cli.cmds.search.options as searchopt
import code42cli.errors as errors
import code42cli.options as opt
from code42cli.bulk import generate_template_cmd_factory
from code42cli.bulk import run_bulk_process
from code42cli.click_ext.groups import OrderedGroup
from code42cli.cmds.search import SendToCommand
from code42cli.cmds.search.cursor_store import AlertCursorStore
from code42cli.cmds.search.options import server_options
from code42cli.cmds.util import convert_to_or_query
from code42cli.cmds.util import create_time_range_filter
from code42cli.cmds.util import try_get_default_header
from code42cli.date_helper import convert_datetime_to_timestamp
from code42cli.date_helper import limit_date_range
from code42cli.enums import JsonOutputFormat
from code42cli.enums import OutputFormat
from code42cli.file_readers import read_csv_arg
from code42cli.options import format_option
from code42cli.output_formats import OutputFormatter
from code42cli.util import hash_event
from code42cli.util import parse_timestamp
from code42cli.util import warn_interrupt

ALERTS_KEYWORD = "alerts"
ALERT_PAGE_SIZE = 25

begin = opt.begin_option(
    ALERTS_KEYWORD,
    callback=lambda ctx, param, arg: convert_datetime_to_timestamp(
        limit_date_range(arg, max_days_back=90)
    ),
)
end = opt.end_option(ALERTS_KEYWORD)
checkpoint = opt.checkpoint_option(ALERTS_KEYWORD)
advanced_query = searchopt.advanced_query_option(ALERTS_KEYWORD)
severity_option = click.option(
    "--severity",
    multiple=True,
    type=click.Choice(Severity.choices()),
    cls=searchopt.AdvancedQueryAndSavedSearchIncompatible,
    callback=searchopt.is_in_filter(f.Severity),
    help="Filter alerts by severity. Defaults to returning all severities.",
)
filter_state_option = click.option(
    "--state",
    multiple=True,
    type=click.Choice(AlertState.choices()),
    cls=searchopt.AdvancedQueryAndSavedSearchIncompatible,
    callback=searchopt.is_in_filter(f.AlertState),
    help="Filter alerts by status. Defaults to returning all statuses.",
)
actor_option = click.option(
    "--actor",
    multiple=True,
    cls=searchopt.AdvancedQueryAndSavedSearchIncompatible,
    callback=searchopt.is_in_filter(f.Actor),
    help="Filter alerts by including the given actor(s) who triggered the alert. "
    "Arguments must match the actor's cloud alias exactly.",
)
actor_contains_option = click.option(
    "--actor-contains",
    multiple=True,
    cls=searchopt.AdvancedQueryAndSavedSearchIncompatible,
    callback=searchopt.contains_filter(f.Actor),
    help="Filter alerts by including actor(s) whose cloud alias contains the given string.",
)
exclude_actor_option = click.option(
    "--exclude-actor",
    multiple=True,
    cls=searchopt.AdvancedQueryAndSavedSearchIncompatible,
    callback=searchopt.not_in_filter(f.Actor),
    help="Filter alerts by excluding the given actor(s) who triggered the alert. "
    "Arguments must match actor's cloud alias exactly.",
)
exclude_actor_contains_option = click.option(
    "--exclude-actor-contains",
    multiple=True,
    cls=searchopt.AdvancedQueryAndSavedSearchIncompatible,
    callback=searchopt.not_contains_filter(f.Actor),
    help="Filter alerts by excluding actor(s) whose cloud alias contains the given string.",
)
rule_name_option = click.option(
    "--rule-name",
    multiple=True,
    cls=searchopt.AdvancedQueryAndSavedSearchIncompatible,
    callback=searchopt.is_in_filter(f.RuleName),
    help="Filter alerts by including the given rule name(s).",
)
exclude_rule_name_option = click.option(
    "--exclude-rule-name",
    multiple=True,
    cls=searchopt.AdvancedQueryAndSavedSearchIncompatible,
    callback=searchopt.not_in_filter(f.RuleName),
    help="Filter alerts by excluding the given rule name(s).",
)
rule_id_option = click.option(
    "--rule-id",
    multiple=True,
    cls=searchopt.AdvancedQueryAndSavedSearchIncompatible,
    callback=searchopt.is_in_filter(f.RuleId),
    help="Filter alerts by including the given rule id(s).",
)
exclude_rule_id_option = click.option(
    "--exclude-rule-id",
    multiple=True,
    cls=searchopt.AdvancedQueryAndSavedSearchIncompatible,
    callback=searchopt.not_in_filter(f.RuleId),
    help="Filter alerts by excluding the given rule id(s).",
)
rule_type_option = click.option(
    "--rule-type",
    multiple=True,
    type=click.Choice(RuleType.choices()),
    cls=searchopt.AdvancedQueryAndSavedSearchIncompatible,
    callback=searchopt.is_in_filter(f.RuleType),
    help="Filter alerts by including the given rule type(s).",
)
exclude_rule_type_option = click.option(
    "--exclude-rule-type",
    multiple=True,
    cls=searchopt.AdvancedQueryAndSavedSearchIncompatible,
    callback=searchopt.not_in_filter(f.RuleType),
    help="Filter alerts by excluding the given rule type(s).",
)
description_option = click.option(
    "--description",
    multiple=True,
    cls=searchopt.AdvancedQueryAndSavedSearchIncompatible,
    callback=searchopt.contains_filter(f.Description),
    help="Filter alerts by description. Does fuzzy search by default.",
)
send_to_format_options = click.option(
    "-f",
    "--format",
    type=click.Choice(JsonOutputFormat(), case_sensitive=False),
    help="The output format of the result. Defaults to json format.",
    default=JsonOutputFormat.RAW,
)
alert_id_arg = click.argument("alert-id")
note_option = click.option("--note", help="A note to attach to the alert.")
update_state_option = click.option(
    "--state",
    help="The state to give to the alert.",
    type=click.Choice(AlertState.choices()),
)


def _get_default_output_header():
    return {
        "id": "Id",
        "name": "RuleName",
        "actor": "Username",
        "createdAt": "ObservedDate",
        "state": "State",
        "severity": "Severity",
        "description": "Description",
    }


def search_options(f):
    f = checkpoint(f)
    f = advanced_query(f)
    f = end(f)
    f = begin(f)
    return f


def filter_options(f):
    f = actor_option(f)
    f = actor_contains_option(f)
    f = exclude_actor_option(f)
    f = exclude_actor_contains_option(f)
    f = rule_name_option(f)
    f = exclude_rule_name_option(f)
    f = rule_id_option(f)
    f = exclude_rule_id_option(f)
    f = rule_type_option(f)
    f = exclude_rule_type_option(f)
    f = description_option(f)
    f = severity_option(f)
    f = filter_state_option(f)
    return f


@click.group(cls=OrderedGroup)
@opt.sdk_options(hidden=True)
def alerts(state):
    """Get and send alert data."""
    # store cursor getter on the group state so shared --begin option can use it in validation
    state.cursor_getter = _get_alert_cursor_store


@alerts.command()
@click.argument("checkpoint-name")
@opt.sdk_options()
def clear_checkpoint(state, checkpoint_name):
    """Remove the saved alert checkpoint from `--use-checkpoint/-c` mode."""
    _get_alert_cursor_store(state.profile.name).delete(checkpoint_name)


@alerts.command()
@filter_options
@search_options
@click.option(
    "--or-query", is_flag=True, cls=searchopt.AdvancedQueryAndSavedSearchIncompatible
)
@opt.sdk_options()
@click.option(
    "--include-all",
    default=False,
    is_flag=True,
    help="Display simple properties of the primary level of the nested response.",
)
@format_option
def search(
    cli_state,
    format,
    begin,
    end,
    advanced_query,
    use_checkpoint,
    or_query,
    include_all,
    **kwargs,
):
    """Search for alerts."""
    output_header = try_get_default_header(
        include_all, _get_default_output_header(), format
    )
    formatter = OutputFormatter(format, output_header)
    cursor = _get_alert_cursor_store(cli_state.profile.name) if use_checkpoint else None
    if use_checkpoint:
        checkpoint_name = use_checkpoint
        checkpoint = cursor.get(checkpoint_name)
        if checkpoint is not None:
            begin = checkpoint

    query = _construct_query(cli_state, begin, end, advanced_query, or_query)
    alerts_gen = cli_state.sdk.alerts.get_all_alert_details(query)

    if use_checkpoint:
        checkpoint_name = use_checkpoint
        # update checkpoint to alertId of last event retrieved
        alerts_gen = _dedupe_checkpointed_events_and_store_updated_checkpoint(
            cursor, checkpoint_name, alerts_gen
        )
    alerts_list = []
    for alert in alerts_gen:
        alerts_list.append(alert)
    if not alerts_list:
        click.echo("No results found.")
        return
    formatter.echo_formatted_list(alerts_list)


def _construct_query(state, begin, end, advanced_query, or_query):

    if advanced_query:
        state.search_filters = advanced_query
    else:
        if begin or end:
            state.search_filters.append(
                create_time_range_filter(f.DateObserved, begin, end)
            )
    if or_query:
        state.search_filters = convert_to_or_query(state.search_filters)
    query = AlertQuery(*state.search_filters)
    query.page_size = ALERT_PAGE_SIZE
    query.sort_direction = "asc"
    query.sort_key = "CreatedAt"
    return query


def _dedupe_checkpointed_events_and_store_updated_checkpoint(
    cursor, checkpoint_name, alerts_gen
):
    """De-duplicates events across checkpointed runs. Since using the timestamp of the last event
    processed as the `--begin` time of the next run causes the last event to show up again in the
    next results, we hash the last event(s) of each run and store those hashes in the cursor to
    filter out on the next run. It's also possible that two events have the exact same timestamp, so
    `checkpoint_events` needs to be a list of hashes so we can filter out everything that's actually
    been processed.
    """

    checkpoint_alerts = cursor.get_alerts(checkpoint_name)
    new_timestamp = None
    new_alerts = []
    for alert in alerts_gen:
        event_hash = hash_event(alert)
        if event_hash not in checkpoint_alerts:
            if alert[f.DateObserved._term] != new_timestamp:
                new_timestamp = alert[f.DateObserved._term]
                new_alerts.clear()
            new_alerts.append(event_hash)
            yield alert
            ts = parse_timestamp(new_timestamp)
            cursor.replace(checkpoint_name, ts)
            cursor.replace_alerts(checkpoint_name, new_alerts)


@alerts.command(cls=SendToCommand)
@filter_options
@search_options
@click.option(
    "--or-query", is_flag=True, cls=searchopt.AdvancedQueryAndSavedSearchIncompatible
)
@opt.sdk_options()
@server_options
@click.option(
    "--include-all",
    default=False,
    is_flag=True,
    help="Display simple properties of the primary level of the nested response.",
)
@send_to_format_options
def send_to(cli_state, begin, end, advanced_query, use_checkpoint, or_query, **kwargs):
    """Send alerts to the given server address.

    HOSTNAME format: address:port where port is optional and defaults to 514.
    """
    cursor = _get_cursor(cli_state, use_checkpoint)

    if use_checkpoint:
        checkpoint_name = use_checkpoint
        checkpoint = cursor.get(checkpoint_name)
        if checkpoint is not None:
            begin = checkpoint

    query = _construct_query(cli_state, begin, end, advanced_query, or_query)
    alerts_gen = cli_state.sdk.alerts.get_all_alert_details(query)

    if use_checkpoint:
        checkpoint_name = use_checkpoint
        alerts_gen = _dedupe_checkpointed_events_and_store_updated_checkpoint(
            cursor, checkpoint_name, alerts_gen
        )
    with warn_interrupt():
        alert = None
        for alert in alerts_gen:
            cli_state.logger.info(alert)
        if alert is None:  # generator was empty
            click.echo("No results found.")


def _get_cursor(state, use_checkpoint):
    return _get_alert_cursor_store(state.profile.name) if use_checkpoint else None


def _get_alert_cursor_store(profile_name):
    return AlertCursorStore(profile_name)


@alerts.command()
@opt.sdk_options()
@alert_id_arg
@click.option(
    "--include-observations", is_flag=True, help="View observations of the alert."
)
def show(state, alert_id, include_observations):
    """Display the details of a single alert."""
    formatter = OutputFormatter(OutputFormat.TABLE, _get_default_output_header())

    try:
        response = state.sdk.alerts.get_details(alert_id)
    except Py42NotFoundError:
        raise errors.Code42CLIError(f"No alert found with ID '{alert_id}'.")

    alert = response["alerts"][0]
    formatter.echo_formatted_list([alert])

    # Show note details
    note = alert.get("note")
    if note:
        click.echo("\nNote:\n")
        click.echo(format_dict(note))

    if include_observations:
        observations = alert.get("observations")
        if observations:
            click.echo("\nObservations:\n")
            click.echo(format_dict(observations))
        else:
            click.echo("\nNo observations found.")


@alerts.command()
@opt.sdk_options()
@alert_id_arg
@update_state_option
@note_option
def update(cli_state, alert_id, state, note):
    """Update alert information."""
    _update_alert(cli_state.sdk, alert_id, state, note)


@alerts.group(cls=OrderedGroup)
@opt.sdk_options(hidden=True)
def bulk(state):
    """Tools for executing bulk alert actions."""
    pass


UPDATE_ALERT_CSV_HEADERS = ["id", "state", "note"]
update_alerts_generate_template = generate_template_cmd_factory(
    group_name=ALERTS_KEYWORD,
    commands_dict={"update": UPDATE_ALERT_CSV_HEADERS},
    help_message="Generate the CSV template needed for bulk alert commands.",
)
bulk.add_command(update_alerts_generate_template)


@bulk.command(
    name="update",
    help=f"Bulk update alerts using a CSV file with format: {','.join(UPDATE_ALERT_CSV_HEADERS)}",
)
@opt.sdk_options()
@read_csv_arg(headers=UPDATE_ALERT_CSV_HEADERS)
def bulk_update(cli_state, csv_rows):
    """Bulk update alerts."""
    sdk = cli_state.sdk

    def handle_row(id, state, note):
        _update_alert(sdk, id, state, note)

    run_bulk_process(
        handle_row,
        csv_rows,
        progress_label="Updating alerts:",
    )


def _update_alert(sdk, alert_id, alert_state, note):
    if alert_state:
        sdk.alerts.update_state(alert_state, [alert_id], note=note)
    elif note:
        sdk.alerts.update_note(alert_id, note)
