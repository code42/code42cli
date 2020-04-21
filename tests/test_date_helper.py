import pytest
from datetime import datetime

from c42eventextractor.common import convert_datetime_to_timestamp

from code42cli.date_helper import parse_min_timestamp, parse_max_timestamp
from .conftest import (
    begin_date_str,
    begin_date_str_with_time,
    end_date_str,
    end_date_str_with_time,
    get_test_date,
)


def test_parse_min_timestamp_when_given_date_str_parses_successfully():
    ts = parse_min_timestamp(begin_date_str)
    assert ts == 1579737600.0


def test_parse_min_timestamp_when_given_date_str_with_time_parses_successfully():
    ts = parse_min_timestamp(begin_date_str_with_time)
    assert ts == 1579749153.0


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
    ts = parse_max_timestamp(end_date_str)
    assert ts == 1586649599.999


def test_parse_max_timestamp_when_given_date_str_with_time_parses_successfully():
    ts = parse_max_timestamp(end_date_str_with_time)
    assert ts == 1586604163.0


def test_parse_max_timestamp_when_given_magic_days_parses_successfully():
    actual_date = datetime.utcfromtimestamp(parse_max_timestamp("20d"))
    expected_date = datetime.utcfromtimestamp(
        convert_datetime_to_timestamp(get_test_date(days_ago=20))
    )
    expected_date = expected_date.replace(hour=23, minute=59, second=59, microsecond=999000)
    assert actual_date == expected_date


def test_parse_max_timestamp_when_given_magic_hours_parses_successfully():
    actual = parse_max_timestamp("20h")
    expected = convert_datetime_to_timestamp(get_test_date(hours_ago=20))
    assert expected - actual < 0.01


def test_parse_magic_minutes_parses_successfully():
    actual = parse_max_timestamp("20m")
    expected = convert_datetime_to_timestamp(get_test_date(minutes_ago=20))
    assert expected - actual < 0.01
