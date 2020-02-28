from datetime import datetime, timedelta
from c42eventextractor.common import convert_datetime_to_timestamp

from code42cli.util import print_error


def parse_timestamps(args):
    min_timestamp = _parse_min_timestamp(args.begin_date) if args.begin_date else None
    max_timestamp = _parse_timestamp(args.end_date) if args.end_date else None
    _verify_timestamp_order(min_timestamp, max_timestamp)
    return min_timestamp, max_timestamp


def _verify_timestamp_order(min_timestamp, max_timestamp):
    if min_timestamp is None or max_timestamp is None:
        return
    if min_timestamp >= max_timestamp:
        print_error("Begin date cannot be after end date")
        exit(1)


def _parse_min_timestamp(begin_date):
    min_timestamp = _parse_timestamp(begin_date)
    boundary_date = datetime.utcnow() - timedelta(days=90)
    boundary = convert_datetime_to_timestamp(boundary_date)
    if min_timestamp and min_timestamp < boundary:
        print("Argument '--begin' must be within 90 days.")
        exit(1)
    return min_timestamp


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

