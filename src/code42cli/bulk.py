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
        columns = [str(arg) for arg in argspec.args if arg not in [u"sdk", u"profile"]]
        path = path or u"{0}/{1}.csv".format(os.getcwd(), str(handler.__name__))
        _write_template_file(path, columns)


def _write_template_file(path, columns):
    with open(path, u"w", encoding=u"utf8") as new_csv:
        new_csv.write(u",".join(columns))


def run_bulk_process(file_path, row_handler, process_type):
    processor = _create_bulk_processor(file_path, row_handler, process_type)
    processor.run()


def _create_bulk_processor(file_path, row_handler, process_type):
    """A factory method to create the bulk processor, useful for testing purposes."""
    reader = _get_reader(process_type)
    return BulkProcessor(file_path, row_handler, reader)


def _get_reader(process_type):
    if process_type == u"add":
        return CSVReader()
    elif process_type == u"remove":
        return FlatFileReader()


class BulkProcessor(object):
    """A class for bulk processing a file. 
    
    Args:
        file_path (str or unicode): The path to the file for processing.
        row_handler (callable): To be executed on each row given **kwargs representing the column 
            names mapped to the properties found in the row. For example, if the file header 
            looked like `prop_a,prop_b` and the next row looked like `1,test`, then row handler 
            would receive args `prop_a: '1', prop_b: 'test'` when processing row 1. If it's a flat 
            file, the handler only needs to take an extra arg. 
    """

    def __init__(self, file_path, row_handler, reader):
        self.file_path = file_path
        self._row_handler = row_handler
        self._reader = reader
        self.__worker = Worker(5)

    def run(self):
        """Processes the csv file specified in the ctor, calling `self.row_handler` on each row."""
        with open(self.file_path, newline=u"", encoding=u"utf8") as bulk_file:
            for row in self._reader(bulk_file=bulk_file):
                self._process_row(row)
            self.__worker.wait()

    def _process_row(self, row):
        if type(row) is dict:
            self.__worker.do_async(
                lambda **kwargs: self._row_handler(**kwargs), **row
            )
        else:
            self.__worker.do_async(
                lambda *args, **kwargs: self._row_handler(*args, **kwargs), row.strip()
            )
        

class CSVReader(object):
    def __call__(self, *args, **kwargs):
        for row in csv.DictReader(kwargs.get(u"bulk_file")):
            yield row


class FlatFileReader(object):
    def __call__(self, *args, **kwargs):
        for row in kwargs[u"bulk_file"]:
            yield row
