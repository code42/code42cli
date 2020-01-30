import sys
import logging
from os import path, makedirs
from datetime import datetime, timedelta
from configparser import ConfigParser
from logging.handlers import RotatingFileHandler

from c42secevents.logging.handlers import NoPrioritySysLogHandler
from c42secevents.common import convert_datetime_to_timestamp


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


def get_error_logger(service_name):
    log_path = get_user_project_path("log")
    log_path = "{0}/{1}_errors.log".format(log_path, service_name)
    logger = logging.getLogger("{0}_error_logger".format(service_name))
    formatter = logging.Formatter("%(asctime)s %(message)s")
    handler = RotatingFileHandler(log_path, maxBytes=250000000)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


class DestinationArgs(object):
    destination_type = None
    destination = None
    destination_port = None
    destination_protocol = None


def get_logger(formatter, service_name, destination_args):
    """Args:
           formatter: The formatter for logger.
           service_name: The name of the script getting the logger.
                Necessary for distinguishing multiple loggers.
           destination_args: DTO holding the destination_type, destination, destination_port, and destination_protocol.
        Returns:
            A logger with the correct handler per destination_type.
            For destination_type == stdout, it uses a StreamHandler.
            For destination_type == file, it uses a FileHandler.
            For destination_type == server, it uses a NoPrioritySyslogHandler.
    """

    logger = logging.getLogger("{0}_logger".format(service_name))
    handler = _get_log_handler(destination_args)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger


def _get_log_handler(destination_args):
    if destination_args.destination_type == "stdout":
        return logging.StreamHandler(sys.stdout)
    elif destination_args.destination_type == "server":
        return NoPrioritySysLogHandler(
            hostname=destination_args.destination,
            port=destination_args.destination_port,
            protocol=destination_args.destination_protocol,
        )
    elif destination_args.destination_type == "file":
        return logging.FileHandler(filename=destination_args.destination)


class SecArgs(object):
    def try_set(self, arg_name, cli_arg=None, config_arg=None):
        if cli_arg is not None:
            setattr(self, arg_name, cli_arg)
        elif config_arg is not None:
            setattr(self, arg_name, config_arg)
