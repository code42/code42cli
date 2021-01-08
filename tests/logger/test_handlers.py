import ssl
from socket import IPPROTO_TCP
from socket import IPPROTO_UDP
from socket import SOCK_DGRAM
from socket import SOCK_STREAM
from socket import socket
from socket import SocketKind

import pytest

from code42cli.logger import FileEventDictToRawJSONFormatter
from code42cli.logger.enums import ServerProtocol
from code42cli.logger.handlers import NoPrioritySysLogHandler

_TEST_HOST = "example.com"
_TEST_PORT = 5000
_TEST_CERTS = "path/to/cert.crt"
tls_and_tcp_test = pytest.mark.parametrize(
    "protocol", (ServerProtocol.TLS_TCP, ServerProtocol.TCP)
)
tcp_and_udp_test = pytest.mark.parametrize(
    "protocol", (ServerProtocol.TCP, ServerProtocol.UDP)
)


class SocketMocks:
    mock_socket = None
    socket_initializer = None
    ssl_wrap_socket_mock = None


@pytest.fixture(autouse=True)
def socket_mocks(mocker):
    mocks = SocketMocks()
    new_socket = mocker.MagicMock(spec=socket)
    new_socket_magic_method = mocker.patch(
        "code42cli.logger.handlers.socket.socket.__new__"
    )
    new_socket_magic_method.return_value = new_socket
    wrap_socket_magic_method = mocker.patch("code42cli.logger.handlers.ssl.wrap_socket")
    wrap_socket_magic_method.return_value = new_socket
    mocks.mock_socket = new_socket
    mocks.socket_initializer = new_socket_magic_method
    mocks.ssl_wrap_socket_mock = wrap_socket_magic_method
    return mocks


class TestNoPrioritySysLogHandler:
    def test_init_sets_expected_address(self):
        handler = NoPrioritySysLogHandler(
            _TEST_HOST, _TEST_PORT, ServerProtocol.UDP, None
        )
        assert handler.address == (_TEST_HOST, _TEST_PORT)

    @tls_and_tcp_test
    def test_init_when_stream_based_sets_expected_sock_type(self, protocol):
        handler = NoPrioritySysLogHandler(_TEST_HOST, _TEST_PORT, protocol, None)
        actual = handler.socktype
        assert actual == SocketKind.SOCK_STREAM

    def test_init_when_udp_sets_expected_sock_type(self):
        handler = NoPrioritySysLogHandler(
            _TEST_HOST, _TEST_PORT, ServerProtocol.UDP, None
        )
        actual = handler.socktype
        assert actual == SocketKind.SOCK_DGRAM

    def test_init_sets_socket_to_none(self):
        handler = NoPrioritySysLogHandler(
            _TEST_HOST, _TEST_PORT, ServerProtocol.UDP, None
        )
        assert handler.socket is None

    @tcp_and_udp_test
    def test_init_when_not_tls_sets_insecure_to_true(self, protocol):
        handler = NoPrioritySysLogHandler(_TEST_HOST, _TEST_PORT, protocol, None)
        assert handler._use_insecure

    def test_init_when_using_tls_sets_insecure_to_false(self):
        handler = NoPrioritySysLogHandler(
            _TEST_HOST, _TEST_PORT, ServerProtocol.TLS_TCP, _TEST_CERTS
        )
        assert not handler._use_insecure
        assert handler._certs == _TEST_CERTS

    def test_connect_socket_only_connects_once(self, socket_mocks):
        handler = NoPrioritySysLogHandler(
            _TEST_HOST, _TEST_PORT, ServerProtocol.UDP, None
        )
        handler.connect_socket()
        handler.connect_socket()
        assert socket_mocks.socket_initializer.call_count == 1

    def test_connect_socket_when_udp_initializes_with_expected_properties(self, socket_mocks):
        handler = NoPrioritySysLogHandler(
            _TEST_HOST, _TEST_PORT, ServerProtocol.UDP, None
        )
        handler.connect_socket()
        call_args = socket_mocks.socket_initializer.call_args[0]
        assert call_args[0] == socket
        assert call_args[2] == SOCK_DGRAM
        assert call_args[3] == IPPROTO_UDP

    @tls_and_tcp_test
    def test_connect_socket_when_tcp_or_tls_initializes_with_expected_properties(
        self, socket_mocks, protocol
    ):
        handler = NoPrioritySysLogHandler(_TEST_HOST, _TEST_PORT, protocol, None)
        handler.connect_socket()
        call_args = socket_mocks.socket_initializer.call_args[0]
        assert call_args[0] == socket
        assert call_args[2] == SOCK_STREAM
        assert call_args[3] == IPPROTO_TCP
        assert socket_mocks.mock_socket.connect.call_count == 1

    @tls_and_tcp_test
    def test_conect_socket_when_tcp_or_tls_sets_timeout_for_connection_and_resets(
        self, socket_mocks, protocol
    ):
        handler = NoPrioritySysLogHandler(_TEST_HOST, _TEST_PORT, protocol, None)
        handler.connect_socket()
        call_args = socket_mocks.mock_socket.settimeout.call_args_list
        assert len(call_args) == 2
        assert call_args[0][0][0] == 10
        assert call_args[1][0][0] is None

    def test_connect_socket_when_tls_and_given_certs_wraps_socket_with_certs(
        self, socket_mocks
    ):
        handler = NoPrioritySysLogHandler(
            _TEST_HOST, _TEST_PORT, ServerProtocol.TLS_TCP, _TEST_CERTS
        )
        handler.connect_socket()
        socket_mocks.ssl_wrap_socket_mock.assert_called_once_with(
            socket_mocks.mock_socket, ca_certs=_TEST_CERTS, cert_reqs=ssl.CERT_REQUIRED,
        )

    def test_connect_socket_when_tls_and_not_given_certs_wraps_socket_with_cert_none(
        self, socket_mocks
    ):
        handler = NoPrioritySysLogHandler(
            _TEST_HOST, _TEST_PORT, ServerProtocol.TLS_TCP, None
        )
        handler.connect_socket()
        socket_mocks.ssl_wrap_socket_mock.assert_called_once_with(
            socket_mocks.mock_socket, ca_certs=None, cert_reqs=ssl.CERT_NONE
        )

    @tls_and_tcp_test
    def test_emit_when_tcp_calls_socket_sendall_with_expected_message(
        self, mock_file_event_log_record, protocol
    ):
        handler = NoPrioritySysLogHandler(
            _TEST_HOST, _TEST_PORT, protocol, None
        )
        handler.connect_socket()
        formatter = FileEventDictToRawJSONFormatter()
        handler.setFormatter(formatter)
        handler.emit(mock_file_event_log_record)
        expected_message = (formatter.format(mock_file_event_log_record) + "\n").encode(
            "utf-8"
        )
        handler.socket.sendall.assert_called_once_with(expected_message)

    def test_emit_when_udp_calls_socket_sendto_with_expected_message_and_address(
        self, mock_file_event_log_record
    ):
        handler = NoPrioritySysLogHandler(
            _TEST_HOST, _TEST_PORT, ServerProtocol.UDP, None
        )
        handler.connect_socket()
        formatter = FileEventDictToRawJSONFormatter()
        handler.setFormatter(formatter)
        handler.emit(mock_file_event_log_record)
        expected_message = (formatter.format(mock_file_event_log_record) + "\n").encode(
            "utf-8"
        )
        handler.socket.sendto.assert_called_once_with(
            expected_message, (_TEST_HOST, _TEST_PORT)
        )
