import json
from datetime import datetime
from datetime import timedelta
from logging import Logger

import pytest
from py42.response import Py42Response
from requests import Response
from tests.cmds.conftest import get_mark_for_search_and_send_to

from code42cli.click_ext.types import MagicDate
from code42cli.cmds.audit_logs import _parse_audit_log_timestamp_string_to_timestamp
from code42cli.cmds.search.cursor_store import AuditLogCursorStore
from code42cli.date_helper import convert_datetime_to_timestamp
from code42cli.date_helper import round_datetime_to_day_end
from code42cli.date_helper import round_datetime_to_day_start
from code42cli.logger.handlers import ServerProtocol
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
        "actorName": "42@example.com",
        "actorAgent": "py42 python code42cli",
        "actorIpAddress": "200.100.300.42",
        "timestamp": TEST_AUDIT_LOG_TIMESTAMP_1,
    },
    {
        "type$": "audit_log::logged_in/1",
        "actorId": "43",
        "actorName": "43@example.com",
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
        "actorName": "44@example.com",
        "actorAgent": "py42 python code42cli",
        "actorIpAddress": "200.100.300.42",
        "timestamp": TEST_AUDIT_LOG_TIMESTAMP_2,
    },
    {
        "type$": "audit_log::logged_in/1",
        "actorId": "45",
        "actorName": "45@example.com",
        "actorAgent": "py42 python code42cli",
        "actorIpAddress": "200.100.300.42",
        "timestamp": TEST_AUDIT_LOG_TIMESTAMP_3,
    },
]
search_and_send_to_test = get_mark_for_search_and_send_to("audit-logs")


@pytest.fixture
def audit_log_cursor_with_checkpoint(mocker):
    mock_cursor = mocker.MagicMock(spec=AuditLogCursorStore)
    mock_cursor.get.return_value = CURSOR_TIMESTAMP
    mocker.patch(
        "code42cli.cmds.audit_logs._get_audit_log_cursor_store",
        return_value=mock_cursor,
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
        "code42cli.cmds.audit_logs._get_audit_log_cursor_store",
        return_value=mock_cursor,
    )
    return mock_cursor


@pytest.fixture
def date_str():
    dt = datetime.utcnow() - timedelta(days=10)
    return dt.strftime("%Y-%m-%d %H:%M:%S")


@pytest.fixture
def send_to_logger_factory(mocker):
    return mocker.patch("code42cli.cmds.search._try_get_logger_for_server")


@pytest.fixture
def send_to_logger(mocker, send_to_logger_factory):
    mock_logger = mocker.MagicMock(spec=Logger)
    send_to_logger_factory.return_value = mock_logger
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


@search_and_send_to_test
def test_search_and_send_to_handles_json_format(runner, cli_state, date_str, command):
    runner.invoke(cli, [*command, "-b", date_str], obj=cli_state)
    assert cli_state.sdk.auditlogs.get_all.call_count == 1


@search_and_send_to_test
def test_search_and_send_to_handles_filter_parameters(
    runner, cli_state, date_str, command
):
    expected_begin_timestamp = convert_datetime_to_timestamp(
        MagicDate(rounding_func=round_datetime_to_day_start).convert(
            date_str, None, None
        )
    )
    runner.invoke(
        cli,
        [
            *command,
            "--actor-username",
            "test@example.com",
            "--actor-username",
            "test2@test.example.com",
            "--begin",
            date_str,
        ],
        obj=cli_state,
    )
    cli_state.sdk.auditlogs.get_all.assert_called_once_with(
        usernames=("test@example.com", "test2@test.example.com"),
        affected_user_ids=(),
        affected_usernames=(),
        begin_time=expected_begin_timestamp,
        end_time=None,
        event_types=(),
        user_ids=(),
        user_ip_addresses=(),
    )


@search_and_send_to_test
def test_search_and_send_to_handles_all_filter_parameters(
    runner, cli_state, date_str, command
):
    end_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    expected_begin_timestamp = convert_datetime_to_timestamp(
        MagicDate(rounding_func=round_datetime_to_day_start).convert(
            date_str, None, None
        )
    )
    expected_end_timestamp = convert_datetime_to_timestamp(
        MagicDate(rounding_func=round_datetime_to_day_end).convert(end_time, None, None)
    )
    runner.invoke(
        cli,
        [
            *command,
            "--actor-username",
            "test@example.com",
            "--actor-username",
            "test2@test.example.com",
            "--event-type",
            "saved-search",
            "--actor-ip",
            "0.0.0.0",
            "--affected-username",
            "test@test.example.com",
            "--affected-user-id",
            "123",
            "--affected-user-id",
            "456",
            "--actor-user-id",
            "userid",
            "-b",
            date_str,
            "--end",
            end_time,
        ],
        obj=cli_state,
    )
    cli_state.sdk.auditlogs.get_all.assert_called_once_with(
        usernames=("test@example.com", "test2@test.example.com"),
        affected_user_ids=("123", "456"),
        affected_usernames=("test@test.example.com",),
        begin_time=expected_begin_timestamp,
        end_time=expected_end_timestamp,
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


def test_send_to_creates_expected_logger(cli_state, runner, send_to_logger_factory):
    runner.invoke(
        cli,
        [
            "audit-logs",
            "send-to",
            "0.0.0.0",
            "--begin",
            "1d",
            "--protocol",
            "TLS-TCP",
            "--certs",
            "certs/file",
        ],
        obj=cli_state,
    )
    send_to_logger_factory.assert_called_once_with(
        "0.0.0.0", "TLS-TCP", "RAW-JSON", "certs/file"
    )


def test_send_to_when_given_ignore_cert_validation_uses_certs_equal_to_ignore_str(
    cli_state, runner, send_to_logger_factory
):
    runner.invoke(
        cli,
        [
            "audit-logs",
            "send-to",
            "0.0.0.0",
            "--begin",
            "1d",
            "--protocol",
            "TLS-TCP",
            "--ignore-cert-validation",
        ],
        obj=cli_state,
    )
    send_to_logger_factory.assert_called_once_with(
        "0.0.0.0", "TLS-TCP", "RAW-JSON", "ignore"
    )


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


@pytest.mark.parametrize("protocol", (ServerProtocol.UDP, ServerProtocol.TCP))
def test_send_to_when_given_ignore_cert_validation_with_non_tls_protocol_fails_expectedly(
    cli_state, runner, protocol
):
    res = runner.invoke(
        cli,
        [
            "audit-logs",
            "send-to",
            "0.0.0.0",
            "--begin",
            "1d",
            "--protocol",
            protocol,
            "--ignore-cert-validation",
        ],
        obj=cli_state,
    )
    assert (
        "'--ignore-cert-validation' can only be used with '--protocol TLS-TCP'"
        in res.output
    )


@pytest.mark.parametrize("protocol", (ServerProtocol.UDP, ServerProtocol.TCP))
def test_send_to_when_given_certs_with_non_tls_protocol_fails_expectedly(
    cli_state, runner, protocol
):
    res = runner.invoke(
        cli,
        [
            "audit-logs",
            "send-to",
            "0.0.0.0",
            "--begin",
            "1d",
            "--protocol",
            protocol,
            "--certs",
            "certs.pem",
        ],
        obj=cli_state,
    )
    assert "'--certs' can only be used with '--protocol TLS-TCP'" in res.output


@search_and_send_to_test
def test_search_and_send_to_with_checkpoint_saves_expected_cursor_timestamp(
    cli_state,
    runner,
    send_to_logger,
    test_audit_log_response,
    audit_log_cursor_with_checkpoint,
    command,
):
    cli_state.sdk.auditlogs.get_all.return_value = test_audit_log_response
    runner.invoke(
        cli, [*command, "--begin", "1d", "--use-checkpoint", "test"], obj=cli_state,
    )
    assert audit_log_cursor_with_checkpoint.replace.call_count == 4
    assert audit_log_cursor_with_checkpoint.replace.call_args_list[3][0] == (
        "test",
        CURSOR_TIMESTAMP,
    )


@search_and_send_to_test
def test_search_and_send_to_with_existing_checkpoint_replaces_begin_arg_if_passed(
    cli_state,
    runner,
    send_to_logger,
    test_audit_log_response,
    audit_log_cursor_with_checkpoint,
    command,
):
    runner.invoke(
        cli, [*command, "--begin", "1d", "--use-checkpoint", "test"], obj=cli_state,
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
    assert "42@example.com" not in result.stdout
    assert "43@example.com" in result.stdout


@search_and_send_to_test
def test_search_and_send_to_without_existing_checkpoint_writes_both_event_hashes_with_same_timestamp(
    cli_state,
    runner,
    send_to_logger,
    test_audit_log_response_with_only_same_timestamps,
    audit_log_cursor_with_checkpoint,
    command,
):
    cli_state.sdk.auditlogs.get_all.return_value = (
        test_audit_log_response_with_only_same_timestamps
    )
    runner.invoke(
        cli, [*command, "--begin", "1d", "--use-checkpoint", "test"], obj=cli_state,
    )
    assert audit_log_cursor_with_checkpoint.replace_events.call_count == 2
    assert audit_log_cursor_with_checkpoint.replace_events.call_args_list[1][0][1] == [
        hash_event(TEST_EVENTS_WITH_SAME_TIMESTAMP[0]),
        hash_event(TEST_EVENTS_WITH_SAME_TIMESTAMP[1]),
    ]


@pytest.mark.parametrize(
    "protocol", (ServerProtocol.TLS_TCP, ServerProtocol.TLS_TCP, ServerProtocol.UDP)
)
def test_send_to_allows_protocol_arg(cli_state, runner, protocol):
    res = runner.invoke(
        cli,
        ["audit-logs", "send-to", "0.0.0.0", "--begin", "1d", "--protocol", protocol],
        obj=cli_state,
    )
    assert res.exit_code == 0


def test_send_when_given_unknown_protocol_fails(cli_state, runner):
    res = runner.invoke(
        cli,
        ["audit-logs", "send-to", "0.0.0.0", "--begin", "1d", "--protocol", "ATM"],
        obj=cli_state,
    )
    assert res.exit_code


def test_send_to_certs_and_ignore_cert_validation_args_are_incompatible(
    cli_state, runner
):
    res = runner.invoke(
        cli,
        [
            "audit-logs",
            "send-to",
            "0.0.0.0",
            "--begin",
            "1d",
            "--protocol",
            "TLS-TCP",
            "--certs",
            "certs/file",
            "--ignore-cert-validation",
        ],
        obj=cli_state,
    )
    assert "Error: --ignore-cert-validation can't be used with: --certs" in res.output


def test_audit_log_parse_timestamp_handles_possible_strings():
    TIMESTAMP_WITH_MILLISECONDS = "2020-01-01T12:00:00.000Z"
    TIMESTAMP_WITHOUT_MILLISECONDS = "2020-01-01T12:00:00Z"
    ts1 = _parse_audit_log_timestamp_string_to_timestamp(TIMESTAMP_WITH_MILLISECONDS)
    ts2 = _parse_audit_log_timestamp_string_to_timestamp(TIMESTAMP_WITHOUT_MILLISECONDS)
    assert ts1 == ts2
