from requests import Response

from c42eventextractor.extractors import BaseExtractor
from py42.response import Py42Response

from code42cli.cmds.search.cursor_store import BaseCursorStore
from code42cli.cmds.search.extraction import create_handlers

key = "events"


class TestQuery(object):
    """"""


def search(*args, **kwargs):
    pass


class TestExtractor(BaseExtractor):
    def __init__(self, handlers, timestamp_filter):
        timestamp_filter._term = "test_term"
        super().__init__(key, search, handlers, timestamp_filter, TestQuery)


def test_create_handlers(mocker, sdk):
    output_format = mocker.MagicMock()
    cursor_store = mocker.MagicMock(sepc=BaseCursorStore)
    handlers = create_handlers(
        sdk, TestExtractor, cursor_store, "chk-name", False, output_format, "header"
    )
    http_response = mocker.MagicMock(spec=Response)
    events = [{"food": "bar"}]
    http_response.text = '{{"{0}": "{1}"}}'.format(key, events)
    py42_response = Py42Response(http_response)
    handlers.handle_response(py42_response)
    output_format.assert_called_once_with(events, "header")
