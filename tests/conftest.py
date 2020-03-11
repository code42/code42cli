import json as json_module
from argparse import Namespace
from datetime import datetime, timedelta

import pytest


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
