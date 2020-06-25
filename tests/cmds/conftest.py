import json as json_module

import pytest

from py42.sdk import SDKClient
from code42cli import PRODUCT_NAME
from code42cli.logger import CliLogger
from tests.conftest import convert_str_to_date


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


def get_filter_value_from_json(json, filter_index):
    return json_module.loads(str(json))["filters"][filter_index]["value"]


def parse_date_from_filter_value(json, filter_index):
    date_str = get_filter_value_from_json(json, filter_index)
    return convert_str_to_date(date_str)


@pytest.fixture(autouse=True)
def sqlite_connection(mocker):
    return mocker.patch("sqlite3.connect")


ACCEPTABLE_ARGS = [
    "-t",
    "SharedToDomain",
    "ApplicationRead",
    "CloudStorage",
    "RemovableMedia",
    "IsPublic",
    "-f",
    "JSON",
    "-d",
    "-b",
    "600",
    "-e",
    "2020-02-02",
    "--c42-username",
    "test.testerson",
    "--actor",
    "test.testerson",
    "--md5",
    "098f6bcd4621d373cade4e832627b4f6",
    "--sha256",
    "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08",
    "--source",
    "Gmail",
    "--file-name",
    "file.txt",
    "--file-path",
    "/path/to/file.txt",
    "--process-owner",
    "test.testerson",
    "--tab-url",
    "https://example.com",
    "--include-non-exposure",
]
