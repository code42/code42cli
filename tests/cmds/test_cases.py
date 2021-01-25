import json
from unittest import mock
from unittest.mock import mock_open

import pytest
from py42.exceptions import Py42BadRequestError
from py42.exceptions import Py42NotFoundError
from py42.response import Py42Response

from code42cli.main import cli


ALL_EVENTS = """{
  "events": [
    {
      "eventId": "0_1d71796f-af5b-4231-9d8e-df6434da4663_984418168383179707_986472527798692818_971",
      "eventTimestamp": "2020-12-23T12:41:38.592Z"
    }
  ]
}"""
ALL_CASES = """{
  "cases": [
    {
      "number": 3,
      "name": "test@test.test",
      "updatedAt": "2021-01-24T11:00:04.217878Z",
      "subject": "942897"
    }
  ],
  "totalCount": 31
}"""
CASE_DETAILS = '{"number": 3, "name": "test@test.test"}'
MISSING_ARGUMENT_ERROR = "Missing argument '{}'."
MISSING_NAME = MISSING_ARGUMENT_ERROR.format("NAME")
MISSING_CASE_NUMBER_ARG = MISSING_ARGUMENT_ERROR.format("CASE_NUMBER")
MISSING_OPTION_ERROR = "Missing option '--{}'."
MISSING_EVENT_ID = MISSING_OPTION_ERROR.format("event-id")
MISSING_CASE_NUMBER_OPTION = MISSING_OPTION_ERROR.format("case-number")


@pytest.fixture
def error(mocker):
    error = mocker.Mock(spec=Exception)
    error.response = "error"
    return error


@pytest.fixture
def py42_response(mocker):
    return mocker.MagicMock(spec=Py42Response)


def test_create_calls_create_with_expected_params(runner, cli_state):
    runner.invoke(
        cli, ["cases", "create", "TEST_CASE"], obj=cli_state,
    )
    cli_state.sdk.cases.create.assert_called_once_with(
        "TEST_CASE", assignee=None, description=None, findings=None, subject=None
    )


def test_create_with_optional_fields_calls_create_with_expected_params(
    runner, cli_state
):
    runner.invoke(
        cli,
        [
            "cases",
            "create",
            "TEST_CASE",
            "--assignee",
            "a",
            "--description",
            "d",
            "--findings",
            "n",
            "--subject",
            "s",
        ],
        obj=cli_state,
    )
    cli_state.sdk.cases.create.assert_called_once_with(
        "TEST_CASE", assignee="a", description="d", findings="n", subject="s"
    )


def test_create_when_missing_name_prints_error(runner, cli_state):
    command = ["cases", "create", "--description", "d"]
    result = runner.invoke(cli, command, obj=cli_state)
    assert result.exit_code == 2
    assert MISSING_NAME in result.output


def test_update_with_optional_fields_calls_update_with_expected_params(
    runner, cli_state
):
    runner.invoke(
        cli,
        [
            "cases",
            "update",
            "1",
            "--name",
            "TEST_CASE2",
            "--assignee",
            "a",
            "--description",
            "d",
            "--findings",
            "n",
            "--subject",
            "s",
            "--status",
            "CLOSED",
        ],
        obj=cli_state,
    )
    cli_state.sdk.cases.update.assert_called_once_with(
        1,
        name="TEST_CASE2",
        status="CLOSED",
        assignee="a",
        description="d",
        findings="n",
        subject="s",
    )


def test_update_calls_update_with_expected_params(runner, cli_state):
    runner.invoke(
        cli, ["cases", "update", "1", "--name", "TEST_CASE2"], obj=cli_state,
    )
    cli_state.sdk.cases.update.assert_called_once_with(
        1,
        name="TEST_CASE2",
        status=None,
        assignee=None,
        description=None,
        findings=None,
        subject=None,
    )


def test_update_when_missing_case_number_prints_error(runner, cli_state):
    command = ["cases", "update", "--description", "d"]
    result = runner.invoke(cli, command, obj=cli_state)
    assert result.exit_code == 2
    assert MISSING_CASE_NUMBER_ARG in result.output


def test_list_calls_get_all_with_expected_params(runner, cli_state):
    runner.invoke(
        cli, ["cases", "list"], obj=cli_state,
    )
    assert cli_state.sdk.cases.get_all.call_count == 1


def test_list_prints_expected_data(runner, cli_state, py42_response):
    py42_response.data = json.loads(ALL_CASES)

    def gen():
        yield py42_response.data

    cli_state.sdk.cases.get_all.return_value = gen()
    result = runner.invoke(cli, ["cases", "list"], obj=cli_state,)
    assert "test@test.test" in result.output
    assert "2021-01-24T11:00:04.217878Z" in result.output
    assert "942897" in result.output


def test_show_calls_get_case_with_expected_params(runner, cli_state):
    runner.invoke(
        cli, ["cases", "show", "1"], obj=cli_state,
    )
    cli_state.sdk.cases.get.assert_called_once_with(1)


def test_show_with_include_file_events_calls_file_events_get_all_with_expected_params(
    runner, cli_state
):
    runner.invoke(
        cli, ["cases", "show", "1", "--include-file-events"], obj=cli_state,
    )
    cli_state.sdk.cases.file_events.get_all.assert_called_once_with(1)


def test_show_when_py42_raises_exception_prints_error_message(runner, cli_state, error):
    cli_state.sdk.cases.file_events.get_all.side_effect = Py42NotFoundError(error)
    result = runner.invoke(
        cli, ["cases", "show", "1", "--include-file-events"], obj=cli_state,
    )
    cli_state.sdk.cases.file_events.get_all.assert_called_once_with(1)
    assert "Invalid case-number 1." in result.output


def test_show_prints_expected_data(runner, cli_state, py42_response):
    py42_response.data = json.loads(CASE_DETAILS)
    cli_state.sdk.cases.get.return_value = py42_response
    result = runner.invoke(cli, ["cases", "show", "1"], obj=cli_state,)
    assert "test@test.test" in result.output


def test_show_prints_expected_data_with_include_file_events_option(
    runner, cli_state, py42_response
):
    py42_response.text = ALL_EVENTS
    cli_state.sdk.cases.file_events.get_all.return_value = py42_response
    result = runner.invoke(
        cli, ["cases", "show", "1", "--include-file-events"], obj=cli_state,
    )
    assert (
        "0_1d71796f-af5b-4231-9d8e-df6434da4663_984418168383179707_986472527798692818_971"
        in result.output
    )


def test_show_case_when_missing_case_number_prints_error(runner, cli_state):
    command = ["cases", "show"]
    result = runner.invoke(cli, command, obj=cli_state)
    assert result.exit_code == 2
    assert MISSING_CASE_NUMBER_ARG in result.output


def test_export_calls_export_summary_with_expected_params(runner, cli_state, mocker):
    with mock.patch("builtins.open", mock_open()) as mf:
        runner.invoke(
            cli, ["cases", "export", "1"], obj=cli_state,
        )
        cli_state.sdk.cases.export_summary.assert_called_once_with(1)
        mf.assert_called_once_with("./1_case_summary.pdf", "wb")


def test_export_when_missing_case_number_prints_error(runner, cli_state):
    command = ["cases", "export"]
    result = runner.invoke(cli, command, obj=cli_state)
    assert result.exit_code == 2
    assert MISSING_CASE_NUMBER_ARG in result.output


def test_file_events_add_calls_add_event_with_expected_params(runner, cli_state):
    runner.invoke(
        cli,
        ["cases", "file-events", "add", "--case-number", "1", "--event-id", "1"],
        obj=cli_state,
    )
    cli_state.sdk.cases.file_events.add.assert_called_once_with(1, "1")


def test_file_events_add_when_py42_raises_exception_prints_error_message(
    runner, cli_state, error
):
    cli_state.sdk.cases.file_events.add.side_effect = Py42BadRequestError(error)
    result = runner.invoke(
        cli,
        ["cases", "file-events", "add", "--case-number", "1", "--event-id", "1"],
        obj=cli_state,
    )
    cli_state.sdk.cases.file_events.add.assert_called_once_with(1, "1")
    assert "Invalid case-number or event-id." in result.output


def test_file_events_add_when_missing_event_id_prints_error(runner, cli_state):
    command = ["cases", "file-events", "remove", "--case-number", "4"]
    result = runner.invoke(cli, command, obj=cli_state)
    assert result.exit_code == 2
    assert MISSING_EVENT_ID in result.output


def test_file_events_add_when_missing_case_number_prints_error(runner, cli_state):
    command = ["cases", "file-events", "add"]
    result = runner.invoke(cli, command, obj=cli_state)
    assert result.exit_code == 2
    assert MISSING_CASE_NUMBER_OPTION in result.output


def test_file_events_remove_calls_delete_event_with_expected_params(runner, cli_state):
    runner.invoke(
        cli,
        ["cases", "file-events", "remove", "--case-number", "1", "--event-id", "1"],
        obj=cli_state,
    )
    cli_state.sdk.cases.file_events.delete.assert_called_once_with(1, "1")


def test_file_events_remove_when_py42_raises_exception_prints_error_message(
    runner, cli_state, error
):
    cli_state.sdk.cases.file_events.delete.side_effect = Py42NotFoundError(error)
    result = runner.invoke(
        cli,
        ["cases", "file-events", "remove", "--case-number", "1", "--event-id", "1"],
        obj=cli_state,
    )
    cli_state.sdk.cases.file_events.delete.assert_called_once_with(1, "1")
    assert "Invalid case-number or event-id." in result.output


def test_file_events_remove_when_missing_event_id_prints_error(runner, cli_state):
    command = ["cases", "file-events", "remove", "--case-number", "4"]
    result = runner.invoke(cli, command, obj=cli_state)
    assert result.exit_code == 2
    assert MISSING_EVENT_ID in result.output


def test_file_events_remove_when_missing_case_number_prints_error(runner, cli_state):
    command = ["cases", "file-events", "add"]
    result = runner.invoke(cli, command, obj=cli_state)
    assert result.exit_code == 2
    assert MISSING_CASE_NUMBER_OPTION in result.output


def test_file_events_list_calls_get_all_with_expected_params(runner, cli_state):
    runner.invoke(
        cli, ["cases", "file-events", "list", "1"], obj=cli_state,
    )
    cli_state.sdk.cases.file_events.get_all.assert_called_once_with(1)


def test_file_events_list_prints_expected_data(runner, cli_state):
    cli_state.sdk.cases.file_events.get_all.return_value = json.loads(ALL_EVENTS)
    result = runner.invoke(cli, ["cases", "file-events", "list", "1"], obj=cli_state,)
    assert (
        "0_1d71796f-af5b-4231-9d8e-df6434da4663_984418168383179707_986472527798692818_971"
        in result.output
    )
    assert "2020-12-23T12:41:38.592Z" in result.output


def test_file_events_list_when_missing_case_number_prints_error(runner, cli_state):
    command = ["cases", "file-events", "list"]
    result = runner.invoke(cli, command, obj=cli_state)
    assert result.exit_code == 2
    assert MISSING_CASE_NUMBER_ARG in result.output
