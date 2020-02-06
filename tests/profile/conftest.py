import pytest
from c42sec.profile._config import ConfigurationKeys


@pytest.fixture
def config_profile(mocker):
    mock_config = mocker.patch("c42sec.profile._config.get_config_profile")
    mock_config.return_value = {
        ConfigurationKeys.USERNAME_KEY: "test.username",
        ConfigurationKeys.AUTHORITY_KEY: "https://authority.example.com",
        ConfigurationKeys.IGNORE_SSL_ERRORS_KEY: "True",
    }
    return mock_config


@pytest.fixture
def config_parser(mocker):
    mocks = ConfigParserMocks()
    mocks.initializer = mocker.patch("configparser.ConfigParser.__init__")
    mocks.item_setter = mocker.patch("configparser.ConfigParser.__setitem__")
    mocks.item_getter = mocker.patch("configparser.ConfigParser.__getitem__")
    mocks.section_adder = mocker.patch("configparser.ConfigParser.add_section")
    mocks.reader = mocker.patch("configparser.ConfigParser.read")
    mocks.initializer.return_value = None
    return mocks


class ConfigParserMocks(object):
    initializer = None
    item_setter = None
    item_getter = None
    section_adder = None
    reader = None
