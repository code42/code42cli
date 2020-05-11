import logging
from logging.handlers import RotatingFileHandler
from requests import Request

from code42cli.logger import (
    add_handler_to_logger,
    logger_has_handlers,
    get_view_exceptions_location_message,
    RedStderrHandler,
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
    actual = get_view_exceptions_location_message()
    path = get_user_project_path()
    expected = u"View exceptions that occurred at {}log/code42_errors.log.".format(path)
    assert actual == expected


class TestRedStderrHandler(object):
    def test_emit_when_error_adds_red_text(self, mocker, caplog):
        handler = RedStderrHandler()
        record = mocker.MagicMock(spec=logging.LogRecord)
        record.msg = "TEST"
        record.levelno = logging.ERROR

        logger = mocker.patch("logging.StreamHandler.emit")
        handler.emit(record)
        actual = logger.call_args[0][0].msg
        assert actual == "\x1b[91mERROR: TEST\x1b[0m"

    def test_emit_when_info_does_not_alter(self, mocker, caplog):
        handler = RedStderrHandler()
        record = mocker.MagicMock(spec=logging.LogRecord)
        record.msg = "TEST"
        record.levelno = logging.INFO

        logger = mocker.patch("logging.StreamHandler.emit")
        handler.emit(record)
        actual = logger.call_args[0][0].msg
        assert actual == "TEST"


class TestCliLogger(object):

    _logger = CliLogger()

    def test_init_creates_user_error_logger_with_expected_handlers(self, mocker):
        is_interactive = mocker.patch("code42cli.logger.is_interactive")
        is_interactive.return_value = True
        logger = CliLogger()
        handler_types = [type(h) for h in logger._user_error_logger.handlers]
        assert RedStderrHandler in handler_types
        assert RotatingFileHandler in handler_types

    def test_print_info_logs_expected_text_at_expected_level(self, caplog):
        with caplog.at_level(logging.INFO):
            self._logger.print_info("TEST")
            assert "TEST" in caplog.text

    def test_print_bold_logs_expected_text_at_expected_level(self, caplog):
        with caplog.at_level(logging.INFO):
            self._logger.print_bold("TEST")
            assert "TEST" in caplog.text

    def test_print_and_log_error_logs_expected_text_at_expected_level(self, caplog):
        with caplog.at_level(logging.ERROR):
            self._logger.print_and_log_error("TEST")
            assert "TEST" in caplog.text

    def test_print_and_log_info_logs_expected_text_at_expected_level(self, caplog):
        with caplog.at_level(logging.INFO):
            self._logger.print_and_log_info("TEST")
            assert "TEST" in caplog.text

    def test_log_error_logs_expected_text_at_expected_level(self, caplog):
        with caplog.at_level(logging.ERROR):
            ex = Exception("TEST")
            self._logger.log_error(ex)
            assert str(ex) in caplog.text

    def test_print_errors_occurred_message_logs_expected_text_at_expected_level(self, caplog):
        with caplog.at_level(logging.ERROR):
            self._logger.print_errors_occurred_message()
            assert "View exceptions that occurred at" in caplog.text

    def test_log_verbose_error_logs_expected_text_at_expected_level(self, mocker, caplog):
        with caplog.at_level(logging.ERROR):
            request = mocker.MagicMock(sepc=Request)
            request.body = {"foo": "bar"}
            self._logger.log_verbose_error("code42 dothing --flag YES", request)
            assert "'code42 dothing --flag YES'" in caplog.text
            assert "Request parameters: {'foo': 'bar'}" in caplog.text
