import logging
import sys
from logging.handlers import RotatingFileHandler
from threading import Lock

from code42cli.compat import str
from code42cli.util import get_user_project_path, is_interactive


logger_deps_lock = Lock()
ERROR_LOG_FILE_NAME = u"code42_errors.log"


def get_logger_for_stdout(name_suffix=u"main", formatter=None):
    logger = logging.getLogger(u"code42_stdout_{}".format(name_suffix))
    if logger_has_handlers(logger):
        return logger

    with logger_deps_lock:
        if not logger_has_handlers(logger):
            handler = logging.StreamHandler(sys.stdout)
            formatter = formatter or _get_standard_formatter()
            logger.setLevel(logging.INFO)
            return add_handler_to_logger(logger, handler, formatter)
    return logger


def _get_standard_formatter():
    return logging.Formatter(u"%(message)s")


def _create_error_file_handler():
    log_path = get_user_project_path(u"log")
    log_path = u"{}/{}".format(log_path, ERROR_LOG_FILE_NAME)
    return RotatingFileHandler(log_path, maxBytes=250000000, encoding=u"utf-8")


def add_handler_to_logger(logger, handler, formatter):
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


def logger_has_handlers(logger):
    return len(logger.handlers)


def _get_error_file_logger(handler=None):
    """Gets the logger where raw exceptions are logged."""
    logger = logging.getLogger(u"code42_error_logger")
    if logger_has_handlers(logger):
        return logger

    with logger_deps_lock:
        if not logger_has_handlers(logger):
            formatter = _create_formatter_for_error_file()
            handler = handler or _create_error_file_handler()
            return add_handler_to_logger(logger, handler, formatter)
    return logger


def get_view_exceptions_location_message():
    """Returns the error message that is printed when errors occur."""
    path = get_user_project_path(u"log")
    return u"View exceptions that occurred at {}/{}.".format(path, ERROR_LOG_FILE_NAME)


def _get_user_error_logger():
    if is_interactive():
        return _get_interactive_user_error_logger()
    else:
        return _get_error_file_logger()


def _get_standard_logger(stream_name):
    return logging.getLogger(u"code42_{}_main".format(stream_name))


def _get_interactive_user_error_logger():
    """This logger has two handlers, one for stderr and one for the error log file."""
    logger = logging.getLogger(u"code42_stderr_main")
    if logger_has_handlers(logger):
        return logger

    with logger_deps_lock:
        if not logger_has_handlers(logger):
            stderr_handler = logging.StreamHandler(sys.stderr)
            stderr_formatter = _get_standard_formatter()
            stderr_handler.setFormatter(stderr_formatter)

            file_handler = _create_error_file_handler()
            file_formatter = _create_formatter_for_error_file()
            file_handler.setFormatter(file_formatter)

            add_handler_to_logger(logger, stderr_handler, stderr_formatter)
            add_handler_to_logger(logger, file_handler, file_formatter)

            logger.setLevel(logging.ERROR)
            return logger
    return logger


def _create_formatter_for_error_file():
    return logging.Formatter(u"%(asctime)s %(message)s")


def _get_red_error_text(text):
    return u"\033[91mERROR: {}\033[0m".format(text)


class CliLogger(object):
    """There are three loggers part of the CliLogger. The following table illustrates where they 
    log too in both interactive mode and non-interactive mode.
    """

    def __init__(self):
        """The following properties explain how to log to different locations:
        
        `self._info_logger` is what you want to display simple information with, like 
            `profile list`. This does not go to the log file.
        
        `self._error_file_logger` logs directly to the error file is only meant for verbose 
            debugging information, such as raw exceptions.
            
        `self._user_error_logger` is what you want to print in red text to the user. It also goes 
            to the log file for debugging purposes.
        """
        self._info_logger = get_logger_for_stdout()
        self._user_error_logger = _get_user_error_logger()
        self._error_file_logger = _get_error_file_logger()

    def print_info(self, message):
        self._info_logger.info(message)

    def print_bold(self, message):
        self._info_logger.info(u"\033[1m{}\033[0m".format(message))

    def print_and_log_error(self, message):
        """For not interrupting stdout output. Excludes red text and 'ERROR: ' from `error()`.
        """
        self._user_error_logger.error(message)

    def print_and_log_info(self, message):
        """Logs red text to stderr and a log file."""
        self._user_error_logger.error(_get_red_error_text(message))

    def log_error(self, exception):
        if exception:
            message = str(exception)  # Filter out empty string logs.
            if message:
                self._error_file_logger.error(message)

    def print_errors_occurred_message(self, additional_info=None):
        """Prints a message telling the user how to retrieve error logs."""
        locations_message = get_view_exceptions_location_message()
        message = (
            u"{}\n{}".format(additional_info, locations_message)
            if additional_info
            else locations_message
        )
        # Use `info()` because this message is pointless in the error log.
        self.print_info(_get_red_error_text(message))


def get_main_cli_logger():
    return CliLogger()
