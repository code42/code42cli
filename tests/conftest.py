from argparse import Namespace
from datetime import datetime, timedelta

import pytest
from py42.sdk import SDKClient

from code42cli.config import ConfigAccessor
from code42cli.profile import Code42Profile


@pytest.fixture
def namespace(mocker):
    mock = mocker.MagicMock(spec=Namespace)
    mock.sdk = mock_42
    mock.profile = create_mock_profile
    mock.incremental = None
    mock.advanced_query = None
    mock.begin = None
    mock.end = None
    mock.type = None
    mock.c42_username = None
    mock.actor = None
    mock.md5 = None
    mock.sha256 = None
    mock.source = None
    mock.file_name = None
    mock.file_path = None
    mock.process_owner = None
    mock.tab_url = None
    mock.include_non_exposure = None
    mock.format = None
    mock.output_file = None
    mock.server = None
    mock.protocol = None
    mock._dict = mock.__dict__
    return mock


def create_profile_values_dict(authority=None, username=None, ignore_ssl=False):
    return {
        ConfigAccessor.AUTHORITY_KEY: "example.com",
        ConfigAccessor.USERNAME_KEY: "foo",
        ConfigAccessor.IGNORE_SSL_ERRORS_KEY: True,
    }


@pytest.fixture
def sdk(mocker):
    return mocker.MagicMock(spec=SDKClient)


@pytest.fixture()
def mock_42(mocker):
    return mocker.patch("py42.sdk.from_local_account")


class MockSection(object):
    def __init__(self, name=None, values_dict=None):
        self.name = name
        self.values_dict = values_dict or create_profile_values_dict()

    def __getitem__(self, item):
        return self.values_dict[item]

    def __setitem__(self, key, value):
        self.values_dict[key] = value

    def get(self, item):
        return self.values_dict.get(item)


def create_mock_profile(name="Test Profile Name"):
    profile_section = MockSection(name)
    profile = Code42Profile(profile_section)
    return profile


def setup_mock_accessor(mock_accessor, name=None, values_dict=None):
    profile_section = MockSection(name, values_dict)
    mock_accessor.get_profile.return_value = profile_section
    return mock_accessor


@pytest.fixture
def profile(mocker):
    return mocker.MagicMock(spec=Code42Profile)


def func_keyword_args(one=None, two=None, three=None, default="testdefault", nargstest=[]):
    pass


def func_positional_args(one, two, three):
    pass


def func_mixed_args(one, two, three=None, four=None):
    pass


def func_with_sdk(sdk, one, two, three=None, four=None):
    pass


def func_with_args(args):
    pass


def convert_str_to_date(date_str):
    return datetime.strptime(date_str, u"%Y-%m-%dT%H:%M:%S.%fZ")


def get_test_date(days_ago=None, hours_ago=None, minutes_ago=None):
    """Note: only pass in one parameter to get the right test date... this is just a test func."""
    now = datetime.utcnow()
    if days_ago:
        return now - timedelta(days=days_ago)
    if hours_ago:
        return now - timedelta(hours=hours_ago)
    if minutes_ago:
        return now - timedelta(minutes=minutes_ago)


def get_test_date_str(days_ago):
    return get_test_date(days_ago).strftime("%Y-%m-%d")


begin_date_str = get_test_date_str(days_ago=89)
begin_date_str_with_time = "{0} 3:12:33".format(begin_date_str)
end_date_str = get_test_date_str(days_ago=10)
end_date_str_with_time = "{0} 11:22:43".format(end_date_str)
begin_date_str = get_test_date_str(days_ago=89)
begin_date_with_time = [get_test_date_str(days_ago=89), "3:12:33"]
end_date_str = get_test_date_str(days_ago=10)
end_date_with_time = [get_test_date_str(days_ago=10), "11:22:43"]
