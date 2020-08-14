from _collections import OrderedDict

import click
import py42.sdk.queries.alerts.filters as f
from c42eventextractor.extractors import AlertExtractor
from click import echo

import code42cli.cmds.search.enums as enum
import code42cli.cmds.search.extraction as ext
import code42cli.cmds.search.options as searchopt
import code42cli.errors as errors
import code42cli.options as opt
from code42cli.cmds.search.cursor_store import AlertCursorStore
from code42cli.output_formats import extraction_format_option as format_option


SEARCH_DEFAULT_HEADER = OrderedDict()
SEARCH_DEFAULT_HEADER["name"] = "RuleName"
SEARCH_DEFAULT_HEADER["actor"] = "Username"
SEARCH_DEFAULT_HEADER["createdAt"] = "ObservedDate"
SEARCH_DEFAULT_HEADER["state"] = "Status"
SEARCH_DEFAULT_HEADER["severity"] = "Severity"
SEARCH_DEFAULT_HEADER["description"] = "Description"

search_options = searchopt.create_search_options("alerts")


severity_option = click.option(
    "--severity",
    multiple=True,
    type=click.Choice(enum.AlertSeverity()),
    cls=searchopt.AdvancedQueryAndSavedSearchIncompatible,
    callback=searchopt.is_in_filter(f.Severity),
    help="Filter alerts by severity. Defaults to returning all severities.",
)
state_option = click.option(
    "--state",
    multiple=True,
    type=click.Choice(enum.AlertState()),
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
    type=click.Choice(enum.RuleType()),
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


@click.group(cls=opt.OrderedGroup)
@opt.sdk_options(hidden=True)
def alerts(state):
    """Tools for getting alert data."""
    # store cursor getter on the group state so shared --begin option can use it in validation
    state.cursor_getter = _get_alert_cursor_store


@alerts.command()
@click.argument("checkpoint-name")
@opt.sdk_options()
def clear_checkpoint(state, checkpoint_name):
    """Remove the saved alert checkpoint from `--use-checkpoint/-c` mode."""
    _get_alert_cursor_store(state.profile.name).delete(checkpoint_name)


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
    cursor = _get_alert_cursor_store(cli_state.profile.name) if use_checkpoint else None
    handlers = ext.create_handlers(
        cli_state.sdk,
        AlertExtractor,
        cursor,
        use_checkpoint,
        include_all=include_all,
        output_format=format,
        output_header=SEARCH_DEFAULT_HEADER,
    )
    extractor = _get_alert_extractor(cli_state.sdk, handlers)
    extractor.use_or_query = or_query
    if advanced_query:
        extractor.extract_advanced(advanced_query)
    else:
        if begin or end:
            cli_state.search_filters.append(
                ext.create_time_range_filter(f.DateObserved, begin, end)
            )
        extractor.extract(*cli_state.search_filters)
    if handlers.TOTAL_EVENTS == 0 and not errors.ERRORED:
        echo("No results found.")


def _get_alert_extractor(sdk, handlers):
    return AlertExtractor(sdk, handlers)


def _get_alert_cursor_store(profile_name):
    return AlertCursorStore(profile_name)
