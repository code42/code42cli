from datetime import datetime, timedelta
import re
import operator

from c42eventextractor.common import convert_datetime_to_timestamp


_FORMAT_VALUE_ERROR_MESSAGE = (
    u"input must be a date in YYYY-MM-DD or YYYY-MM-DD HH:MM:SS format, "
    u"or a short value in days, hours, or minutes (e.g. 30d, 24h, 15m)"
)
TIMESTAMP_REGEX = re.compile(u"(\d{4}-\d{2}-\d{2})\s*(.*)?")
MAGIC_TIME_REGEX = re.compile(u"(\d+)([dhm])$")


class DateArgumentException(Exception):
    def __init__(self, message=_FORMAT_VALUE_ERROR_MESSAGE):
        super(DateArgumentException, self).__init__(message)


def parse_min_timestamp(begin_date_str, max_days_back=90):
    dt = _parse_timestamp(begin_date_str, _round_datetime_to_day_start, operator.sub)

    boundary_date = _round_datetime_to_day_start(datetime.utcnow() - timedelta(days=max_days_back))
    if dt < boundary_date:
        raise DateArgumentException(u"'Begin date' must be within 90 days.")

    return convert_datetime_to_timestamp(dt)


def parse_max_timestamp(end_date_str):
    dt = _parse_timestamp(end_date_str, _round_datetime_to_day_end, operator.sub)
    return convert_datetime_to_timestamp(dt)


def _parse_timestamp(date_str, rounding_func, op):
    timestamp_match = TIMESTAMP_REGEX.match(date_str)
    magic_match = MAGIC_TIME_REGEX.match(date_str)

    if timestamp_match:
        date, time = timestamp_match.groups()
        dt = _get_dt_from_date_time_pair(date, time)
        if not time:
            dt = rounding_func(dt)

    elif magic_match:
        num, period = magic_match.groups()
        dt = _get_dt_from_magic_time_pair(num, period, op)
        if period == u"d":
            dt = rounding_func(dt)

    else:
        raise DateArgumentException()
    return dt


def _get_dt_from_date_time_pair(date, time):
    date_format = u"%Y-%m-%d %H:%M:%S"
    time = time or u"00:00:00"
    date_string = u"{} {}".format(date, time)
    try:
        dt = datetime.strptime(date_string, date_format)
    except ValueError:
        raise DateArgumentException()
    else:
        return dt


def _get_dt_from_magic_time_pair(num, period, op):
    num = int(num)
    if period == u"d":
        td = timedelta(days=num)
    elif period == u"h":
        td = timedelta(hours=num)
    elif period == u"m":
        td = timedelta(minutes=num)
    else:
        raise DateArgumentException(u"Couldn't parse magic time string: {}{}".format(num, period))
    
    return op(datetime.utcnow(), td)


def _round_datetime_to_day_start(dt):
    return dt.replace(hour=0, minute=0, second=0, microsecond=0)


def _round_datetime_to_day_end(dt):
    return dt.replace(hour=23, minute=59, second=59, microsecond=999000)
