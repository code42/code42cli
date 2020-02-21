import sys
import logging
from logging.handlers import RotatingFileHandler

from c42secevents.logging.formatters import AEDDictToJSONFormatter, AEDDictToCEFFormatter
from c42secevents.logging.handlers import NoPrioritySysLogHandler

from c42sec._internal.options import OutputFormat
from c42sec.util import get_user_project_path


def get_logger_for_stdout(output_format):
    logger = logging.getLogger("c42sec_stdout_{0}".format(output_format))
    if len(logger.handlers) > 0:
        return logger

    handler = logging.StreamHandler(sys.stdout)
    return _init_logger(logger, handler, output_format)


def get_logger_for_file(filename, output_format):
    logger = logging.getLogger("c42sec_file_{0}".format(output_format))
    if len(logger.handlers) > 0:
        return logger

    handler = logging.FileHandler(filename)
    return _init_logger(logger, handler, output_format)


def get_logger_for_server(hostname, protocol, output_format):
    logger = logging.getLogger("c42sec_syslog_{0}".format(output_format))
    if len(logger.handlers) > 0:
        return logger

    handler = NoPrioritySysLogHandler(hostname, protocol=protocol)
    return _init_logger(logger, handler, output_format)


def get_error_logger():
    log_path = get_user_project_path("log")
    log_path = "{0}/c42sec_errors.log".format(log_path)
    logger = logging.getLogger("c42sec_error_logger")
    if len(logger.handlers) > 0:
        return logger

    formatter = logging.Formatter("%(asctime)s %(message)s")
    handler = RotatingFileHandler(log_path, maxBytes=250000000)
    return _apply_logger_dependencies(logger, handler, formatter)


def _init_logger(logger, handler, output_format):
    formatter = _get_formatter(output_format)
    logger.setLevel(logging.INFO)
    return _apply_logger_dependencies(logger, handler, formatter)


def _apply_logger_dependencies(logger, handler, formatter):
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


def _get_formatter(output_format):
    return (
        AEDDictToJSONFormatter() if output_format == OutputFormat.JSON else AEDDictToCEFFormatter()
    )
