import os
import inspect
import csv

from code42cli.compat import open, str
from code42cli.worker import Worker


def generate_template(handler, path=None):
    """Looks at the parameter names of `handler` and creates a csv file with the same column names.
    """
    if callable(handler):
        argspec = inspect.getargspec(handler)
        columns = [
            str(arg)
            for arg in argspec.args
            if arg not in [u"sdk", u"profile", u"*args", u"**kwargs"]
        ]
        path = path or u"{0}/{1}.csv".format(os.getcwd(), str(handler.__name__))
        _write_template_file(path, columns)


def _write_template_file(path, columns):
    with open(path, u"w", encoding=u"utf8") as new_csv:
        new_csv.write(u",".join(columns))


def create_bulk_processor(csv_file_path, row_handler):
    """A factory method to create the bulk processor, useful for testing purposes."""
    return BulkProcessor(csv_file_path, row_handler)


class BulkProcessor(object):
    """A class for bulk processing a csv file. 
    
    Args:
        csv_file_path (str): The path to the csv file for processing.
        row_handler (callable): To be executed on each row given **kwargs representing the column 
            names mapped to the properties found in the row. For example, if the csv file header 
            looked like `prop_a,prop_b` and the next row looked like `1,test`, then row handler 
            would receive args `prop_a: '1', prop_b: 'test'` when processing row 1.
    """

    def __init__(self, csv_file_path, row_handler):
        self.csv_file_path = csv_file_path
        self._row_handler = row_handler
        self.__worker = Worker(5)

    @property
    def row_handler(self):
        """A `callable` property  executed on each row in the csv file when `run()` is called."""
        return self._row_handler

    def run(self):
        """Processes the csv file specified in the ctor, calling `self.row_handler` on each row."""
        rows = self._get_rows()
        self._process_rows(rows)
        self.__worker.wait()

    def _get_rows(self):
        with open(self.csv_file_path, newline=u"", encoding=u"utf8") as csv_file:
            return csv.DictReader(csv_file)

    def _process_rows(self, rows):
        for row in rows:
            self.__worker.do_async(lambda **kwargs: self.row_handler(**kwargs), **row)
