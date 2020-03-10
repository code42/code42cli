import json as json_module
from argparse import Namespace
from datetime import datetime, timedelta

import pytest

from code42cli.profile.config import ConfigurationKeys


@pytest.fixture
def config_profile(mocker):
    mock_config = mocker.patch("code42cli.profile.config.get_profile")

    model_dict = {
        ConfigurationKeys.USERNAME_KEY: "test.username",
        ConfigurationKeys.AUTHORITY_KEY: "https://authority.example.com",
        ConfigurationKeys.IGNORE_SSL_ERRORS_KEY: "True",
    }

    class MockConfig(object):
        name = "PROFILE NAME"

        def __getitem__(self, item):
            return model_dict[item]

        def get(self, item):
            return model_dict.get(item)

    mock_config.return_value = MockConfig()
    return mock_config


@pytest.fixture
def config_parser(mocker):
    mocks = ConfigParserMocks()
    mocks.initializer = mocker.patch("configparser.ConfigParser.__init__")
    mocks.item_setter = mocker.patch("configparser.ConfigParser.__setitem__")
    mocks.item_getter = mocker.patch("configparser.ConfigParser.__getitem__")
    mocks.section_adder = mocker.patch("configparser.ConfigParser.add_section")
    mocks.reader = mocker.patch("configparser.ConfigParser.read")
    mocks.sections = mocker.patch("configparser.ConfigParser.sections")
    mocks.initializer.return_value = None
    return mocks


@pytest.fixture
def namespace(mocker):
    mock = mocker.MagicMock(spec=Namespace)
    mock.is_incremental = None
    mock.advanced_query = None
    mock.is_debug_mode = None
    mock.begin_date = None
    mock.end_date = None
    mock.exposure_types = None
    mock.c42username = None
    mock.actor = None
    mock.md5 = None
    mock.sha256 = None
    mock.source = None
    mock.filename = None
    mock.filepath = None
    mock.process_owner = None
    mock.tab_url = None
    mock.include_non_exposure_events = None
    return mock


class ConfigParserMocks(object):
    initializer = None
    item_setter = None
    item_getter = None
    section_adder = None
    reader = None
    sections = None


def get_filter_value_from_json(json, filter_index):
    return json_module.loads(str(json))["filters"][filter_index]["value"]


def parse_date_from_filter_value(json, filter_index):
    date_str = get_filter_value_from_json(json, filter_index)
    return convert_str_to_date(date_str)


def convert_str_to_date(date_str):
    return datetime.strptime(date_str, u"%Y-%m-%dT%H:%M:%S.%fZ")


def get_test_date(days_ago):
    now = datetime.utcnow()
    return now - timedelta(days=days_ago)


def get_test_date_str(days_ago):
    return get_test_date(days_ago).strftime("%Y-%m-%d")
