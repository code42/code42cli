import pytest
from datetime import datetime

from code42cli.date_helper import create_event_timestamp_range
from .conftest import (
    get_first_filter_value_from_json,
    get_second_filter_value_from_json,
    parse_date_from_first_filter_value,
    parse_date_from_second_filter_value,
    get_date_from_minutes_ago,
    get_test_date,
    get_test_date_str,
)


def test_create_event_timestamp_range_when_given_no_args_creates_range_from_sixty_days_back_to_now():
    ts_range = create_event_timestamp_range()
    actual_begin = parse_date_from_first_filter_value(ts_range)
    actual_end = parse_date_from_second_filter_value(ts_range)
    expected_begin = get_test_date(days_ago=60)
    expected_end = datetime.utcnow()
    assert (expected_begin - actual_begin).total_seconds() < 0.1
    assert (expected_end - actual_end).total_seconds() < 0.1


def test_create_event_timestamp_range_when_given_begin_builds_expected_query():
    begin_date_tuple = (get_test_date_str(days_ago=89),)
    ts_range = create_event_timestamp_range(begin_date_tuple)
    actual = get_first_filter_value_from_json(ts_range)
    expected = "{0}T00:00:00.000Z".format(begin_date_tuple[0])
    assert actual == expected


def test_create_event_timestamp_range_when_given_begin_with_time_builds_expected_query():
    time_str = "3:12:33"
    begin_date_tuple = (get_test_date_str(days_ago=89), time_str)
    ts_range = create_event_timestamp_range(begin_date_tuple)
    actual = get_first_filter_value_from_json(ts_range)
    expected = "{0}T0{1}.000Z".format(begin_date_tuple[0], time_str)
    assert actual == expected


def test_create_event_timestamp_range_when_given_begin_as_minutes_ago_builds_expected_query():
    ts_range = create_event_timestamp_range("600")
    actual = parse_date_from_first_filter_value(ts_range)
    expected = get_date_from_minutes_ago(600)
    assert (expected - actual).total_seconds() < 0.1


def test_create_event_timestamp_range_when_given_end_builds_expected_query():
    end_date_tuple = (get_test_date_str(days_ago=10),)
    ts_range = create_event_timestamp_range(None, end_date_tuple)
    actual = get_second_filter_value_from_json(ts_range)
    expected = "{0}T00:00:00.000Z".format(end_date_tuple[0])
    assert actual == expected


def test_create_event_timestamp_range_when_given_end_with_time_builds_expected_query():
    time_str = "11:22:43"
    end_date_tuple = (get_test_date_str(days_ago=10), time_str)
    ts_range = create_event_timestamp_range(None, end_date_tuple)
    actual = get_second_filter_value_from_json(ts_range)
    expected = "{0}T{1}.000Z".format(end_date_tuple[0], time_str)
    assert actual == expected


def test_create_event_timestamp_range_when_given_end_as_seconds_ago_builds_expected_query():
    ts_range = create_event_timestamp_range(None, ("600",))
    actual = parse_date_from_second_filter_value(ts_range)
    expected = get_date_from_minutes_ago(600)
    assert (expected - actual).total_seconds() < 0.1


def test_create_event_timestamp_range_when_given_both_begin_and_end_builds_expected_query():
    being_date_tuple = (get_test_date_str(days_ago=89),)
    ts_range = create_event_timestamp_range(being_date_tuple, ("600",))
    actual_begin = get_first_filter_value_from_json(ts_range)
    actual_end = parse_date_from_second_filter_value(ts_range)
    expected_begin = "{0}T00:00:00.000Z".format(being_date_tuple[0])
    expected_end = get_date_from_minutes_ago(600)
    assert actual_begin == expected_begin
    assert (expected_end - actual_end).total_seconds() < 0.1


def test_create_event_timestamp_range_when_begin_more_than_ninety_days_back_causes_value_error():
    begin_date_tuple = (get_test_date_str(days_ago=91),)
    with pytest.raises(ValueError):
        create_event_timestamp_range(begin_date_tuple)


def test_create_event_timestamp_when_end_is_before_begin_causes_value_error():
    begin_date_tuple = (get_test_date_str(days_ago=5),)
    end_date_str = (get_test_date_str(days_ago=7),)
    with pytest.raises(ValueError):
        create_event_timestamp_range(begin_date_tuple, end_date_str)


def test_create_event_timestamp_when_given_minutes_ago_and_time_raises_value_error():
    with pytest.raises(ValueError):
        create_event_timestamp_range("600", "12:00:00")
