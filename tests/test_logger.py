import logging
import os
from logging.handlers import RotatingFileHandler

from requests import Request
from code42cli.logger import (
    add_handler_to_logger,
    logger_has_handlers,
    get_view_error_details_message,
    CliLogger,
)
from code42cli.util import get_user_project_path


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
    expected = u"View details in {}".format(path)
    assert actual == expected


class TestCliLogger(object):

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

    def test_log_verbose_error_logs_expected_text_at_expected_level(self, mocker, caplog):
        with caplog.at_level(logging.ERROR):
            request = mocker.MagicMock(sepc=Request)
            request.body = {"foo": "bar"}
            self._logger.log_verbose_error("code42 dothing --flag YES", request)
            assert "'code42 dothing --flag YES'" in caplog.text
            assert "Request parameters: {'foo': 'bar'}" in caplog.text
