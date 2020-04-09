import os
import inspect
import csv

from code42cli.compat import open, str
from code42cli.worker import WorkerGroup


def generate_template(handler, path=None):
    """Looks at the parameter names of `handler` and creates a csv file with the same column names.
    """
    if callable(handler):
        argspec = inspect.getfullargspec(handler)
        columns = [str(arg) for arg in argspec.args if arg not in [u"sdk", u"profile"]]
        path = path or u"{0}/{1}.csv".format(os.getcwd(), str(handler.__name__))
        with open(path, u"w", encoding=u"utf8") as new_csv:
            new_csv.write(u",".join(columns))


class BulkProcessor(object):
    def __init__(self, csv_file_path, row_handler, primary_key):
        self.csv_file_path = csv_file_path
        self.row_handler = row_handler
        self.primary_key = primary_key
        self.__workers = WorkerGroup(row_handler)

    def run(self):
        with open(self.csv_file_path, newline=u"") as csv_file:
            rows = csv.DictReader(csv_file)
            self._process_rows(rows)
        self.__workers.wait_all()

    def _process_rows(self, rows):
        for row in rows:
            worker = self.__workers.add_and_get_worker(row[self.primary_key])
            worker.do_async(self._process_row, **row)

    def _process_row(self, **kwargs):
        self.row_handler(**kwargs)
