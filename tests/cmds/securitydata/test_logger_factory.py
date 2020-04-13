import logging
import pytest
from c42eventextractor.logging.formatters import (
    FileEventDictToCEFFormatter,
    FileEventDictToJSONFormatter,
    FileEventDictToRawJSONFormatter,
)

import code42cli.cmds.securitydata.logger_factory as factory


@pytest.fixture
def no_priority_syslog_handler(mocker):
    mock = mocker.patch("c42eventextractor.logging.handlers.NoPrioritySysLogHandlerWrapper.handler")

    # Set handlers to empty list so it gets initialized each test
    factory.get_logger_for_server("example.com", "TCP", "CEF").handlers = []
    return mock


def test_get_logger_for_stdout_has_info_level():
    logger = factory.get_logger_for_stdout("CEF")
    assert logger.level == logging.INFO


def test_get_logger_for_stdout_when_given_cef_format_uses_cef_formatter():
    logger = factory.get_logger_for_stdout("CEF")
    assert type(logger.handlers[0].formatter) == FileEventDictToCEFFormatter


def test_get_logger_for_stdout_when_given_json_format_uses_json_formatter():
    logger = factory.get_logger_for_stdout("JSON")
    assert type(logger.handlers[0].formatter) == FileEventDictToJSONFormatter


def test_get_logger_for_stdout_when_given_raw_json_format_uses_raw_json_formatter():
    logger = factory.get_logger_for_stdout("RAW-JSON")
    assert type(logger.handlers[0].formatter) == FileEventDictToRawJSONFormatter


def test_get_logger_for_stdout_when_called_twice_has_only_one_handler():
    factory.get_logger_for_stdout("CEF")
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
    assert type(logger.handlers[0].formatter) == FileEventDictToCEFFormatter


def test_get_logger_for_file_when_given_json_format_uses_json_formatter():
    logger = factory.get_logger_for_file("Test.out", "JSON")
    assert type(logger.handlers[0].formatter) == FileEventDictToJSONFormatter


def test_get_logger_for_file_when_given_raw_json_format_uses_raw_json_formatter():
    logger = factory.get_logger_for_file("Test.out", "RAW-JSON")
    assert type(logger.handlers[0].formatter) == FileEventDictToRawJSONFormatter


def test_get_logger_for_file_when_called_twice_has_only_one_handler():
    factory.get_logger_for_file("Test.out", "JSON")
    logger = factory.get_logger_for_file("Test.out", "JSON")
    assert type(logger.handlers[0].formatter) == FileEventDictToJSONFormatter


def test_get_logger_for_file_uses_file_handler():
    logger = factory.get_logger_for_file("Test.out", "JSON")
    assert type(logger.handlers[0]) == logging.FileHandler


def test_get_logger_for_file_uses_given_file_name():
    logger = factory.get_logger_for_file("Test.out", "JSON")
    assert logger.handlers[0].baseFilename[-8:] == "Test.out"


def test_get_logger_for_server_has_info_level(no_priority_syslog_handler):
    logger = factory.get_logger_for_server("example.com", "TCP", "CEF")
    assert logger.level == logging.INFO


def test_get_logger_for_server_when_given_cef_format_uses_cef_formatter(no_priority_syslog_handler):
    factory.get_logger_for_server("example.com", "TCP", "CEF")
    assert (
        type(no_priority_syslog_handler.setFormatter.call_args[0][0]) == FileEventDictToCEFFormatter
    )


def test_get_logger_for_server_when_given_json_format_uses_json_formatter(
    no_priority_syslog_handler
):
    factory.get_logger_for_server("example.com", "TCP", "JSON").handlers = []
    factory.get_logger_for_server("example.com", "TCP", "JSON")
    actual = type(no_priority_syslog_handler.setFormatter.call_args[0][0])
    assert actual == FileEventDictToJSONFormatter


def test_get_logger_for_server_when_given_raw_json_format_uses_raw_json_formatter(
    no_priority_syslog_handler
):
    factory.get_logger_for_server("example.com", "TCP", "RAW-JSON").handlers = []
    factory.get_logger_for_server("example.com", "TCP", "RAW-JSON")
    actual = type(no_priority_syslog_handler.setFormatter.call_args[0][0])
    assert actual == FileEventDictToRawJSONFormatter


def test_get_logger_for_server_when_called_twice_only_has_one_handler(no_priority_syslog_handler):
    factory.get_logger_for_server("example.com", "TCP", "JSON")
    logger = factory.get_logger_for_server("example.com", "TCP", "CEF")
    assert len(logger.handlers) == 1


def test_get_logger_for_server_uses_no_priority_syslog_handler(no_priority_syslog_handler):
    logger = factory.get_logger_for_server("example.com", "TCP", "CEF")
    assert logger.handlers[0] == no_priority_syslog_handler


def test_get_logger_for_server_constructs_handler_with_expected_args(
    mocker, no_priority_syslog_handler, monkeypatch
):
    no_priority_syslog_handler_wrapper = mocker.patch(
        "c42eventextractor.logging.handlers.NoPrioritySysLogHandlerWrapper.__init__"
    )
    no_priority_syslog_handler_wrapper.return_value = None
    factory.get_logger_for_server("example.com", "TCP", "CEF")
    no_priority_syslog_handler_wrapper.assert_called_once_with(
        "example.com", port=514, protocol="TCP"
    )


def test_get_logger_for_server_when_hostname_includes_port_constructs_handler_with_expected_args(
    mocker, no_priority_syslog_handler
):
    no_priority_syslog_handler_wrapper = mocker.patch(
        "c42eventextractor.logging.handlers.NoPrioritySysLogHandlerWrapper.__init__"
    )
    no_priority_syslog_handler_wrapper.return_value = None
    factory.get_logger_for_server("example.com:999", "TCP", "CEF")
    no_priority_syslog_handler_wrapper.assert_called_once_with(
        "example.com", port=999, protocol="TCP"
    )
