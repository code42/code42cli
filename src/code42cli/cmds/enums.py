class OutputFormat:
    ASCII = "ASCII-TABLE"
    CSV = "CSV"
    JSON = "JSON"
    RAW = "RAW-JSON"

    def __iter__(self):
        return iter([self.ASCII, self.CSV, self.JSON, self.RAW])
