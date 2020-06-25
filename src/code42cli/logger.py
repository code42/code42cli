import os, logging, sys, traceback
from logging.handlers import RotatingFileHandler
from threading import Lock
import copy

from click import echo, secho
from code42cli.util import get_user_project_path, is_interactive

# prevent loggers from printing stacks to stderr if a pipe is broken
logging.raiseExceptions = False

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


def _get_error_log_path():
    log_path = get_user_project_path(u"log")
    return os.path.join(log_path, ERROR_LOG_FILE_NAME)


def _create_error_file_handler():
    log_path = _get_error_log_path()
    return RotatingFileHandler(log_path, maxBytes=250000000, encoding=u"utf-8", delay=True)


def add_handler_to_logger(logger, handler, formatter):
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


def logger_has_handlers(logger):
    return len(logger.handlers)


def _get_error_file_logger():
    """Gets the logger where raw exceptions are logged."""
    logger = logging.getLogger(u"code42_error_logger")
    if logger_has_handlers(logger):
        return logger

    with logger_deps_lock:
        if not logger_has_handlers(logger):
            formatter = _create_formatter_for_error_file()
            handler = _create_error_file_handler()
            return add_handler_to_logger(logger, handler, formatter)
    return logger


def get_view_error_details_message():
    """Returns the error message that is printed when errors occur."""
    path = _get_error_log_path()
    return u"View details in {}".format(path)


def _get_user_error_logger():
    if is_interactive():
        return _get_interactive_user_error_logger()
    else:
        return _get_error_file_logger()


class RedStderrHandler(logging.StreamHandler):
    """Logging handler for logging error messages to stderr using red scary text prefixed by the 
    word `ERROR`. For logging info to stderr, it will not add the scary red text."""

    def __init__(self):
        super(RedStderrHandler, self).__init__(sys.stderr)

    def emit(self, record):
        if record.levelno == logging.ERROR:
            message = _get_red_error_text(record.msg)
            record = copy.copy(record)
            record.msg = message
        super(RedStderrHandler, self).emit(record)


def _get_interactive_user_error_logger():
    """This logger has two handlers, one for stderr and one for the error log file."""
    logger = logging.getLogger(u"code42_stderr_main")
    if logger_has_handlers(logger):
        return logger

    with logger_deps_lock:
        if not logger_has_handlers(logger):
            stderr_handler = RedStderrHandler()
            stderr_formatter = _get_standard_formatter()
            stderr_handler.setFormatter(stderr_formatter)

            file_handler = _create_error_file_handler()
            file_formatter = _create_formatter_for_error_file()
            file_handler.setFormatter(file_formatter)

            add_handler_to_logger(logger, stderr_handler, stderr_formatter)
            add_handler_to_logger(logger, file_handler, file_formatter)

            logger.setLevel(logging.INFO)
            return logger
    return logger


def _create_formatter_for_error_file():
    return logging.Formatter(u"%(asctime)s %(message)s")


def get_progress_logger(handler=None):
    logger = logging.getLogger(u"code42cli_progress_bar")
    if logger_has_handlers(logger):
        return logger

    with logger_deps_lock:
        if not logger_has_handlers(logger):
            handler = handler or InPlaceStreamHandler()
            formatter = _get_standard_formatter()
            logger.setLevel(logging.INFO)
            return add_handler_to_logger(logger, handler, formatter)
    return logger


class InPlaceStreamHandler(logging.StreamHandler):
    def __init__(self):
        super(InPlaceStreamHandler, self).__init__(sys.stdout)

    def emit(self, record):
        # Borrowed some from python3's logging.StreamHandler to make work on python2.
        try:
            msg = "\r{}\r".format(self.format(record))
            stream = self.stream
            stream.write(msg)
            self.flush()
        except RuntimeError as err:
            if "recursion" in str(err):
                raise
        except Exception:
            self.handleError(record)


class CliLogger(object):
    """There are three loggers part of the CliLogger. The following table illustrates where they 
    log to in both interactive mode and non-interactive mode.
    """

    def __init__(self):
        """The following properties explain how to log to different locations:
        
        `self._info_logger` is for when you want to display simple information, like 
            `profile list`. This does _not_ go to the log file.
            
        `self._user_error_logger` is for when you want to print in red text to the user. It also 
            goes to the log file for debugging purposes.
        
        `self._error_file_logger` logs directly to the error file and is only meant for verbose 
            debugging information, such as raw exceptions.
        """
        self._logger = _get_error_file_logger()

    def log_error(self, err):
        if err:
            message = str(err)  # Filter out empty string logs.
            if message:
                self._logger.error(message)

    def log_verbose_error(self, invocation_str=None, http_request=None):
        """For logging traces, invocation strs, and request parameters during exceptions to the 
        error log file."""
        prefix = (
            "Exception occurred."
            if not invocation_str
            else "Exception occurred from input: '{}'.".format(invocation_str)
        )
        message = "{}. See error below.".format(prefix)
        self.log_error(message)
        self.log_error(traceback.format_exc())
        if http_request:
            self.log_error("Request parameters: {}".format(http_request.body))


def get_main_cli_logger():
    return CliLogger()
