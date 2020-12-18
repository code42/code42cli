import logging
import socket
import ssl
from logging.handlers import SysLogHandler

from code42cli.cmds.search.enums import ServerProtocol


class NoPrioritySysLogHandlerWrapper:
    """
    Uses NoPrioritySysLogHandler but does not make the connection in the constructor. Instead,
    it connects the first time you access the handler property. This makes testing against
    a syslog handler easier.
    Args:
        hostname: The hostname of the syslog server to send log messages to.
        port: The port of the syslog server to send log messages to.
        protocol: The protocol over which to submit syslog messages. Accepts TCP or UDP.
    """

    def __init__(self, hostname, port, protocol, use_insecure, certs):
        self.hostname = hostname
        self.port = port
        self.protocol = protocol
        self._handler = None
        self._use_insecure = use_insecure
        self.certs = certs

    @property
    def handler(self):
        if not self._handler:
            self._handler = self._create_handler()
        return self._handler

    def _create_handler(self):
        return NoPrioritySysLogHandler(
            self.hostname, self.port, self.protocol, self._use_insecure, self.certs
        )


class NoPrioritySysLogHandler(SysLogHandler):
    """
    Overrides the default implementation of SysLogHandler to not send a <PRI> at the
    beginning of the message. Most CEF consumers seem to not expect the <PRI> to be
    present in CEF messages. Attach to a logger via `.addHandler` to use.
    Args:
        hostname: The hostname of the syslog server to send log messages to.
        port: The port of the syslog server to send log messages to.
        protocol: The protocol over which to submit syslog messages. Accepts TCP or UDP.
    """

    def __init__(self, hostname, port, protocol, use_insecure, certs):
        self.address = (hostname, port)
        logging.Handler.__init__(self)
        
        # SSL required TCP
        if not use_insecure:
            protocol = ServerProtocol.TCP

        sock_type = _get_socket_type_from_protocol(protocol.lower().strip())
        self.unixsocket = False
        if sock_type is None:
            sock_type = socket.SOCK_DGRAM
        ress = socket.getaddrinfo(hostname, port, 0, sock_type)
        if not ress:
            raise OSError("getaddrinfo returns an empty list")
        err = None
        sock = None
        for res in ress:
            af, sock_type, proto, _, sa = res
            err = sock = None
            try:
                sock = socket.socket(af, sock_type, proto)
                # SSL setup
                if not use_insecure:
                    if certs:
                        sock = ssl.wrap_socket(
                            sock, ca_certs=certs, cert_reqs=ssl.CERT_REQUIRED
                        )
                    else:
                        sock = ssl.wrap_socket(sock, cert_reqs=ssl.CERT_NONE)

                if sock_type == socket.SOCK_STREAM:
                    sock.connect(sa)
                break
            except OSError as exc:
                err = exc
                if sock is not None:
                    sock.close()
        if err is not None:
            raise err
        self.socket = sock
        self.socktype = sock_type

    def emit(self, record):
        try:
            msg = self.format(record) + "\n"
            msg = msg.encode("utf-8")
            if self.unixsocket:
                try:
                    self.socket.send(msg)
                except OSError:
                    self.socket.close()
                    self._connect_unixsocket(self.address)
                    self.socket.send(msg)
            elif self.socktype == socket.SOCK_DGRAM:
                self.socket.sendto(msg, self.address)
            else:
                self.socket.sendall(msg)
        except Exception:
            self.handleError(record)

    def close(self):
        self.socket.close()
        logging.Handler.close(self)

    def _connect_unixsocket(self, address):
        use_socktype = self.socktype
        if use_socktype is None:
            use_socktype = socket.SOCK_DGRAM
        self.socket = socket.socket(socket.AF_UNIX, use_socktype)
        try:
            self.socket.connect(address)
            # it worked, so set self.socktype to the used type
            self.socktype = use_socktype
        except OSError:
            self.socket.close()
            if self.socktype is not None:
                # user didn't specify falling back, so fail
                raise
            use_socktype = socket.SOCK_STREAM
            self.socket = socket.socket(socket.AF_UNIX, use_socktype)
            try:
                self.socket.connect(address)
                # it worked, so set self.socktype to the used type
                self.socktype = use_socktype
            except OSError:
                self.socket.close()
                raise


def _get_socket_type_from_protocol(protocol):
    socket_type = None
    if protocol == "tcp":
        socket_type = socket.SOCK_STREAM
    elif protocol == "udp":
        socket_type = socket.SOCK_DGRAM

    if socket_type is None:
        msg = "Could not determine socket type. Expected TCP or UDP, got {}.".format(
            protocol
        )
        raise ValueError(msg)

    return socket_type
