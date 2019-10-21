import sys
from os import path
from socket import gaierror
from datetime import datetime, timedelta
from configparser import ConfigParser
from logging import StreamHandler, FileHandler, getLogger, INFO, Formatter
from logging.handlers import RotatingFileHandler

from c42secevents.logging.handlers import NoPrioritySysLogHandler
from c42secevents.common import convert_datetime_to_timestamp


def get_project_path():
    package_name = __name__.split(".")[0]
    path_to_this_file = path.realpath(__file__)
    last_pos = path_to_this_file.rfind(package_name)
    ending_pos = last_pos + len(package_name)
    desired_dir_name = path_to_this_file[0:ending_pos]
    return desired_dir_name


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
    save_path = get_project_path()
    log_path = "{0}/c42seceventcli_errors.log".format(save_path)
    logger = getLogger("Code42_SecEventCli_Error_Logger")
    formatter = Formatter("%(message)s")
    handler = RotatingFileHandler(log_path, maxBytes=250000000)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


def get_logger(formatter, destination, destination_type, syslog_port=514, syslog_protocol="TCP"):
    destination_type = destination_type.lower()
    logger = getLogger("Code42_SecEventCli_Logger")
    handler = _get_log_handler(
        destination=destination,
        destination_type=destination_type,
        syslog_port=syslog_port,
        syslog_protocol=syslog_protocol,
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(INFO)
    return logger


def _get_log_handler(destination, destination_type, syslog_port=514, syslog_protocol="TCP"):
    if destination_type == "stdout":
        return StreamHandler(sys.stdout)
    elif destination_type == "syslog":
        return _get_no_priority_syslog_handler(destination, syslog_port, syslog_protocol)
    elif destination_type == "file":
        return _get_file_handler(destination)


def _get_no_priority_syslog_handler(hostname, port=514, protocol="TCP"):
    try:
        return NoPrioritySysLogHandler(hostname=hostname, port=port, protocol=protocol)
    except (AttributeError, gaierror):
        print(
            "Error with provided syslog arguments: hostname={0}, port={1}, protocol={2}.".format(
                hostname, port, protocol
            )
        )
        exit(1)


def _get_file_handler(filename):
    try:
        return FileHandler(filename=filename)
    except IOError:
        print("Error with provided file path {0}. Try --dest path/to/file.".format(filename))
        exit(1)
