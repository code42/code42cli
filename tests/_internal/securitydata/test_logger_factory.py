from logging.handlers import RotatingFileHandler

import pytest
import logging

from c42secevents.logging.formatters import AEDDictToCEFFormatter, AEDDictToJSONFormatter
import code42cli._internal.securitydata.logger_factory as factory


@pytest.fixture
def no_priority_syslog_handler(mocker):
    mock_no_priority_syslog_handler = mocker.MagicMock()
    mock_new = mocker.patch("c42secevents.logging.handlers.NoPrioritySysLogHandler.__new__")
    mock_new.return_value = mock_no_priority_syslog_handler
    return mock_no_priority_syslog_handler


def test_get_logger_for_stdout_has_info_level():
    logger = factory.get_logger_for_stdout("CEF")
    assert logger.level == logging.INFO


def test_get_logger_for_stdout_when_given_cef_format_uses_cef_formatter():
    logger = factory.get_logger_for_stdout("CEF")
    assert type(logger.handlers[0].formatter) == AEDDictToCEFFormatter


def test_get_logger_for_stdout_when_given_json_format_uses_json_formatter():
    logger = factory.get_logger_for_stdout("JSON")
    assert type(logger.handlers[0].formatter) == AEDDictToJSONFormatter


def test_get_logger_for_stdout_when_called_twice_has_only_one_handler():
    _ = factory.get_logger_for_stdout("CEF")
    logger = factory.get_logger_for_stdout("CEF")
    assert len(logger.handlers) == 1


def test_get_logger_for_stdout_uses_stream_handler():
    logger = factory.get_logger_for_stdout("CEF")
    assert type(logger.handlers[0]) == logging.StreamHandler


def test_get_logger_for_file_has_info_level():
    logger = factory.get_logger_for_file("Test.out", "CEF")
    assert logger.level == logging.INFO


def test_get_logger_for_file_when_given_cef_format_uses_cef_formatter():
    logger = factory.get_logger_for_file("Test.out", "CEF")
    assert type(logger.handlers[0].formatter) == AEDDictToCEFFormatter


def test_get_logger_for_file_when_given_json_format_uses_json_formatter():
    logger = factory.get_logger_for_file("Test.out", "JSON")
    assert type(logger.handlers[0].formatter) == AEDDictToJSONFormatter


def test_get_logger_for_file_when_called_twice_has_only_one_handler():
    _ = factory.get_logger_for_file("Test.out", "JSON")
    logger = factory.get_logger_for_file("Test.out", "JSON")
    assert type(logger.handlers[0].formatter) == AEDDictToJSONFormatter


def test_get_logger_for_file_uses_file_handler():
    logger = factory.get_logger_for_file("Test.out", "JSON")
    assert type(logger.handlers[0]) == logging.FileHandler


def test_get_logger_for_file_uses_given_file_name():
    logger = factory.get_logger_for_file("Test.out", "JSON")
    assert logger.handlers[0].baseFilename[-8:] == "Test.out"


def test_get_logger_for_server_has_info_level(no_priority_syslog_handler):
    logger = factory.get_logger_for_server("https://example.com", "TCP", "CEF")
    assert logger.level == logging.INFO


def test_get_logger_for_server_when_given_cef_format_uses_cef_formatter(no_priority_syslog_handler):
    factory.get_logger_for_server("https://example.com", "TCP", "CEF").handlers = []
    _ = factory.get_logger_for_server("https://example.com", "TCP", "CEF")
    assert type(no_priority_syslog_handler.setFormatter.call_args[0][0]) == AEDDictToCEFFormatter


def test_get_logger_for_server_when_given_cef_format_uses_json_formatter(
    no_priority_syslog_handler
):
    factory.get_logger_for_server("https://example.com", "TCP", "CEF").handlers = []
    _ = factory.get_logger_for_server("https://example.com", "TCP", "JSON")
    assert type(no_priority_syslog_handler.setFormatter.call_args[0][0]) == AEDDictToJSONFormatter


def test_get_logger_for_server_when_called_twice_only_has_one_handler(no_priority_syslog_handler):
    factory.get_logger_for_server("https://example.com", "TCP", "CEF").handlers = []
    _ = factory.get_logger_for_server("https://example.com", "TCP", "JSON")
    logger = factory.get_logger_for_server("https://example.com", "TCP", "CEF")
    assert len(logger.handlers) == 1


def test_get_logger_for_server_uses_no_priority_syslog_handler(no_priority_syslog_handler):
    factory.get_logger_for_server("https://example.com", "TCP", "CEF").handlers = []
    logger = factory.get_logger_for_server("https://example.com", "TCP", "CEF")
    assert logger.handlers[0] == no_priority_syslog_handler


def test_get_logger_for_server_uses_given_host_and_protocol(mocker):
    factory.get_logger_for_server("https://example.com", "TCP", "CEF").handlers = []
    mock_init = mocker.patch("c42secevents.logging.handlers.NoPrioritySysLogHandler.__init__")
    mock_init.return_value = None
    _ = factory.get_logger_for_server("https://example.com", "TCP", "CEF")
    mock_init.assert_called_once_with("https://example.com", protocol="TCP")


def test_get_error_logger_when_called_twice_only_sets_handler_once():
    _ = factory.get_error_logger()
    logger = factory.get_error_logger()
    assert len(logger.handlers) == 1


def test_get_error_logger_uses_rotating_file_handler():
    logger = factory.get_error_logger()
    assert type(logger.handlers[0]) == RotatingFileHandler
