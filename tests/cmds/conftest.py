import json as json_module
import threading

import pytest
from py42.exceptions import Py42UserAlreadyAddedError
from py42.exceptions import Py42UserNotOnListError
from py42.sdk import SDKClient
from requests import HTTPError
from requests import Request
from requests import Response
from tests.conftest import convert_str_to_date
from tests.conftest import TEST_ID

from code42cli.logger import CliLogger


TEST_EMPLOYEE = "risky employee"


def get_user_not_on_list_side_effect(mocker, list_name):
    def side_effect(*args, **kwargs):
        err = mocker.MagicMock(spec=HTTPError)
        resp = mocker.MagicMock(spec=Response)
        resp.text = "TEST_ERR"
        err.response = resp
        err.response.request = mocker.MagicMock(spec=Request)
        raise Py42UserNotOnListError(err, TEST_ID, list_name)

    return side_effect


@pytest.fixture
def sdk(mocker):
    return mocker.MagicMock(spec=SDKClient)


@pytest.fixture()
def mock_42(mocker):
    return mocker.patch("py42.sdk.from_local_account")


@pytest.fixture
def logger(mocker):
    mock = mocker.MagicMock()
    return mock


@pytest.fixture
def cli_logger(mocker):
    mock = mocker.MagicMock(spec=CliLogger)
    return mock


@pytest.fixture
def event_extractor_logger(mocker):
    mock = mocker.patch(
        "c42eventextractor.logging.handlers.NoPrioritySysLogHandlerWrapper"
    )
    mock.emit.return_value = mocker.MagicMock()
    return mock


@pytest.fixture
def cli_state_with_user(sdk_with_user, cli_state):
    cli_state.sdk = sdk_with_user
    return cli_state


@pytest.fixture
def cli_state_without_user(sdk_without_user, cli_state):
    cli_state.sdk = sdk_without_user
    return cli_state


@pytest.fixture
def user_already_added_error(mocker):
    err = mocker.MagicMock(spec=HTTPError)
    resp = mocker.MagicMock(spec=Response)
    resp.text = "TEST_ERR"
    err.response = resp
    return Py42UserAlreadyAddedError(err, TEST_ID, "detection list")


def get_filter_value_from_json(json, filter_index):
    return json_module.loads(str(json))["filters"][filter_index]["value"]


def filter_term_is_in_call_args(extractor, term):
    arg_filters = extractor.extract.call_args[0]
    for f in arg_filters:
        if term in str(f):
            return True
    return False


def parse_date_from_filter_value(json, filter_index):
    date_str = get_filter_value_from_json(json, filter_index)
    return convert_str_to_date(date_str)


def thread_safe_side_effect():
    def f(*args):
        with threading.Lock():
            f.call_count += 1
            f.call_args_list.append(args)

    f.call_count = 0
    f.call_args_list = []
    return f
