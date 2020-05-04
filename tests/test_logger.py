import logging

from code42cli.logger import (
    add_handler_to_logger,
    logger_has_handlers,
    get_view_exceptions_location_message,
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


class TestCliLogger(object):

    _logger = CliLogger()

    def test_info_logs_expected_text_at_expected_level(self, caplog):
        with caplog.at_level(logging.INFO):
            self._logger.info("TEST")
            assert "TEST" in caplog.text

    def test_info_bold_logs_expected_text_at_expected_level(self, caplog):
        with caplog.at_level(logging.INFO):
            self._logger.info_bold("TEST")
            assert "TEST" in caplog.text

    def test_error_logs_expected_text_at_expected_level(self, caplog):
        with caplog.at_level(logging.ERROR):
            self._logger.error("TEST")
            assert "TEST" in caplog.text

    def test_log_exception_detail_to_file_logs_expected_text_at_expected_level(self, caplog):
        with caplog.at_level(logging.ERROR):
            ex = Exception("TEST")
            self._logger.log_exception_detail_to_file(ex)
            assert str(ex) in caplog.text

    def test_log_errors_occurred_message_logs_expected_text_at_expected_level(self, caplog):
        with caplog.at_level(logging.ERROR):
            self._logger.log_errors_occurred_message()
            assert "View exceptions that occurred at" in caplog.text

    def test_log_no_existing_profile_logs_expected_text_at_expected_level(self, caplog):
        with caplog.at_level(logging.ERROR):
            self._logger.log_no_existing_profile()
            assert u"No existing profile." in caplog.text

    def test_create_profile_help_logs_expected_error_text(self, caplog):
        with caplog.at_level(logging.INFO):
            self._logger.log_create_profile_help()
            assert u"To add a profile, use: " in caplog.text

    def test_log_set_default_profile_help_logs_expected_message_at_expected_level(self, caplog):
        with caplog.at_level(logging.INFO):
            self._logger.log_set_default_profile_help(["p1", "p2"])
