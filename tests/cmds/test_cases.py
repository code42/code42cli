from code42cli.main import cli


def test_create_case_calls_create_with_expected_params(runner, cli_state):
    cli_state.sdk.cases.create.return_value = {}
    runner.invoke(
        cli,
        ["cases", "create",  "TEST_CASE"],
        obj=cli_state,
    )
    cli_state.sdk.cases.create.assert_called_once_with(
        "TEST_CASE"
    )


def test_update_case_calls_update_with_expected_params(runner, cli_state):
    cli_state.sdk.cases.update.return_value = {}
    runner.invoke(
        cli,
        ["cases", "update",  1, "--name", "TEST_CASE2"],
        obj=cli_state,
    )
    cli_state.sdk.cases.create.assert_called_once_with(
        1, name="TEST_CASE2"
    )


def test_list_calls_get_all_with_expected_params(runner, cli_state):
    cli_state.sdk.cases.update.return_value = {}
    runner.invoke(
        cli,
        ["cases", "list"],
        obj=cli_state,
    )
    cli_state.sdk.cases.get_all.call_count == 1


def test_show_calls_get_case_with_expected_params(runner, cli_state):
    cli_state.sdk.cases.update.return_value = {}
    runner.invoke(
        cli,
        ["cases", "list", 1],
        obj=cli_state,
    )
    cli_state.sdk.cases.get_case.assert_called_once_with(1)


def test_export_calls_export_summary_with_expected_params(runner, cli_state):
    cli_state.sdk.cases.update.return_value = {}
    runner.invoke(
        cli,
        ["cases", "export", 1],
        obj=cli_state,
    )
    cli_state.sdk.cases.export_summary.assert_called_once_with(1)


def test_file_events_add_calls_add_event_with_expected_params(runner, cli_state):
    cli_state.sdk.cases.update.return_value = {}
    runner.invoke(
        cli,
        ["cases", "file-events", "add", 1, "1"],
        obj=cli_state,
    )
    cli_state.sdk.cases.file_events.add_event.assert_called_once_with(1, 1)


def test_file_events_remove_calls_delete_event_with_expected_params(runner, cli_state):
    cli_state.sdk.cases.update.return_value = {}
    runner.invoke(
        cli,
        ["cases", "file-events", "remove", 1, "1"],
        obj=cli_state,
    )
    cli_state.sdk.cases.file_events.delete_event.assert_called_once_with(1, 1)


def test_file_events_list_calls_get_all_events_with_expected_params(runner, cli_state):
    cli_state.sdk.cases.update.return_value = {}
    runner.invoke(
        cli,
        ["cases", "file-events", "list", 1],
        obj=cli_state,
    )
    cli_state.sdk.cases.file_events.get_all_events.assert_called_once_with(1, 1)


def test_file_events_show_calls_get_event_with_expected_params(runner, cli_state):
    cli_state.sdk.cases.update.return_value = {}
    runner.invoke(
        cli,
        ["cases", "file-events", "show", 1, "1"],
        obj=cli_state,
    )
    cli_state.sdk.cases.file_events.get_event.assert_called_once_with(1, 1)
