import re
from datetime import datetime, timedelta

from c42eventextractor.common import convert_datetime_to_timestamp
from py42.sdk.queries.fileevents.filters.event_filter import EventTimestamp

_MAX_LOOK_BACK_DAYS = 90
_FORMAT_VALUE_ERROR_MESSAGE = u"input must be a date/time string (e.g. 'YYYY-MM-DD', 'YY-MM-DD HH:MM', 'YY-MM-DD HH:MM:SS'), or a short value in days, hours, or minutes (e.g. 30d, 24h, 15m)"


class DateArgumentException(Exception):
    def __init__(self, message=_FORMAT_VALUE_ERROR_MESSAGE):
        super(DateArgumentException, self).__init__(message)


TIMESTAMP_REGEX = re.compile(u"(\d{4}-\d{2}-\d{2})\s*(.*)?")
MAGIC_TIME_REGEX = re.compile(u"(\d+)([dhm])$")


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


def _create_in_range_filter(min_timestamp, max_timestamp):
    _verify_timestamp_order(min_timestamp, max_timestamp)
    return EventTimestamp.in_range(min_timestamp, max_timestamp)


def _create_on_or_after_filter(min_timestamp):
    return EventTimestamp.on_or_after(min_timestamp)


def _create_on_or_before_filter(max_timestamp):
    return EventTimestamp.on_or_before(max_timestamp)


def _parse_timestamp(date_str, rounding_func):
    timestamp_match = TIMESTAMP_REGEX.match(date_str)
    magic_match = MAGIC_TIME_REGEX.match(date_str)

    if timestamp_match:
        date, time = timestamp_match.groups()
        dt = _get_dt_from_date_time_pair(date, time)
        if not time:
            dt = rounding_func(dt)

    elif magic_match:
        num, period = magic_match.groups()
        dt = _get_dt_from_magic_time_pair(num, period)
        if period == u"d":
            dt = rounding_func(dt)

    else:
        raise DateArgumentException()
    return dt


def _parse_min_timestamp(begin_date_str):
    dt = _parse_timestamp(begin_date_str, _round_datetime_to_day_start)

    boundary_date = _round_datetime_to_day_start(
        datetime.utcnow() - timedelta(days=_MAX_LOOK_BACK_DAYS)
    )
    if dt < boundary_date:
        raise DateArgumentException(u"'Begin date' must be within 90 days.")

    return convert_datetime_to_timestamp(dt)


def _parse_max_timestamp(end_date_str):
    dt = _parse_timestamp(end_date_str, _round_datetime_to_day_end)
    return convert_datetime_to_timestamp(dt)


def _get_dt_from_date_time_pair(date, time):
    date_format = u"%Y-%m-%d %H:%M:%S"
    if time:
        time = u"{}:{}:{}".format(*time.split(":") + [u"00", u"00"])
    else:
        time = u"00:00:00"
    date_string = u"{} {}".format(date, time)
    try:
        dt = datetime.strptime(date_string, date_format)
    except ValueError:
        raise DateArgumentException()
    else:
        return dt


def _get_dt_from_magic_time_pair(num, period):
    num = int(num)
    if period == u"d":
        dt = datetime.utcnow() - timedelta(days=num)
    elif period == u"h":
        dt = datetime.utcnow() - timedelta(hours=num)
    elif period == u"m":
        dt = datetime.utcnow() - timedelta(minutes=num)
    else:
        raise DateArgumentException(u"Couldn't parse magic time string: {}{}".format(num, period))
    return dt


def _verify_timestamp_order(min_timestamp, max_timestamp):
    if min_timestamp is None or max_timestamp is None:
        return
    if min_timestamp >= max_timestamp:
        raise DateArgumentException(u"Begin date cannot be after end date")


def _round_datetime_to_day_start(dt):
    return dt.replace(hour=0, minute=0, second=0, microsecond=0)


def _round_datetime_to_day_end(dt):
    return dt.replace(hour=23, minute=59, second=59, microsecond=999000)
