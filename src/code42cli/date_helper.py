from datetime import datetime, timedelta
from c42eventextractor.common import convert_datetime_to_timestamp
from py42.sdk.file_event_query.event_query import EventTimestamp

_DEFAULT_LOOK_BACK_DAYS = 60


def create_event_timestamp_range(begin_date_str=None, end_date_str=None):
    min_timestamp = _parse_min_timestamp(begin_date_str)
    max_timestamp = _parse_max_timestamp(end_date_str)
    _verify_timestamp_order(min_timestamp, max_timestamp)
    return EventTimestamp.in_range(min_timestamp, max_timestamp)


def _parse_min_timestamp(begin_date_str):
    if begin_date_str is None:
        return _get_default_min_timestamp()
    min_timestamp = _parse_timestamp(begin_date_str)
    boundary_date = datetime.utcnow() - timedelta(days=90)
    boundary = convert_datetime_to_timestamp(boundary_date)
    if min_timestamp and min_timestamp < boundary:
        raise ValueError("'Begin date' must be within 90 days.")
    return min_timestamp


def _parse_max_timestamp(end_date_str):
    if end_date_str is None:
        return _get_default_max_timestamp()
    return _parse_timestamp(end_date_str)


def _verify_timestamp_order(min_timestamp, max_timestamp):
    if min_timestamp is None or max_timestamp is None:
        return
    if min_timestamp >= max_timestamp:
        raise ValueError("Begin date cannot be after end date")


def _parse_timestamp(date_str):
    try:
        # Input represents date str like '2020-02-13'
        time = datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        # Input represents amount of seconds ago like '86400'
        if date_str and date_str.isdigit():
            now = datetime.utcnow()
            time = now - timedelta(minutes=int(date_str))
        else:
            raise ValueError("input must be a positive integer or a date in YYYY-MM-DD format.")

    return convert_datetime_to_timestamp(time)


def _get_default_min_timestamp():
    now = datetime.utcnow()
    start_day = timedelta(days=_DEFAULT_LOOK_BACK_DAYS)
    days_ago = now - start_day
    return convert_datetime_to_timestamp(days_ago)


def _get_default_max_timestamp():
    return convert_datetime_to_timestamp(datetime.utcnow())
