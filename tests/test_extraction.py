from c42eventextractor.extractors import BaseExtractor
from py42.response import Py42Response
from requests import Response

from code42cli.cmds.search.cursor_store import BaseCursorStore
from code42cli.cmds.search.extraction import create_handlers

key = "events"


class TestQuery:
    """"""


def search(*args, **kwargs):
    pass


def test_create_handlers_creates_handlers_that_pass_events_to_output_format(
    mocker, sdk
):
    class TestExtractor(BaseExtractor):
        def __init__(self, handlers, timestamp_filter):
            timestamp_filter._term = "test_term"
            super().__init__(key, search, handlers, timestamp_filter, TestQuery)

    output_format = mocker.MagicMock()
    cursor_store = mocker.MagicMock(sepc=BaseCursorStore)
    handlers = create_handlers(
        sdk, TestExtractor, cursor_store, "chk-name", False, output_format, "header"
    )
    http_response = mocker.MagicMock(spec=Response)
    events = [{"food": "bar"}]
    http_response.text = '{{"{0}": [{{"food": "bar"}}]}}'.format(key)
    py42_response = Py42Response(http_response)
    handlers.handle_response(py42_response)
    output_format.assert_called_once_with(events, "header")
