import pytest
from datetime import datetime, timedelta
from logging import StreamHandler, FileHandler
from logging.handlers import RotatingFileHandler

from c42secevents.logging.handlers import NoPrioritySysLogHandler

from c42seceventcli.common.common import get_config_args, parse_timestamp, get_logger, get_error_logger


_DUMMY_KEY = "Key"


@pytest.fixture
def mock_config_read(mocker):
    return mocker.patch("configparser.ConfigParser.read")


@pytest.fixture
def mock_config_get_function(mocker):
    return mocker.patch("configparser.ConfigParser.get")


@pytest.fixture
def mock_config_get_bool_function(mocker):
    return mocker.patch("configparser.ConfigParser.getboolean")


@pytest.fixture
def mock_get_logger(mocker):
    return mocker.patch("c42seceventcli.common.common.getLogger")


@pytest.fixture
def mock_config_file_reader(mocker):
    reader = mocker.patch("configparser.ConfigParser.read")
    reader.return_value = ["NOT EMPTY LIST"]
    return reader


@pytest.fixture
def mock_config_file_sections(mocker):
    sections = mocker.patch("configparser.ConfigParser.sections")
    sections.return_value = ["NOT EMPTY LIST"]
    return sections


def test_get_config_args_when_read_returns_empty_list_raises_io_error(mocker):
    reader = mocker.patch("configparser.ConfigParser.read")
    reader.return_value = []
    with pytest.raises(IOError):
        get_config_args("Test")


def test_get_config_args_when_sections_returns_empty_list_returns_empty_dict(
    mocker, mock_config_file_reader
):
    sections = mocker.patch("configparser.ConfigParser.sections")
    sections.return_value = []
    assert get_config_args("Test") == {}


def test_get_config_args_returns_dict_made_from_items(
    mocker, mock_config_file_reader, mock_config_file_sections
):
    mock_tuples = mocker.patch("configparser.ConfigParser.items")
    mock_tuples.return_value = [("Hi", "Bye"), ("Pizza", "FrenchFries")]
    arg_dict = get_config_args("Test")
    assert arg_dict == {"Hi": "Bye", "Pizza": "FrenchFries"}


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


def test_get_logger_when_destination_type_is_file_adds_file_handler_to_logger(
    mocker, mock_get_logger
):
    mock_handler_init = mocker.patch("logging.FileHandler.__init__")
    mock_handler_init.return_value = None
    logger = get_logger(None, "Somewhere", "file")
    actual = type(logger.addHandler.call_args[0][0])
    expected = FileHandler
    assert actual == expected


def test_get_logger_when_destination_type_is_syslog_adds_no_priority_sys_log_handler_to_logger(
    mocker, mock_get_logger
):
    mock_handler_init = mocker.patch(
        "c42secevents.logging.handlers.NoPrioritySysLogHandler.__init__"
    )
    mock_handler_init.return_value = None
    logger = get_logger(None, "Somewhere", "syslog")
    actual = type(logger.addHandler.call_args[0][0])
    expected = NoPrioritySysLogHandler
    assert actual == expected


def test_get_error_logger_uses_rotating_file_handler(mocker, mock_get_logger):
    mock_handler = mocker.patch("logging.handlers.RotatingFileHandler.__init__")
    mock_handler.return_value = None
    logger = get_error_logger()
    actual = type(logger.addHandler.call_args[0][0])
    expected = RotatingFileHandler
    assert actual == expected
