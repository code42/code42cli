import pytest

from code42cli.cmds.search.enums import ServerProtocol
from code42cli.logger import NoPrioritySysLogHandlerWrapper


_TEST_HOST = "example.com"
_TEST_PORT = 5000
_TEST_PROTOCOL = ServerProtocol.UDP
_TEST_CERTS = "path/to/cert.crt"


@pytest.fixture()
def handler_initializer(mocker):
    mock = mocker.patch("code42cli.logger.handlers.NoPrioritySysLogHandler.__init__")
    mock.return_value = None
    return mock


class TestNoPrioritySysLogHandlerWrapper:
    def test_init_sets_handler_to_none(self):
        wrapper = NoPrioritySysLogHandlerWrapper(
            _TEST_HOST, _TEST_PORT, _TEST_PROTOCOL, _TEST_CERTS
        )
        assert wrapper._handler is None

    def test_handler_initializes_only_once(self, handler_initializer):
        wrapper = NoPrioritySysLogHandlerWrapper(
            _TEST_HOST, _TEST_PORT, _TEST_PROTOCOL, _TEST_CERTS
        )
        _ = wrapper.handler
        _ = wrapper.handler
        assert handler_initializer.call_count == 1

    def test_handler_initializes_handler_with_expected_properties(
        self, handler_initializer
    ):
        wrapper = NoPrioritySysLogHandlerWrapper(
            _TEST_HOST, _TEST_PORT, _TEST_PROTOCOL, _TEST_CERTS
        )
        _ = wrapper.handler
        handler_initializer.assert_called_once_with(
            _TEST_HOST, _TEST_PORT, _TEST_PROTOCOL, _TEST_CERTS
        )
