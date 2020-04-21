import pytest

from code42cli.cmds.securitydata.date_helper import (
    create_event_timestamp_filter,
    DateArgumentException,
)
from .conftest import (
    begin_date_str,
    begin_date_with_time,
    end_date_str,
    end_date_with_time,
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
    ts_range = create_event_timestamp_filter(begin_date_str)
    actual = get_filter_value_from_json(ts_range, filter_index=0)
    expected = "{0}T00:00:00.000Z".format(begin_date_str)
    assert actual == expected


def test_create_event_timestamp_filter_when_given_begin_with_time_builds_expected_query():
    time_str = u"{} {}".format(*begin_date_with_time)
    ts_range = create_event_timestamp_filter(time_str)
    actual = get_filter_value_from_json(ts_range, filter_index=0)
    expected = "{0}T0{1}.000Z".format(*begin_date_with_time)
    assert actual == expected


def test_create_event_timestamp_filter_when_given_end_builds_expected_query():
    ts_range = create_event_timestamp_filter(begin_date_str, end_date_str)
    actual = get_filter_value_from_json(ts_range, filter_index=1)
    expected = "{0}T23:59:59.999Z".format(end_date_str)
    assert actual == expected


def test_create_event_timestamp_filter_when_given_end_with_time_builds_expected_query():
    end_date_str = "{} {}".format(*end_date_with_time)
    ts_range = create_event_timestamp_filter(begin_date_str, end_date_str)
    actual = get_filter_value_from_json(ts_range, filter_index=1)
    expected = "{0}T{1}.000Z".format(*end_date_with_time)
    assert actual == expected


def test_create_event_timestamp_filter_when_given_both_begin_and_end_builds_expected_query():
    end_date = "{} {}".format(*end_date_with_time)
    ts_range = create_event_timestamp_filter(begin_date_str, end_date)
    actual_begin = get_filter_value_from_json(ts_range, filter_index=0)
    actual_end = get_filter_value_from_json(ts_range, filter_index=1)
    expected_begin = "{0}T00:00:00.000Z".format(begin_date_str)
    expected_end = "{0}T{1}.000Z".format(*end_date_with_time)
    assert actual_begin == expected_begin
    assert actual_end == expected_end


def test_create_event_timestamp_filter_when_begin_more_than_ninety_days_back_causes_value_error():
    begin_date_str = get_test_date_str(days_ago=91)
    with pytest.raises(DateArgumentException):
        create_event_timestamp_filter(begin_date_str)


def test_create_event_timestamp_filter_when_end_is_before_begin_causes_value_error():
    begin_date = get_test_date_str(days_ago=5)
    end_date = get_test_date_str(days_ago=7)
    with pytest.raises(DateArgumentException):
        create_event_timestamp_filter(begin_date, end_date)


def test_create_event_timestamp_filter_when_args_are_magic_days_builds_expected_query():
    begin_magic_str = "10d"
    end_magic_str = "6d"
    ts_range = create_event_timestamp_filter(begin_magic_str, end_magic_str)
    actual_begin = get_filter_value_from_json(ts_range, filter_index=0)
    expected_begin = "{}T00:00:00.000Z".format(get_test_date_str(days_ago=10))
    actual_end = get_filter_value_from_json(ts_range, filter_index=1)
    expected_end = "{}T23:59:59.999Z".format(get_test_date_str(days_ago=6))
    assert actual_begin == expected_begin
    assert actual_end == expected_end


def test_create_event_timestamp_filter_when_given_improperly_formatted_arg_raises_value_error():
    missing_seconds = "{} {}".format(get_test_date_str(days_ago=5), "12:00")
    month_first_date = "01-01-2020"
    time_typo = "{} {}".format(get_test_date_str(days_ago=5), "b20:30:00")
    bad_magic = "2months"
    bad_magic_2 = "100s"
    bad_magic_3 = "10 d"
    with pytest.raises(DateArgumentException):
        create_event_timestamp_filter(missing_seconds)
    with pytest.raises(DateArgumentException):
        create_event_timestamp_filter(month_first_date)
    with pytest.raises(DateArgumentException):
        create_event_timestamp_filter(time_typo)
    with pytest.raises(DateArgumentException):
        create_event_timestamp_filter(bad_magic)
    with pytest.raises(DateArgumentException):
        create_event_timestamp_filter(bad_magic_2)
    with pytest.raises(DateArgumentException):
        create_event_timestamp_filter(bad_magic_3)
