import logging
import sys
from logging.handlers import RotatingFileHandler
from threading import Lock

from code42cli.compat import str
from code42cli.util import get_user_project_path, is_interactive


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


def get_logger_for_stdout(name_suffix=None, formatter=None):
    suffix = name_suffix or u"main"
    logger = logging.getLogger(u"code42_stdout_{0}".format(suffix))
    if logger_has_handlers(logger):
        return logger

    with logger_deps_lock:
        if not logger_has_handlers(logger):
            handler = logging.StreamHandler(sys.stdout)
            formatter = formatter or logging.Formatter(u"%(message)s")
            logger.setLevel(logging.INFO)
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


def _get_logger():
    if is_interactive():
        return get_logger_for_stdout()
    return get_error_logger()


_logger = _get_logger()


def print_error(error_text):
    """Prints red text."""
    _logger.error(u"\033[91mERROR: {}\033[0m".format(error_text))


def print_bold(bold_text):
    _logger.info(u"\033[1m{}\033[0m".format(bold_text))


def print_no_existing_profile_message():
    print_error(u"No existing profile.")
    print_create_profile_help()


def print_create_profile_help():
    _logger.info(u"\nTo add a profile, use: ")
    print_bold(u"\tcode42 profile create <profile-name> <authority-URL> <username>\n")


def print_set_default_profile_help(existing_profiles):
    _logger.info(
        u"\nNo default profile set.\n",
        u"\nUse the --profile flag to specify which profile to use.\n",
        u"\nTo set the default profile (used whenever --profile argument is not provided), use:",
    )
    print_bold(u"\tcode42 profile use <profile-name>")
    _logger.info(u"\nExisting profiles:")
    for profile in existing_profiles:
        _logger.info("\t{}".format(profile))
        print("\t{}".format(profile))
    _logger.info(u"")


def print_to_stderr(error_text):
    sys.stderr.write(error_text)
