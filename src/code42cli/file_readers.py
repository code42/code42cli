import csv

from code42cli.errors import BadFileError


class CliFileReader(object):
    _ROWS_COUNT = -1

    def __init__(self, file_path):
        self.file_path = file_path

    def __call__(self, *args, **kwargs):
        pass

    def get_rows_count(self):
        if self._ROWS_COUNT == -1:
            self._ROWS_COUNT = sum(1 for _ in open(self.file_path))
        if self._ROWS_COUNT == 0:
            raise BadFileError(u"Given empty file {}.".format(self.file_path))
        return self._ROWS_COUNT


class CSVReader(CliFileReader):
    """A generator that yields header keys mapped to row values from a csv file."""

    def __init__(self, file_path):
        with open(file_path) as f:
            try:
                self.has_header = csv.Sniffer().has_header(next(f))
            except StopIteration:
                raise BadFileError(u"Given empty file {}.".format(file_path))
        super(CSVReader, self).__init__(file_path)

    def __call__(self, *args, **kwargs):
        for row in csv.DictReader(kwargs.get(u"bulk_file")):
            yield row

    def get_rows_count(self):
        rows_count = super(CSVReader, self).get_rows_count()
        return rows_count - 1 if self.has_header else rows_count


class FlatFileReader(CliFileReader):
    """A generator that yields a single-value per row from a file."""

    def __call__(self, *args, **kwargs):
        for row in kwargs[u"bulk_file"]:
            yield row


def create_csv_reader(file_path):
    return CSVReader(file_path)


def create_flat_file_reader(file_path):
    return FlatFileReader(file_path)
