from datetime import datetime
from datetime import timedelta

import pytest
from py42.response import Py42Response
from requests import Response

from code42cli.date_helper import parse_max_timestamp
from code42cli.date_helper import parse_min_timestamp
from code42cli.main import cli


@pytest.fixture
def date_str():
    dt = datetime.utcnow() - timedelta(days=10)
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def test_search_audit_logs_json_format(runner, cli_state, date_str):
    print(date_str)
    runner.invoke(cli, ["audit-logs", "search", "-b", date_str], obj=cli_state)
    assert cli_state.sdk.auditlogs.get_all.call_count == 1


def test_search_audit_logs_with_filter_parameters(runner, cli_state, date_str):
    runner.invoke(
        cli,
        [
            "audit-logs",
            "search",
            "--username",
            "test@test.com",
            "--username",
            "test2@test.test",
            "--begin",
            date_str,
        ],
        obj=cli_state,
    )
    assert cli_state.sdk.auditlogs.get_all.call_count == 1
    cli_state.sdk.auditlogs.get_all.assert_called_once_with(
        usernames=("test@test.com", "test2@test.test"),
        affected_user_ids=(),
        affected_usernames=(),
        begin_time=parse_min_timestamp(date_str),
        end_time=None,
        event_types=(),
        user_ids=(),
        user_ip_addresses=(),
    )


def test_search_audit_logs_with_all_filter_parameters(runner, cli_state, date_str):
    end_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    runner.invoke(
        cli,
        [
            "audit-logs",
            "search",
            "--username",
            "test@test.com",
            "--username",
            "test2@test.test",
            "--event-type",
            "saved-search",
            "--user-ip",
            "0.0.0.0",
            "--affected-username",
            "test@test.test",
            "--affected-user-id",
            "123",
            "--affected-user-id",
            "456",
            "--user-id",
            "userid",
            "-b",
            date_str,
            "--end",
            end_time,
        ],
        obj=cli_state,
    )
    assert cli_state.sdk.auditlogs.get_all.call_count == 1
    cli_state.sdk.auditlogs.get_all.assert_called_once_with(
        usernames=("test@test.com", "test2@test.test"),
        affected_user_ids=("123", "456"),
        affected_usernames=("test@test.test",),
        begin_time=parse_min_timestamp(date_str),
        end_time=parse_max_timestamp(end_time),
        event_types=("saved-search",),
        user_ids=("userid",),
        user_ip_addresses=("0.0.0.0",),
    )


def test_send_to_makes_call_to_the_extract_method(
    cli_state, runner, event_extractor_logger, mocker
):

    http_response = mocker.MagicMock(spec=Response)
    http_response.text = '{"events": [{"property": "bar"}]}'
    py42_response = Py42Response(http_response)
    cli_state.sdk.auditlogs.get_all.return_value = [py42_response]
    runner.invoke(
        cli, ["audit-logs", "send-to", "localhost", "--begin", "1d"], obj=cli_state
    )
    assert cli_state.sdk.auditlogs.get_all.call_count == 1
