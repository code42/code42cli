import click
from c42eventextractor.extractors import AlertExtractor
from click import echo
from py42.sdk.queries.alerts.filters import *

import code42cli.errors as errors
from code42cli.cmds.search import logger_factory
from code42cli.cmds.search.cursor_store import AlertCursorStore
from code42cli.cmds.search.enums import (
    AlertOutputFormat,
    AlertSeverity as AlertSeverityOptions,
    AlertState as AlertStateOptions,
    RuleType as RuleTypeOptions,
)
from code42cli.cmds.search.extraction import (
    create_handlers,
    create_time_range_filter,
)
from code42cli.cmds.search.options import (
    create_search_options,
    AdvancedQueryAndSavedSearchIncompatible,
    is_in_filter,
    contains_filter,
    not_contains_filter,
    not_in_filter,
)
from code42cli.options import sdk_options, OrderedGroup

search_options = create_search_options("alerts")

format_option = click.option(
    "-f",
    "--format",
    type=click.Choice(AlertOutputFormat()),
    default=AlertOutputFormat.JSON,
    help="The format used for outputting alerts.",
)
severity_option = click.option(
    "--severity",
    multiple=True,
    type=click.Choice(AlertSeverityOptions()),
    cls=AdvancedQueryAndSavedSearchIncompatible,
    callback=is_in_filter(Severity),
    help="Filter alerts by severity. Defaults to returning all severities.",
)
state_option = click.option(
    "--state",
    multiple=True,
    type=click.Choice(AlertStateOptions()),
    cls=AdvancedQueryAndSavedSearchIncompatible,
    callback=is_in_filter(AlertState),
    help="Filter alerts by state. Defaults to returning all states.",
)
actor_option = click.option(
    "--actor",
    multiple=True,
    cls=AdvancedQueryAndSavedSearchIncompatible,
    callback=is_in_filter(Actor),
    help="Filter alerts by including the given actor(s) who triggered the alert. "
    "Args must match actor username exactly.",
)
actor_contains_option = click.option(
    "--actor-contains",
    multiple=True,
    cls=AdvancedQueryAndSavedSearchIncompatible,
    callback=contains_filter(Actor),
    help="Filter alerts by including actor(s) whose username contains the given string.",
)
exclude_actor_option = click.option(
    "--exclude-actor",
    multiple=True,
    cls=AdvancedQueryAndSavedSearchIncompatible,
    callback=not_in_filter(Actor),
    help="Filter alerts by excluding the given actor(s) who triggered the alert. "
    "Args must match actor username exactly.",
)
exclude_actor_contains_option = click.option(
    "--exclude-actor-contains",
    multiple=True,
    cls=AdvancedQueryAndSavedSearchIncompatible,
    callback=not_contains_filter(Actor),
    help="Filter alerts by excluding actor(s) whose username contains the given string.",
)
rule_name_option = click.option(
    "--rule-name",
    multiple=True,
    cls=AdvancedQueryAndSavedSearchIncompatible,
    callback=is_in_filter(RuleName),
    help="Filter alerts by including the given rule name(s).",
)
exclude_rule_name_option = click.option(
    "--exclude-rule-name",
    multiple=True,
    cls=AdvancedQueryAndSavedSearchIncompatible,
    callback=not_in_filter(RuleName),
    help="Filter alerts by excluding the given rule name(s).",
)
rule_id_option = click.option(
    "--rule-id",
    multiple=True,
    cls=AdvancedQueryAndSavedSearchIncompatible,
    callback=is_in_filter(RuleId),
    help="Filter alerts by including the given rule id(s).",
)
exclude_rule_id_option = click.option(
    "--exclude-rule-id",
    multiple=True,
    cls=AdvancedQueryAndSavedSearchIncompatible,
    callback=not_in_filter(RuleId),
    help="Filter alerts by excluding the given rule id(s).",
)
rule_type_option = click.option(
    "--rule-type",
    multiple=True,
    type=click.Choice(RuleTypeOptions()),
    cls=AdvancedQueryAndSavedSearchIncompatible,
    callback=is_in_filter(RuleType),
    help="Filter alerts by including the given rule type(s).",
)
exclude_rule_type_option = click.option(
    "--exclude-rule-type",
    multiple=True,
    cls=AdvancedQueryAndSavedSearchIncompatible,
    callback=not_in_filter(RuleType),
    help="Filter alerts by excluding the given rule type(s).",
)
description_option = click.option(
    "--description",
    multiple=True,
    cls=AdvancedQueryAndSavedSearchIncompatible,
    callback=contains_filter(Description),
    help="Filter alerts by description. Does fuzzy search by default.",
)


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
    f = format_option(f)
    return f


@click.group(cls=OrderedGroup)
@sdk_options
def alerts(state):
    """Tools for getting alert data."""
    # store cursor getter on the group state so shared --begin option can use it in validation
    state.cursor_getter = _get_alert_cursor_store


@alerts.command()
@click.argument("checkpoint-name")
@sdk_options
def clear_checkpoint(state, checkpoint_name):
    """Remove the saved alert checkpoint from '--use-checkpoint/-c' mode."""
    _get_alert_cursor_store(state.profile.name).delete(checkpoint_name)


@alerts.command()
@alert_options
@search_options
@sdk_options
def search(cli_state, format, begin, end, advanced_query, use_checkpoint, **kwargs):
    """Search for alerts."""
    output_logger = logger_factory.get_logger_for_stdout(format)
    cursor = _get_alert_cursor_store(cli_state.profile.name) if use_checkpoint else None
    handlers = create_handlers(cli_state.sdk, AlertExtractor, output_logger, cursor, use_checkpoint)
    extractor = _get_alert_extractor(cli_state.sdk, handlers)
    if advanced_query:
        extractor.extract_advanced(advanced_query)
    else:
        if begin or end:
            cli_state.search_filters.append(create_time_range_filter(DateObserved, begin, end))
        extractor.extract(*cli_state.search_filters)
    if handlers.TOTAL_EVENTS == 0 and not errors.ERRORED:
        echo("No results found.")


def _get_alert_extractor(sdk, handlers):
    return AlertExtractor(sdk, handlers)


def _get_alert_cursor_store(profile_name):
    return AlertCursorStore(profile_name)
