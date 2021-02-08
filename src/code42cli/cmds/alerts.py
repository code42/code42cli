import click
import py42.sdk.queries.alerts.filters as f
from c42eventextractor.extractors import AlertExtractor
from py42.sdk.queries.alerts.filters import AlertState
from py42.sdk.queries.alerts.filters import RuleType
from py42.sdk.queries.alerts.filters import Severity

import code42cli.click_ext.groups
import code42cli.cmds.search.extraction as ext
import code42cli.cmds.search.options as searchopt
import code42cli.errors as errors
import code42cli.options as opt
from code42cli.cmds.search import SendToCommand
from code42cli.cmds.search.cursor_store import AlertCursorStore
from code42cli.cmds.search.extraction import handle_no_events
from code42cli.cmds.search.options import server_options
from code42cli.date_helper import convert_datetime_to_timestamp
from code42cli.date_helper import limit_date_range
from code42cli.options import format_option
from code42cli.output_formats import JsonOutputFormat
from code42cli.output_formats import OutputFormatter


ALERTS_KEYWORD = "alerts"
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
state_option = click.option(
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


def _get_search_default_header():
    return {
        "name": "RuleName",
        "actor": "Username",
        "createdAt": "ObservedDate",
        "state": "Status",
        "severity": "Severity",
        "description": "Description",
    }


def search_options(f):
    f = checkpoint(f)
    f = advanced_query(f)
    f = end(f)
    f = begin(f)
    return f


def alert_options(f):
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
    f = state_option(f)
    return f


@click.group(cls=code42cli.click_ext.groups.OrderedGroup)
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


def _call_extractor(
    cli_state, handlers, begin, end, or_query, advanced_query, **kwargs
):
    extractor = _get_alert_extractor(cli_state.sdk, handlers)
    extractor.use_or_query = or_query
    if advanced_query:
        cli_state.search_filters = advanced_query
    if begin or end:
        cli_state.search_filters.append(
            ext.create_time_range_filter(f.DateObserved, begin, end)
        )
    extractor.extract(*cli_state.search_filters)


@alerts.command()
@alert_options
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
    **kwargs
):
    """Search for alerts."""
    output_header = ext.try_get_default_header(
        include_all, _get_search_default_header(), format
    )
    formatter = OutputFormatter(format, output_header)
    cursor = _get_alert_cursor_store(cli_state.profile.name) if use_checkpoint else None
    handlers = ext.create_handlers(
        cli_state.sdk,
        AlertExtractor,
        cursor,
        use_checkpoint,
        formatter=formatter,
        force_pager=include_all,
    )
    _call_extractor(cli_state, handlers, begin, end, or_query, advanced_query, **kwargs)
    handle_no_events(not handlers.TOTAL_EVENTS and not errors.ERRORED)


@alerts.command(cls=SendToCommand)
@alert_options
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
    handlers = ext.create_send_to_handlers(
        cli_state.sdk, AlertExtractor, cursor, use_checkpoint, cli_state.logger,
    )
    _call_extractor(cli_state, handlers, begin, end, or_query, advanced_query, **kwargs)
    handle_no_events(not handlers.TOTAL_EVENTS and not errors.ERRORED)


def _get_cursor(state, use_checkpoint):
    return _get_alert_cursor_store(state.profile.name) if use_checkpoint else None


def _get_alert_extractor(sdk, handlers):
    return AlertExtractor(sdk, handlers)


def _get_alert_cursor_store(profile_name):
    return AlertCursorStore(profile_name)
