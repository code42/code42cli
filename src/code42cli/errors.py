from code42cli.logger import get_error_logger, ERROR_LOG_FILE_NAME
from code42cli.util import is_interactive, print_error, get_user_project_path

ERRORED = False


def log_error(exception):
    logger = get_error_logger()
    logger.error(exception)
    print_errors_occurred_if_needed()


def print_errors_occurred_if_needed():
    if is_interactive() and ERRORED:
        path = get_user_project_path(u"log")
        print_error(u"View exceptions that occurred at {}/{}.".format(path, ERROR_LOG_FILE_NAME))
