from py42.response import Py42Response
from requests import Request
from tests.cmds.conftest import get_user_not_on_list_side_effect
from tests.cmds.conftest import thread_safe_side_effect
from tests.conftest import TEST_ID

from .conftest import TEST_EMPLOYEE
from code42cli.main import cli


DEPARTING_EMPLOYEE_ITEM = """{
    "type$": "DEPARTING_EMPLOYEE_V2",
    "tenantId": "1111111-af5b-4231-9d8e-000000000",
    "userId": "TEST USER UID",
    "userName": "test.testerson@example.com",
    "displayName": "Testerson",
    "notes": "Leaving for competitor",
    "createdAt": "2020-06-23T19:57:37.1345130Z",
    "status": "OPEN",
    "cloudUsernames": ["cloud@example.com"],
    "departureDate": "2020-07-07"
}
"""


def test_list_departing_employees_lists_expected_properties(
    runner, cli_state_with_user, mocker
):
    def gen(*args, **kwargs):
        response = mocker.MagicMock(spec=Request)
        response.text = """{{"items": [{0}]}}""".format(DEPARTING_EMPLOYEE_ITEM)
        pages = [response, response, response]
        for page in pages:
            yield Py42Response(page)

    cli_state_with_user.sdk.detectionlists.departing_employee.get_all.side_effect = gen
    res = runner.invoke(cli, ["departing-employee", "list"], obj=cli_state_with_user)
    assert "Username" in res.output
    assert "Notes" in res.output
    assert "test.testerson@example.com" in res.output
    assert "Leaving for competitor" in res.output
    assert "Departure Date" in res.output
    assert "2020-07-07" in res.output


def test_list_departing_employees_when_given_raw_json_lists_expected_properties(
    runner, cli_state_with_user, mocker
):
    def gen(*args, **kwargs):
        response = mocker.MagicMock(spec=Request)
        response.text = """{{"items": [{0}]}}""".format(DEPARTING_EMPLOYEE_ITEM)
        pages = [response, response, response]
        for page in pages:
            yield Py42Response(page)

    cli_state_with_user.sdk.detectionlists.departing_employee.get_all.side_effect = gen
    res = runner.invoke(
        cli, ["departing-employee", "list", "-f", "RAW-JSON"], obj=cli_state_with_user
    )
    assert "userName" in res.output
    assert "notes" in res.output
    assert "test.testerson@example.com" in res.output
    assert "Leaving for competitor" in res.output
    assert "cloudUsernames" in res.output
    assert "cloud@example.com" in res.output
    assert "departureDate" in res.output
    assert "2020-07-07" in res.output


def test_list_departing_employee_when_no_employees_echos_expected_message(
    runner, cli_state_with_user, mocker
):
    def gen(*args, **kwargs):
        response = mocker.MagicMock(spec=Request)
        response.text = """{"items": []}"""
        pages = [response]
        for page in pages:
            yield Py42Response(page)

    cli_state_with_user.sdk.detectionlists.departing_employee.get_all.side_effect = gen
    res = runner.invoke(cli, ["departing-employee", "list"], obj=cli_state_with_user)
    assert "There are currently no users on the departing employee list." in res.output


def test_add_departing_employee_when_given_cloud_alias_adds_alias(
    runner, cli_state_with_user
):
    alias = "departing employee alias"
    runner.invoke(
        cli,
        ["departing-employee", "add", TEST_EMPLOYEE, "--cloud-alias", alias],
        obj=cli_state_with_user,
    )
    cli_state_with_user.sdk.detectionlists.add_user_cloud_alias.assert_called_once_with(
        TEST_ID, alias
    )


def test_add_departing_employee_when_given_notes_updates_notes(
    runner, cli_state_with_user, profile
):
    notes = "is leaving"
    runner.invoke(
        cli,
        ["departing-employee", "add", TEST_EMPLOYEE, "--notes", notes],
        obj=cli_state_with_user,
    )
    cli_state_with_user.sdk.detectionlists.update_user_notes.assert_called_once_with(
        TEST_ID, notes
    )


def test_add_departing_employee_adds(
    runner, cli_state_with_user,
):
    departure_date = "2020-02-02"
    runner.invoke(
        cli,
        [
            "departing-employee",
            "add",
            TEST_EMPLOYEE,
            "--departure-date",
            departure_date,
        ],
        obj=cli_state_with_user,
    )
    cli_state_with_user.sdk.detectionlists.departing_employee.add.assert_called_once_with(
        TEST_ID, "2020-02-02"
    )


def test_add_departing_employee_when_user_does_not_exist_exits(
    runner, cli_state_without_user
):
    result = runner.invoke(
        cli, ["departing-employee", "add", TEST_EMPLOYEE], obj=cli_state_without_user
    )
    assert result.exit_code == 1
    assert "User '{}' does not exist.".format(TEST_EMPLOYEE) in result.output


def test_add_departing_employee_when_user_already_exits_with_correct_message(
    mocker, runner, cli_state_with_user, user_already_added_error
):
    def add_user(user):
        raise user_already_added_error

    cli_state_with_user.sdk.detectionlists.departing_employee.add.side_effect = add_user
    result = runner.invoke(
        cli, ["departing-employee", "add", TEST_EMPLOYEE], obj=cli_state_with_user
    )
    assert result.exit_code == 1
    assert "'{}' is already on the departing-employee list.".format(TEST_EMPLOYEE)


def test_remove_departing_employee_calls_remove(runner, cli_state_with_user):
    runner.invoke(
        cli, ["departing-employee", "remove", TEST_EMPLOYEE], obj=cli_state_with_user
    )
    cli_state_with_user.sdk.detectionlists.departing_employee.remove.assert_called_once_with(
        TEST_ID
    )


def test_remove_departing_employee_when_user_does_not_exist_exits(
    runner, cli_state_without_user
):
    result = runner.invoke(
        cli, ["departing-employee", "remove", TEST_EMPLOYEE], obj=cli_state_without_user
    )
    assert result.exit_code == 1
    assert "User '{}' does not exist.".format(TEST_EMPLOYEE) in result.output


def test_add_bulk_users_calls_expected_py42_methods(runner, mocker, cli_state):
    de_add_user = thread_safe_side_effect()
    add_user_cloud_alias = thread_safe_side_effect()
    update_user_notes = thread_safe_side_effect()

    cli_state.sdk.detectionlists.departing_employee.add.side_effect = de_add_user
    cli_state.sdk.detectionlists.add_user_cloud_alias.side_effect = add_user_cloud_alias
    cli_state.sdk.detectionlists.update_user_notes.side_effect = update_user_notes

    with runner.isolated_filesystem():
        with open("test_add.csv", "w") as csv:
            csv.writelines(
                [
                    "username,cloud_alias,departure_date,notes\n",
                    "test_user,test_alias,2020-01-01,test_note\n",
                    "test_user_2,test_alias_2,2020-02-01,test_note_2\n",
                    "test_user_3,,,\n",
                    "test_user_3,,2020-30-02,\n",
                    "test_user_3,,20-02-2020,\n",
                ]
            )
        runner.invoke(
            cli, ["departing-employee", "bulk", "add", "test_add.csv"], obj=cli_state
        )
    de_add_user_call_args = [call[1] for call in de_add_user.call_args_list]
    assert de_add_user.call_count == 3
    assert "2020-01-01" in de_add_user_call_args
    assert "2020-02-01" in de_add_user_call_args
    assert None in de_add_user_call_args

    add_user_cloud_alias_call_args = [
        call[1] for call in add_user_cloud_alias.call_args_list
    ]
    assert add_user_cloud_alias.call_count == 2
    assert "test_alias" in add_user_cloud_alias_call_args
    assert "test_alias_2" in add_user_cloud_alias_call_args

    update_user_notes_call_args = [call[1] for call in update_user_notes.call_args_list]
    assert update_user_notes.call_count == 2
    assert "test_note" in update_user_notes_call_args
    assert "test_note_2" in update_user_notes_call_args


def test_remove_bulk_users_uses_expected_arguments(runner, mocker, cli_state_with_user):
    bulk_processor = mocker.patch("code42cli.cmds.departing_employee.run_bulk_process")
    with runner.isolated_filesystem():
        with open("test_remove.csv", "w") as csv:
            csv.writelines(["# username\n", "test_user1\n", "test_user2\n"])
        runner.invoke(
            cli,
            ["departing-employee", "bulk", "remove", "test_remove.csv"],
            obj=cli_state_with_user,
        )
    assert bulk_processor.call_args[0][1] == ["test_user1", "test_user2"]


def test_add_departing_employee_when_invalid_date_validation_raises_error(
    runner, cli_state_with_user
):
    departure_date = "2020-02-30"
    result = runner.invoke(
        cli,
        [
            "departing-employee",
            "add",
            TEST_EMPLOYEE,
            "--departure-date",
            departure_date,
        ],
        obj=cli_state_with_user,
    )
    assert result.exit_code == 2
    assert (
        "Invalid value for '--departure-date': invalid datetime format" in result.output
    )


def test_add_departing_employee_when_invalid_date_format_validation_raises_error(
    runner, cli_state_with_user
):
    departure_date = "2020-30-01"
    result = runner.invoke(
        cli,
        [
            "departing-employee",
            "add",
            TEST_EMPLOYEE,
            "--departure-date",
            departure_date,
        ],
        obj=cli_state_with_user,
    )
    assert result.exit_code == 2
    assert (
        "Invalid value for '--departure-date': invalid datetime format" in result.output
    )


def test_remove_departing_employee_when_user_not_on_list_prints_expected_error(
    mocker, runner, cli_state
):
    cli_state.sdk.detectionlists.departing_employee.remove.side_effect = get_user_not_on_list_side_effect(
        mocker
    )
    test_username = "test@example.com"
    result = runner.invoke(
        cli, ["departing-employee", "remove", test_username], obj=cli_state
    )
    assert (
        "User {} is not currently on the departing-employee detection list.".format(
            test_username
        )
        in result.output
    )
