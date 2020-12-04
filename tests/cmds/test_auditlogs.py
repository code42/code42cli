from datetime import datetime
from datetime import timedelta
from logging import Logger

import pytest
from py42.response import Py42Response
from requests import Response

from code42cli.cmds.auditlogs import _parse_audit_log_timestamp_string_to_timestamp
from code42cli.cmds.search.cursor_store import AuditLogCursorStore
from code42cli.date_helper import parse_max_timestamp
from code42cli.date_helper import parse_min_timestamp
from code42cli.main import cli

TEST_AUDIT_LOG_TIMESTAMP_1 = "2020-01-01T12:00:00.000Z"
TEST_AUDIT_LOG_TIMESTAMP_2 = "2020-01-01T12:01:00.000111Z"
CURSOR_TIMESTAMP = _parse_audit_log_timestamp_string_to_timestamp(
    TEST_AUDIT_LOG_TIMESTAMP_2
)


@pytest.fixture
def audit_log_cursor_with_checkpoint(mocker):
    mock_cursor = mocker.MagicMock(spec=AuditLogCursorStore)
    mock_cursor.get.return_value = CURSOR_TIMESTAMP
    mocker.patch(
        "code42cli.cmds.auditlogs._get_audit_log_cursor_store", return_value=mock_cursor
    )
    return mock_cursor


@pytest.fixture
def date_str():
    dt = datetime.utcnow() - timedelta(days=10)
    return dt.strftime("%Y-%m-%d %H:%M:%S")


@pytest.fixture
def send_to_logger(mocker):
    mock_logger = mocker.MagicMock(spec=Logger)
    mocker.patch(
        "code42cli.cmds.auditlogs.get_logger_for_server", return_value=mock_logger
    )
    return mock_logger


@pytest.fixture
def test_audit_log_response(mocker):
    http_response = mocker.MagicMock(spec=Response)
    http_response.status_code = 200
    http_response.text = '{{"events": [{{"property": "bar", "timestamp": "{}"}}, {{"property": "baz", "timestamp": "{}"}}]}}'.format(
        TEST_AUDIT_LOG_TIMESTAMP_2, TEST_AUDIT_LOG_TIMESTAMP_1
    )
    http_response._content_consumed = ""
    return Py42Response(http_response)


def test_search_audit_logs_json_format(runner, cli_state, date_str):
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


def test_send_to_makes_expected_call_count_to_the_logger_method(
    cli_state, runner, send_to_logger, test_audit_log_response
):
    cli_state.sdk.auditlogs.get_all.return_value = [test_audit_log_response]
    runner.invoke(
        cli, ["audit-logs", "send-to", "localhost", "--begin", "1d"], obj=cli_state
    )
    assert send_to_logger.info.call_count == 2


def test_send_to_emits_events_in_chronological_order(
    cli_state, runner, send_to_logger, test_audit_log_response
):
    cli_state.sdk.auditlogs.get_all.return_value = [test_audit_log_response]
    runner.invoke(
        cli, ["audit-logs", "send-to", "localhost", "--begin", "1d"], obj=cli_state
    )
    assert (
        send_to_logger.info.call_args_list[0][0][0]["timestamp"]
        == TEST_AUDIT_LOG_TIMESTAMP_1
    )
    assert (
        send_to_logger.info.call_args_list[1][0][0]["timestamp"]
        == TEST_AUDIT_LOG_TIMESTAMP_2
    )


def test_search_with_checkpoint_saves_expected_cursor_timestamp(
    cli_state, runner, test_audit_log_response, audit_log_cursor_with_checkpoint
):
    cli_state.sdk.auditlogs.get_all.return_value = [test_audit_log_response]
    runner.invoke(
        cli,
        ["audit-logs", "search", "--begin", "1d", "--use-checkpoint", "test"],
        obj=cli_state,
    )
    assert audit_log_cursor_with_checkpoint.replace.called_once_with(
        "test", CURSOR_TIMESTAMP
    )


def test_send_to_with_checkpoint_saves_expected_cursor_timestamp(
    cli_state,
    runner,
    test_audit_log_response,
    audit_log_cursor_with_checkpoint,
    send_to_logger,
):
    cli_state.sdk.auditlogs.get_all.return_value = [test_audit_log_response]
    runner.invoke(
        cli,
        [
            "audit-logs",
            "send-to",
            "localhost",
            "--begin",
            "1d",
            "--use-checkpoint",
            "test",
        ],
        obj=cli_state,
    )
    assert audit_log_cursor_with_checkpoint.replace.call_count == 2
    assert audit_log_cursor_with_checkpoint.replace.call_args_list[1][0] == (
        "test",
        CURSOR_TIMESTAMP,
    )


def test_search_with_existing_checkpoint_replaces_begin_arg_if_passed(
    cli_state, runner, test_audit_log_response, audit_log_cursor_with_checkpoint
):
    runner.invoke(
        cli,
        ["audit-logs", "search", "--begin", "1d", "--use-checkpoint", "test"],
        obj=cli_state,
    )
    assert (
        cli_state.sdk.auditlogs.get_all.call_args[1]["begin_time"] == CURSOR_TIMESTAMP
    )


def test_send_to_with_existing_checkpoint_replaces_begin_arg_if_passed(
    cli_state, runner, test_audit_log_response, audit_log_cursor_with_checkpoint
):
    runner.invoke(
        cli,
        [
            "audit-logs",
            "send-to",
            "localhost",
            "--begin",
            "1d",
            "--use-checkpoint",
            "test",
        ],
        obj=cli_state,
    )
    assert (
        cli_state.sdk.auditlogs.get_all.call_args[1]["begin_time"] == CURSOR_TIMESTAMP
    )
