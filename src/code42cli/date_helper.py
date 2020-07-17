import re
from datetime import datetime
from datetime import timedelta

import click
from c42eventextractor.common import convert_datetime_to_timestamp

TIMESTAMP_REGEX = re.compile(r"(\d{4}-\d{2}-\d{2})\s*(.*)?")
MAGIC_TIME_REGEX = re.compile(r"(\d+)([dhm])$")

_FORMAT_VALUE_ERROR_MESSAGE = (
    "input must be a date/time string (e.g. 'yyyy-MM-dd', "
    "'yy-MM-dd HH:MM', 'yy-MM-dd HH:MM:SS'), or a short value in days, "
    "hours, or minutes (e.g. 30d, 24h, 15m)"
)


def verify_timestamp_order(min_timestamp, max_timestamp):
    if min_timestamp is None or max_timestamp is None:
        return
    if min_timestamp >= max_timestamp:
        raise click.BadParameter(
            param_hint=["-b", "--begin"], message="cannot be after --end date."
        )


def parse_min_timestamp(begin_date_str, max_days_back=90):
    if begin_date_str is None:
        return
    dt = _parse_timestamp(begin_date_str, _round_datetime_to_day_start)
    boundary_date = _round_datetime_to_day_start(
        datetime.utcnow() - timedelta(days=max_days_back)
    )
    if dt < boundary_date:
        raise click.BadParameter(
            message="must be within {} days.".format(max_days_back)
        )
    return convert_datetime_to_timestamp(dt)


def parse_max_timestamp(end_date_str):
    if end_date_str is None:
        return
    dt = _parse_timestamp(end_date_str, _round_datetime_to_day_end)
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
        if period == "d":
            dt = rounding_func(dt)

    else:
        raise click.BadParameter(message=_FORMAT_VALUE_ERROR_MESSAGE)
    return dt


def _get_dt_from_date_time_pair(date, time):
    date_format = "%Y-%m-%d %H:%M:%S"
    if time:
        time = "{}:{}:{}".format(*time.split(":") + ["00", "00"])
    else:
        time = "00:00:00"
    date_string = "{} {}".format(date, time)
    try:
        dt = datetime.strptime(date_string, date_format)
    except ValueError:
        raise click.ClickException("Unable to parse date string.")
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
        raise click.ClickException(
            "Couldn't parse magic time string: {}{}".format(num, period)
        )
    return dt


def _round_datetime_to_day_start(dt):
    return dt.replace(hour=0, minute=0, second=0, microsecond=0)


def _round_datetime_to_day_end(dt):
    return dt.replace(hour=23, minute=59, second=59, microsecond=999000)
