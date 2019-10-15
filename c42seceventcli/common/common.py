from datetime import datetime, timedelta
from configparser import ConfigParser, NoOptionError


class SecEventConfigParser(object):
    _SECTION = "Code42"

    def __init__(self, config_file):
        config = ConfigParser()
        self._is_valid = len(config.read(config_file)) > 0
        self._config = config

    @property
    def is_valid(self):
        return self._is_valid

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

    def _get(self, key):
        try:
            return self._config.get(self._SECTION, key)
        except NoOptionError:
            return None

    def _get_bool(self, key):
        try:
            return self._config.getboolean(self._SECTION, key)
        except NoOptionError:
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

    return convert_date_to_timestamp(time)


def convert_date_to_timestamp(date):
    return (date - datetime.utcfromtimestamp(0)).total_seconds()
