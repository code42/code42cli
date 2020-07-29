IS_CHECKPOINT_KEY = "use_checkpoint"


class OutputFormat:
    CEF = "CEF"
    JSON = "JSON"
    RAW = "RAW-JSON"

    def __iter__(self):
        return iter([self.CEF, self.JSON, self.RAW])


class AlertOutputFormat:
    JSON = "JSON"
    RAW = "RAW-JSON"

    def __iter__(self):
        return iter([self.JSON, self.RAW])


class ServerProtocol:
    TCP = "TCP"
    UDP = "UDP"

    def __iter__(self):
        return iter([self.TCP, self.UDP])
