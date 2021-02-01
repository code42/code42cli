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
from code42cli.logger.handlers import NoPrioritySysLogHandler, SyslogServerNetworkConnectionError

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

    class SSLMocks:
        mock_ssl_context = None
        context_creator = None


@pytest.fixture(autouse=True)
def socket_mocks(mocker):
    mocks = SocketMocks()
    new_socket = mocker.MagicMock(spec=ssl.SSLSocket)
    mocks.mock_socket = new_socket
    mocks.socket_initializer = _get_normal_socket_initializer_mocks(mocker, new_socket)
    mocks.SSLMocks.mock_ssl_context = mocker.MagicMock(ssl.SSLContext)
    mocks.SSLMocks.mock_ssl_context.wrap_socket.return_value = new_socket
    mocks.SSLMocks.context_creator = mocker.patch(
        "code42cli.logger.handlers.ssl.create_default_context"
    )
    mocks.SSLMocks.context_creator.return_value = mocks.SSLMocks.mock_ssl_context
    return mocks


@pytest.fixture()
def broken_pipe_error(mocker):
    mock_exc_info = mocker.patch("code42cli.logger.handlers.sys.exc_info")
    mock_exc_info.return_value = (BrokenPipeError, None, None)
    return mock_exc_info


def _get_normal_socket_initializer_mocks(mocker, new_socket):
    new_socket_magic_method = mocker.patch(
        "code42cli.logger.handlers.socket.socket.__new__"
    )
    new_socket_magic_method.return_value = new_socket
    return new_socket_magic_method


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
    def test_init_when_not_tls_sets_wrap_socket_to_false(self, protocol):
        handler = NoPrioritySysLogHandler(_TEST_HOST, _TEST_PORT, protocol, None)
        assert not handler._wrap_socket

    def test_init_when_using_tls_sets_wrap_socket_to_true(self):
        handler = NoPrioritySysLogHandler(
            _TEST_HOST, _TEST_PORT, ServerProtocol.TLS_TCP, _TEST_CERTS
        )
        assert handler._wrap_socket
        assert handler._certs == _TEST_CERTS

    def test_connect_socket_only_connects_once(self, socket_mocks):
        handler = NoPrioritySysLogHandler(
            _TEST_HOST, _TEST_PORT, ServerProtocol.UDP, None
        )
        handler.connect_socket()
        handler.connect_socket()
        assert socket_mocks.socket_initializer.call_count == 1

    def test_connect_socket_when_udp_initializes_with_expected_properties(
        self, socket_mocks
    ):
        handler = NoPrioritySysLogHandler(
            _TEST_HOST, _TEST_PORT, ServerProtocol.UDP, None
        )
        handler.connect_socket()
        call_args = socket_mocks.socket_initializer.call_args[0]
        assert call_args[0] == socket
        assert call_args[2] == SOCK_DGRAM
        assert call_args[3] == IPPROTO_UDP

    @tls_and_tcp_test
    def test_connect_socket_when_tcp_initializes_with_expected_properties(
        self, socket_mocks, protocol
    ):
        handler = NoPrioritySysLogHandler(_TEST_HOST, _TEST_PORT, protocol, None)
        handler.connect_socket()
        call_args = socket_mocks.socket_initializer.call_args[0]
        assert call_args[0] == socket
        assert call_args[2] == SOCK_STREAM
        assert call_args[3] == IPPROTO_TCP
        assert socket_mocks.mock_socket.connect.call_count == 1

    def test_connect_when_tls_calls_create_default_context(self, socket_mocks):
        handler = NoPrioritySysLogHandler(
            _TEST_HOST, _TEST_PORT, ServerProtocol.TLS_TCP, "certs"
        )
        handler.connect_socket()
        call_args = socket_mocks.SSLMocks.context_creator.call_args
        assert call_args[1]["cafile"] == "certs"

    @pytest.mark.parametrize("ignore", ("ignore", "IGNORE"))
    def test_connect_when_tls_and_told_to_ignore_certs_sets_expected_context_properties(
        self, socket_mocks, ignore
    ):
        handler = NoPrioritySysLogHandler(
            _TEST_HOST, _TEST_PORT, ServerProtocol.TLS_TCP, ignore
        )
        handler.connect_socket()
        assert socket_mocks.SSLMocks.mock_ssl_context.verify_mode == ssl.CERT_NONE
        assert not socket_mocks.SSLMocks.mock_ssl_context.check_hostname

    @pytest.mark.parametrize("ignore", ("ignore", "IGNORE"))
    def test_connect_when_tls_and_told_to_ignore_certs_creates_context_with_none_certs(
        self, socket_mocks, ignore
    ):
        handler = NoPrioritySysLogHandler(
            _TEST_HOST, _TEST_PORT, ServerProtocol.TLS_TCP, ignore
        )
        handler.connect_socket()
        socket_mocks.SSLMocks.context_creator.assert_called_once_with(cafile=None)

    @tls_and_tcp_test
    def test_connect_socket_when_tcp_or_tls_sets_timeout_for_connection_and_resets(
        self, socket_mocks, protocol
    ):
        handler = NoPrioritySysLogHandler(_TEST_HOST, _TEST_PORT, protocol, None)
        handler.connect_socket()
        call_args = socket_mocks.mock_socket.settimeout.call_args_list
        assert len(call_args) == 2
        assert call_args[0][0][0] == 10
        assert call_args[1][0][0] is None

    @tls_and_tcp_test
    def test_emit_when_tcp_calls_socket_sendall_with_expected_message(
        self, mock_file_event_log_record, protocol
    ):
        handler = NoPrioritySysLogHandler(_TEST_HOST, _TEST_PORT, protocol, None)
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
    
    def test_handle_error_raises_expected_error(
        self, mock_file_event_log_record, broken_pipe_error
    ):
        handler = NoPrioritySysLogHandler(
            _TEST_HOST, _TEST_PORT, ServerProtocol.UDP, None
        )
        with pytest.raises(SyslogServerNetworkConnectionError):
            handler.handleError(mock_file_event_log_record)

    def test_close_when_using_tls_unwraps_socket(self):
        handler = NoPrioritySysLogHandler(
            _TEST_HOST, _TEST_PORT, ServerProtocol.TLS_TCP, None
        )
        handler.connect_socket()
        handler.close()
        assert handler.socket.unwrap.call_count == 1

    @tcp_and_udp_test
    def test_close_when_not_using_tls_does_not_unwrap_socket(self, protocol):
        handler = NoPrioritySysLogHandler(_TEST_HOST, _TEST_PORT, protocol, None)
        handler.connect_socket()
        handler.close()
        assert not handler.socket.unwrap.call_count

    def test_close_globally_closes(self, mocker):
        global_close = mocker.patch("code42cli.logger.handlers.logging.Handler.close")
        handler = NoPrioritySysLogHandler(
            _TEST_HOST, _TEST_PORT, ServerProtocol.UDP, None
        )
        handler.connect_socket()
        handler.close()
        assert global_close.call_count == 1
