import re
from datetime import datetime
from datetime import timedelta
from datetime import timezone

import click

TIMESTAMP_REGEX = re.compile(r"(\d{4}-\d{2}-\d{2})\s*(.*)?")
MAGIC_TIME_REGEX = re.compile(r"(\d+)([dhm])$")

_FORMAT_VALUE_ERROR_MESSAGE = (
    "input must be a date/time string (e.g. 'yyyy-MM-dd', "
    "'yy-MM-dd HH:MM', 'yy-MM-dd HH:MM:SS'), or a short value in days, "
    "hours, or minutes (e.g. 30d, 24h, 15m)"
)


def convert_datetime_to_timestamp(dt):
    if dt is None:
        return
    return dt.replace(tzinfo=timezone.utc).timestamp()


def verify_timestamp_order(
    min_timestamp, max_timestamp, min_param=("-b", "--begin"), max_param="--end"
):
    if min_timestamp is None or max_timestamp is None:
        return
    if min_timestamp >= max_timestamp:
        raise click.BadParameter(
            param_hint=min_param, message=f"cannot be after {max_param} date."
        )


def limit_date_range(dt, max_days_back=90, param=None):
    if dt is None:
        return
    now = datetime.utcnow().replace(tzinfo=timezone.utc)
    if now - dt > timedelta(days=max_days_back):
        raise click.BadParameter(
            message="must be within {} days.".format(max_days_back), param=param
        )
    return dt


def round_datetime_to_day_start(dt):
    return dt.replace(hour=0, minute=0, second=0, microsecond=0)


def round_datetime_to_day_end(dt):
    return dt.replace(hour=23, minute=59, second=59, microsecond=999000)
