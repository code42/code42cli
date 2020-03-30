from datetime import datetime, timedelta

from c42eventextractor.common import convert_datetime_to_timestamp
from py42.sdk.queries.fileevents.filters.event_filter import EventTimestamp

_MAX_LOOK_BACK_DAYS = 90
_FORMAT_VALUE_ERROR_MESSAGE = u"input must be a date in YYYY-MM-DD or YYYY-MM-DD HH:MM:SS format."


def create_event_timestamp_filter(begin_date=None, end_date=None):
    """Creates a `py42.sdk.file_event_query.event_query.EventTimestamp` filter using the given dates.
        Returns None if not given a begin_date or an end_date.

        Args:
            begin_date: The begin date for the range.
            end_date: The end date for the range.
    """

    if begin_date and end_date:
        min_timestamp = _parse_min_timestamp(begin_date)
        max_timestamp = _parse_max_timestamp(end_date)
        return _create_in_range_filter(min_timestamp, max_timestamp)
    elif begin_date and not end_date:
        min_timestamp = _parse_min_timestamp(begin_date)
        return _create_on_or_after_filter(min_timestamp)
    elif end_date and not begin_date:
        max_timestamp = _parse_max_timestamp(end_date)
        return _create_on_or_before_filter(max_timestamp)


def _parse_max_timestamp(end_date):
    if len(end_date) == 1:
        end_date = _get_end_date_with_eod_time_if_needed(end_date)
        max_time = _parse_timestamp(end_date)
        max_time = _add_milliseconds(max_time)
    else:
        max_time = _parse_timestamp(end_date)

    return convert_datetime_to_timestamp(max_time)


def _add_milliseconds(max_time):
    return max_time + timedelta(milliseconds=999)


def _create_in_range_filter(min_timestamp, max_timestamp):
    _verify_timestamp_order(min_timestamp, max_timestamp)
    return EventTimestamp.in_range(min_timestamp, max_timestamp)


def _create_on_or_after_filter(min_timestamp):
    return EventTimestamp.on_or_after(min_timestamp)


def _create_on_or_before_filter(max_timestamp):
    return EventTimestamp.on_or_before(max_timestamp)


def _get_end_date_with_eod_time_if_needed(end_date):
    return end_date[0], "23:59:59"


def _parse_min_timestamp(begin_date_str):
    min_time = _parse_timestamp(begin_date_str)
    min_timestamp = convert_datetime_to_timestamp(min_time)
    boundary_date = datetime.utcnow() - timedelta(days=_MAX_LOOK_BACK_DAYS)
    boundary = convert_datetime_to_timestamp(boundary_date)
    if min_timestamp and min_timestamp < boundary:
        raise ValueError(u"'Begin date' must be within 90 days.")
    return min_timestamp


def _verify_timestamp_order(min_timestamp, max_timestamp):
    if min_timestamp is None or max_timestamp is None:
        return
    if min_timestamp >= max_timestamp:
        raise ValueError(u"Begin date cannot be after end date")


def _parse_timestamp(date_and_time):
    try:
        date_str = _join_date_and_time(date_and_time)
        date_format = u"%Y-%m-%d" if len(date_and_time) == 1 else u"%Y-%m-%d %H:%M:%S"
        time = datetime.strptime(date_str, date_format)
        return time
    except ValueError:
        raise ValueError(_FORMAT_VALUE_ERROR_MESSAGE)


def _join_date_and_time(date_and_time):
    if not date_and_time:
        return None
    date_str = date_and_time[0]
    if len(date_and_time) == 1:
        return date_str
    if len(date_and_time) == 2:
        date_str = "{0} {1}".format(date_str, date_and_time[1])
    else:
        raise ValueError(_FORMAT_VALUE_ERROR_MESSAGE)
    return date_str
