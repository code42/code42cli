import pytest

from code42cli import PRODUCT_NAME
from code42cli.util import does_user_agree, get_url_parts, find_format_width


TEST_HEADER = {u"key1": u"Column 1", u"key2": u"Column 10", u"key3": u"Column 100"}


@pytest.fixture
def mock_input(mocker):
    return mocker.patch("{}.util.get_input".format(PRODUCT_NAME))


def test_get_url_parts_when_given_host_and_port_returns_expected_parts():
    url_str = "www.example.com:123"
    parts = get_url_parts(url_str)
    assert parts == ("www.example.com", 123)


def test_get_url_parts_when_given_host_without_port_returns_expected_parts():
    url_str = "www.example.com"
    parts = get_url_parts(url_str)
    assert parts == ("www.example.com", None)


def test_does_user_agree_when_user_says_y_returns_true(mock_input):
    mock_input.return_value = "y"
    assert does_user_agree("Test Prompt")


def test_does_user_agree_when_user_says_capital_y_returns_true(mock_input):
    mock_input.return_value = "Y"
    assert does_user_agree("Test Prompt")


def test_does_user_agree_when_user_says_n_returns_false(mock_input):
    mock_input.return_value = "n"
    assert not does_user_agree("Test Prompt")


def test_find_format_width_when_zero_records_sets_width_to_header_length():
    _, column_width = find_format_width([], TEST_HEADER)
    assert column_width[u"key1"] == len(TEST_HEADER[u"key1"])
    assert column_width[u"key2"] == len(TEST_HEADER[u"key2"])
    assert column_width[u"key3"] == len(TEST_HEADER[u"key3"])


def test_find_format_width_when_records_sets_width_to_greater_of_data_or_header_length():
    report = [
        {u"key1": u"test 1", u"key2": u"value xyz test", u"key3": u"test test test test"},
        {u"key1": u"1", u"key2": u"value xyz", u"key3": u"test test test test"},
    ]
    _, column_width = find_format_width(report, TEST_HEADER)
    assert column_width[u"key1"] == len(TEST_HEADER[u"key1"])
    assert column_width[u"key2"] == len(report[0][u"key2"])
    assert column_width[u"key3"] == len(report[1][u"key3"])


def test_find_format_width_filters_keys_not_present_in_header():
    report = [
        {u"key1": u"test 1", u"key2": u"value xyz test", u"key3": u"test test test test"},
        {u"key1": u"1", u"key2": u"value xyz", u"key3": u"test test test test"},
    ]
    header_with_subset_keys = {u"key1": u"Column 1", u"key3": u"Column 100"}
    result, _ = find_format_width(report, header_with_subset_keys)
    for item in result:
        assert u"key2" not in item.keys()
