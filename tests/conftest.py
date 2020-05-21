from datetime import datetime, timedelta

import pytest
from py42.sdk import SDKClient

from code42cli.file_readers import CliFileReader
from code42cli.config import ConfigAccessor
from code42cli.profile import Code42Profile
from code42cli.commands import DictObject

import code42cli.errors as error_tracker


@pytest.fixture(autouse=True)
def io_prevention(monkeypatch):
    monkeypatch.setattr("logging.FileHandler._open", lambda *args, **kwargs: None)


@pytest.fixture
def file_event_namespace():
    args = DictObject(
        dict(
            sdk=mock_42,
            profile=create_mock_profile(),
            incremental=None,
            advanced_query=None,
            begin=None,
            end=None,
            type=None,
            c42_username=None,
            actor=None,
            md5=None,
            sha256=None,
            source=None,
            file_name=None,
            file_path=None,
            process_owner=None,
            tab_url=None,
            include_non_exposure=None,
            format=None,
            output_file=None,
            server=None,
            protocol=None,
        )
    )
    return args


@pytest.fixture
def alert_namespace():
    args = DictObject(
        dict(
            sdk=mock_42,
            profile=create_mock_profile(),
            incremental=None,
            advanced_query=None,
            begin=None,
            end=None,
            severity=None,
            state=None,
            actor=None,
            actor_contains=None,
            exclude_actor=None,
            exclude_actor_contains=None,
            rule_name=None,
            exclude_rule_name=None,
            rule_id=None,
            exclude_rule_id=None,
            rule_type=None,
            exclude_rule_type=None,
            description=None,
            format=None,
            output_file=None,
            server=None,
            protocol=None,
        )
    )
    return args


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


def func_single_positional_arg(one):
    pass


def func_single_positional_arg_many_optional_args(one, two=None, three=None, four=None):
    pass


def func_positional_args(one, two, three):
    pass


def func_mixed_args(one, two, three=None, four=None):
    pass


def func_with_sdk(sdk, one, two, three=None, four=None):
    pass


def func_single_positional_arg_with_sdk_and_profile(
    sdk, profile, one, two=None, three=None, four=None
):
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


class ErrorTrackerTestHelper:
    def __enter__(self):
        error_tracker.ERRORED = True

    def __exit__(self, exc_type, exc_val, exc_tb):
        error_tracker.ERRORED = False


TEST_FILE_PATH = "some/path"


def create_mock_reader(rows):
    class MockDictReader(CliFileReader):
        def __call__(self, *args, **kwargs):
            return rows

        def get_rows_count(self):
            return len(rows)

    return MockDictReader(TEST_FILE_PATH)
