from datetime import datetime

from c42secevents.common import convert_datetime_to_timestamp


def test_convert_datetime_to_timestamp_returns_expected_timestamp():
    test_date = datetime.utcnow()
    actual = convert_datetime_to_timestamp(test_date)
    expected = (test_date - datetime.utcfromtimestamp(0)).total_seconds()
    assert actual == expected
