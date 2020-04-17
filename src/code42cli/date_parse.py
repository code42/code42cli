import re
from datetime import datetime, timedelta

from c42eventextractor.common import convert_datetime_to_timestamp


_MAX_LOOK_BACK_DAYS = 90
_FORMAT_VALUE_ERROR_MESSAGE = u"input must be a date in YYYY-MM-DD or YYYY-MM-DD HH:MM:SS format, or a short value in days, hours, or minutes (30d, 24h, 30m)"

TIMESTAMP_REGEX = re.compile("(\d{4}-\d{2}-\d{2})\s*(.*)?")
MAGIC_TIME_REGEX = re.compile("(\d+)([dhm])$")


def parse_min_timestamp(begin_date_str):
    timestamp_match = TIMESTAMP_REGEX.match(begin_date_str)
    magic_match = MAGIC_TIME_REGEX.match(begin_date_str)

    if timestamp_match:
        date, time = timestamp_match.groups()
        dt = _get_dt_from_date_time_pair(date, time)

    elif magic_match:
        num, period = magic_match.groups()
        dt = _get_dt_from_magic_time_pair(num, period)
        if period == "d":
            dt = _round_datetime_to_day_start(dt)

    else:
        raise ValueError(_FORMAT_VALUE_ERROR_MESSAGE)

    boundary_date = _round_datetime_to_day_start(
        datetime.utcnow() - timedelta(days=_MAX_LOOK_BACK_DAYS)
    )
    if dt < boundary_date:
        raise ValueError(u"'Begin date' must be within 90 days.")

    return convert_datetime_to_timestamp(dt)


def parse_max_timestamp(end_date_str):
    timestamp_match = TIMESTAMP_REGEX.match(end_date_str)
    magic_match = MAGIC_TIME_REGEX.match(end_date_str)

    if timestamp_match:
        date, time = timestamp_match.groups()
        dt = _get_dt_from_date_time_pair(date, time)
        if not time:
            dt = _round_datetime_to_day_end(dt)

    elif magic_match:
        num, period = magic_match.groups()
        dt = _get_dt_from_magic_time_pair(num, period)
        if period == "d":
            dt = _round_datetime_to_day_end(dt)

    else:
        raise ValueError(_FORMAT_VALUE_ERROR_MESSAGE)

    return convert_datetime_to_timestamp(dt)


def _get_dt_from_date_time_pair(date, time):
    date_format = u"%Y-%m-%d %H:%M:%S"
    time = time or u"00:00:00"
    date_string = u"{} {}".format(date, time)
    try:
        dt = datetime.strptime(date_string, date_format)
    except ValueError:
        raise ValueError(_FORMAT_VALUE_ERROR_MESSAGE)
    else:
        return dt


def _get_dt_from_magic_time_pair(num, period):
    num = int(num)
    if period == "d":
        dt = datetime.utcnow() - timedelta(days=num)
    elif period == "h":
        dt = datetime.utcnow() - timedelta(hours=num)
    elif period == "m":
        dt = datetime.utcnow() - timedelta(minutes=num)
    else:
        raise ValueError(u"Couldn't parse magic time string: {}{}".format(num, period))
    return dt


def _verify_timestamp_order(min_timestamp, max_timestamp):
    if min_timestamp is None or max_timestamp is None:
        return
    if min_timestamp >= max_timestamp:
        raise ValueError(u"Begin date cannot be after end date")


def _round_datetime_to_day_start(dt):
    return dt.replace(hour=0, minute=0, second=0, microsecond=0)


def _round_datetime_to_day_end(dt):
    return dt.replace(hour=23, minute=59, second=59, microsecond=999000)
