import logging
import os
from logging.handlers import RotatingFileHandler

import pytest
from c42eventextractor.logging.formatters import FileEventDictToCEFFormatter
from c42eventextractor.logging.formatters import FileEventDictToJSONFormatter
from c42eventextractor.logging.formatters import FileEventDictToRawJSONFormatter
from requests import Request

from code42cli.logger import add_handler_to_logger
from code42cli.logger import CliLogger
from code42cli.logger import get_logger_for_server
from code42cli.logger import get_view_error_details_message
from code42cli.logger import logger_has_handlers
from code42cli.util import get_user_project_path


@pytest.fixture
def no_priority_syslog_handler(mocker):
    mock = mocker.patch(
        "c42eventextractor.logging.handlers.NoPrioritySysLogHandlerWrapper.handler"
    )

    # Set handlers to empty list so it gets initialized each test
    get_logger_for_server("example.com", "TCP", "CEF").handlers = []
    return mock


def test_add_handler_to_logger_does_as_expected():
    logger = logging.getLogger("TEST_CODE42_CLI")
    formatter = logging.Formatter()
    handler = logging.Handler()
    add_handler_to_logger(logger, handler, formatter)
    assert handler in logger.handlers
    assert handler.formatter == formatter


def test_logger_has_handlers_when_logger_has_handlers_returns_true():
    logger = logging.getLogger("TEST_CODE42_CLI")
    handler = logging.Handler()
    logger.addHandler(handler)
    assert logger_has_handlers(logger)


def test_logger_has_handlers_when_logger_does_not_have_handlers_returns_false():
    logger = logging.getLogger("TEST_CODE42_CLI")
    logger.handlers = []
    assert not logger_has_handlers(logger)


def test_get_view_exceptions_location_message_returns_expected_message():
    actual = get_view_error_details_message()
    path = os.path.join(get_user_project_path("log"), "code42_errors.log")
    expected = "View details in {}".format(path)
    assert actual == expected


def test_get_logger_for_server_has_info_level(no_priority_syslog_handler):
    logger = get_logger_for_server("example.com", "TCP", "CEF")
    assert logger.level == logging.INFO


def test_get_logger_for_server_when_given_cef_format_uses_cef_formatter(
    no_priority_syslog_handler,
):
    get_logger_for_server("example.com", "TCP", "CEF")
    assert (
        type(no_priority_syslog_handler.setFormatter.call_args[0][0])
        == FileEventDictToCEFFormatter
    )


def test_get_logger_for_server_when_given_json_format_uses_json_formatter(
    no_priority_syslog_handler,
):
    get_logger_for_server("example.com", "TCP", "JSON").handlers = []
    get_logger_for_server("example.com", "TCP", "JSON")
    actual = type(no_priority_syslog_handler.setFormatter.call_args[0][0])
    assert actual == FileEventDictToJSONFormatter


def test_get_logger_for_server_when_given_raw_json_format_uses_raw_json_formatter(
    no_priority_syslog_handler,
):
    get_logger_for_server("example.com", "TCP", "RAW-JSON").handlers = []
    get_logger_for_server("example.com", "TCP", "RAW-JSON")
    actual = type(no_priority_syslog_handler.setFormatter.call_args[0][0])
    assert actual == FileEventDictToRawJSONFormatter


def test_get_logger_for_server_when_called_twice_only_has_one_handler(
    no_priority_syslog_handler,
):
    get_logger_for_server("example.com", "TCP", "JSON")
    logger = get_logger_for_server("example.com", "TCP", "CEF")
    assert len(logger.handlers) == 1


def test_get_logger_for_server_uses_no_priority_syslog_handler(
    no_priority_syslog_handler,
):
    logger = get_logger_for_server("example.com", "TCP", "CEF")
    assert logger.handlers[0] == no_priority_syslog_handler


def test_get_logger_for_server_constructs_handler_with_expected_args(
    mocker, no_priority_syslog_handler, monkeypatch
):
    no_priority_syslog_handler_wrapper = mocker.patch(
        "c42eventextractor.logging.handlers.NoPrioritySysLogHandlerWrapper.__init__"
    )
    no_priority_syslog_handler_wrapper.return_value = None
    get_logger_for_server("example.com", "TCP", "CEF")
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
    get_logger_for_server("example.com:999", "TCP", "CEF")
    no_priority_syslog_handler_wrapper.assert_called_once_with(
        "example.com", port=999, protocol="TCP"
    )


class TestCliLogger:

    _logger = CliLogger()

    def test_init_creates_user_error_logger_with_expected_handlers(self):
        logger = CliLogger()
        handler_types = [type(h) for h in logger._logger.handlers]
        assert RotatingFileHandler in handler_types

    def test_log_error_logs_expected_text_at_expected_level(self, caplog):
        with caplog.at_level(logging.ERROR):
            ex = Exception("TEST")
            self._logger.log_error(ex)
            assert str(ex) in caplog.text

    def test_log_verbose_error_logs_expected_text_at_expected_level(
        self, mocker, caplog
    ):
        with caplog.at_level(logging.ERROR):
            request = mocker.MagicMock(sepc=Request)
            request.body = {"foo": "bar"}
            self._logger.log_verbose_error("code42 dothing --flag YES", request)
            assert "'code42 dothing --flag YES'" in caplog.text
            assert "Request parameters: {'foo': 'bar'}" in caplog.text
