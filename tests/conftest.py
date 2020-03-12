import json as json_module
from argparse import Namespace
from datetime import datetime, timedelta

import pytest

from code42cli.profile.config import ConfigAccessor
from code42cli.profile.profile import Code42Profile


@pytest.fixture
def namespace(mocker):
    mock = mocker.MagicMock(spec=Namespace)
    mock.profile_name = None
    mock.is_incremental = None
    mock.advanced_query = None
    mock.is_debug_mode = None
    mock.begin_date = None
    mock.end_date = None
    mock.exposure_types = None
    mock.c42usernames = None
    mock.actors = None
    mock.md5_hashes = None
    mock.sha256_hashes = None
    mock.sources = None
    mock.filenames = None
    mock.filepaths = None
    mock.process_owners = None
    mock.tab_urls = None
    mock.include_non_exposure_events = None
    return mock


class MockSection(object):
    def __init__(self, name="Test Profile Name", values_dict=None):
        self.name = name
        self.values_dict = values_dict or {
            ConfigAccessor.AUTHORITY_KEY: None,
            ConfigAccessor.USERNAME_KEY: None,
            ConfigAccessor.IGNORE_SSL_ERRORS_KEY: False,
        }

    def __getitem__(self, item):
        return self.values_dict[item]

    def __setitem__(self, key, value):
        self.values_dict[key] = value

    def get(self, item):
        return self.values_dict.get(item)


def create_mock_profile(name=None):
    profile_section = MockSection(name)
    profile = Code42Profile(profile_section)

    def mock_get_password():
        return "Test Password"

    profile.get_password = mock_get_password
    return profile


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
