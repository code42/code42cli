import logging
import sys
from logging.handlers import RotatingFileHandler
from threading import Lock

from code42cli.compat import str
from code42cli.util import get_user_project_path, get_red_text, is_interactive
import code42cli.errors as errors

logger_deps_lock = Lock()
ERROR_LOG_FILE_NAME = u"code42_errors.log"


def get_stream_logger(stream=sys.stdout, name_suffix=None, formatter=None, additional_handlers=None):
    """Supply additional handlers to log to multiple locations besides stdout."""
    suffix = name_suffix or u"main"
    logger = logging.getLogger(u"code42_stdout_{0}".format(suffix))
    if logger_has_handlers(logger):
        return logger

    with logger_deps_lock:
        if not logger_has_handlers(logger):
            handlers = additional_handlers or []
            handlers.extend([logging.StreamHandler(stream)])
            formatter = formatter or logging.Formatter(u"%(message)s")
            level = logging.ERROR if stream == sys.stderr else logging.INFO
            logger.setLevel(level)
            return apply_logger_dependencies(logger, handlers, formatter)
    return logger


def apply_logger_dependencies(logger, handlers, formatter):
    for handler in handlers:
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger


def logger_has_handlers(logger):
    return len(logger.handlers)


def get_error_file_logger(handler=None):
    """Gets the logger where raw exceptions are logged."""
    logger = logging.getLogger(u"code42_error_logger")
    if logger_has_handlers(logger):
        return logger

    with logger_deps_lock:
        if not logger_has_handlers(logger):
            formatter = logging.Formatter(u"%(asctime)s %(message)s")
            handler = handler or get_error_log_handler()

            # Can't use apply_logger_dependencies() in case it raises an exception and causes
            # a stack overflow.
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            return logger
    return logger


def get_error_log_handler():
    log_path = get_user_project_path(u"log")
    log_path = u"{}/{}".format(log_path, ERROR_LOG_FILE_NAME)
    return RotatingFileHandler(log_path, maxBytes=250000000, encoding=u"utf-8")


# def log_error_to_log_file(cmd, exception, additional_info=None):
#     """Logs the error to the CLI error log file. If running interactively, it will also print a 
#     message telling the user the location of the error log file."""
#     logger = get_error_file_logger()
#     logger.error(
#         u"Exception {} raised during invocation of '{}'. Additional info: {}".format(
#             str(exception), cmd.invocation, additional_info
#         )
#     )
#     errors.ERRORED = True
#     logger = get_main_cli_logger()
#     logger.print_errors_occurred(additional_info)


# def get_view_exceptions_location_message():
#     """Returns the error message that is printed when errors occur."""
#     path = get_user_project_path(u"log")
#     return u"View exceptions that occurred at {}/{}.".format(path, ERROR_LOG_FILE_NAME)


class CliLogger(object):
    """There are three loggers part of the CliLogger. The following table illustrates where they 
    log too in both interactive mode and non-interactive mode.
    
    | interactive mode | info logger       | error logger      | error file logger
    ------------------------------------------------------------------------------
    | True             | stdout + log file | stderr + log file | log file
    | False            | log file          | log file          | log file
    """

    def __init__(self):
        handlers = [get_error_log_handler()]
        error_file_logger = get_error_file_logger(handler=handlers[0])
        self._error_file_logger = error_file_logger
        if is_interactive():
            # Add error log handlers to CLI basic output loggers for debugging purposes.
            self._info_logger = get_stream_logger(stream=sys.stdout, additional_handlers=handlers)
            self._error_logger = get_stream_logger(stream=sys.stderr, additional_handlers=handlers)
        else:
            self._info_logger = error_file_logger
            self._error_logger = error_file_logger

    def info(self, message):
        self._info_logger.info(message)

    def info_bold(self, message):
        self._info_logger.info(u"\033[1m{}\033[0m".format(message))

    def error(self, message):
        """Logs red text to stderr and a log file."""
        self._error_logger.error(u"\033[91mERROR: {}\033[0m".format(message))

    def print_errors_occurred(self, additional_info=None):
        """Prints a message telling the user how to retrieve error logs."""
        self.error(u"{}\n{}".format(additional_info, get_view_exceptions_location_message()))

    def print_no_existing_profile_message(self):
        self.error(u"No existing profile.")
        self.print_create_profile_help()

    def print_create_profile_help(self):
        self.info(u"\nTo add a profile, use: ")
        self.info_bold(u"\tcode42 profile create <profile-name> <authority-URL> <username>\n")

    def print_set_default_profile_help(self, existing_profiles):
        self.info(
            u"\nNo default profile set.\n"
            u"\nUse the --profile flag to specify which profile to use.\n"
            u"\nTo set the default profile (used whenever --profile argument is not provided), use:"
        )
        self.info_bold(u"\tcode42 profile use <profile-name>")
        self.info_bold(u"\tcode42 profile use <profile-name>")
        self.info(u"\nExisting profiles:")
        for profile in existing_profiles:
            self.info("\t{}".format(profile))
            self.info("\t{}".format(profile))
        self.info(u"")


def get_main_cli_logger():
    return CliLogger()
