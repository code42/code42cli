import logging

from c42eventextractor.logging.formatters import (
    FileEventDictToCEFFormatter,
    FileEventDictToJSONFormatter,
    FileEventDictToRawJSONFormatter,
)
from c42eventextractor.logging.handlers import NoPrioritySysLogHandlerWrapper

from code42cli.cmds.search_shared.enums import OutputFormat
from code42cli.util import get_url_parts
from code42cli.logger import (
    logger_has_handlers,
    logger_deps_lock,
    add_handler_to_logger,
    get_main_cli_logger,
    get_logger_for_stdout as get_stdout_logger,
)


def get_logger_for_stdout(output_format):
    """Gets the stdout logger for the given format.
        Args:
            output_format: CEF, JSON, or RAW_JSON. Each type results in a different logger instance.
    """
    formatter = _get_formatter(output_format)
    return get_stdout_logger(output_format.lower(), formatter)


def get_logger_for_file(filename, output_format):
    """Gets the logger that logs to a file for the given format.

        Args:
            filename: The name of the file to write logs to.
            output_format: CEF, JSON, or RAW_JSON. Each type results in a different logger instance.
    """
    logger = logging.getLogger(u"code42_file_{0}".format(output_format.lower()))
    if logger_has_handlers(logger):
        return logger

    with logger_deps_lock:
        if not logger_has_handlers(logger):
            handler = logging.FileHandler(filename, delay=True, encoding="utf-8")
            return _init_logger(logger, handler, output_format)
    return logger


def get_logger_for_server(hostname, protocol, output_format):
    """Gets the logger that sends logs to a server for the given format.

        Args:
            hostname: The hostname of the server. It may include the port.
            protocol: The transfer protocol for sending logs.
            output_format: CEF, JSON, or RAW_JSON. Each type results in a different logger instance.
    """
    logger = logging.getLogger(u"code42_syslog_{0}".format(output_format.lower()))
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
            except:
                logger = get_main_cli_logger()
                logger.print_and_log_error(u"Unable to connect to {0}.".format(hostname))
                exit(1)
            return _init_logger(logger, handler, output_format)
    return logger


def _init_logger(logger, handler, output_format):
    formatter = _get_formatter(output_format)
    logger.setLevel(logging.INFO)
    return add_handler_to_logger(logger, handler, formatter)


def _get_formatter(output_format):
    if output_format == OutputFormat.JSON:
        return FileEventDictToJSONFormatter()
    elif output_format == OutputFormat.CEF:
        return FileEventDictToCEFFormatter()
    else:
        return FileEventDictToRawJSONFormatter()
