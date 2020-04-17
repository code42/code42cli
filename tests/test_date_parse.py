from code42cli.date_parse import parse_min_timestamp, parse_max_timestamp

from .conftest import begin_date_str, begin_date_with_time, end_date_str, end_date_with_time


def test_parse_min_timestamp_when_given_just_date_parses():
    ts = parse_min_timestamp(begin_date_str)
    assert ts == 1579392000.0


def test_parse_min_timestamp_when_given_date_and_time_parses():
    time_str = u"{} {}".format(*begin_date_with_time)
    ts = parse_min_timestamp(time_str)
    assert ts == 1579403553.0


def test_parse_min_timestamp_when_give_magic_str_parses():
    ts = parse_min_timestamp("30d")
    assert ts == 1584489600.0


def test_parse_max_timestamp_when_given_just_date_parses():
    ts = parse_max_timestamp(end_date_str)
    assert ts == 1586303999.999


def test_parse_max_timestamp_when_given_date_and_time_parses():
    time_str = u"{} {}".format(*end_date_with_time)
    ts = parse_max_timestamp(time_str)
    assert ts == 1586258563.0


def test_parse_max_timestamp_when_give_magic_str_parses():
    ts = parse_max_timestamp("30d")
    assert ts == 1584575999.999

