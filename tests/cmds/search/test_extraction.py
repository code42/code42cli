import pytest
from c42eventextractor.extractors import BaseExtractor
from py42.response import Py42Response
from requests import Response

from code42cli import errors
from code42cli.cmds.search.cursor_store import BaseCursorStore
from code42cli.cmds.search.extraction import create_handlers
from code42cli.cmds.search.extraction import handle_include_all

key = "events"
header = {"property": "Property"}


class TestQuery:
    """"""

    pass


def search(*args, **kwargs):
    pass


def test_handle_include_all_raises_cli_error_when_using_include_all_with_csv():
    def _format():
        pass

    with pytest.raises(errors.Code42CLIError) as err:
        handle_include_all(True, {}, _format)

    assert str(err.value) == "--include-all only allowed for non-Table output formats."


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
    handlers = create_handlers(
        sdk,
        TestExtractor,
        cursor_store,
        "chk-name",
        False,
        output_format,
        output_header=header,
    )
    http_response = mocker.MagicMock(spec=Response)
    events = [{"property": "bar"}]
    http_response.text = '{{"{0}": [{{"property": "bar"}}]}}'.format(key)
    py42_response = Py42Response(http_response)
    handlers.handle_response(py42_response)
    output_format.assert_called_once_with(events, header)
