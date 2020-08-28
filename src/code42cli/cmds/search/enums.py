from code42cli.output_formats import OutputFormat

IS_CHECKPOINT_KEY = "use_checkpoint"


class FileEventsOutputFormat(OutputFormat):
    CEF = "CEF"

    def __iter__(self):
        return iter([self.TABLE, self.CSV, self.JSON, self.RAW, self.CEF])


class ServerProtocol:
    TCP = "TCP"
    UDP = "UDP"

    def __iter__(self):
        return iter([self.TCP, self.UDP])
