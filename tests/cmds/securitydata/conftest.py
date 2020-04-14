import json as json_module
from datetime import datetime, timedelta

import pytest

SECURITYDATA_NAMESPACE = "code42cli.cmds.securitydata"


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


begin_date_str = get_test_date_str(days_ago=89)
begin_date_str_with_time = "{0} 3:12:33".format(begin_date_str)
end_date_str = get_test_date_str(days_ago=10)
end_date_str_with_time = "{0} 11:22:43".format(end_date_str)
begin_date_list = [get_test_date_str(days_ago=89)]
begin_date_list_with_time = [get_test_date_str(days_ago=89), "3:12:33"]
end_date_list = [get_test_date_str(days_ago=10)]
end_date_list_with_time = [get_test_date_str(days_ago=10), "11:22:43"]


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
