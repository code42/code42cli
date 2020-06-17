from datetime import datetime, timedelta
import re

from c42eventextractor.common import convert_datetime_to_timestamp

from code42cli.errors import DateArgumentError


TIMESTAMP_REGEX = re.compile(u"(\d{4}-\d{2}-\d{2})\s*(.*)?")
MAGIC_TIME_REGEX = re.compile(u"(\d+)([dhm])$")

_FORMAT_VALUE_ERROR_MESSAGE = (
    u"input must be a date/time string (e.g. 'yyyy-MM-dd', "
    u"'yy-MM-dd HH:MM', 'yy-MM-dd HH:MM:SS'), or a short value in days, "
    u"hours, or minutes (e.g. 30d, 24h, 15m)"
)


def verify_timestamp_order(min_timestamp, max_timestamp):
    if min_timestamp is None or max_timestamp is None:
        return
    if min_timestamp >= max_timestamp:
        raise DateArgumentError(option_name="begin", message="date cannot be after end date.")


def parse_min_timestamp(begin_date_str):
    if begin_date_str is None:
        return
    try:
        dt = _parse_timestamp(begin_date_str, _round_datetime_to_day_start)
    except Exception:
        raise DateArgumentError(option_name="begin", message=_FORMAT_VALUE_ERROR_MESSAGE)
    boundary_date = _round_datetime_to_day_start(datetime.utcnow() - timedelta(days=90))
    if dt < boundary_date:
        raise DateArgumentError(option_name="begin", message="must be within {0} days.".format(90))

    return convert_datetime_to_timestamp(dt)


def parse_max_timestamp(end_date_str):
    if end_date_str is None:
        return
    try:
        dt = _parse_timestamp(end_date_str, _round_datetime_to_day_end)
    except Exception:
        raise DateArgumentError(option_name="end", message=_FORMAT_VALUE_ERROR_MESSAGE)
    return convert_datetime_to_timestamp(dt)


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
        raise
    return dt


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
        raise DateArgumentError()
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
        raise DateArgumentError(u"Couldn't parse magic time string: {}{}".format(num, period))
    return dt


def _round_datetime_to_day_start(dt):
    return dt.replace(hour=0, minute=0, second=0, microsecond=0)


def _round_datetime_to_day_end(dt):
    return dt.replace(hour=23, minute=59, second=59, microsecond=999000)
