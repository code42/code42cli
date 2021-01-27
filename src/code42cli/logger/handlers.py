import logging
import socket
import ssl
from logging.handlers import SysLogHandler

from code42cli.logger.enums import ServerProtocol


class NoPrioritySysLogHandler(SysLogHandler):
    """
    Overrides the default implementation of SysLogHandler to not send a `<PRI>` at the
    beginning of the message. Most CEF consumers seem to not expect the `<PRI>` to be
    present in CEF messages. Attach to a logger via `.addHandler` to use.

    `self.socket` is lazily loaded for testing purposes, so the connection does not get
    made for TCP/TLS until the first log record is about to be transmitted.

    Args:
        hostname: The hostname of the syslog server to send log messages to.
        port: The port of the syslog server to send log messages to.
        protocol: The protocol over which to submit syslog messages. Accepts TCP, UDP, or TLS.
    """

    def __init__(self, hostname, port, protocol, certs):
        self._hostname = hostname
        self._port = port
        self._certs = certs
        self.address = (hostname, port)
        logging.Handler.__init__(self)
        self._use_insecure = protocol != ServerProtocol.TLS_TCP
        self.socktype = _try_get_socket_type_from_protocol(protocol)
        self.socket = None

    def connect_socket(self):
        """Call to initialize the socket. If using TCP/TLS, it will also establish the connection."""
        if not self.socket:
            self.socket = self._create_socket(
                self._hostname, self._port, self._use_insecure, self._certs
            )

    def _create_socket(self, hostname, port, use_insecure, certs):
        socket_info = self._get_socket_address_info(hostname, port)
        sock = _try_create_socket_from_address_info(socket_info[0], use_insecure, certs)
        return sock

    def _get_socket_address_info(self, hostname, port):
        info = socket.getaddrinfo(hostname, port, 0, self.socktype)
        if not info:
            raise OSError("getaddrinfo() returns an empty list")
        return info

    def emit(self, record):
        try:
            self._send_record(record)
        except Exception:
            self.handleError(record)

    def _send_record(self, record):
        formatted_record = self.format(record)
        msg = formatted_record + "\n"
        msg = msg.encode("utf-8")
        if self.socktype == socket.SOCK_DGRAM:
            self.socket.sendto(msg, self.address)
        else:
            self.socket.sendall(msg)

    def close(self):
        if not self._use_insecure:
            self.socket.unwrap()
        self.socket.close()
        logging.Handler.close(self)


def _try_create_socket_from_address_info(info, use_insecure, certs):
    address_family, sock_type, proto, _, sa = info
    sock = None
    try:
        sock = _create_socket_from_uncoupled_address_info(
            address_family, sock_type, proto, use_insecure, certs, sa
        )
    except Exception as exc:
        if sock is not None:
            sock.close()
        raise exc

    return sock


def _create_socket_from_uncoupled_address_info(
    address_family, sock_type, proto, use_insecure, certs, sa
):
    sock = socket.socket(address_family, sock_type, proto)
    if not use_insecure:
        sock = _wrap_socket_for_ssl(sock, certs)
    if sock_type == socket.SOCK_STREAM:
        sock = _connect_socket(sock, sa)
    return sock


def _wrap_socket_for_ssl(sock, certs):
    certs = certs or None
    cert_reqs = ssl.CERT_REQUIRED if certs else ssl.CERT_NONE
    return ssl.wrap_socket(sock, ca_certs=certs, cert_reqs=cert_reqs)


def _connect_socket(sock, sa):
    sock.settimeout(10)
    sock.connect(sa)
    # Set timeout back to None for 'blocking' mode, required for `sendall()`.
    sock.settimeout(None)
    return sock


def _try_get_socket_type_from_protocol(protocol):
    socket_type = _get_socket_type_from_protocol(protocol)
    if socket_type is None:
        _raise_socket_type_error(protocol)
    return socket_type


def _get_socket_type_from_protocol(protocol):
    if protocol in [ServerProtocol.TCP, ServerProtocol.TLS_TCP]:
        return socket.SOCK_STREAM
    elif protocol == ServerProtocol.UDP:
        return socket.SOCK_DGRAM


def _raise_socket_type_error(protocol):
    msg = "Could not determine socket type. Expected one of {}, but got {}".format(
        list(ServerProtocol()), protocol
    )
    raise ValueError(msg)
