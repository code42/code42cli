import ssl
from socket import AddressFamily
from socket import IPPROTO_TCP
from socket import IPPROTO_UDP
from socket import SOCK_DGRAM
from socket import SOCK_STREAM
from socket import socket
from socket import SocketKind

import pytest

from code42cli.cmds.search.enums import ServerProtocol
from code42cli.logger import FileEventDictToRawJSONFormatter
from code42cli.logger.handlers import NoPrioritySysLogHandler

_TEST_HOST = "example.com"
_TEST_PORT = 5000
_TEST_CERTS = "path/to/cert.crt"


@pytest.fixture()
def socket_initializer(mocker):
    new_socket = mocker.MagicMock()
    new_socket_magic_method = mocker.patch(
        "code42cli.logger.handlers.socket.socket.__new__"
    )
    new_socket_magic_method.return_value = new_socket
    return new_socket_magic_method


@pytest.fixture()
def socket_ssl_wrapper(mocker, socket_initializer):
    patch = mocker.patch("code42cli.logger.handlers.ssl.wrap_socket")
    patch.return_value = socket_initializer.return_value
    return patch


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
        assert actual == SocketKind.SOCK_STREAM

    def test_init_when_tls_sets_expected_sock_type(self):
        handler = NoPrioritySysLogHandler(
            _TEST_HOST, _TEST_PORT, ServerProtocol.TLS, None
        )
        actual = handler.socktype
        assert actual == SocketKind.SOCK_STREAM

    def test_init_when_udp_sets_expected_sock_type(self):
        handler = NoPrioritySysLogHandler(
            _TEST_HOST, _TEST_PORT, ServerProtocol.UDP, None
        )
        actual = handler.socktype
        assert actual == SocketKind.SOCK_DGRAM

    def test_init_sets_internal_socket_to_none(self):
        handler = NoPrioritySysLogHandler(
            _TEST_HOST, _TEST_PORT, ServerProtocol.UDP, None
        )
        assert handler._socket is None

    def test_init_when_not_tls_sets_insecure_to_true(self):
        handler = NoPrioritySysLogHandler(
            _TEST_HOST, _TEST_PORT, ServerProtocol.UDP, None
        )
        assert handler._use_insecure

    def test_init_when_using_tls_sets_insecure_to_false(self):
        handler = NoPrioritySysLogHandler(
            _TEST_HOST, _TEST_PORT, ServerProtocol.TLS, _TEST_CERTS
        )
        assert not handler._use_insecure
        assert handler._certs == _TEST_CERTS

    def test_socket_only_initializes_once(self, socket_initializer):
        handler = NoPrioritySysLogHandler(
            _TEST_HOST, _TEST_PORT, ServerProtocol.UDP, None
        )
        _ = handler.socket
        _ = handler.socket
        assert socket_initializer.call_count == 1

    def test_socket_when_udp_initializes_with_expected_properties(
        self, socket_initializer
    ):
        handler = NoPrioritySysLogHandler(
            _TEST_HOST, _TEST_PORT, ServerProtocol.UDP, None
        )
        _ = handler.socket
        socket_initializer.assert_called_once_with(
            socket, AddressFamily.AF_INET6, SOCK_DGRAM, IPPROTO_UDP
        )

    def test_socket_when_tcp_initializes_with_expected_properties(
        self, socket_initializer
    ):
        handler = NoPrioritySysLogHandler(
            _TEST_HOST, _TEST_PORT, ServerProtocol.TCP, None
        )
        _ = handler.socket
        socket_initializer.assert_called_once_with(
            socket, AddressFamily.AF_INET6, SOCK_STREAM, IPPROTO_TCP
        )
        assert socket_initializer.return_value.connect.call_count == 1

    def test_socket_when_tcp_connects_only_once(self, socket_initializer):
        handler = NoPrioritySysLogHandler(
            _TEST_HOST, _TEST_PORT, ServerProtocol.TCP, None
        )
        _ = handler.socket
        _ = handler.socket
        assert socket_initializer.return_value.connect.call_count == 1

    def test_socket_when_tls_initializes_with_expected_properties(
        self, socket_initializer, socket_ssl_wrapper
    ):
        handler = NoPrioritySysLogHandler(
            _TEST_HOST, _TEST_PORT, ServerProtocol.TLS, None
        )
        _ = handler.socket
        socket_initializer.assert_called_once_with(
            socket, AddressFamily.AF_INET6, SOCK_STREAM, IPPROTO_TCP
        )

    def test_socket_when_tls_and_given_certs_wraps_socket_with_certs(
        self, socket_initializer, socket_ssl_wrapper
    ):
        handler = NoPrioritySysLogHandler(
            _TEST_HOST, _TEST_PORT, ServerProtocol.TLS, _TEST_CERTS
        )
        _ = handler.socket
        socket_ssl_wrapper.assert_called_once_with(
            socket_initializer.return_value,
            ca_certs=_TEST_CERTS,
            cert_reqs=ssl.CERT_REQUIRED,
        )

    def test_socket_when_tls_and_not_given_certs_wraps_socket_with_certs(
        self, socket_initializer, socket_ssl_wrapper
    ):
        handler = NoPrioritySysLogHandler(
            _TEST_HOST, _TEST_PORT, ServerProtocol.TLS, None
        )
        _ = handler.socket
        socket_ssl_wrapper.assert_called_once_with(
            socket_initializer.return_value, ca_certs=None, cert_reqs=ssl.CERT_NONE
        )

    def test_socket_when_tls_connect_only_once(self, socket_ssl_wrapper):
        handler = NoPrioritySysLogHandler(
            _TEST_HOST, _TEST_PORT, ServerProtocol.TLS, None
        )
        _ = handler.socket
        _ = handler.socket
        assert socket_ssl_wrapper.return_value.connect.call_count == 1

    def test_emit_when_tcp_calls_socket_sendall_with_expected_message(
        self, socket_initializer, mock_file_event_log_record
    ):
        handler = NoPrioritySysLogHandler(
            _TEST_HOST, _TEST_PORT, ServerProtocol.TCP, None
        )
        formatter = FileEventDictToRawJSONFormatter()
        handler.setFormatter(formatter)
        handler.emit(mock_file_event_log_record)
        expected_message = (formatter.format(mock_file_event_log_record) + "\n").encode(
            "utf-8"
        )
        handler.socket.sendall.assert_called_once_with(expected_message)

    def test_emit_when_tls_calls_socket_sendall_with_expected_message(
        self, socket_initializer, socket_ssl_wrapper, mock_file_event_log_record
    ):
        handler = NoPrioritySysLogHandler(
            _TEST_HOST, _TEST_PORT, ServerProtocol.TLS, None
        )
        formatter = FileEventDictToRawJSONFormatter()
        handler.setFormatter(formatter)
        handler.emit(mock_file_event_log_record)
        expected_message = (formatter.format(mock_file_event_log_record) + "\n").encode(
            "utf-8"
        )
        handler.socket.sendall.assert_called_once_with(expected_message)

    def test_emit_when_udp_calls_socket_sendto_with_expected_message_and_address(
        self, socket_initializer, socket_ssl_wrapper, mock_file_event_log_record
    ):
        handler = NoPrioritySysLogHandler(
            _TEST_HOST, _TEST_PORT, ServerProtocol.UDP, None
        )
        formatter = FileEventDictToRawJSONFormatter()
        handler.setFormatter(formatter)
        handler.emit(mock_file_event_log_record)
        expected_message = (formatter.format(mock_file_event_log_record) + "\n").encode(
            "utf-8"
        )
        handler.socket.sendto.assert_called_once_with(
            expected_message, (_TEST_HOST, _TEST_PORT)
        )
