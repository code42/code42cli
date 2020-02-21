import pytest
import logging

from c42secevents.logging.formatters import AEDDictToCEFFormatter, AEDDictToJSONFormatter
import c42sec._internal.logger_factory as factory


@pytest.fixture
def mock_get_logger_function(mocker):
    mock = mocker.MagicMock()
    mock_get_logger_function = mocker.patch("logging.getLogger")
    mock_get_logger_function.return_value = mock


@pytest.fixture
def stream_handler(mocker):
    mock_init = mocker.patch("logging.StreamHandler.__init__")
    mock_init.return_value = None
    mock_new = mocker.patch("logging.StreamHandler.__new__")
    mock = mocker.MagicMock()
    mock_new.return_value = mock
    return mock


@pytest.fixture
def file_handler(mocker):
    mock_init = mocker.patch("logging.FileHandler.__init__")
    mock_init.return_value = None
    mock_new = mocker.patch("logging.FileHandler.__new__")
    mock = mocker.MagicMock()
    mock_new.return_value = mock
    return mock


@pytest.fixture
def no_priority_syslog_handler(mocker):
    mock_init = mocker.patch("c42secevents.logging.handlers.NoPrioritySysLogHandler.__init__")
    mock_init.return_value = None
    mock_new = mocker.patch("c42secevents.logging.handlers.NoPrioritySysLogHandler.__new__")
    mock = mocker.MagicMock()
    mock_new.return_value = mock
    return mock


@pytest.fixture
def rotating_file_handler(mocker):
    mock_init = mocker.patch("logging.handlers.RotatingFileHandler.__init__")
    mock_init.return_value = None
    mock_new = mocker.patch("logging.handlers.RotatingFileHandler.__new__")
    mock = mocker.MagicMock()
    mock_new.return_value = mock
    return mock


def test_get_logger_for_stdout_has_info_level(mock_get_logger_function, stream_handler):
    logger = factory.get_logger_for_stdout("CEF")
    assert logger.setLevel.call_args[0][0] == logging.INFO


def test_get_logger_for_stdout_when_given_cef_format_uses_cef_formatter(
    mock_get_logger_function, stream_handler
):
    _ = factory.get_logger_for_stdout("CEF")
    assert type(stream_handler.setFormatter.call_args[0][0]) == AEDDictToCEFFormatter


def test_get_logger_for_stdout_when_given_json_format_uses_json_formatter(
    mock_get_logger_function, stream_handler
):
    _ = factory.get_logger_for_stdout("JSON")
    assert type(stream_handler.setFormatter.call_args[0][0]) == AEDDictToJSONFormatter


def test_get_logger_for_stdout_uses_stream_handler(mock_get_logger_function, stream_handler):
    logger = factory.get_logger_for_stdout("JSON")
    assert logger.addHandler.call_args[0][0] == stream_handler


def test_get_logger_for_file_has_info_level(mock_get_logger_function, file_handler):
    logger = factory.get_logger_for_file("out.txt", "CEF")
    assert logger.setLevel.call_args[0][0] == logging.INFO


def test_get_logger_for_file_when_given_cef_format_uses_cef_formatter(
    mock_get_logger_function, file_handler
):
    _ = factory.get_logger_for_file("out.txt", "CEF")
    assert type(file_handler.setFormatter.call_args[0][0]) == AEDDictToCEFFormatter


def test_get_logger_for_file_when_given_json_format_uses_json_formatter(
    mock_get_logger_function, file_handler
):
    _ = factory.get_logger_for_file("out.txt", "JSON")
    assert type(file_handler.setFormatter.call_args[0][0]) == AEDDictToJSONFormatter


def test_get_logger_for_file_uses_file_handler(mock_get_logger_function, file_handler):
    logger = factory.get_logger_for_file("out.txt", "JSON")
    assert logger.addHandler.call_args[0][0] == file_handler


def test_get_logger_for_server_has_info_level(mock_get_logger_function, no_priority_syslog_handler):
    logger = factory.get_logger_for_server("https://www.syslog.company.com", "TCP", "CEF")
    assert logger.setLevel.call_args[0][0] == logging.INFO


def test_get_logger_for_server_when_given_cef_format_uses_cef_formatter(
    mock_get_logger_function, no_priority_syslog_handler
):
    _ = factory.get_logger_for_server("https://www.syslog.company.com", "TCP", "CEF")
    assert type(no_priority_syslog_handler.setFormatter.call_args[0][0]) == AEDDictToCEFFormatter


def test_get_logger_for_server_when_given_json_format_uses_json_formatter(
    mock_get_logger_function, no_priority_syslog_handler
):
    _ = factory.get_logger_for_server("https://www.syslog.company.com", "TCP", "JSON")
    assert type(no_priority_syslog_handler.setFormatter.call_args[0][0]) == AEDDictToJSONFormatter


def test_get_logger_for_server_uses_no_priority_syslog_handler(
    mock_get_logger_function, no_priority_syslog_handler
):
    logger = factory.get_logger_for_server("https://www.syslog.company.com", "TCP", "JSON")
    assert logger.addHandler.call_args[0][0] == no_priority_syslog_handler


def test_get_error_logger_uses_rotating_file_handler(
    mock_get_logger_function, rotating_file_handler
):
    logger = factory.get_error_logger()
    assert logger.addHandler.call_args[0][0] == rotating_file_handler
