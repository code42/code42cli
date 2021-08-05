from datetime import datetime
from datetime import timedelta
from datetime import timezone

import pytest
from click.exceptions import BadParameter

from .conftest import begin_date_str
from .conftest import begin_date_str_with_t_time
from .conftest import begin_date_str_with_time
from .conftest import end_date_str
from .conftest import end_date_str_with_time
from .conftest import get_test_date
from code42cli.click_ext.types import MagicDate
from code42cli.date_helper import round_datetime_to_day_end
from code42cli.date_helper import round_datetime_to_day_start

one_ms = timedelta(milliseconds=1)


def utc(dt):
    return dt.replace(tzinfo=timezone.utc)


class TestMagicDateNoRounding:
    md = MagicDate()

    def convert(self, val):
        return self.md.convert(val, ctx=None, param=None)

    def test_when_given_date_str_parses_successfully(self):
        actual = self.convert(begin_date_str)
        expected = utc(datetime.strptime(begin_date_str, "%Y-%m-%d"))
        assert actual == expected

    @pytest.mark.parametrize(
        "param", [begin_date_str_with_time, begin_date_str_with_t_time],
    )
    def test_when_given_date_str_with_time_parses_successfully(self, param):
        actual = self.convert(param)
        expected = utc(datetime.strptime(begin_date_str_with_time, "%Y-%m-%d %H:%M:%S"))
        assert actual == expected

    @pytest.mark.parametrize("param", ["20d", "20D"])
    def test_when_given_magic_days_parses_successfully(self, param):
        actual_date = self.convert(param)
        expected_date = utc(get_test_date(days_ago=20))
        assert actual_date - expected_date < one_ms

    @pytest.mark.parametrize("param", ["20h", "20H"])
    def test_when_given_magic_hours_parses_successfully(self, param):
        actual = self.convert(param)
        expected = utc(get_test_date(hours_ago=20))
        assert expected - actual < one_ms

    @pytest.mark.parametrize("param", ["20m", "20M"])
    def test_when_given_magic_minutes_parses_successfully(self, param):
        actual = self.convert(param)
        expected = utc(get_test_date(minutes_ago=20))
        assert expected - actual < one_ms

    @pytest.mark.parametrize(
        "badparam",
        [
            "20days",
            "20S",
            "d20",
            "01-01-2020",
            "2020-01-0110:10:10",
            "2020-01-01 30:30:30",
        ],
    )
    def test_when_given_bad_values_raises_exception(self, badparam):
        with pytest.raises(BadParameter):
            self.convert(badparam)


class TestMagicDateRoundingToStart:
    md = MagicDate(rounding_func=round_datetime_to_day_start)

    def convert(self, val):
        return self.md.convert(val, ctx=None, param=None)

    def test_when_given_date_str_parses_successfully(self):
        actual = self.convert(begin_date_str)
        expected = utc(datetime.strptime(begin_date_str, "%Y-%m-%d"))
        assert actual == expected

    def test_when_given_date_str_with_time_parses_successfully(self,):
        actual = self.convert(begin_date_str_with_time)
        expected = utc(datetime.strptime(begin_date_str_with_time, "%Y-%m-%d %H:%M:%S"))
        assert actual == expected

    def test_when_given_magic_days_parses_successfully(self):
        actual_date = self.convert("20d")
        expected_date = utc(get_test_date(days_ago=20))
        assert actual_date - expected_date < one_ms

    def test_when_given_magic_hours_parses_successfully(self):
        actual = self.convert("20h")
        expected = utc(get_test_date(hours_ago=20))
        assert expected - actual < one_ms

    def test_when_given_magic_minutes_parses_successfully(self):
        actual = self.convert("20m")
        expected = utc(get_test_date(minutes_ago=20))
        assert expected - actual < one_ms


class TestMagicDateRoundingToEnd:
    md = MagicDate(rounding_func=round_datetime_to_day_end)

    def convert(self, val):
        return self.md.convert(val, ctx=None, param=None)

    def test_when_given_date_str_parses_successfully(self):
        actual = self.convert(end_date_str)
        expected = datetime.strptime(end_date_str, "%Y-%m-%d")
        expected = utc(
            expected.replace(hour=23, minute=59, second=59, microsecond=999999)
        )
        assert actual == expected

    def test_when_given_date_str_with_time_parses_successfully(self):
        actual = self.convert(end_date_str_with_time)
        expected = utc(datetime.strptime(end_date_str_with_time, "%Y-%m-%d %H:%M:%S"))
        assert actual == expected

    def test_when_given_magic_days_parses_successfully(self):
        actual_date = self.convert("20d")
        expected_date = get_test_date(days_ago=20)
        expected_date = utc(
            expected_date.replace(hour=23, minute=59, second=59, microsecond=999999)
        )
        assert actual_date == expected_date

    def test_when_given_magic_hours_parses_successfully(self):
        actual = self.convert("20h")
        expected = utc(get_test_date(hours_ago=20))
        assert expected - actual < one_ms

    def test_when_given_magic_minutes_parses_successfully(self):
        actual = self.convert("20m")
        expected = utc(get_test_date(minutes_ago=20))
        assert expected - actual < one_ms
