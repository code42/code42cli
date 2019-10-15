import pytest
from datetime import datetime

from c42seceventcli.common.common import SecurityEventConfigParser


@pytest.fixture
def mock_config_reader(mocker):
    return mocker.patch("configparser.ConfigParser.read")


class TestSecurityEventConfigParser(object):
    def test_is_valid_when_read_returns_empty_list_is_false(self, mock_config_reader):
        mock_config_reader.return_value = []
        parser = SecurityEventConfigParser("test")
        assert not parser.is_valid

    def test_is_valid_when_read_returns_list_with_values_is_true(self, mock_config_reader):
        mock_config_reader.return_value = []
        parser = SecurityEventConfigParser("test")
        assert parser.is_valid


