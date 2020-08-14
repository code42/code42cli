import json

import click
from c42eventextractor import ExtractionHandlers
from click import secho
from py42.sdk.queries.query_filter import QueryFilterTimestampField

import code42cli.errors as errors
from code42cli.date_helper import verify_timestamp_order
from code42cli.logger import get_main_cli_logger
from code42cli.output_formats import get_format_header
from code42cli.util import warn_interrupt

logger = get_main_cli_logger()

_ALERT_DETAIL_BATCH_SIZE = 100
_EVENT_COUNT_PER_PAGE = 10


def _get_alert_details(sdk, alert_summary_list):
    alert_ids = [alert["id"] for alert in alert_summary_list]
    batches = [
        alert_ids[i : i + _ALERT_DETAIL_BATCH_SIZE]
        for i in range(0, len(alert_ids), _ALERT_DETAIL_BATCH_SIZE)
    ]
    results = []
    for batch in batches:
        r = sdk.alerts.get_details(batch)
        results.extend(r["alerts"])
    results = sorted(results, key=lambda x: x["createdAt"], reverse=True)
    return results


def _pager(events, page_size):
    while len(events) > page_size:
        yield events[:page_size]
        del events[:page_size]
    yield events[:]


def create_handlers(
    sdk, extractor_class, cursor_store, checkpoint_name, include_all, output_format
):
    extractor = extractor_class(sdk, ExtractionHandlers())
    handlers = ExtractionHandlers()
    handlers.TOTAL_EVENTS = 0

    def handle_error(exception):
        errors.ERRORED = True
        if hasattr(exception, "response") and hasattr(exception.response, "text"):
            message = "{}: {}".format(exception, exception.response.text)
        else:
            message = exception
        logger.log_error(message)
        secho(str(message), err=True, fg="red")

    handlers.handle_error = handle_error

    if cursor_store:
        handlers.record_cursor_position = lambda value: cursor_store.replace(
            checkpoint_name, value
        )
        handlers.get_cursor_position = lambda: cursor_store.get(checkpoint_name)

    @warn_interrupt(
        warning="Attempting to cancel cleanly to keep checkpoint data accurate. One moment..."
    )
    def handle_response(response):
        response_dict = json.loads(response.text)
        events = response_dict.get(extractor._key)
        if extractor._key == "alerts":
            try:
                events = _get_alert_details(sdk, events)
            except Exception as ex:
                handlers.handle_error(ex)

        total_events = len(events)
        handlers.TOTAL_EVENTS += total_events

        for events_per_page in _pager(events, _EVENT_COUNT_PER_PAGE):
            output = _process_events(output_format, include_all, events_per_page)
            click.echo_via_pager(output)

        if total_events:
            last_event_timestamp = extractor._get_timestamp_from_item(events[-1])
            handlers.record_cursor_position(last_event_timestamp)

    handlers.handle_response = handle_response
    return handlers


def create_time_range_filter(filter_cls, begin_date=None, end_date=None):
    """Creates a filter using the given filter class (must be a subclass of
        :class:`py42.sdk.queries.query_filter.QueryFilterTimestampField`) and date args. Returns
        `None` if both begin_date and end_date args are `None`.

        Args:
            filter_cls: The class of filter to create. (must be a subclass of
              :class:`py42.sdk.queries.query_filter.QueryFilterTimestampField`)
            begin_date: The begin date for the range.
            end_date: The end date for the range.
    """
    if not issubclass(filter_cls, QueryFilterTimestampField):
        raise Exception("filter_cls must be a subclass of QueryFilterTimestampField")

    if begin_date and end_date:
        verify_timestamp_order(begin_date, end_date)
        return filter_cls.in_range(begin_date, end_date)

    elif begin_date and not end_date:
        return filter_cls.on_or_after(begin_date)

    elif end_date and not begin_date:
        return filter_cls.on_or_before(end_date)


def _process_events(output_format, include_all, events):
    format_header = get_format_header(include_all, events[0])
    return output_format(events, format_header)
