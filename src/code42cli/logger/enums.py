class ServerProtocol:
    TCP = "TCP"
    UDP = "UDP"
    TLS = "TLS"

    def __iter__(self):
        return iter([self.TCP, self.UDP, self.TLS])
