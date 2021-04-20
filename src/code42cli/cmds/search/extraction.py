import json

import click
from c42eventextractor import ExtractionHandlers
from click import secho
from py42.sdk.queries.query_filter import QueryFilterTimestampField

import code42cli.errors as errors
from code42cli.date_helper import verify_timestamp_order
from code42cli.logger import get_main_cli_logger
from code42cli.output_formats import OutputFormat
from code42cli.util import warn_interrupt

logger = get_main_cli_logger()

_ALERT_DETAIL_BATCH_SIZE = 100
INTERRUPT_WARNING = (
    "Attempting to cancel cleanly to keep checkpoint data accurate. One moment..."
)


def try_get_default_header(include_all, default_header, output_format):
    """Returns appropriate header based on include-all and output format. If returns None,
    the CLI format option will figure out the header based on the data keys."""
    output_header = None if include_all else default_header
    if output_format != OutputFormat.TABLE and include_all:
        err_text = "--include-all only allowed for Table output format."
        logger.log_error(err_text)
        raise errors.Code42CLIError(err_text)
    return output_header


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


def _set_handlers(cursor_store, checkpoint_name):
    handlers = ExtractionHandlers()
    handlers.TOTAL_EVENTS = 0

    def handle_error(exception):
        if isinstance(exception, OSError):  # let click handle it
            raise

        errors.ERRORED = True
        if hasattr(exception, "response") and hasattr(exception.response, "text"):
            message = "{}: {}".format(exception, exception.response.text)
        else:
            message = exception
        logger.log_error(message)

        message = str(message)
        if not message.lower().startswith("error:"):
            message = f"Error: {message}"

        secho(message, err=True, fg="red")

    handlers.handle_error = handle_error
    if cursor_store:
        handlers.record_cursor_position = lambda value: cursor_store.replace(
            checkpoint_name, value
        )
        handlers.get_cursor_position = lambda: cursor_store.get(checkpoint_name)
    return handlers


def _get_events(sdk, handlers, extractor_key, response):
    response_dict = json.loads(response.text)
    events = response_dict.get(extractor_key)
    if extractor_key == "alerts":
        try:
            events = _get_alert_details(sdk, events)
        except Exception as ex:
            handlers.handle_error(ex)
    return events


def _record_timestamp(extractor, handlers, event):
    last_event_timestamp = extractor._get_timestamp_from_item(event)
    handlers.record_cursor_position(last_event_timestamp)


def create_handlers(
    sdk, extractor_class, cursor_store, checkpoint_name, formatter, force_pager
):
    extractor = extractor_class(sdk, ExtractionHandlers())
    handlers = _set_handlers(cursor_store, checkpoint_name)

    @warn_interrupt(warning=INTERRUPT_WARNING)
    def handle_response(response):
        events = _get_events(sdk, handlers, extractor._key, response)
        total_events = len(events)
        handlers.TOTAL_EVENTS += total_events
        formatter.echo_formatted_list(events, force_pager=force_pager)

        # To make sure the extractor records correct timestamp event when `CTRL-C` is pressed.
        if total_events:
            _record_timestamp(extractor, handlers, events[-1])

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


def create_send_to_handlers(
    sdk, extractor_class, cursor_store, checkpoint_name, logger
):
    extractor = extractor_class(sdk, ExtractionHandlers())
    handlers = _set_handlers(cursor_store, checkpoint_name)

    @warn_interrupt(warning=INTERRUPT_WARNING)
    def handle_response(response):
        events = _get_events(sdk, handlers, extractor._key, response)

        total_events = len(events)
        handlers.TOTAL_EVENTS += total_events

        for event in events:
            logger.info(event)

        # To make sure the extractor records correct timestamp event when `CTRL-C` is pressed.
        if total_events:
            _record_timestamp(extractor, handlers, events[-1])

    handlers.handle_response = handle_response
    return handlers


def handle_no_events(no_events):
    if no_events:
        click.echo("No results found.")
