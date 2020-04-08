import pytest

from code42cli.cmds.securitydata.date_helper import create_event_timestamp_filter
from .conftest import (
    begin_date_list,
    begin_date_list_with_time,
    end_date_list,
    end_date_list_with_time,
    get_filter_value_from_json,
    get_test_date_str,
)


def test_create_event_timestamp_filter_when_given_nothing_returns_none():
    ts_range = create_event_timestamp_filter()
    assert not ts_range


def test_create_event_timestamp_filter_when_given_nones_returns_none():
    ts_range = create_event_timestamp_filter(None, None)
    assert not ts_range


def test_create_event_timestamp_filter_builds_expected_query():
    ts_range = create_event_timestamp_filter(begin_date_list)
    actual = get_filter_value_from_json(ts_range, filter_index=0)
    expected = "{0}T00:00:00.000Z".format(begin_date_list[0])
    assert actual == expected


def test_create_event_timestamp_filter_when_given_begin_with_time_builds_expected_query():
    ts_range = create_event_timestamp_filter(begin_date_list_with_time)
    actual = get_filter_value_from_json(ts_range, filter_index=0)
    expected = "{0}T0{1}.000Z".format(begin_date_list_with_time[0], begin_date_list_with_time[1])
    assert actual == expected


def test_create_event_timestamp_filter_when_given_end_builds_expected_query():
    ts_range = create_event_timestamp_filter(begin_date_list, end_date_list)
    actual = get_filter_value_from_json(ts_range, filter_index=1)
    expected = "{0}T23:59:59.999Z".format(end_date_list[0])
    assert actual == expected


def test_create_event_timestamp_filter_when_given_end_with_time_builds_expected_query():
    ts_range = create_event_timestamp_filter(begin_date_list, end_date_list_with_time)
    actual = get_filter_value_from_json(ts_range, filter_index=1)
    expected = "{0}T{1}.000Z".format(end_date_list_with_time[0], end_date_list_with_time[1])
    assert actual == expected


def test_create_event_timestamp_filter_when_given_both_begin_and_end_builds_expected_query():
    ts_range = create_event_timestamp_filter(begin_date_list, end_date_list_with_time)
    actual_begin = get_filter_value_from_json(ts_range, filter_index=0)
    actual_end = get_filter_value_from_json(ts_range, filter_index=1)
    expected_begin = "{0}T00:00:00.000Z".format(begin_date_list[0])
    expected_end = "{0}T{1}.000Z".format(end_date_list_with_time[0], end_date_list_with_time[1])
    assert actual_begin == expected_begin
    assert actual_end == expected_end


def test_create_event_timestamp_filter_when_begin_more_than_ninety_days_back_causes_value_error():
    begin_date_tuple = (get_test_date_str(days_ago=91),)
    with pytest.raises(ValueError):
        create_event_timestamp_filter(begin_date_tuple)


def test_create_event_timestamp_filter_when_end_is_before_begin_causes_value_error():
    begin_date_tuple = (get_test_date_str(days_ago=5),)
    end_date_str = (get_test_date_str(days_ago=7),)
    with pytest.raises(ValueError):
        create_event_timestamp_filter(begin_date_tuple, end_date_str)


def test_create_event_timestamp_filter_when_given_three_date_args_raises_value_error():
    begin_date_tuple = (get_test_date_str(days_ago=5), "12:00:00", "end_date=12:00:00")
    with pytest.raises(ValueError):
        create_event_timestamp_filter(begin_date_tuple)
