import sys
from os import path, makedirs
import keyring
from keyring.errors import PasswordDeleteError
from datetime import datetime, timedelta
from configparser import ConfigParser
from logging import StreamHandler, FileHandler, getLogger, INFO, Formatter
from logging.handlers import RotatingFileHandler

from c42secevents.logging.handlers import NoPrioritySysLogHandler
from c42secevents.common import convert_datetime_to_timestamp


def get_user_project_path(subdir=None):
    """The path on the system user directory to the directory .c42seceventcli"""
    package_name = __name__.split(".")[0]
    home = path.expanduser("~")
    user_project_path = path.join(home, ".{0}".format(package_name), subdir)

    if not path.exists(user_project_path):
        makedirs(user_project_path)

    return user_project_path


def get_input(prompt):
    if sys.version_info >= (3, 0):
        return input(prompt)
    else:
        return raw_input(prompt)


def get_config_args(config_file_path):
    args = {}
    parser = ConfigParser()
    if config_file_path:
        if not parser.read(path.expanduser(config_file_path)):
            raise IOError("Supplied an empty config file {0}".format(config_file_path))

    if not parser.sections():
        return args

    items = parser.items("Code42")
    for item in items:
        args[item[0]] = item[1]

    return args


def parse_timestamp(input_string):
    try:
        time = datetime.strptime(input_string, "%Y-%m-%d")
    except ValueError:
        if input_string and input_string.isdigit():
            now = datetime.utcnow()
            time = now - timedelta(minutes=int(input_string))
        else:
            raise ValueError("input must be a positive integer or a date in YYYY-MM-DD format.")

    return convert_datetime_to_timestamp(time)


def get_error_logger():
    log_path = get_user_project_path("log")
    log_path = "{0}/c42seceventcli_aed_errors.log".format(log_path)
    logger = getLogger("Code42_SecEventCli_Error_Logger")
    formatter = Formatter("%(asctime)s %(message)s")
    handler = RotatingFileHandler(log_path, maxBytes=250000000)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


def get_logger(
    formatter, destination, destination_type, destination_port=514, destination_protocol="TCP"
):
    destination_type = destination_type.lower()
    logger = getLogger("Code42_SecEventCli_Logger")
    handler = _get_log_handler(
        destination=destination,
        destination_type=destination_type,
        destination_port=destination_port,
        destination_protocol=destination_protocol,
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(INFO)
    return logger


def _get_log_handler(
    destination, destination_type, destination_port=514, destination_protocol="TCP"
):
    if destination_type == "stdout":
        return StreamHandler(sys.stdout)
    elif destination_type == "server":
        return NoPrioritySysLogHandler(
            hostname=destination, port=destination_port, protocol=destination_protocol
        )
    elif destination_type == "file":
        return FileHandler(filename=destination)


def delete_stored_password(service_name, username):
    try:
        keyring.delete_password(service_name, username)
    except PasswordDeleteError:
        return
