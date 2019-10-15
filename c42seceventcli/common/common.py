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
        self._config = config

    def parse_server(self):
        return self._get("server")

    def parse_username(self):
        return self._get("username")

    def parse_begin_date(self):
        return self._get("begin_date")

    def parse_end_date(self):
        return self._get("end_date")

    def parse_ignore_ssl_errors(self):
        return self._get_bool("ignore_ssl_errors")

    def parse_output_format(self):
        return self._get("output_format")

    def parse_record_cursor(self):
        return self._get("record_cursor")

    def parse_exposure_types(self):
        types = self._get("exposure_types")
        return types.split(",") if types else None

    def parse_debug_mode(self):
        return self._get_bool("debug_mode")

    def parse_destination_type(self):
        return self._get("destination_type")

    def parse_destination(self):
        return self._get("destination")

    def parse_syslog_port(self):
        return self._get("destination_port")

    def parse_syslog_protocol(self):
        return self._get("destination_protocol")

    def _get(self, key):
        try:
            return self._config.get(self._MAIN_SECTION, key)
        except (NoOptionError, NoSectionError):
            return None

    def _get_bool(self, key):
        try:
            return self._config.getboolean(self._MAIN_SECTION, key)
        except (NoOptionError, NoSectionError):
            return None

    def _get_int(self, key):
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


def get_logger(formatter, destination):
    logger = getLogger("Code42_SecEventCli_Logger")
    handler = _get_log_handler(destination)
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
