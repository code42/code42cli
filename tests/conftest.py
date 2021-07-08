import json
from datetime import datetime
from datetime import timedelta

import pytest
from click.testing import CliRunner
from py42.response import Py42Response
from py42.sdk import SDKClient
from requests import HTTPError
from requests import Response

import code42cli.errors as error_tracker
from code42cli.config import ConfigAccessor
from code42cli.options import CLIState
from code42cli.profile import Code42Profile

TEST_ID = "TEST_ID"


@pytest.fixture(scope="session")
def runner():
    return CliRunner()


@pytest.fixture(autouse=True)
def io_prevention(monkeypatch):
    monkeypatch.setattr("logging.FileHandler._open", lambda *args, **kwargs: None)


@pytest.fixture
def file_event_namespace():
    args = dict(
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
        saved_search=None,
    )
    return args


@pytest.fixture
def alert_namespace():
    args = dict(
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


@pytest.fixture
def sdk_with_user(sdk):
    sdk.users.get_by_username.return_value = {"users": [{"userUid": TEST_ID}]}
    return sdk


@pytest.fixture
def sdk_without_user(sdk):
    sdk.users.get_by_username.return_value = {"users": []}
    return sdk


@pytest.fixture
def mock_42(mocker):
    return mocker.patch("py42.sdk.from_local_account")


@pytest.fixture
def cli_state(mocker, sdk, profile):
    mock_state = mocker.MagicMock(spec=CLIState)
    mock_state._sdk = sdk
    mock_state.profile = profile
    mock_state.search_filters = []
    mock_state.assume_yes = False
    return mock_state


class MockSection:
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
    mock = mocker.MagicMock(spec=Code42Profile)
    mock.name = "testcliprofile"
    return mock


@pytest.fixture(autouse=True)
def mock_makedirs(mocker):
    return mocker.patch("os.makedirs")


@pytest.fixture(autouse=True)
def mock_remove(mocker):
    return mocker.patch("os.remove")


@pytest.fixture(autouse=True)
def mock_listdir(mocker):
    return mocker.patch("os.listdir")


def func_keyword_args(
    one=None, two=None, three=None, default="testdefault", nargstest=None
):
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
    return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%fZ")


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
begin_date_str_with_time = f"{begin_date_str} 3:12:33"
begin_date_str_with_t_time = f"{begin_date_str}T3:12:33"
end_date_str = get_test_date_str(days_ago=10)
end_date_str_with_time = f"{end_date_str} 11:22:43"
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


@pytest.fixture
def mock_to_table(mocker):
    return mocker.patch("code42cli.output_formats.to_table")


@pytest.fixture
def mock_to_csv(mocker):
    return mocker.patch("code42cli.output_formats.to_csv")


@pytest.fixture
def mock_to_json(mocker):
    return mocker.patch("code42cli.output_formats.to_json")


@pytest.fixture
def mock_to_formatted_json(mocker):
    return mocker.patch("code42cli.output_formats.to_formatted_json")


@pytest.fixture
def mock_dataframe_to_json(mocker):
    return mocker.patch("pandas.DataFrame.to_json")


@pytest.fixture
def mock_dataframe_to_csv(mocker):
    return mocker.patch("pandas.DataFrame.to_csv")


@pytest.fixture
def mock_dataframe_to_string(mocker):
    return mocker.patch("pandas.DataFrame.to_string")


def create_mock_response(mocker, data=None, status=200):
    if isinstance(data, dict):
        data = json.dumps(data)
    elif not data:
        data = ""
    response = mocker.MagicMock(spec=Response)
    response.text = data
    response.status_code = status
    response.encoding = None
    response._content_consumed = ""
    return Py42Response(response)


def create_mock_http_error(mocker, data=None, status=400):
    mock_http_error = mocker.MagicMock(spec=HTTPError)
    mock_http_error.response = create_mock_response(mocker, data=data, status=status)
    return mock_http_error
