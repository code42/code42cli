import pytest
from datetime import datetime, timedelta
from logging import StreamHandler, FileHandler

from c42secevents.logging.handlers import NoPrioritySysLogHandler

from c42seceventcli.common.common import SecurityEventConfigParser, parse_timestamp, get_logger


_DUMMY_KEY = "Key"


@pytest.fixture
def mock_config_get_function(mocker):
    return mocker.patch("configparser.ConfigParser.get")


@pytest.fixture
def mock_config_get_bool_function(mocker):
    return mocker.patch("configparser.ConfigParser.getboolean")


@pytest.fixture
def mock_get_logger(mocker):
    return mocker.patch("c42seceventcli.common.common.getLogger")


class TestSecurityEventConfigParser(object):
    def test_get_returns_expected_value(self, mock_config_get_function):
        expected = "Value"
        mock_config_get_function.return_value = expected
        parser = SecurityEventConfigParser("test")
        actual = parser.get(_DUMMY_KEY)
        assert actual == expected

    def test_get_bool_returns_expected_bool(self, mock_config_get_bool_function):
        mock_config_get_bool_function.return_value = True
        parser = SecurityEventConfigParser("test")
        assert parser.get_bool(_DUMMY_KEY)

    def test_get_int_returns_expected_int(self, mock_config_get_function):
        expected = 42
        mock_config_get_function.return_value = 42
        parser = SecurityEventConfigParser("test")
        actual = parser.get_int(_DUMMY_KEY)
        assert actual == expected


def test_parse_timestamp_when_given_date_format_returns_expected_timestamp():
    date_str = "2019-10-01"
    date = datetime.strptime(date_str, "%Y-%m-%d")
    expected = (date - date.utcfromtimestamp(0)).total_seconds()
    actual = parse_timestamp(date_str)
    assert actual == expected


def test_parse_timestamp_when_given_minutes_ago_format_returns_expected_timestamp():
    minutes_ago = 1000
    now = datetime.utcnow()
    time = now - timedelta(minutes=minutes_ago)
    expected = (time - datetime.utcfromtimestamp(0)).total_seconds()
    actual = parse_timestamp("1000")
    assert pytest.approx(actual, expected)


def test_parse_timestamp_when_given_bad_string_throws_value_error():
    with pytest.raises(ValueError):
        parse_timestamp("BAD!")


def test_get_logger_when_destination_type_is_stdout_adds_stream_handler_to_logger(mock_get_logger):
    logger = get_logger(None, "Somewhere", "stdout")
    actual = type(logger.addHandler.call_args[0][0])
    expected = StreamHandler
    assert actual == expected


def test_get_logger_when_destination_type_is_file_adds_file_handler_to_logger(mock_get_logger):
    logger = get_logger(None, "Somewhere", "file")
    actual = type(logger.addHandler.call_args[0][0])
    expected = FileHandler
    assert actual == expected


def test_get_logger_when_destination_type_is_syslog_adds_no_priority_sys_log_handler_to_logger(mocker, mock_get_logger):
    mock_handler_init = mocker.patch("c42secevents.logging.handlers.NoPrioritySysLogHandler.__init__")
    mock_handler_init.return_value = None
    logger = get_logger(None, "Somewhere", "syslog")
    actual = type(logger.addHandler.call_args[0][0])
    expected = NoPrioritySysLogHandler
    assert actual == expected
