from py42.choices import Choices


class JsonOutputFormat(Choices):
    JSON = "JSON"
    RAW = "RAW-JSON"

    def __iter__(self):
        return iter([self.JSON, self.RAW])


class OutputFormat(JsonOutputFormat):
    TABLE = "TABLE"
    CSV = "CSV"

    def __iter__(self):
        return iter([self.TABLE, self.CSV, self.JSON, self.RAW])


class SendToFileEventsOutputFormat(JsonOutputFormat):
    CEF = "CEF"

    def __iter__(self):
        return iter([self.CEF, self.JSON, self.RAW])


class FileEventsOutputFormat(OutputFormat):
    CEF = "CEF"

    def __iter__(self):
        return iter([self.TABLE, self.CSV, self.JSON, self.RAW, self.CEF])
