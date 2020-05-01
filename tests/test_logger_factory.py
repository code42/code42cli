from logging import StreamHandler, Formatter
from logging.handlers import RotatingFileHandler

import code42cli.logger as factory


def test_get_logger_for_stdout_when_called_twice_only_sets_handler_once():
    _ = factory.get_logger_for_stdout("test")
    logger = factory.get_logger_for_stdout("test")
    assert len(logger.handlers) == 1


def test_get_logger_for_stdout_uses_expected_handler():
    logger = factory.get_logger_for_stdout("test")
    assert type(logger.handlers[0]) == StreamHandler


def test_get_logger_for_stdout_when_not_given_formatter_uses_expected_formatter():
    logger = factory.get_logger_for_stdout("test")
    assert type(logger.handlers[0].formatter) == Formatter
    assert logger.handlers[0].formatter._fmt == "%(message)s"


def test_get_logger_for_stdout_when_given_formatter_uses_expected_formatter():
    logger = factory.get_logger_for_stdout("test", Formatter("%(asctime)s %(message)s"))
    assert type(logger.handlers[0].formatter) == Formatter
    assert logger.handlers[0].formatter._fmt == "%(asctime)s %(message)s"


def test_get_error_logger_when_called_twice_only_sets_handler_once():
    _ = factory.get_exception_logger()
    logger = factory.get_exception_logger()
    assert len(logger.handlers) == 1


def test_get_error_logger_uses_rotating_file_handler():
    logger = factory.get_exception_logger()
    assert type(logger.handlers[0]) == RotatingFileHandler
