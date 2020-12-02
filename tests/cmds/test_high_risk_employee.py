from py42.response import Py42Response
from requests import Request
from tests.cmds.conftest import get_user_not_on_list_side_effect
from tests.cmds.conftest import TEST_EMPLOYEE
from tests.cmds.conftest import thread_safe_side_effect
from tests.conftest import TEST_ID

from code42cli.main import cli

_NAMESPACE = "code42cli.cmds.high_risk_employee"


HIGH_RISK_EMPLOYEE_ITEM = """{
    "type$": "HIGH_RISK_EMPLOYEE_V2",
    "tenantId": "1111111-af5b-4231-9d8e-000000000",
    "userId": "TEST USER UID",
    "userName": "test.testerson@example.com",
    "displayName": "Testerson",
    "notes": "Leaving for competitor",
    "createdAt": "2020-06-23T19:57:37.1345130Z",
    "status": "OPEN",
    "cloudUsernames": ["cloud@example.com"],
    "riskFactors": ["PERFORMANCE_CONCERNS"]
}
"""


def test_list_high_risk_employees_lists_expected_properties(
    runner, cli_state_with_user, mocker
):
    def gen(*args, **kwargs):
        response = mocker.MagicMock(spec=Request)
        response.text = """{{"items": [{0}]}}""".format(HIGH_RISK_EMPLOYEE_ITEM)
        pages = [response, response, response]
        for page in pages:
            yield Py42Response(page)

    cli_state_with_user.sdk.detectionlists.high_risk_employee.get_all.side_effect = gen
    res = runner.invoke(cli, ["high-risk-employee", "list"], obj=cli_state_with_user)
    assert "Username" in res.output
    assert "Notes" in res.output
    assert "test.testerson@example.com" in res.output


def test_list_high_risk_employees_when_given_raw_json_lists_expected_properties(
    runner, cli_state_with_user, mocker
):
    def gen(*args, **kwargs):
        response = mocker.MagicMock(spec=Request)
        response.text = """{{"items": [{0}]}}""".format(HIGH_RISK_EMPLOYEE_ITEM)
        pages = [response, response, response]
        for page in pages:
            yield Py42Response(page)

    cli_state_with_user.sdk.detectionlists.high_risk_employee.get_all.side_effect = gen
    res = runner.invoke(
        cli, ["high-risk-employee", "list", "-f", "RAW-JSON"], obj=cli_state_with_user
    )
    assert "userName" in res.output
    assert "notes" in res.output
    assert "test.testerson@example.com" in res.output
    assert "Leaving for competitor" in res.output
    assert "cloudUsernames" in res.output
    assert "cloud@example.com" in res.output
    assert "riskFactors" in res.output
    assert "PERFORMANCE_CONCERNS" in res.output


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
    res = runner.invoke(cli, ["high-risk-employee", "list"], obj=cli_state_with_user)
    assert "There are currently no users on the high risk employee list." in res.output


def test_add_high_risk_employee_adds(runner, cli_state_with_user):
    runner.invoke(
        cli, ["high-risk-employee", "add", TEST_EMPLOYEE], obj=cli_state_with_user
    )
    cli_state_with_user.sdk.detectionlists.high_risk_employee.add.assert_called_once_with(
        TEST_ID
    )


def test_add_high_risk_employee_when_given_cloud_alias_adds_alias(
    runner, cli_state_with_user
):
    alias = "risk employee alias"
    runner.invoke(
        cli,
        ["high-risk-employee", "add", TEST_EMPLOYEE, "--cloud-alias", alias],
        obj=cli_state_with_user,
    )
    cli_state_with_user.sdk.detectionlists.add_user_cloud_alias.assert_called_once_with(
        TEST_ID, alias
    )


def test_add_high_risk_employee_when_given_risk_tags_adds_tags(
    runner, cli_state_with_user
):
    runner.invoke(
        cli,
        [
            "high-risk-employee",
            "add",
            TEST_EMPLOYEE,
            "-t",
            "FLIGHT_RISK",
            "-t",
            "ELEVATED_ACCESS_PRIVILEGES",
            "-t",
            "POOR_SECURITY_PRACTICES",
        ],
        obj=cli_state_with_user,
    )
    cli_state_with_user.sdk.detectionlists.add_user_risk_tags.assert_called_once_with(
        TEST_ID,
        ("FLIGHT_RISK", "ELEVATED_ACCESS_PRIVILEGES", "POOR_SECURITY_PRACTICES"),
    )


def test_add_high_risk_employee_when_given_notes_updates_notes(
    runner, cli_state_with_user
):
    notes = "being risky"
    runner.invoke(
        cli,
        ["high-risk-employee", "add", TEST_EMPLOYEE, "--notes", notes],
        obj=cli_state_with_user,
    )
    cli_state_with_user.sdk.detectionlists.update_user_notes.assert_called_once_with(
        TEST_ID, notes
    )


def test_add_high_risk_employee_when_user_does_not_exist_exits_with_correct_message(
    runner, cli_state_without_user
):
    result = runner.invoke(
        cli, ["high-risk-employee", "add", TEST_EMPLOYEE], obj=cli_state_without_user
    )
    assert result.exit_code == 1
    assert "User '{}' does not exist.".format(TEST_EMPLOYEE) in result.output


def test_add_high_risk_employee_when_user_already_added_exits_with_correct_message(
    mocker, runner, cli_state_with_user, user_already_added_error
):
    def add_user(user):
        raise user_already_added_error

    cli_state_with_user.sdk.detectionlists.high_risk_employee.add.side_effect = add_user

    result = runner.invoke(
        cli, ["high-risk-employee", "add", TEST_EMPLOYEE], obj=cli_state_with_user
    )
    assert result.exit_code == 1
    assert "User with ID TEST_ID is already on the detection list" in result.output


def test_remove_high_risk_employee_calls_remove(runner, cli_state_with_user):
    runner.invoke(
        cli, ["high-risk-employee", "remove", TEST_EMPLOYEE], obj=cli_state_with_user
    )
    cli_state_with_user.sdk.detectionlists.high_risk_employee.remove.assert_called_once_with(
        TEST_ID
    )


def test_remove_high_risk_employee_when_user_does_not_exist_exits_with_correct_message(
    runner, cli_state_without_user
):
    result = runner.invoke(
        cli, ["high-risk-employee", "remove", TEST_EMPLOYEE], obj=cli_state_without_user
    )
    assert result.exit_code == 1
    assert "User '{}' does not exist.".format(TEST_EMPLOYEE) in result.output


def test_generate_template_file_when_given_add_generates_template_from_handler(
    runner, cli_state
):
    pass


def test_generate_template_file_when_given_remove_generates_template_from_handler():
    pass


def test_bulk_add_employees_calls_expected_py42_methods(runner, cli_state):
    add_user_cloud_alias = thread_safe_side_effect()
    add_user_risk_tags = thread_safe_side_effect()
    update_user_notes = thread_safe_side_effect()
    hre_add_user = thread_safe_side_effect()

    cli_state.sdk.detectionlists.add_user_cloud_alias.side_effect = add_user_cloud_alias
    cli_state.sdk.detectionlists.add_user_risk_tags.side_effect = add_user_risk_tags
    cli_state.sdk.detectionlists.update_user_notes.side_effect = update_user_notes
    cli_state.sdk.detectionlists.high_risk_employee.add.side_effect = hre_add_user

    with runner.isolated_filesystem():
        with open("test_add.csv", "w") as csv:
            csv.writelines(
                [
                    "username,cloud_alias,risk_tag,notes\n",
                    "test_user,test_alias,test_tag_1 test_tag_2,test_note\n",
                    "test_user_2,test_alias_2,test_tag_3,test_note_2\n",
                    "test_user_3,,,\n",
                ]
            )
        runner.invoke(
            cli, ["high-risk-employee", "bulk", "add", "test_add.csv"], obj=cli_state
        )
    alias_args = [call[1] for call in add_user_cloud_alias.call_args_list]
    assert add_user_cloud_alias.call_count == 2
    assert "test_alias" in alias_args
    assert "test_alias_2" in alias_args

    add_risk_tags_call_args = [call[1] for call in add_user_risk_tags.call_args_list]
    assert add_user_risk_tags.call_count == 2
    assert ["test_tag_1", "test_tag_2"] in add_risk_tags_call_args
    assert ["test_tag_3"] in add_risk_tags_call_args

    add_notes_call_args = [call[1] for call in update_user_notes.call_args_list]
    assert update_user_notes.call_count == 2
    assert "test_note" in add_notes_call_args
    assert "test_note_2" in add_notes_call_args

    assert hre_add_user.call_count == 3


def test_bulk_remove_employees_uses_expected_arguments(runner, cli_state, mocker):
    bulk_processor = mocker.patch("{}.run_bulk_process".format(_NAMESPACE))
    with runner.isolated_filesystem():
        with open("test_remove.csv", "w") as csv:
            csv.writelines(["# username\n", "test@example.com\n", "test2@example.com"])
        runner.invoke(
            cli,
            ["high-risk-employee", "bulk", "remove", "test_remove.csv"],
            obj=cli_state,
        )
        assert bulk_processor.call_args[0][1] == [
            "test@example.com",
            "test2@example.com",
        ]


def test_bulk_add_risk_tags_uses_expected_arguments(runner, cli_state, mocker):
    bulk_processor = mocker.patch("{}.run_bulk_process".format(_NAMESPACE))
    with runner.isolated_filesystem():
        with open("test_add_risk_tags.csv", "w") as csv:
            csv.writelines(
                ["username,tag\n", "test@example.com,tag1\n", "test2@example.com,tag2"]
            )
        runner.invoke(
            cli,
            ["high-risk-employee", "bulk", "add-risk-tags", "test_add_risk_tags.csv"],
            obj=cli_state,
        )
        assert bulk_processor.call_args[0][1] == [
            {"username": "test@example.com", "tag": "tag1"},
            {"username": "test2@example.com", "tag": "tag2"},
        ]


def test_bulk_remove_risk_tags_uses_expected_arguments(runner, cli_state, mocker):
    bulk_processor = mocker.patch("{}.run_bulk_process".format(_NAMESPACE))
    with runner.isolated_filesystem():
        with open("test_remove_risk_tags.csv", "w") as csv:
            csv.writelines(
                ["username,tag\n", "test@example.com,tag1\n", "test2@example.com,tag2"]
            )
        runner.invoke(
            cli,
            [
                "high-risk-employee",
                "bulk",
                "remove-risk-tags",
                "test_remove_risk_tags.csv",
            ],
            obj=cli_state,
        )
        assert bulk_processor.call_args[0][1] == [
            {"username": "test@example.com", "tag": "tag1"},
            {"username": "test2@example.com", "tag": "tag2"},
        ]


def test_remove_high_risk_employee_when_user_not_on_list_prints_expected_error(
    mocker, runner, cli_state
):
    cli_state.sdk.detectionlists.high_risk_employee.remove.side_effect = get_user_not_on_list_side_effect(
        mocker
    )
    test_username = "test@example.com"
    result = runner.invoke(
        cli, ["high-risk-employee", "remove", test_username], obj=cli_state
    )
    assert (
        "User {} is not currently on the high-risk-employee detection list.".format(
            test_username
        )
        in result.output
    )
