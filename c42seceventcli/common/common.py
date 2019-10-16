import sys
from datetime import datetime, timedelta
from configparser import ConfigParser, NoOptionError, NoSectionError
from logging import StreamHandler, FileHandler, getLogger, INFO

from c42secevents.logging.handlers import NoPrioritySysLogHandler
from c42secevents.common import convert_datetime_to_timestamp


class SecurityEventConfigParser(object):
    _MAIN_SECTION = "Code42"

    def __init__(self, config_file):
        config = ConfigParser()
        config.read(config_file)
        self._config = config

    def get(self, key):
        try:
            return self._config.get(self._MAIN_SECTION, key)
        except (NoOptionError, NoSectionError):
            return None

    def get_bool(self, key):
        try:
            return self._config.getboolean(self._MAIN_SECTION, key)
        except (NoOptionError, NoSectionError):
            return None

    def get_int(self, key):
        try:
            return self._config.getint(self._MAIN_SECTION, key)
        except (NoOptionError, NoSectionError):
            return None


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


def get_logger(formatter, destination, destination_type="stdout"):
    destination_type = destination_type.lower()
    logger = getLogger("Code42_SecEventCli_Logger")
    handler = _get_log_handler(destination, destination_type)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(INFO)
    return logger


def _get_log_handler(destination, destination_type="stdout"):
    if destination_type == "stdout":
        return StreamHandler(sys.stdout)
    elif destination_type == "syslog":
        return NoPrioritySysLogHandler(destination)
    elif destination_type == "file":
        return FileHandler(filename=destination)
