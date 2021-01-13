import json
from unittest import mock
from unittest.mock import mock_open

import pytest
from py42.exceptions import Py42BadRequestError
from py42.exceptions import Py42NotFoundError
from requests import Request
from tests.cmds.conftest import get_generator_for_get_all

from code42cli.main import cli


EVENT_DETAILS = """{"eventId": "0_1d71796f-af5b-4231-9d8e-df6434da4663_984418168383179707_986472527798692818_971"}
"""

ALL_EVENTS = """{"events": [{"eventId": "0_1d71796f-af5b-4231-9d8e-df6434da4663_984418168383179707_986472527798692818_971"}]}"""

ALL_CASES = """{"cases": [{"number": 3,"name": "test@test.test"}], "totalCount": 31}"""

CASE_DETAILS = """{"number": 3, "name": "test@test.test"}"""


@pytest.fixture
def error(mocker):
    error = mocker.Mock(spec=Exception)
    error.response = "error"
    return error


@pytest.fixture
def py42_response(mocker):
    return mocker.MagicMock(spec=Request)


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
            "--notes",
            "n",
            "--subject",
            "s",
        ],
        obj=cli_state,
    )
    cli_state.sdk.cases.create.assert_called_once_with(
        "TEST_CASE", assignee="a", description="d", findings="n", subject="s"
    )


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
            "--notes",
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


def test_list_calls_get_all_with_expected_params(runner, cli_state):
    runner.invoke(
        cli, ["cases", "list"], obj=cli_state,
    )
    assert cli_state.sdk.cases.get_all.call_count == 1


def test_show_calls_get_case_with_expected_params(runner, cli_state):
    runner.invoke(
        cli, ["cases", "show", "1"], obj=cli_state,
    )
    cli_state.sdk.cases.get.assert_called_once_with(1)


def test_export_calls_export_summary_with_expected_params(runner, cli_state, mocker):
    with mock.patch("builtins.open", mock_open()) as mf:
        runner.invoke(
            cli, ["cases", "export", "1"], obj=cli_state,
        )
        cli_state.sdk.cases.export_summary.assert_called_once_with(1)
        mf.assert_called_once_with("./1_case_summary.pdf", "wb")


def test_file_events_add_calls_add_event_with_expected_params(runner, cli_state):
    runner.invoke(
        cli, ["cases", "file-events", "add", "1", "--event-id", "1"], obj=cli_state,
    )
    cli_state.sdk.cases.file_events.add.assert_called_once_with(1, "1")


def test_file_events_remove_calls_delete_event_with_expected_params(runner, cli_state):
    runner.invoke(
        cli, ["cases", "file-events", "remove", "1", "--event-id", "1"], obj=cli_state,
    )
    cli_state.sdk.cases.file_events.delete.assert_called_once_with(1, "1")


def test_file_events_list_calls_get_all_with_expected_params(runner, cli_state):
    runner.invoke(
        cli, ["cases", "file-events", "list", "1"], obj=cli_state,
    )
    cli_state.sdk.cases.file_events.get_all.assert_called_once_with(1)


def test_file_events_show_calls_get_event_with_expected_params(runner, cli_state):
    runner.invoke(
        cli, ["cases", "file-events", "show", "1", "--event-id", "1"], obj=cli_state,
    )
    cli_state.sdk.cases.file_events.get.assert_called_once_with(1, "1")


def test_file_events_show_returns_error_message_when_py42_raises_exception(
    runner, cli_state, error
):
    cli_state.sdk.cases.file_events.get.side_effect = Py42NotFoundError(error)
    result = runner.invoke(
        cli, ["cases", "file-events", "show", "1", "--event-id", "1"], obj=cli_state,
    )
    cli_state.sdk.cases.file_events.get.assert_called_once_with(1, "1")
    assert "Invalid case-number or event-id." in result.output


def test_file_events_add_returns_error_message_when_py42_raises_exception(
    runner, cli_state, error
):
    cli_state.sdk.cases.file_events.add.side_effect = Py42BadRequestError(error)
    result = runner.invoke(
        cli, ["cases", "file-events", "add", "1", "--event-id", "1"], obj=cli_state,
    )
    cli_state.sdk.cases.file_events.add.assert_called_once_with(1, "1")
    assert "Invalid case-number or event-id." in result.output


def test_file_events_remove_returns_error_message_when_py42_raises_exception(
    runner, cli_state, error
):
    cli_state.sdk.cases.file_events.delete.side_effect = Py42NotFoundError(error)
    result = runner.invoke(
        cli, ["cases", "file-events", "remove", "1", "--event-id", "1"], obj=cli_state,
    )
    cli_state.sdk.cases.file_events.delete.assert_called_once_with(1, "1")
    assert "Invalid case-number or event-id." in result.output


def test_show_returns_expected_data(runner, cli_state, py42_response):
    py42_response.data = json.loads(CASE_DETAILS)
    cli_state.sdk.cases.get.return_value = py42_response
    result = runner.invoke(cli, ["cases", "show", "1"], obj=cli_state,)
    assert "test@test.test" in result.output


def test_list_returns_expected_data(runner, cli_state, py42_response, mocker):
    py42_response.data = json.loads(ALL_CASES)

    def gen():
        yield py42_response.data

    cli_state.sdk.cases.get_all.return_value = gen()
    result = runner.invoke(cli, ["cases", "list"], obj=cli_state,)
    assert "test@test.test" in result.output


def test_events_show_returns_expected_data(runner, cli_state, py42_response):
    py42_response.data = json.loads(EVENT_DETAILS)
    cli_state.sdk.cases.file_events.get.return_value = py42_response
    result = runner.invoke(cli, ["cases", "file-events", "show", "1", "--event-id", "e"], obj=cli_state,)
    assert "0_1d71796f-af5b-4231-9d8e-df6434da4663_984418168383179707_986472527798692818_971" in result.output


def test_events_list_returns_expected_data(runner, cli_state):
    cli_state.sdk.cases.file_events.get_all.return_value = json.loads(ALL_EVENTS)
    result = runner.invoke(cli, ["cases", "file-events", "list", "1"], obj=cli_state,)
    assert "0_1d71796f-af5b-4231-9d8e-df6434da4663_984418168383179707_986472527798692818_971" in result.output