import logging
from logging.handlers import RotatingFileHandler
from threading import Lock

from code42cli.compat import str
from code42cli.util import get_user_project_path, print_error


logger_deps_lock = Lock()
ERROR_LOG_FILE_NAME = u"code42_errors.log"


def get_error_logger():
    """Gets the logger where exceptions are logged."""
    log_path = get_user_project_path(u"log")
    log_path = u"{}/{}".format(log_path, ERROR_LOG_FILE_NAME)
    logger = logging.getLogger(u"code42_error_logger")
    if logger_has_handlers(logger):
        return logger

    with logger_deps_lock:
        if not logger_has_handlers(logger):
            formatter = logging.Formatter(u"%(asctime)s %(message)s")
            handler = RotatingFileHandler(log_path, maxBytes=250000000, encoding=u"utf-8")
            return apply_logger_dependencies(logger, handler, formatter)
    return logger


def logger_has_handlers(logger):
    return len(logger.handlers)


def apply_logger_dependencies(logger, handler, formatter):
    try:
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    except Exception as ex:
        print_error(str(ex))
        exit(1)
    return logger
