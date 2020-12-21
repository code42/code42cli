import pytest

from code42cli.cmds.search.enums import ServerProtocol
from code42cli.logger.handlers import NoPrioritySysLogHandler

_TEST_HOST = "example.com"
_TEST_PORT = 5000
_TEST_CERTS = "path/to/cert.crt"


@pytest.fixture()
def handler_initializer(mocker):
    mock = mocker.patch("code42cli.logger.handlers.NoPrioritySysLogHandler.__init__")
    mock.return_value = None
    return mock


class TestNoPrioritySysLogHandler:
    def test_init_sets_expected_address(self):
        handler = NoPrioritySysLogHandler(
            _TEST_HOST, _TEST_PORT, ServerProtocol.UDP, None
        )
        assert handler.address == (_TEST_HOST, _TEST_PORT)

    def test_init_when_tcp_sets_expected_sock_type(self):
        handler = NoPrioritySysLogHandler(
            _TEST_HOST, _TEST_PORT, ServerProtocol.TCP, None
        )
        actual = handler.socktype
        assert actual
