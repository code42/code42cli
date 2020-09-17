from code42cli.main import cli


def test_search_audit_logs_json_format(runner, cli_state):
    runner.invoke(cli, ["audit-logs", "search"], obj=cli_state)
    assert cli_state.sdk.auditlogs.get_all.call_count == 1


def test_search_audit_logs_with_filter_parameters(runner, cli_state):
    runner.invoke(
        cli,
        [
            "audit-logs",
            "search",
            "--usernames",
            "test@test.com",
            "--usernames",
            "test2@test.test",
        ],
        obj=cli_state,
    )
    assert cli_state.sdk.auditlogs.get_all.call_count == 1
    cli_state.sdk.auditlogs.get_all.assert_called_once_with(
        usernames=("test@test.com", "test2@test.test"),
        affected_user_ids=(),
        affected_usernames=(),
        begin_time=None,
        end_time=None,
        event_types=(),
        user_ids=(),
        user_ip_addresses=(),
    )


def test_search_audit_logs_with_all_filter_parameters(runner, cli_state):
    runner.invoke(
        cli,
        [
            "audit-logs",
            "search",
            "--usernames",
            "test@test.com",
            "--usernames",
            "test2@test.test",
            "--event-types",
            "saved-search",
            "--user-ips",
            "0.0.0.0",
            "--affected-usernames",
            "test@test.test",
            "--affected-user-ids",
            "123",
            "--affected-user-ids",
            "456",
            "--user-ids",
            "userid",
        ],
        obj=cli_state,
    )
    assert cli_state.sdk.auditlogs.get_all.call_count == 1
    cli_state.sdk.auditlogs.get_all.assert_called_once_with(
        usernames=("test@test.com", "test2@test.test"),
        affected_user_ids=("123", "456"),
        affected_usernames=("test@test.test",),
        begin_time=None,
        end_time=None,
        event_types=("saved-search",),
        user_ids=("userid",),
        user_ip_addresses=("0.0.0.0",),
    )
