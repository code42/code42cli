import logging
import os
from logging.handlers import RotatingFileHandler

import pytest
from requests import Request

from code42cli.cmds.search.enums import ServerProtocol
from code42cli.logger import add_handler_to_logger
from code42cli.logger import CliLogger
from code42cli.logger import get_logger_for_server
from code42cli.logger import get_view_error_details_message
from code42cli.logger import logger_has_handlers
from code42cli.logger.formatters import FileEventDictToCEFFormatter
from code42cli.logger.formatters import FileEventDictToJSONFormatter
from code42cli.logger.formatters import FileEventDictToRawJSONFormatter
from code42cli.logger.handlers import NoPrioritySysLogHandler
from code42cli.output_formats import OutputFormat
from code42cli.output_formats import SendToFileEventsOutputFormat
from code42cli.util import get_user_project_path


@pytest.fixture(autouse=True)
def fresh_syslog_handler():
    # Set handlers to empty list so it gets initialized each test
    get_logger_for_server(
        "example.com", ServerProtocol.TCP, SendToFileEventsOutputFormat.CEF, None
    ).handlers = []


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


def test_get_logger_for_server_has_info_level(fresh_syslog_handler):
    logger = get_logger_for_server(
        "example.com", ServerProtocol.TCP, SendToFileEventsOutputFormat.CEF, None
    )
    assert logger.level == logging.INFO


def test_get_logger_for_server_when_given_cef_format_uses_cef_formatter(mocker):
    logger = get_logger_for_server(
        "example.com", ServerProtocol.TCP, SendToFileEventsOutputFormat.CEF, None
    )
    assert type(logger.handlers[0].formatter) == FileEventDictToCEFFormatter


def test_get_logger_for_server_when_given_json_format_uses_json_formatter(
    fresh_syslog_handler,
):
    logger = get_logger_for_server(
        "example.com", ServerProtocol.TCP, OutputFormat.JSON, None
    )
    actual = type(logger.handlers[0].formatter)
    assert actual == FileEventDictToJSONFormatter


def test_get_logger_for_server_when_given_raw_json_format_uses_raw_json_formatter(
    fresh_syslog_handler,
):
    logger = get_logger_for_server(
        "example.com", ServerProtocol.TCP, OutputFormat.RAW, None
    )
    actual = type(logger.handlers[0].formatter)
    assert actual == FileEventDictToRawJSONFormatter


def test_get_logger_for_server_when_called_twice_only_has_one_handler(
    fresh_syslog_handler,
):
    get_logger_for_server("example.com", ServerProtocol.TCP, OutputFormat.JSON, None)
    logger = get_logger_for_server(
        "example.com", ServerProtocol.TCP, SendToFileEventsOutputFormat.CEF, None
    )
    assert len(logger.handlers) == 1


def test_get_logger_for_server_uses_no_priority_syslog_handler(fresh_syslog_handler,):
    logger = get_logger_for_server(
        "example.com", ServerProtocol.TCP, SendToFileEventsOutputFormat.CEF, None
    )
    assert type(logger.handlers[0]) == NoPrioritySysLogHandler


def test_get_logger_for_server_constructs_handler_with_expected_args(
    mocker, fresh_syslog_handler, monkeypatch
):
    no_priority_syslog_handler = mocker.patch(
        "code42cli.logger.handlers.NoPrioritySysLogHandler.__init__"
    )
    no_priority_syslog_handler.return_value = None
    get_logger_for_server(
        "example.com", ServerProtocol.TCP, SendToFileEventsOutputFormat.CEF, "cert"
    )
    no_priority_syslog_handler.assert_called_once_with(
        "example.com", 514, ServerProtocol.TCP, "cert"
    )


def test_get_logger_for_server_when_hostname_includes_port_constructs_handler_with_expected_args(
    mocker, fresh_syslog_handler
):
    no_priority_syslog_handler = mocker.patch(
        "code42cli.logger.handlers.NoPrioritySysLogHandler.__init__"
    )
    no_priority_syslog_handler.return_value = None
    get_logger_for_server(
        "example.com:999", ServerProtocol.TCP, SendToFileEventsOutputFormat.CEF, None
    )
    no_priority_syslog_handler.assert_called_once_with(
        "example.com", 999, ServerProtocol.TCP, None,
    )


class TestCliLogger:
    def test_init_creates_user_error_logger_with_expected_handlers(self):
        logger = CliLogger()
        handler_types = [type(h) for h in logger._logger.handlers]
        assert RotatingFileHandler in handler_types

    def test_log_error_logs_expected_text_at_expected_level(self, caplog):
        with caplog.at_level(logging.ERROR):
            ex = Exception("TEST")
            CliLogger().log_error(ex)
            assert str(ex) in caplog.text

    def test_log_verbose_error_logs_expected_text_at_expected_level(
        self, mocker, caplog
    ):
        with caplog.at_level(logging.ERROR):
            request = mocker.MagicMock(sepc=Request)
            request.body = {"foo": "bar"}
            CliLogger().log_verbose_error("code42 dothing --flag YES", request)
            assert "'code42 dothing --flag YES'" in caplog.text
            assert "Request parameters: {'foo': 'bar'}" in caplog.text
