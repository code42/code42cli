from code42cli.main import cli

from tests.conftest import TEST_ID
from tests.cmds.conftest import thread_safe_side_effect

_NAMESPACE = "code42cli.cmds.high_risk_employee"
_EMPLOYEE = "risky employee"


def test_add_high_risk_employee_adds(runner, cli_state_with_user):
    result = runner.invoke(cli, ["high-risk-employee", "add", _EMPLOYEE], obj=cli_state_with_user)
    cli_state_with_user.sdk.detectionlists.high_risk_employee.add.assert_called_once_with(TEST_ID)


def test_add_high_risk_employee_when_given_cloud_alias_adds_alias(runner, cli_state_with_user):
    alias = "risk employee alias"
    result = runner.invoke(
        cli,
        ["high-risk-employee", "add", _EMPLOYEE, "--cloud-alias", alias],
        obj=cli_state_with_user,
    )
    cli_state_with_user.sdk.detectionlists.add_user_cloud_alias.assert_called_once_with(
        TEST_ID, alias
    )


def test_add_high_risk_employee_when_given_risk_tags_adds_tags(runner, cli_state_with_user):
    result = runner.invoke(
        cli,
        [
            "high-risk-employee",
            "add",
            _EMPLOYEE,
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
        TEST_ID, ("FLIGHT_RISK", "ELEVATED_ACCESS_PRIVILEGES", "POOR_SECURITY_PRACTICES")
    )


def test_add_high_risk_employee_when_given_notes_updates_notes(runner, cli_state_with_user):
    notes = "being risky"
    result = runner.invoke(
        cli, ["high-risk-employee", "add", _EMPLOYEE, "--notes", notes], obj=cli_state_with_user,
    )
    cli_state_with_user.sdk.detectionlists.update_user_notes.assert_called_once_with(TEST_ID, notes)


def test_add_high_risk_employee_when_user_does_not_exist_exits_with_correct_message(
    runner, cli_state_without_user
):
    result = runner.invoke(
        cli, ["high-risk-employee", "add", _EMPLOYEE], obj=cli_state_without_user
    )
    assert result.exit_code == 1
    assert "User '{}' does not exist.".format(_EMPLOYEE) in result.output


def test_add_high_risk_employee_when_user_already_added_exits_with_correct_message(
    runner, cli_state_with_user, bad_request_for_user_already_added
):
    cli_state_with_user.sdk.detectionlists.high_risk_employee.add.side_effect = (
        bad_request_for_user_already_added
    )
    result = runner.invoke(cli, ["high-risk-employee", "add", _EMPLOYEE], obj=cli_state_with_user)
    assert result.exit_code == 1
    assert "'{}' is already on the high-risk-employee list.".format(_EMPLOYEE) in result.output


def test_add_high_risk_employee_when_bad_request_but_not_user_already_added_exits_with_message_to_see_logs(
    runner, cli_state_with_user, generic_bad_request
):
    cli_state_with_user.sdk.detectionlists.high_risk_employee.add.side_effect = generic_bad_request
    result = runner.invoke(cli, ["high-risk-employee", "add", _EMPLOYEE], obj=cli_state_with_user)
    assert result.exit_code == 1
    assert "Problem making request to server." in result.output
    assert "View details in" in result.output


def test_remove_high_risk_employee_calls_remove(runner, cli_state_with_user):
    result = runner.invoke(
        cli, ["high-risk-employee", "remove", _EMPLOYEE], obj=cli_state_with_user
    )
    cli_state_with_user.sdk.detectionlists.high_risk_employee.remove.assert_called_once_with(
        TEST_ID
    )


def test_remove_high_risk_employee_when_user_does_not_exist_exits_with_correct_message(
    runner, cli_state_without_user
):
    result = runner.invoke(
        cli, ["high-risk-employee", "remove", _EMPLOYEE], obj=cli_state_without_user
    )
    assert result.exit_code == 1
    assert "User '{}' does not exist.".format(_EMPLOYEE) in result.output


def test_generate_template_file_when_given_add_generates_template_from_handler(
    runner, mocker, cli_state
):
    pass


def test_generate_template_file_when_given_remove_generates_template_from_handler():
    pass


def test_bulk_add_employees_calls_expected_py42_methods(runner, cli_state, mocker):
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
        result = runner.invoke(
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
        result = runner.invoke(
            cli, ["high-risk-employee", "bulk", "remove", "test_remove.csv"], obj=cli_state
        )
        assert bulk_processor.call_args[0][1] == ["test@example.com", "test2@example.com"]


def test_bulk_add_risk_tags_uses_expected_arguments(runner, cli_state, mocker):
    bulk_processor = mocker.patch("{}.run_bulk_process".format(_NAMESPACE))
    with runner.isolated_filesystem():
        with open("test_add_risk_tags.csv", "w") as csv:
            csv.writelines(["username,tag\n", "test@example.com,tag1\n", "test2@example.com,tag2"])
        result = runner.invoke(
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
            csv.writelines(["username,tag\n", "test@example.com,tag1\n", "test2@example.com,tag2"])
        result = runner.invoke(
            cli,
            ["high-risk-employee", "bulk", "remove-risk-tags", "test_remove_risk_tags.csv"],
            obj=cli_state,
        )
        assert bulk_processor.call_args[0][1] == [
            {"username": "test@example.com", "tag": "tag1"},
            {"username": "test2@example.com", "tag": "tag2"},
        ]
