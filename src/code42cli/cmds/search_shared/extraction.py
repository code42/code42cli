import json

from c42eventextractor import ExtractionHandlers
from py42.sdk.queries.query_filter import QueryFilterTimestampField

import code42cli.errors as errors
from code42cli.date_helper import parse_min_timestamp, parse_max_timestamp, verify_timestamp_order
from code42cli.logger import get_main_cli_logger
from code42cli.cmds.alerts_mod.util import get_alert_details
from code42cli.util import warn_interrupt

logger = get_main_cli_logger()

_ALERT_DETAIL_BATCH_SIZE = 100


def _get_alert_details(sdk, alert_summary_list):
    alert_ids = [alert[u"id"] for alert in alert_summary_list]
    batches = [
        alert_ids[i : i + _ALERT_DETAIL_BATCH_SIZE]
        for i in range(0, len(alert_ids), _ALERT_DETAIL_BATCH_SIZE)
    ]
    results = []
    for batch in batches:
        r = sdk.alerts.get_details(batch)
        results.extend(r[u"alerts"])
    results = sorted(results, key=lambda x: x[u"createdAt"], reverse=True)
    return results


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
        if extractor._key == u"alerts_mod":
            try:
                events = _get_alert_details(sdk, events)
            except Exception as ex:
                handlers.handle_error(ex)
        handlers.TOTAL_EVENTS += len(events)
        for event in events:
            output_logger.info(event)
        last_event_timestamp = extractor._get_timestamp_from_item(event)
        handlers.record_cursor_position(last_event_timestamp)

    handlers.handle_response = handle_response
    return handlers


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
        verify_timestamp_order(begin_date, end_date)
        return filter_cls.in_range(begin_date, end_date)

    elif begin_date and not end_date:
        return filter_cls.on_or_after(begin_date)

    elif end_date and not begin_date:
        return filter_cls.on_or_before(end_date)
