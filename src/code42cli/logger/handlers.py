import logging
import socket
import ssl
import sys
from logging.handlers import SysLogHandler

from code42cli.logger.enums import ServerProtocol


class SyslogServerNetworkConnectionError(Exception):
    """An error raised when the connection is disrupted during logging."""

    def __init__(self):
        super().__init__(
            "The network connection broke while sending results. "
            "This might happen if your connection requires TLS and you are attempting "
            "unencrypted TCP communication."
        )


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
        certs: Certs to specify when using TLS-TCP for the `protocol` argument. Use "ignore" for
            ssl.CERT_NONE (ignoring certificate validation).
    """

    def __init__(self, hostname, port, protocol, certs):
        self._hostname = hostname
        self._port = port
        self._protocol = protocol
        self._certs = certs
        self.address = (hostname, port)
        logging.Handler.__init__(self)
        self.socktype = _try_get_socket_type_from_protocol(protocol)
        self.socket = None

    @property
    def _wrap_socket(self):
        return self._protocol == ServerProtocol.TLS_TCP

    def connect_socket(self):
        """Call to initialize the socket. If using TCP/TLS, it will also establish the connection.
        """
        if not self.socket:
            self.socket = self._create_socket(self._hostname, self._port, self._certs)

    def _create_socket(self, hostname, port, certs):
        socket_info = self._get_socket_address_info(hostname, port)
        address_family, sock_type, proto, _, sa = socket_info
        sock = None
        try:
            sock = socket.socket(address_family, sock_type, proto)
            if self._wrap_socket:
                sock = _wrap_socket_for_ssl(sock, certs, hostname)
            if sock_type == socket.SOCK_STREAM:
                sock = _connect_socket(sock, sa)
            return sock
        except Exception as exc:
            if sock is not None:
                sock.close()
            raise exc

    def _get_socket_address_info(self, hostname, port):
        info = socket.getaddrinfo(hostname, port, 0, self.socktype)
        if not info:
            raise OSError("getaddrinfo() returns an empty list")
        return info[0]

    def emit(self, record):
        try:
            self._send_record(record)
        except Exception:
            self.handleError(record)

    def handleError(self, record):
        """Override logger's `handleError` method to exit if an exception is raised while trying to
        log, otherwise it would continue to gather and process events if the connection breaks but send
        them nowhere.
        """
        t, _, _ = sys.exc_info()
        if issubclass(t, ConnectionError):
            raise SyslogServerNetworkConnectionError()
        super().handleError(record)

    def _send_record(self, record):
        formatted_record = self.format(record)
        msg = formatted_record + "\n"
        msg = msg.encode("utf-8")
        if self.socktype == socket.SOCK_DGRAM:
            self.socket.sendto(msg, self.address)
        else:
            self.socket.sendall(msg)

    def close(self):
        if self._wrap_socket:
            self.socket.unwrap()
        self.socket.close()
        logging.Handler.close(self)


def _wrap_socket_for_ssl(sock, certs, hostname):
    do_ignore_certs = certs and certs.lower() == "ignore"
    if do_ignore_certs:
        certs = None
    context = ssl.create_default_context(cafile=certs)
    if do_ignore_certs:
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
    return context.wrap_socket(sock, server_hostname=hostname)


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
    msg = "Could not determine socket type. Expected one of {}, but got {}.".format(
        list(ServerProtocol()), protocol
    )
    raise ValueError(msg)
