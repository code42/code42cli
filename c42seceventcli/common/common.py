import sys
from os.path import expanduser, dirname, realpath
from datetime import datetime, timedelta
from configparser import ConfigParser
from logging import StreamHandler, FileHandler, getLogger, INFO, Formatter
from logging.handlers import RotatingFileHandler

from c42secevents.logging.handlers import NoPrioritySysLogHandler
from c42secevents.common import convert_datetime_to_timestamp


def get_config_args(config_file_path):
    args = {}
    parser = ConfigParser()
    if config_file_path:
        if not parser.read(expanduser(config_file_path)):
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


def get_error_logger():
    script_path = dirname(realpath(__file__))
    log_path = "{0}/c42seceventcli_errors.log".format(script_path)
    logger = getLogger("Code42_SecEventCli_Error_Logger")
    formatter = Formatter("%(message)s")
    handler = RotatingFileHandler(log_path, maxBytes=250000000)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


def _get_log_handler(destination, destination_type, syslog_port=514, syslog_protocol="TCP"):
    if destination_type == "stdout":
        return StreamHandler(sys.stdout)
    elif destination_type == "syslog":
        return NoPrioritySysLogHandler(
            hostname=destination, port=syslog_port, protocol=syslog_protocol
        )
    elif destination_type == "file":
        return FileHandler(filename=destination)
