from code42cli.logger import get_error_logger
from code42cli.util import is_interactive, print_error

ERRORED = False


def log_error(exception):
    logger = get_error_logger()
    logger.error(exception)
    print_errors_occurred_if_needed()


def print_errors_occurred_if_needed():
    if is_interactive() and ERRORED:
        print_error(u"View exceptions that occurred at [HOME]/.code42cli/log/code42_errors.")
