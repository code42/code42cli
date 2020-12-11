import json
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
from code42cli.util import hash_event

TEST_AUDIT_LOG_TIMESTAMP_1 = "2020-01-01T12:00:00.000Z"
TEST_AUDIT_LOG_TIMESTAMP_2 = "2020-02-01T12:01:00.000111Z"
TEST_AUDIT_LOG_TIMESTAMP_3 = "2020-03-01T02:00:00.123456Z"
CURSOR_TIMESTAMP = _parse_audit_log_timestamp_string_to_timestamp(
    TEST_AUDIT_LOG_TIMESTAMP_3
)
TEST_EVENTS_WITH_SAME_TIMESTAMP = [
    {
        "type$": "audit_log::logged_in/1",
        "actorId": "42",
        "actorName": "42@code42.com",
        "actorAgent": "py42 python code42cli",
        "actorIpAddress": "200.100.300.42",
        "timestamp": TEST_AUDIT_LOG_TIMESTAMP_1,
    },
    {
        "type$": "audit_log::logged_in/1",
        "actorId": "43",
        "actorName": "43@code42.com",
        "actorAgent": "py42 python code42cli",
        "actorIpAddress": "200.100.300.42",
        "timestamp": TEST_AUDIT_LOG_TIMESTAMP_1,
    },
]
TEST_HIGHEST_TIMESTAMP = "2020-03-01T02:00:00.123456Z"
TEST_EVENTS_WITH_DIFFERENT_TIMESTAMPS = [
    {
        "type$": "audit_log::logged_in/1",
        "actorId": "44",
        "actorName": "44@code42.com",
        "actorAgent": "py42 python code42cli",
        "actorIpAddress": "200.100.300.42",
        "timestamp": TEST_AUDIT_LOG_TIMESTAMP_2,
    },
    {
        "type$": "audit_log::logged_in/1",
        "actorId": "45",
        "actorName": "45@code42.com",
        "actorAgent": "py42 python code42cli",
        "actorIpAddress": "200.100.300.42",
        "timestamp": TEST_AUDIT_LOG_TIMESTAMP_3,
    },
]
TEST_CHECKPOINT_EVENT_HASHLIST = [
    hash_event(event) for event in TEST_EVENTS_WITH_SAME_TIMESTAMP
]


@pytest.fixture
def audit_log_cursor_with_checkpoint(mocker):
    mock_cursor = mocker.MagicMock(spec=AuditLogCursorStore)
    mock_cursor.get.return_value = CURSOR_TIMESTAMP
    mocker.patch(
        "code42cli.cmds.auditlogs._get_audit_log_cursor_store", return_value=mock_cursor
    )
    return mock_cursor


@pytest.fixture
def audit_log_cursor_with_checkpoint_and_events(mocker):
    mock_cursor = mocker.MagicMock(spec=AuditLogCursorStore)
    mock_cursor.get.return_value = CURSOR_TIMESTAMP
    mock_cursor.get_events.return_value = [
        hash_event(TEST_EVENTS_WITH_SAME_TIMESTAMP[0])
    ]
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
    http_response1 = mocker.MagicMock(spec=Response)
    http_response1.status_code = 200
    http_response1.text = json.dumps({"events": TEST_EVENTS_WITH_SAME_TIMESTAMP})
    http_response1._content_consumed = ""

    http_response2 = mocker.MagicMock(spec=Response)
    http_response2.status_code = 200
    http_response2.text = json.dumps({"events": TEST_EVENTS_WITH_DIFFERENT_TIMESTAMPS})
    http_response2._content_consumed = ""
    Py42Response(http_response2)

    def response_gen():
        yield Py42Response(http_response1)
        yield Py42Response(http_response2)

    return response_gen()


@pytest.fixture
def test_audit_log_response_with_only_same_timestamps(mocker):
    http_response = mocker.MagicMock(spec=Response)
    http_response.status_code = 200
    http_response.text = json.dumps({"events": TEST_EVENTS_WITH_SAME_TIMESTAMP})
    http_response._content_consumed = ""

    def response_gen():
        yield Py42Response(http_response)

    return response_gen()


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
    cli_state.sdk.auditlogs.get_all.return_value = test_audit_log_response
    runner.invoke(
        cli, ["audit-logs", "send-to", "localhost", "--begin", "1d"], obj=cli_state
    )
    assert send_to_logger.info.call_count == 4


def test_send_to_emits_events_in_chronological_order(
    cli_state, runner, send_to_logger, test_audit_log_response
):
    cli_state.sdk.auditlogs.get_all.return_value = test_audit_log_response
    runner.invoke(
        cli, ["audit-logs", "send-to", "localhost", "--begin", "1d"], obj=cli_state
    )
    assert (
        send_to_logger.info.call_args_list[0][0][0]["timestamp"]
        == TEST_AUDIT_LOG_TIMESTAMP_1
    )
    assert (
        send_to_logger.info.call_args_list[1][0][0]["timestamp"]
        == TEST_AUDIT_LOG_TIMESTAMP_1
    )
    assert (
        send_to_logger.info.call_args_list[2][0][0]["timestamp"]
        == TEST_AUDIT_LOG_TIMESTAMP_2
    )
    assert (
        send_to_logger.info.call_args_list[3][0][0]["timestamp"]
        == TEST_AUDIT_LOG_TIMESTAMP_3
    )


def test_search_with_checkpoint_saves_expected_cursor_timestamp(
    cli_state, runner, test_audit_log_response, audit_log_cursor_with_checkpoint
):
    cli_state.sdk.auditlogs.get_all.return_value = test_audit_log_response
    runner.invoke(
        cli,
        ["audit-logs", "search", "--begin", "1d", "--use-checkpoint", "test"],
        obj=cli_state,
    )
    assert audit_log_cursor_with_checkpoint.replace.call_count == 4
    assert audit_log_cursor_with_checkpoint.replace.call_args_list[3][0] == (
        "test",
        CURSOR_TIMESTAMP,
    )


def test_send_to_with_checkpoint_saves_expected_cursor_timestamp(
    cli_state,
    runner,
    test_audit_log_response,
    audit_log_cursor_with_checkpoint,
    send_to_logger,
):
    cli_state.sdk.auditlogs.get_all.return_value = test_audit_log_response
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
    assert audit_log_cursor_with_checkpoint.replace.call_count == 4
    assert audit_log_cursor_with_checkpoint.replace.call_args_list[3][0] == (
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


def test_search_with_existing_checkpoint_events_skips_duplicate_events(
    cli_state,
    runner,
    test_audit_log_response,
    audit_log_cursor_with_checkpoint_and_events,
):
    cli_state.sdk.auditlogs.get_all.return_value = test_audit_log_response
    result = runner.invoke(
        cli,
        ["audit-logs", "search", "--begin", "1d", "--use-checkpoint", "test"],
        obj=cli_state,
    )
    assert "42@code42.com" not in result.stdout
    assert "43@code42.com" in result.stdout


def test_send_to_with_existing_checkpoint_events_skips_duplicate_events(
    cli_state,
    runner,
    test_audit_log_response,
    audit_log_cursor_with_checkpoint_and_events,
    send_to_logger,
):
    cli_state.sdk.auditlogs.get_all.return_value = test_audit_log_response
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
    assert send_to_logger.info.call_count == 3
    assert send_to_logger.info.call_args_list[0][0][0]["actorName"] != "42@code42.com"


def test_search_without_existing_checkpoint_writes_both_event_hashes_with_same_timestamp(
    cli_state,
    runner,
    test_audit_log_response_with_only_same_timestamps,
    audit_log_cursor_with_checkpoint,
):
    cli_state.sdk.auditlogs.get_all.return_value = (
        test_audit_log_response_with_only_same_timestamps
    )
    runner.invoke(
        cli,
        ["audit-logs", "search", "--begin", "1d", "--use-checkpoint", "test"],
        obj=cli_state,
    )
    assert audit_log_cursor_with_checkpoint.replace_events.call_count == 2
    assert audit_log_cursor_with_checkpoint.replace_events.call_args_list[1][0][1] == [
        hash_event(TEST_EVENTS_WITH_SAME_TIMESTAMP[0]),
        hash_event(TEST_EVENTS_WITH_SAME_TIMESTAMP[1]),
    ]


def test_send_to_without_existing_checkpoint_writes_both_event_hashes_with_same_timestamp(
    cli_state,
    runner,
    test_audit_log_response_with_only_same_timestamps,
    audit_log_cursor_with_checkpoint,
    send_to_logger,
):
    cli_state.sdk.auditlogs.get_all.return_value = (
        test_audit_log_response_with_only_same_timestamps
    )
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
    assert audit_log_cursor_with_checkpoint.replace_events.call_count == 2
    assert audit_log_cursor_with_checkpoint.replace_events.call_args_list[1][0][1] == [
        hash_event(TEST_EVENTS_WITH_SAME_TIMESTAMP[0]),
        hash_event(TEST_EVENTS_WITH_SAME_TIMESTAMP[1]),
    ]
