import os


class cleanup(object):
    def __init__(self, filename):    
        self.filename = filename

    def __enter__(self):
        return open(self.filename, "r")
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        os.remove(self.filename)


def cleanup_after_validation(filename):
    """Decorator to read response from file for `write-to` commands and cleanup the file after test
    execution.

    The decorated function should return validation function that takes the content of the file
    as input. e.g `test_alerts.py::test_alert_writes_to_file_and_filters_result_by_severity`
    """
    def wrap(test_function):
        def wrapper():
            validate = test_function()
            with cleanup(filename) as f:
                response = f.read()
                validate(response)
        return wrapper
    return wrap
