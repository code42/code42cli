from c42eventextractor.extractors import AlertExtractor
from py42.sdk.queries.alerts.filters import (
    Actor,
    AlertState,
    Severity,
    DateObserved,
    Description,
    RuleName,
    RuleId,
    RuleType,
)

import code42cli.cmds.search_shared.enums as enums
import code42cli.errors as errors
from code42cli.cmds.search_shared.cursor_store import AlertCursorStore
from code42cli.cmds.search_shared.extraction import (
    verify_begin_date_requirements,
    create_handlers,
    exit_if_advanced_query_used_with_other_search_args,
    create_time_range_filter,
)
from code42cli.logger import get_main_cli_logger

logger = get_main_cli_logger()


def extract(sdk, profile, output_logger, args):
    """Extracts alerts using the given command-line arguments.

        Args:
            sdk (py42.sdk.SDKClient): The py42 sdk.
            profile (Code42Profile): The profile under which to execute this command.
            output_logger (Logger): The logger specified by which subcommand you use. For example,
                print: uses a logger that streams to stdout.
                write-to: uses a logger that logs to a file.
                send-to: uses a logger that sends logs to a server.
            args: Command line args used to build up alert query filters.
    """
    store = AlertCursorStore(profile.name) if args.incremental else None
    handlers = create_handlers(sdk, AlertExtractor, output_logger, store)
    extractor = AlertExtractor(sdk, handlers)
    if args.advanced_query:
        exit_if_advanced_query_used_with_other_search_args(args, enums.AlertFilterArguments())
        extractor.extract_advanced(args.advanced_query)
    else:
        verify_begin_date_requirements(args, store)
        _verify_alert_state(args.state)
        _verify_alert_severity(args.severity)
        filters = _create_alert_filters(args)
        extractor.extract(*filters)
    if handlers.TOTAL_EVENTS == 0 and not errors.ERRORED:
        logger.print_info(u"No results found\n")


def _verify_alert_state(alert_state):
    options = list(enums.AlertState())
    if alert_state and alert_state not in options:
        logger.print_and_log_error(
            u"'{0}' is not a valid alert state, options are {1}.".format(alert_state, options)
        )
        exit(1)


def _verify_alert_severity(severity):
    if severity is None:
        return
    options = list(enums.AlertSeverity())
    for s in severity:
        if s not in options:
            logger.print_and_log_error(
                u"'{0}' is not a valid alert severity, options are {1}".format(s, options)
            )
            exit(1)


def _create_alert_filters(args):
    filters = []
    alert_timestamp_filter = create_time_range_filter(DateObserved, args.begin, args.end)
    not alert_timestamp_filter or filters.append(alert_timestamp_filter)
    not args.actor or filters.append(Actor.is_in(args.actor))
    not args.actor_contains or [filters.append(Actor.contains(arg)) for arg in args.actor_contains]
    not args.exclude_actor or filters.append(Actor.not_in(args.exclude_actor))
    not args.exclude_actor_contains or [
        filters.append(Actor.not_contains(arg)) for arg in args.exclude_actor_contains
    ]
    not args.rule_name or filters.append(RuleName.is_in(args.rule_name))
    not args.exclude_rule_name or filters.append(RuleName.not_in(args.exclude_rule_name))
    not args.rule_id or filters.append(RuleId.is_in(args.rule_id))
    not args.exclude_rule_id or filters.append(RuleId.not_in(args.exclude_rule_id))
    not args.rule_type or filters.append(RuleType.is_in(args.rule_type))
    not args.exclude_rule_type or filters.append(RuleType.not_in(args.exclude_rule_type))
    not args.description or filters.append(Description.contains(args.description))
    not args.severity or filters.append(Severity.is_in(args.severity))
    not args.state or filters.append(AlertState.eq(args.state))
    return filters
