import pytest
from datetime import datetime

from c42seceventcli.common.common import SecurityEventConfigParser


_DUMMY_KEY = "Key"


@pytest.fixture
def mock_config_get_function(mocker):
    return mocker.patch("configparser.ConfigParser.get")


class TestSecurityEventConfigParser(object):
    def test_get_returns_expected_value(self, mock_config_get_function):
        expected = "Value"
        mock_config_get_function.return_value = expected
        parser = SecurityEventConfigParser("test")
        actual = parser.get(_DUMMY_KEY)
        assert actual == expected

    def test_get_bool_returns_expected_bool(self, mock_config_get_function):
        mock_config_get_function.return_value = True
        parser = SecurityEventConfigParser("test")
        assert parser.get_bool(_DUMMY_KEY)

    def test_get_int_returns_expected_int(self, mock_config_get_function):
        expected = 42
        mock_config_get_function.return_value = 42
        parser = SecurityEventConfigParser("test")
        actual = parser.get_int(_DUMMY_KEY)
        assert actual == expected
