class OutputFormat:
    TABLE = "TABLE"
    CSV = "CSV"
    JSON = "JSON"
    RAW = "RAW-JSON"

    def __iter__(self):
        return iter([self.TABLE, self.CSV, self.JSON, self.RAW])
