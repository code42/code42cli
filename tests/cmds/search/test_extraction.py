import pytest
from c42eventextractor.extractors import BaseExtractor
from py42.response import Py42Response
from requests import Response

from code42cli import errors
from code42cli.cmds.search.cursor_store import BaseCursorStore
from code42cli.cmds.search.extraction import create_handlers
from code42cli.cmds.search.extraction import create_send_to_handlers
from code42cli.cmds.search.extraction import try_get_default_header
from code42cli.cmds.search.output_processor import print_events
from code42cli.output_formats import OutputFormat


key = "events"
header = {"property": "Property"}


class TestQuery:
    """"""

    pass


def search(*args, **kwargs):
    pass


def test_try_get_default_header_raises_cli_error_when_using_include_all_with_none_table_format():
    with pytest.raises(errors.Code42CLIError) as err:
        try_get_default_header(True, {}, OutputFormat.CSV)

    assert str(err.value) == "--include-all only allowed for non-Table output formats."


def test_try_get_default_header_uses_default_header_when_not_include_all_and_is_table():
    default_header = {"default": "header"}
    actual = try_get_default_header(False, default_header, OutputFormat.TABLE)
    assert actual is default_header


def test_try_get_default_header_returns_none_when_is_table_and_told_to_include_all():
    default_header = {"default": "header"}
    actual = try_get_default_header(True, default_header, OutputFormat.TABLE)
    assert actual is None


def test_create_handlers_creates_handlers_that_pass_events_to_output_format(
    mocker, sdk,
):
    class TestExtractor(BaseExtractor):
        def __init__(self, handlers, timestamp_filter):
            timestamp_filter._term = "test_term"
            super().__init__(key, search, handlers, timestamp_filter, TestQuery)

        def _get_timestamp_from_item(self, item):
            pass

    output_format = mocker.MagicMock()
    cursor_store = mocker.MagicMock(sepc=BaseCursorStore)
    output_function = print_events(output_format, header)
    handlers = create_handlers(
        sdk, TestExtractor, cursor_store, "chk-name", output_function=output_function,
    )
    http_response = mocker.MagicMock(spec=Response)
    events = [{"property": "bar"}]
    http_response.text = '{{"{0}": [{{"property": "bar"}}]}}'.format(key)
    py42_response = Py42Response(http_response)
    handlers.handle_response(py42_response)
    output_format.assert_called_once_with(events, header)


def test_send_to_handlers_creates_handlers_that_pass_events_to_logger(
    mocker, sdk, event_extractor_logger
):
    class TestExtractor(BaseExtractor):
        def __init__(self, handlers, timestamp_filter):
            timestamp_filter._term = "test_term"
            super().__init__(key, search, handlers, timestamp_filter, TestQuery)

        def _get_timestamp_from_item(self, item):
            pass

    cursor_store = mocker.MagicMock(sepc=BaseCursorStore)
    handlers = create_send_to_handlers(
        sdk, TestExtractor, cursor_store, "chk-name", event_extractor_logger
    )
    http_response = mocker.MagicMock(spec=Response)
    events = [{"property": "bar"}]
    http_response.text = '{{"{0}": [{{"property": "bar"}}]}}'.format(key)
    py42_response = Py42Response(http_response)
    handlers.handle_response(py42_response)
    event_extractor_logger.info.assert_called_once_with(events[0])
