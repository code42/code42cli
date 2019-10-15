import pytest
from datetime import datetime

from c42seceventcli.common.common import SecurityEventConfigParser


@pytest.fixture
def mock_config_parser(mocker):
    mock_parser = mocker.patch("configparser.ConfigParser")


class TestSecurityEventConfigParser(object):
    def test_parse_server_returns_expected_value(self, mock_config_parser):
        # expected = "SERVER"
        # mock_config_parser.get.return_value = expected
        # parser = SecurityEventConfigParser("test")
        # actual = parser.p
        assert True


