import logging

from c42eventextractor.logging.formatters import FileEventDictToCEFFormatter
from c42eventextractor.logging.formatters import FileEventDictToJSONFormatter
from c42eventextractor.logging.formatters import FileEventDictToRawJSONFormatter

import code42cli.cmds.search.logger_factory as factory


def test_get_logger_for_stdout_has_info_level():
    logger = factory.get_logger_for_stdout("CEF")
    assert logger.level == logging.INFO


def test_get_logger_for_stdout_when_given_cef_format_uses_cef_formatter():
    logger = factory.get_logger_for_stdout("CEF")
    assert type(logger.handlers[0].formatter) == FileEventDictToCEFFormatter


def test_get_logger_for_stdout_when_given_json_format_uses_json_formatter():
    logger = factory.get_logger_for_stdout("JSON")
    assert type(logger.handlers[0].formatter) == FileEventDictToJSONFormatter


def test_get_logger_for_stdout_when_given_raw_json_format_uses_raw_json_formatter():
    logger = factory.get_logger_for_stdout("RAW-JSON")
    assert type(logger.handlers[0].formatter) == FileEventDictToRawJSONFormatter


def test_get_logger_for_stdout_when_called_twice_has_only_one_handler():
    factory.get_logger_for_stdout("CEF")
    logger = factory.get_logger_for_stdout("CEF")
    assert len(logger.handlers) == 1


def test_get_logger_for_stdout_uses_stream_handler():
    logger = factory.get_logger_for_stdout("CEF")
    assert type(logger.handlers[0]) == logging.StreamHandler
