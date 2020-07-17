from datetime import datetime

from c42eventextractor.common import convert_datetime_to_timestamp

from .conftest import begin_date_str
from .conftest import begin_date_str_with_time
from .conftest import end_date_str
from .conftest import end_date_str_with_time
from .conftest import get_test_date
from code42cli.date_helper import parse_max_timestamp
from code42cli.date_helper import parse_min_timestamp


def test_parse_min_timestamp_when_given_date_str_parses_successfully():
    actual = parse_min_timestamp(begin_date_str)
    expected = convert_datetime_to_timestamp(
        datetime.strptime(begin_date_str, "%Y-%m-%d")
    )
    assert actual == expected


def test_parse_min_timestamp_when_given_date_str_with_time_parses_successfully():
    actual = parse_min_timestamp(begin_date_str_with_time)
    expected = convert_datetime_to_timestamp(
        datetime.strptime(begin_date_str_with_time, "%Y-%m-%d %H:%M:%S")
    )
    assert actual == expected


def test_parse_min_timestamp_when_given_magic_days_parses_successfully():
    actual_date = datetime.utcfromtimestamp(parse_min_timestamp("20d"))
    expected_date = datetime.utcfromtimestamp(
        convert_datetime_to_timestamp(get_test_date(days_ago=20))
    )
    expected_date = expected_date.replace(hour=0, minute=0, second=0, microsecond=0)
    assert actual_date == expected_date


def test_parse_min_timestamp_when_given_magic_hours_parses_successfully():
    actual = parse_min_timestamp("20h")
    expected = convert_datetime_to_timestamp(get_test_date(hours_ago=20))
    assert expected - actual < 0.01


def test_parse_min_timestamp_when_given_magic_minutes_parses_successfully():
    actual = parse_min_timestamp("20m")
    expected = convert_datetime_to_timestamp(get_test_date(minutes_ago=20))
    assert expected - actual < 0.01


def test_parse_max_timestamp_when_given_date_str_parses_successfully():
    actual = parse_min_timestamp(end_date_str)
    expected = convert_datetime_to_timestamp(
        datetime.strptime(end_date_str, "%Y-%m-%d")
    )
    assert actual == expected


def test_parse_max_timestamp_when_given_date_str_with_time_parses_successfully():
    actual = parse_min_timestamp(end_date_str_with_time)
    expected = convert_datetime_to_timestamp(
        datetime.strptime(end_date_str_with_time, "%Y-%m-%d %H:%M:%S")
    )
    assert actual == expected


def test_parse_max_timestamp_when_given_magic_days_parses_successfully():
    actual_date = datetime.utcfromtimestamp(parse_max_timestamp("20d"))
    expected_date = datetime.utcfromtimestamp(
        convert_datetime_to_timestamp(get_test_date(days_ago=20))
    )
    expected_date = expected_date.replace(
        hour=23, minute=59, second=59, microsecond=999000
    )
    assert actual_date == expected_date


def test_parse_max_timestamp_when_given_magic_hours_parses_successfully():
    actual = parse_max_timestamp("20h")
    expected = convert_datetime_to_timestamp(get_test_date(hours_ago=20))
    assert expected - actual < 0.01


def test_parse_magic_minutes_parses_successfully():
    actual = parse_max_timestamp("20m")
    expected = convert_datetime_to_timestamp(get_test_date(minutes_ago=20))
    assert expected - actual < 0.01
