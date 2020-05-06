import code42cli.cmds.shared.enums as enums

from c42eventextractor.extractors import AlertExtractor
from py42.sdk.queries.alerts.filters import (
    Actor,
    AlertState,
    Severity,
    DateObserved,
    Description,
    RuleName,
)
from code42cli.cmds.shared.cursor_store import AlertCursorStore
from code42cli.cmds.shared.extraction import (
    verify_begin_date_requirements,
    create_handlers,
    exit_if_advanced_query_used_with_other_search_args,
    create_time_range_filter,
)
from code42cli.util import print_error, print_to_stderr


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
    handlers = create_handlers(output_logger, store, event_key=u"alerts")
    extractor = AlertExtractor(sdk, handlers)
    if args.advanced_query:
        exit_if_advanced_query_used_with_other_search_args(args)
        extractor.extract_advanced(args.advanced_query)
    else:
        verify_begin_date_requirements(args, store)
        _verify_alert_state(args.state)
        _verify_alert_severity(args.severity)
        filters = _create_alert_filters(args)
        extractor.extract(*filters)
    if handlers.TOTAL_EVENTS == 0:
        print_to_stderr(u"No results found\n")


def _verify_alert_state(alert_state):
    options = list(enums.AlertState())
    if alert_state and alert_state not in options:
        print_error(
            u"'{0}' is not a valid alert state, options are {1}.".format(alert_state, options)
        )
        exit(1)


def _verify_alert_severity(severity):
    if severity is None:
        return
    options = list(enums.AlertSeverity())
    for s in severity:
        if s not in options:
            print_error(u"'{0}' is not a valid alert severity, options are {1}".format(s, options))
            exit(1)


def _create_alert_filters(args):
    filters = []
    alert_timestamp_filter = create_time_range_filter(DateObserved, args.begin, args.end)
    not alert_timestamp_filter or filters.append(alert_timestamp_filter)
    not args.actor_is or filters.append(Actor.is_in(args.actor_is))
    not args.actor_contains or [filters.append(Actor.contains(arg)) for arg in args.actor_contains]
    not args.actor_not or filters.append(Actor.not_in(args.actor_not))
    not args.actor_not_contains or [
        filters.append(Actor.not_contains(arg)) for arg in args.actor_not_contains
    ]
    not args.rule_name_is or filters.append(RuleName.is_in(args.rule_name_is))
    not args.rule_name_contains or [
        filters.append(RuleName.contains(arg)) for arg in args.rule_name_contains
    ]
    not args.rule_name_not or filters.append(RuleName.not_in(args.rule_name_not))
    not args.rule_name_not_contains or [
        filters.append(RuleName.not_contains(arg)) for arg in args.rule_name_not_contains
    ]
    not args.description or filters.append(Description.contains(args.description))
    not args.severity or filters.append(Severity.is_in(args.severity))
    not args.state or filters.append(AlertState.eq(args.state))
    return filters
