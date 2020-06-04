import json

from c42eventextractor import ExtractionHandlers
from py42.sdk.queries.query_filter import QueryFilterTimestampField

import code42cli.errors as errors
from code42cli.date_helper import parse_min_timestamp, parse_max_timestamp, verify_timestamp_order
from code42cli.logger import get_main_cli_logger
from code42cli.cmds.alerts.util import get_alert_details
from code42cli.util import warn_interrupt
from code42cli.cmds.search_shared.args import create_advanced_query_incompatible_search_args

logger = get_main_cli_logger()


def begin_date_is_required(args, cursor_store):
    if not args.incremental:
        return True
    is_required = cursor_store and cursor_store.get_stored_cursor_timestamp() is None

    # Ignore begin date when in incremental mode, it is not required, and it was passed an argument.
    if not is_required and args.begin:
        logger.print_and_log_info(
            u"Ignoring --begin value as --incremental was passed and cursor checkpoint exists.\n"
        )
        args.begin = None
    return is_required


def verify_begin_date_requirements(args, cursor_store):
    if begin_date_is_required(args, cursor_store) and not args.begin:
        logger.print_and_log_error(u"'begin date' is required.\n")
        logger.print_bold(u"Try using  '-b' or '--begin'. Use `-h` for more info.\n")
        exit(1)


def create_handlers(sdk, extractor_class, output_logger, cursor_store):
    extractor = extractor_class(sdk, ExtractionHandlers())
    handlers = ExtractionHandlers()
    handlers.TOTAL_EVENTS = 0

    def handle_error(exception):
        errors.ERRORED = True
        if hasattr(exception, u"response") and hasattr(exception.response, u"text"):
            message = u"{0}: {1}".format(exception, exception.response.text)
        else:
            message = exception
        logger.print_and_log_error(message)

    handlers.handle_error = handle_error

    if cursor_store:
        handlers.record_cursor_position = cursor_store.replace_stored_cursor_timestamp
        handlers.get_cursor_position = cursor_store.get_stored_cursor_timestamp

    @warn_interrupt(
        warning=u"Attempting to cancel cleanly to keep checkpoint data accurate. One moment..."
    )
    def handle_response(response):
        response_dict = json.loads(response.text)
        events = response_dict.get(extractor._key)
        if extractor._key == u"alerts":
            try:
                events = get_alert_details(sdk, events)
            except Exception as ex:
                handlers.handle_error(ex)
        handlers.TOTAL_EVENTS += len(events)
        for event in events:
            output_logger.info(event)
        last_event_timestamp = extractor._get_timestamp_from_item(event)
        handlers.record_cursor_position(last_event_timestamp)

    handlers.handle_response = handle_response
    return handlers


def exit_if_advanced_query_used_with_other_search_args(args, search_arg_enum):
    incompatible_search_args_dict = create_advanced_query_incompatible_search_args()
    incompatible_search_args_list = list(incompatible_search_args_dict.keys())
    invalid_args = incompatible_search_args_list + list(search_arg_enum)
    for arg in invalid_args:
        if args.__dict__[arg]:
            logger.print_and_log_error(
                u"You cannot use --advanced-query with additional search args."
            )
            exit(1)


def create_time_range_filter(filter_cls, begin_date=None, end_date=None):
    """Creates a filter using the given filter class (must be a subclass of 
        :class:`py42.sdk.queries.query_filter.QueryFilterTimestampField`) and date args. Returns 
        `None` if both begin_date and end_date args are `None`.
        
        Args:
            begin_date: The begin date for the range.
            end_date: The end date for the range.
    """
    if not issubclass(filter_cls, QueryFilterTimestampField):
        raise Exception(u"filter_cls must be a subclass of QueryFilterTimestampField")

    if begin_date and end_date:
        min_timestamp = parse_min_timestamp(begin_date)
        max_timestamp = parse_max_timestamp(end_date)
        verify_timestamp_order(min_timestamp, max_timestamp)
        return filter_cls.in_range(min_timestamp, max_timestamp)

    elif begin_date and not end_date:
        min_timestamp = parse_min_timestamp(begin_date)
        return filter_cls.on_or_after(min_timestamp)

    elif end_date and not begin_date:
        max_timestamp = parse_max_timestamp(end_date)
        return filter_cls.on_or_before(max_timestamp)
