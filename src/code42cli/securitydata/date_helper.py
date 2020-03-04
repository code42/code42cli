from datetime import datetime, timedelta
from c42eventextractor.common import convert_datetime_to_timestamp
from py42.sdk.file_event_query.event_query import EventTimestamp

_DEFAULT_LOOK_BACK_DAYS = 60
_MAX_LOOK_BACK_DAYS = 90
_FORMAT_VALUE_ERROR_MESSAGE = u"input must be a date in YYYY-MM-DD or YYYY-MM-DD HH:MM:SS format."


def create_event_timestamp_range(begin_date, end_date=None):
    """Creates a `py42.sdk.file_event_query.event_query.EventTimestamp.in_range` filter
            using the provided dates.  If begin_date is None, it uses a date that is 60 days back.
            If end_date is None, it uses the current UTC time.

        Args:
            begin_date: The begin date for the range. If None, defaults to 60 days back from the current UTC time.
            end_date: The end date for the range. If None, defaults to the current time.

    """
    end_date = _get_end_date_with_eod_time_if_needed(end_date)
    min_timestamp = _parse_min_timestamp(begin_date)
    max_timestamp = _parse_max_timestamp(end_date)
    _verify_timestamp_order(min_timestamp, max_timestamp)
    return EventTimestamp.in_range(min_timestamp, max_timestamp)


def _get_end_date_with_eod_time_if_needed(end_date):
    if end_date and len(end_date) == 1:
        return end_date[0], "23:59:59"
    return end_date


def _parse_min_timestamp(begin_date_str):
    min_timestamp = _parse_timestamp(begin_date_str)
    boundary_date = datetime.utcnow() - timedelta(days=_MAX_LOOK_BACK_DAYS)
    boundary = convert_datetime_to_timestamp(boundary_date)
    if min_timestamp and min_timestamp < boundary:
        raise ValueError(u"'Begin date' must be within 90 days.")
    return min_timestamp


def _parse_max_timestamp(end_date_str):
    if not end_date_str:
        return _get_default_max_timestamp()
    return _parse_timestamp(end_date_str)


def _verify_timestamp_order(min_timestamp, max_timestamp):
    if min_timestamp is None or max_timestamp is None:
        return
    if min_timestamp >= max_timestamp:
        raise ValueError(u"Begin date cannot be after end date")


def _parse_timestamp(date_tuple):
    try:
        date_str = _join_date_tuple(date_tuple)
        date_format = u"%Y-%m-%d" if len(date_tuple) == 1 else u"%Y-%m-%d %H:%M:%S"
        time = datetime.strptime(date_str, date_format)
    except ValueError:
        raise ValueError(_FORMAT_VALUE_ERROR_MESSAGE)
    return convert_datetime_to_timestamp(time)


def _join_date_tuple(date_tuple):
    if not date_tuple:
        return None
    date_str = date_tuple[0]
    if len(date_tuple) == 1:
        return date_str
    if len(date_tuple) == 2:
        date_str = "{0} {1}".format(date_str, date_tuple[1])
    else:
        raise ValueError(_FORMAT_VALUE_ERROR_MESSAGE)
    return date_str


def _get_default_max_timestamp():
    return convert_datetime_to_timestamp(datetime.utcnow())
