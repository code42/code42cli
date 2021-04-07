import re
from datetime import datetime
from datetime import timedelta
from datetime import timezone

import chardet
import click
from click.exceptions import BadParameter

from code42cli.logger import CliLogger


class AutoDecodedFile(click.File):
    """Attempts to autodetect file's encoding prior to normal click.File processing."""

    def convert(self, value, param, ctx):
        try:
            with open(value, "rb") as file:
                self.encoding = chardet.detect(file.read())["encoding"]
            if self.encoding is None:
                CliLogger().log_error(f"Failed to detect encoding of file: {value}")
        except Exception:
            pass  # we'll let click.File do it's own exception handling for the filepath

        return super().convert(value, param, ctx)


class FileOrString(AutoDecodedFile):
    """Declares a parameter to be a file (if the argument begins with `@`), otherwise accepts it as
    a string.
    """

    def __init__(self):
        super().__init__("r")

    def convert(self, value, param, ctx):
        if value.startswith("@") or value == "-":
            value = value.lstrip("@")
            file = super().convert(value, param, ctx)
            return file.read()
        else:
            return value


class MagicDate(click.ParamType):
    """Declares a parameter to be a 'magic' date string. Accepts an optional `round` argument
    which can be a function that takes a datetime and returns it rounded appropriately. This allows
    imprecise "day" input values (2020-01-01, 3d) to be rounded to the start or end of the day
    if needed. Accepts the following values as user input:

    timestamp formats:
        yyyy-MM-dd
        yyyy-MM-dd HH
        yyyy-MM-dd HH:MM
        yyyy-MM-dd HH:MM:SS

    short-string (day, hour, min) formats:
        30d
        24h
        15m

    and converts them to datetime objects.
    """

    TIMESTAMP_REGEX = re.compile(r"(\d{4}-\d{2}-\d{2})(?:$|T|\s+)([0-9:]+)?")
    MAGIC_TIME_REGEX = re.compile(r"(\d+)([dhmDHM])$")
    HELP_TEXT = (
        "Accepts a date/time in yyyy-MM-dd (UTC) or yyyy-MM-dd HH:MM:SS "
        "(UTC+24-hr time) format where the 'time' portion of the string "
        "can be partial (e.g. '2020-01-01 12' or '2020-01-01 01:15') or "
        "a 'short time' value representing days (30d), hours (24h) or "
        "minutes (15m) from the current time."
    )

    name = "magicdate"

    def __init__(self, rounding_func=None):
        self.round = rounding_func

    def get_metavar(self, param):
        return "[DATE|TIMESTAMP|SHORT_TIME]"

    def __repr__(self):
        return "MagicDate"

    def convert(self, value, param, ctx):
        timestamp_match = self.TIMESTAMP_REGEX.match(value)
        magic_match = self.MAGIC_TIME_REGEX.match(value)

        if timestamp_match:
            date, time = timestamp_match.groups()
            dt = self._get_dt_from_date_time_pair(date, time)
            if not time and callable(self.round):
                dt = self.round(dt)

        elif magic_match:
            num, period = magic_match.groups()
            dt = self._get_dt_from_magic_time_pair(num, period)
            if period == "d" and callable(self.round):
                dt = self.round(dt)

        else:
            self.fail(self.HELP_TEXT, param=param)

        return dt.replace(tzinfo=timezone.utc)

    @staticmethod
    def _get_dt_from_magic_time_pair(num, period):
        num = int(num)
        period = period.lower()
        if period == "d":
            delta = timedelta(days=num)
        elif period == "h":
            delta = timedelta(hours=num)
        elif period == "m":
            delta = timedelta(minutes=num)
        else:
            raise BadParameter(
                "Couldn't parse magic time string: {}{}".format(num, period)
            )
        return datetime.utcnow() - delta

    @staticmethod
    def _get_dt_from_date_time_pair(date, time):
        date_format = "%Y-%m-%d %H:%M:%S"
        if time:
            time = "{}:{}:{}".format(*time.split(":") + ["00", "00"])
        else:
            time = "00:00:00"
        date_string = "{} {}".format(date, time)
        try:
            dt = datetime.strptime(date_string, date_format)
        except ValueError:
            raise BadParameter("Unable to parse date string: {}.".format(date_string))
        else:
            return dt


class MapChoice(click.Choice):
    """Choice subclass that takes an extra map of additional 'valid' keys to map to correct
    choices list, allowing backward compatible choice changes. The extra keys don't show up
    in help text, but work when passed as a choice.
    """

    def __init__(self, choices, extras_map, **kwargs):
        self.extras_map = extras_map
        super().__init__(choices, **kwargs)

    def convert(self, value, param, ctx):
        if value in self.extras_map:
            value = self.extras_map[value]
        return super().convert(value, param, ctx)
