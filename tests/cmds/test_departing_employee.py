import pytest

from code42cli.main import cli
from code42cli.errors import UserAlreadyAddedError, UserDoesNotExistError


from tests.conftest import TEST_ID

from py42.exceptions import Py42BadRequestError


_EMPLOYEE = "departing employee"


def test_add_departing_employee_when_given_cloud_alias_adds_alias(runner, cli_state_with_user):
    alias = "departing employee alias"
    result = runner.invoke(
        cli,
        ["departing-employee", "add", _EMPLOYEE, "--cloud-alias", alias],
        obj=cli_state_with_user,
    )
    cli_state_with_user.sdk.detectionlists.add_user_cloud_alias.assert_called_once_with(
        TEST_ID, alias
    )


def test_add_departing_employee_when_given_notes_updates_notes(
    runner, cli_state_with_user, profile
):
    notes = "is leaving"
    result = runner.invoke(
        cli, ["departing-employee", "add", _EMPLOYEE, "--notes", notes], obj=cli_state_with_user,
    )
    cli_state_with_user.sdk.detectionlists.update_user_notes.assert_called_once_with(TEST_ID, notes)


def test_add_departing_employee_adds(
    runner, cli_state_with_user,
):
    departure_date = "2020-02-02"
    result = runner.invoke(
        cli,
        ["departing-employee", "add", _EMPLOYEE, "--departure-date", departure_date],
        obj=cli_state_with_user,
    )
    cli_state_with_user.sdk.detectionlists.departing_employee.add.assert_called_once_with(
        TEST_ID, "2020-02-02"
    )


def test_add_departing_employee_when_user_does_not_exist_exits(runner, cli_state_without_user):
    result = runner.invoke(
        cli, ["departing-employee", "add", _EMPLOYEE], obj=cli_state_without_user
    )
    assert result.exit_code == 1
    assert "User '{}' does not exist.".format(_EMPLOYEE) in result.output


def test_add_departing_employee_when_user_already_added_raises_UserAlreadyAddedError(
    runner, cli_state_with_user, bad_request_for_user_already_added
):
    cli_state_with_user.sdk.detectionlists.departing_employee.add.side_effect = (
        bad_request_for_user_already_added
    )
    result = runner.invoke(cli, ["departing-employee", "add", _EMPLOYEE], obj=cli_state_with_user)
    assert result.exit_code == 1
    assert "'{}' is already on the departing-employee list.".format(_EMPLOYEE)


def test_add_departing_employee_when_bad_request_but_not_user_already_added_raises_Py42BadRequestError(
    runner, cli_state_with_user, generic_bad_request
):
    cli_state_with_user.sdk.detectionlists.departing_employee.add.side_effect = generic_bad_request
    result = runner.invoke(cli, ["departing-employee", "add", _EMPLOYEE], obj=cli_state_with_user)
    assert result.exit_code == 1
    assert "Problem making request to server." in result.output
    assert "View details in" in result.output


def test_remove_departing_employee_calls_remove(runner, cli_state_with_user):
    result = runner.invoke(
        cli, ["departing-employee", "remove", _EMPLOYEE], obj=cli_state_with_user
    )
    cli_state_with_user.sdk.detectionlists.departing_employee.remove.assert_called_once_with(
        TEST_ID
    )


def test_remove_departing_employee_when_user_does_not_exist_exits(runner, cli_state_without_user):
    result = runner.invoke(
        cli, ["departing-employee", "remove", _EMPLOYEE], obj=cli_state_without_user
    )
    assert result.exit_code == 1
    assert "User '{}' does not exist.".format(_EMPLOYEE) in result.output


def test_add_bulk_users_uses_expected_arguments(runner, mocker, cli_state):
    with runner.isolated_filesystem():
        with open("test_add.csv", "w") as csv:
            csv.writelines(
                [
                    "username,cloud_alias,departure_date,notes\n",
                    "test_user,test_alias,2020-01-01,test_note\n",
                    "test_user_2,test_alias_2,2020-02-01,test_note_2\n",
                    "test_user_3,,,\n",
                ]
            )
        result = runner.invoke(
            cli, ["departing-employee", "bulk", "add", "test_add.csv"], obj=cli_state
        )
    departing_employee_add_call_args = [
        call[0][1] for call in cli_state.sdk.detectionlists.departing_employee.add.call_args_list
    ]
    assert cli_state.sdk.detectionlists.departing_employee.add.call_count == 3
    assert "2020-01-01" in departing_employee_add_call_args
    assert "2020-02-01" in departing_employee_add_call_args
    assert None in departing_employee_add_call_args

    cloud_alias_call_args = [
        call[0][1] for call in cli_state.sdk.detectionlists.add_user_cloud_alias.call_args_list
    ]
    assert cli_state.sdk.detectionlists.add_user_cloud_alias.call_count == 2
    assert "test_alias" in cloud_alias_call_args
    assert "test_alias_2" in cloud_alias_call_args

    add_notes_call_args = [
        call[0][1] for call in cli_state.sdk.detectionlists.update_user_notes.call_args_list
    ]
    assert cli_state.sdk.detectionlists.update_user_notes.call_count == 2
    assert "test_note" in add_notes_call_args
    assert "test_note_2" in add_notes_call_args


def test_remove_bulk_users_uses_expected_arguments(runner, mocker, cli_state_with_user):
    bulk_processor = mocker.patch("code42cli.cmds.departing_employee.run_bulk_process")
    with runner.isolated_filesystem():
        with open("test_remove.csv", "w") as csv:
            csv.writelines(["# username\n", "test_user1\n", "test_user2\n"])
        result = runner.invoke(
            cli,
            ["departing-employee", "bulk", "remove", "test_remove.csv"],
            obj=cli_state_with_user,
        )
    assert bulk_processor.call_args[0][1] == ["test_user1", "test_user2"]
