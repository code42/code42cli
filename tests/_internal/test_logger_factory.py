import pytest
import logging

from c42secevents.logging.formatters import AEDDictToCEFFormatter, AEDDictToJSONFormatter
import c42sec._internal.logger_factory as factory


@pytest.fixture
def no_priority_syslog_handler(mocker):
    mock_init = mocker.patch("c42secevents.logging.handlers.NoPrioritySysLogHandler.__init__")
    mock_init.return_value = None
    mock_new = mocker.patch("c42secevents.logging.handlers.NoPrioritySysLogHandler.__new__")
    mock = mocker.MagicMock()
    mock_new.return_value = mock
    return mock


def test_get_logger_for_stdout_has_info_level():
    logger = factory.get_logger_for_stdout("CEF")
    assert logger.level == logging.INFO


def test_get_logger_for_stdout_when_given_cef_format_uses_cef_formatter():
    logger = factory.get_logger_for_stdout("CEF")
    assert type(logger.handlers[0].formatter) == AEDDictToCEFFormatter


def test_get_logger_for_stdout_when_given_json_format_uses_json_formatter():
    logger = factory.get_logger_for_stdout("JSON")
    assert type(logger.handlers[0].formatter) == AEDDictToJSONFormatter
