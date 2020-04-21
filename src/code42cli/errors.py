from code42cli.logger import get_error_logger, ERROR_LOG_FILE_NAME
from code42cli.util import is_interactive, print_error, get_user_project_path


ERRORED = False


def log_error(exception):
    """Logs the error to the CLI error log file. If running interactively, it will also print a 
    message telling the user the location of the error log file."""
    logger = get_error_logger()
    logger.error(exception)
    global ERRORED
    ERRORED = True
    print_errors_occurred_if_needed()


def print_errors_occurred_if_needed():
    """If interactive and errors occurred, it will print a message telling the user how to retrieve 
    error logs."""
    if is_interactive() and ERRORED:
        print_errors_occurred()


def print_errors_occurred():
    """Prints a message telling the user how to retrieve error logs."""
    print_error(get_error_message())


def get_error_message():
    """Returns the error message that is printed when errors occur."""
    path = get_user_project_path(u"log")
    return u"View exceptions that occurred at {}/{}.".format(path, ERROR_LOG_FILE_NAME)
