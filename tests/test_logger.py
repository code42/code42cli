from logging.handlers import RotatingFileHandler
import code42cli.logger as factory


def test_get_error_logger_when_called_twice_only_sets_handler_once():
    _ = factory.get_error_logger()
    logger = factory.get_error_logger()
    assert len(logger.handlers) == 1


def test_get_error_logger_uses_rotating_file_handler():
    logger = factory.get_error_logger()
    assert type(logger.handlers[0]) == RotatingFileHandler
