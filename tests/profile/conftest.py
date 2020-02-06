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
    mocker.patch("configparser.ConfigParser.__setitem__")
    mocker.patch("configparser.ConfigParser.add_section")
    mocker.patch("configparser.ConfigParser.read")
    mock_init = mocker.patch("configparser.ConfigParser.__init__")
    mock_init.return_value = None
    return mock_init
