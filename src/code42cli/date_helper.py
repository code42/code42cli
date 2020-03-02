from datetime import datetime, timedelta
from c42eventextractor.common import convert_datetime_to_timestamp
from py42.sdk.file_event_query.event_query import EventTimestamp

_DEFAULT_LOOK_BACK_DAYS = 60
_MAX_LOOK_BACK_DAYS = 90


def create_event_timestamp_range(begin_date=None, end_date=None):
    min_timestamp = _parse_min_timestamp(begin_date)
    max_timestamp = _parse_max_timestamp(end_date)
    _verify_timestamp_order(min_timestamp, max_timestamp)
    return EventTimestamp.in_range(min_timestamp, max_timestamp)


def _parse_min_timestamp(begin_date_str):
    if not begin_date_str:
        return _get_default_min_timestamp()
    min_timestamp = _parse_timestamp(begin_date_str)
    boundary_date = datetime.utcnow() - timedelta(days=_MAX_LOOK_BACK_DAYS)
    boundary = convert_datetime_to_timestamp(boundary_date)
    if min_timestamp and min_timestamp < boundary:
        raise ValueError("'Begin date' must be within 90 days.")
    return min_timestamp


def _parse_max_timestamp(end_date_str):
    if not end_date_str:
        return _get_default_max_timestamp()
    return _parse_timestamp(end_date_str)


def _verify_timestamp_order(min_timestamp, max_timestamp):
    if min_timestamp is None or max_timestamp is None:
        return
    if min_timestamp >= max_timestamp:
        raise ValueError("Begin date cannot be after end date")


def _parse_timestamp(date_tuple):
    try:
        if date_tuple and date_tuple[0].isdigit() and len(date_tuple) == 1:
            date_str = date_tuple[0]
            now = datetime.utcnow()
            time = now - timedelta(minutes=int(date_str))
        else:
            date_str = _join_date_tuple(date_tuple)
            date_format = "%Y-%m-%d" if len(date_tuple) == 1 else "%Y-%m-%d %H:%M:%S"
            time = datetime.strptime(date_str, date_format)
    except ValueError:
        raise ValueError(
            "input must be a positive integer or a date in YYYY-MM-DD or YYYY-MM-DD HH:MM:SS format."
        )

    return convert_datetime_to_timestamp(time)


def _join_date_tuple(date_tuple):
    if not date_tuple:
        return None
    if type(date_tuple) is str:
        return date_tuple
    date_str = date_tuple[0]
    if len(date_tuple) == 2:
        date_str = "{0} {1}".format(date_str, date_tuple[1])
    return date_str


def _get_default_min_timestamp():
    now = datetime.utcnow()
    start_day = timedelta(days=_DEFAULT_LOOK_BACK_DAYS)
    days_ago = now - start_day
    return convert_datetime_to_timestamp(days_ago)


def _get_default_max_timestamp():
    return convert_datetime_to_timestamp(datetime.utcnow())
