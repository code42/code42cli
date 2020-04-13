import pytest
from argparse import Namespace
from py42.sdk import SDKClient

from code42cli.bulk import BulkProcessor
from code42cli.config import ConfigAccessor
from code42cli.profile import Code42Profile


@pytest.fixture
def namespace(mocker):
    mock = mocker.MagicMock(spec=Namespace)
    mock.incremental = None
    mock.advanced_query = None
    mock.begin = None
    mock.end = None
    mock.type = None
    mock.c42username = None
    mock.actor = None
    mock.md5 = None
    mock.sha256 = None
    mock.source = None
    mock.filename = None
    mock.filepath = None
    mock.processOwner = None
    mock.tabURL = None
    mock.include_non_exposure = None
    mock.format = None
    mock.output_file = None
    mock.server = None
    mock.protocol = None
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


@pytest.fixture
def bulk_processor(mocker):
    return mocker.MagicMock(spec=BulkProcessor)
