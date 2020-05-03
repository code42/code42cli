import pytest

from code42cli.date_helper import DateArgumentException
from code42cli.cmds.shared.extraction import create_time_range_filter
from py42.sdk.queries.fileevents.filters import InsertionTimestamp, EventTimestamp
from py42.sdk.queries.alerts.filters import DateObserved
from .conftest import get_filter_value_from_json
from ...conftest import (
    begin_date_str,
    begin_date_with_time,
    end_date_str,
    end_date_with_time,
    get_test_date_str,
)

timestamp_filter_list = [InsertionTimestamp, EventTimestamp, DateObserved]


@pytest.mark.parametrize("timestamp_filter_class", timestamp_filter_list)
def test_create_event_timestamp_filter_when_given_nothing_returns_none(timestamp_filter_class):
    ts_range = create_time_range_filter(timestamp_filter_class)
    assert not ts_range


@pytest.mark.parametrize("timestamp_filter_class", timestamp_filter_list)
def test_create_event_timestamp_filter_when_given_nones_returns_none(timestamp_filter_class):
    ts_range = create_time_range_filter(timestamp_filter_class, None, None)
    assert not ts_range


@pytest.mark.parametrize("timestamp_filter_class", timestamp_filter_list)
def test_create_event_timestamp_filter_builds_expected_query(timestamp_filter_class):
    ts_range = create_time_range_filter(timestamp_filter_class, begin_date_str)
    actual = get_filter_value_from_json(ts_range, filter_index=0)
    expected = "{0}T00:00:00.000Z".format(begin_date_str)
    assert actual == expected


@pytest.mark.parametrize("timestamp_filter_class", timestamp_filter_list)
def test_create_event_timestamp_filter_when_given_begin_with_time_builds_expected_query(
    timestamp_filter_class,
):
    time_str = u"{} {}".format(*begin_date_with_time)
    ts_range = create_time_range_filter(timestamp_filter_class, time_str)
    actual = get_filter_value_from_json(ts_range, filter_index=0)
    expected = "{0}T0{1}.000Z".format(*begin_date_with_time)
    assert actual == expected


@pytest.mark.parametrize("timestamp_filter_class", timestamp_filter_list)
def test_create_event_timestamp_filter_when_given_end_builds_expected_query(timestamp_filter_class):
    ts_range = create_time_range_filter(timestamp_filter_class, begin_date_str, end_date_str)
    actual = get_filter_value_from_json(ts_range, filter_index=1)
    expected = "{0}T23:59:59.999Z".format(end_date_str)
    assert actual == expected


@pytest.mark.parametrize("timestamp_filter_class", timestamp_filter_list)
def test_create_event_timestamp_filter_when_given_end_with_time_builds_expected_query(
    timestamp_filter_class,
):
    end_date_str = "{} {}".format(*end_date_with_time)
    ts_range = create_time_range_filter(timestamp_filter_class, begin_date_str, end_date_str)
    actual = get_filter_value_from_json(ts_range, filter_index=1)
    expected = "{0}T{1}.000Z".format(*end_date_with_time)
    assert actual == expected


@pytest.mark.parametrize("timestamp_filter_class", timestamp_filter_list)
def test_create_event_timestamp_filter_when_given_both_begin_and_end_builds_expected_query(
    timestamp_filter_class,
):
    end_date = "{} {}".format(*end_date_with_time)
    ts_range = create_time_range_filter(timestamp_filter_class, begin_date_str, end_date)
    actual_begin = get_filter_value_from_json(ts_range, filter_index=0)
    actual_end = get_filter_value_from_json(ts_range, filter_index=1)
    expected_begin = "{0}T00:00:00.000Z".format(begin_date_str)
    expected_end = "{0}T{1}.000Z".format(*end_date_with_time)
    assert actual_begin == expected_begin
    assert actual_end == expected_end


@pytest.mark.parametrize("timestamp_filter_class", timestamp_filter_list)
def test_create_event_timestamp_filter_when_given_short_time_args_builds_expected_query(
    timestamp_filter_class,
):
    begin_date = "{} 10".format(begin_date_str)
    end_date = "{} 12:37".format(end_date_str)
    ts_range = create_time_range_filter(timestamp_filter_class, begin_date, end_date)
    actual_begin = get_filter_value_from_json(ts_range, filter_index=0)
    actual_end = get_filter_value_from_json(ts_range, filter_index=1)
    expected_begin = "{0}T10:00:00.000Z".format(begin_date_str)
    expected_end = "{0}T12:37:00.000Z".format(end_date_str)
    assert actual_begin == expected_begin
    assert actual_end == expected_end


@pytest.mark.parametrize("timestamp_filter_class", timestamp_filter_list)
def test_create_event_timestamp_filter_when_begin_more_than_ninety_days_back_causes_value_error(
    timestamp_filter_class,
):
    begin_date_str = get_test_date_str(days_ago=91)
    with pytest.raises(DateArgumentException):
        create_time_range_filter(timestamp_filter_class, begin_date_str)


@pytest.mark.parametrize("timestamp_filter_class", timestamp_filter_list)
def test_create_event_timestamp_filter_when_end_is_before_begin_causes_value_error(
    timestamp_filter_class,
):
    begin_date = get_test_date_str(days_ago=5)
    end_date = get_test_date_str(days_ago=7)
    with pytest.raises(DateArgumentException):
        create_time_range_filter(timestamp_filter_class, begin_date, end_date)


@pytest.mark.parametrize("timestamp_filter_class", timestamp_filter_list)
def test_create_event_timestamp_filter_when_args_are_magic_days_builds_expected_query(
    timestamp_filter_class,
):
    begin_magic_str = "10d"
    end_magic_str = "6d"
    ts_range = create_time_range_filter(timestamp_filter_class, begin_magic_str, end_magic_str)
    actual_begin = get_filter_value_from_json(ts_range, filter_index=0)
    expected_begin = "{}T00:00:00.000Z".format(get_test_date_str(days_ago=10))
    actual_end = get_filter_value_from_json(ts_range, filter_index=1)
    expected_end = "{}T23:59:59.999Z".format(get_test_date_str(days_ago=6))
    assert actual_begin == expected_begin
    assert actual_end == expected_end


@pytest.mark.parametrize(
    "bad_date_param",
    [
        "01-01-2020",
        "{} {}".format(get_test_date_str(days_ago=5), "b20:30:00"),
        "2months",
        "100s",
        "10 d",
    ],
)
@pytest.mark.parametrize("timestamp_filter_class", timestamp_filter_list)
def test_create_event_timestamp_filter_when_given_improperly_formatted_arg_raises_value_error(
    bad_date_param, timestamp_filter_class
):
    with pytest.raises(DateArgumentException):
        create_time_range_filter(timestamp_filter_class, bad_date_param)
