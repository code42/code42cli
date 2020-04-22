from py42.sdk.queries.fileevents.filters.event_filter import EventTimestamp

from code42cli.date_helper import DateArgumentException, parse_min_timestamp, parse_max_timestamp


def create_event_timestamp_filter(begin_date=None, end_date=None):
    """Creates a `py42.sdk.file_event_query.event_query.EventTimestamp` filter using the given dates.
        Returns None if not given a begin_date or an end_date.
        Args:
            begin_date: The begin date for the range.
            end_date: The end date for the range.
    """
    if begin_date and end_date:
        min_timestamp = parse_min_timestamp(begin_date)
        max_timestamp = parse_max_timestamp(end_date)
        return _create_in_range_filter(min_timestamp, max_timestamp)

    elif begin_date and not end_date:
        min_timestamp = parse_min_timestamp(begin_date)
        return _create_on_or_after_filter(min_timestamp)

    elif end_date and not begin_date:
        max_timestamp = parse_max_timestamp(end_date)
        return _create_on_or_before_filter(max_timestamp)


def _create_in_range_filter(min_timestamp, max_timestamp):
    _verify_timestamp_order(min_timestamp, max_timestamp)
    return EventTimestamp.in_range(min_timestamp, max_timestamp)


def _verify_timestamp_order(min_timestamp, max_timestamp):
    if min_timestamp is None or max_timestamp is None:
        return
    if min_timestamp >= max_timestamp:
        raise DateArgumentException(u"Begin date cannot be after end date")


def _create_on_or_after_filter(min_timestamp):
    return EventTimestamp.on_or_after(min_timestamp)


def _create_on_or_before_filter(max_timestamp):
    return EventTimestamp.on_or_before(max_timestamp)
