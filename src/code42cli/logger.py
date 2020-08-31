import logging
import os
import sys
import traceback
from logging.handlers import RotatingFileHandler
from threading import Lock

from c42eventextractor.logging.formatters import FileEventDictToCEFFormatter
from c42eventextractor.logging.formatters import FileEventDictToJSONFormatter
from c42eventextractor.logging.formatters import FileEventDictToRawJSONFormatter
from c42eventextractor.logging.handlers import NoPrioritySysLogHandlerWrapper
from click.exceptions import ClickException

from code42cli.cmds.search.enums import FileEventsOutputFormat
from code42cli.util import get_url_parts
from code42cli.util import get_user_project_path

# prevent loggers from printing stacks to stderr if a pipe is broken
logging.raiseExceptions = False

logger_deps_lock = Lock()
ERROR_LOG_FILE_NAME = "code42_errors.log"


def _get_formatter(output_format):
    if output_format == FileEventsOutputFormat.JSON:
        return FileEventDictToJSONFormatter()
    elif output_format == FileEventsOutputFormat.CEF:
        return FileEventDictToCEFFormatter()
    else:
        return FileEventDictToRawJSONFormatter()


def _init_logger(logger, handler, output_format):
    formatter = _get_formatter(output_format)
    logger.setLevel(logging.INFO)
    return add_handler_to_logger(logger, handler, formatter)


def handleError(record):
    """Override logger's `handleError` method to exit if an exception is raised while trying to
    log, otherwise it would continue to gather and process events if the connection breaks but send
    them nowhere.
    """
    t, v, tb = sys.exc_info()
    if t == BrokenPipeError:
        raise ClickException("Network connection broken while sending results.")


def get_logger_for_server(hostname, protocol, output_format):
    """Gets the logger that sends logs to a server for the given format.

    Args:
        hostname: The hostname of the server. It may include the port.
        protocol: The transfer protocol for sending logs.
        output_format: CEF, JSON, or RAW_JSON. Each type results in a different logger instance.
    """
    logger = logging.getLogger("code42_syslog_{}".format(output_format.lower()))
    if logger_has_handlers(logger):
        return logger

    with logger_deps_lock:
        if not logger_has_handlers(logger):
            url_parts = get_url_parts(hostname)
            port = url_parts[1] or 514
            try:
                handler = NoPrioritySysLogHandlerWrapper(
                    url_parts[0], port=port, protocol=protocol
                ).handler
            except Exception as e:
                raise Exception(
                    "Unable to connect {}. Failed with error {}".format(
                        hostname, str(e)
                    )
                )
            return _init_logger(logger, handler, output_format)
    return logger


def _get_standard_formatter():
    return logging.Formatter("%(message)s")


def _get_error_log_path():
    log_path = get_user_project_path("log")
    return os.path.join(log_path, ERROR_LOG_FILE_NAME)


def _create_error_file_handler():
    log_path = _get_error_log_path()
    return RotatingFileHandler(
        log_path, maxBytes=250000000, encoding="utf-8", delay=True
    )


def add_handler_to_logger(logger, handler, formatter):
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


def logger_has_handlers(logger):
    return len(logger.handlers)


def _get_error_file_logger():
    """Gets the logger where raw exceptions are logged."""
    logger = logging.getLogger("code42_error_logger")
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
    return "View details in {}".format(path)


def _create_formatter_for_error_file():
    return logging.Formatter("%(asctime)s %(message)s")


class CliLogger:
    def __init__(self):
        self._logger = _get_error_file_logger()

    def log_error(self, err):
        message = str(err) if err else None
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
