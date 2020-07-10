import logging

from c42eventextractor.logging.formatters import (
    FileEventDictToCEFFormatter,
    FileEventDictToJSONFormatter,
    FileEventDictToRawJSONFormatter,
)

from code42cli.cmds.search.enums import OutputFormat
from code42cli.logger import (
    add_handler_to_logger,
    get_logger_for_stdout as get_stdout_logger,
)


def get_logger_for_stdout(output_format):
    """Gets the stdout logger for the given format.
        Args:
            output_format: CEF, JSON, or RAW_JSON. Each type results in a different logger instance.
    """
    formatter = _get_formatter(output_format)
    return get_stdout_logger(output_format.lower(), formatter)


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
