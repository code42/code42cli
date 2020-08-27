import pytest
from py42.exceptions import Py42InvalidRuleOperationError
from requests import HTTPError
from requests import Response

from code42cli.main import cli

TEST_RULE_ID = "rule-id"
TEST_USER_ID = "test-user-id"
TEST_USERNAME = "test@code42.com"
TEST_SOURCE = "rule source"

TEST_EMPTY_RULE_RESPONSE = {"ruleMetadata": []}

TEST_RULE_RESPONSE = {
    "ruleMetadata": [
        {
            "observerRuleId": TEST_RULE_ID,
            "type": "FED_FILE_TYPE_MISMATCH",
            "isEnabled": True,
            "ruleSource": "NOTVALID",
            "name": "Test",
            "severity": "high",
        }
    ]
}

TEST_GET_ALL_RESPONSE_EXFILTRATION = {
    "ruleMetadata": [
        {"observerRuleId": TEST_RULE_ID, "type": "FED_ENDPOINT_EXFILTRATION"}
    ]
}
TEST_GET_ALL_RESPONSE_CLOUD_SHARE = {
    "ruleMetadata": [
        {"observerRuleId": TEST_RULE_ID, "type": "FED_CLOUD_SHARE_PERMISSIONS"}
    ]
}
TEST_GET_ALL_RESPONSE_FILE_TYPE_MISMATCH = {
    "ruleMetadata": [{"observerRuleId": TEST_RULE_ID, "type": "FED_FILE_TYPE_MISMATCH"}]
}


def create_invalid_rule_type_side_effect(mocker):
    def side_effect(*args, **kwargs):
        err = mocker.MagicMock(spec=HTTPError)
        resp = mocker.MagicMock(spec=Response)
        resp.text = "TEST_ERR"
        err.response = resp
        raise Py42InvalidRuleOperationError(err, TEST_RULE_ID)

    return side_effect


@pytest.fixture
def get_user_id(mocker):
    return mocker.patch("code42cli.cmds.alert_rules.get_user_id")


@pytest.fixture
def alert_rules_sdk(sdk):
    sdk.alerts.rules.add_user.return_value = {}
    sdk.alerts.rules.remove_user.return_value = {}
    sdk.alerts.rules.remove_all_users.return_value = {}
    sdk.alerts.rules.get_all.return_value = {}
    sdk.alerts.rules.exfiltration.get.return_value = {}
    sdk.alerts.rules.cloudshare.get.return_value = {}
    sdk.alerts.rules.filetypemismatch.get.return_value = {}
    return sdk


def test_add_user_adds_user_list_to_alert_rules(runner, cli_state):
    cli_state.sdk.users.get_by_username.return_value = {
        "users": [{"userUid": TEST_USER_ID}]
    }
    runner.invoke(
        cli,
        ["alert-rules", "add-user", "--rule-id", TEST_RULE_ID, "-u", TEST_USERNAME],
        obj=cli_state,
    )
    cli_state.sdk.alerts.rules.add_user.assert_called_once_with(
        TEST_RULE_ID, TEST_USER_ID
    )


def test_add_user_when_returns_invalid_rule_type_error_and_system_rule_exits(
    mocker, runner, cli_state
):
    cli_state.sdk.alerts.rules.add_user.side_effect = create_invalid_rule_type_side_effect(
        mocker
    )
    result = runner.invoke(
        cli,
        ["alert-rules", "add-user", "--rule-id", TEST_RULE_ID, "-u", TEST_USERNAME],
        obj=cli_state,
    )
    assert result.exit_code == 1
    assert (
        "Unable to find or access Rule with ID 'rule-id'. You might be trying to access a system rule."
        in result.output
    )


def test_add_user_when_raises_invalid_rules_type_error_shows_correct_message(
    mocker, runner, cli_state
):
    cli_state.sdk.alerts.rules.add_user.side_effect = create_invalid_rule_type_side_effect(
        mocker
    )
    result = runner.invoke(
        cli,
        ["alert-rules", "add-user", "--rule-id", TEST_RULE_ID, "-u", TEST_USERNAME],
        obj=cli_state,
    )
    assert result.exit_code == 1
    assert (
        "Unable to find or access Rule with ID 'rule-id'. You might be trying to access a system rule."
        in result.output
    )


def test_remove_user_removes_user_list_from_alert_rules(runner, cli_state):
    cli_state.sdk.users.get_by_username.return_value = {
        "users": [{"userUid": TEST_USER_ID}]
    }
    runner.invoke(
        cli,
        ["alert-rules", "remove-user", "--rule-id", TEST_RULE_ID, "-u", TEST_USERNAME],
        obj=cli_state,
    )
    cli_state.sdk.alerts.rules.remove_user.assert_called_once_with(
        TEST_RULE_ID, TEST_USER_ID
    )


def test_remove_user_when_raise_invalid_rule_type_error_and_system_rule_raises_InvalidRuleTypeError(
    mocker, runner, cli_state
):
    cli_state.sdk.alerts.rules.remove_user.side_effect = create_invalid_rule_type_side_effect(
        mocker
    )
    result = runner.invoke(
        cli,
        ["alert-rules", "remove-user", "--rule-id", TEST_RULE_ID, "-u", TEST_USERNAME],
        obj=cli_state,
    )
    assert result.exit_code == 1
    assert (
        "Unable to find or access Rule with ID 'rule-id'. You might be trying to access a system rule."
        in result.output
    )


def test_remove_user_when_raises_invalid_rule_type_side_effect_and_not_system_rule_raises_Py42InternalServerError(
    mocker, runner, cli_state
):
    cli_state.sdk.alerts.rules.remove_user.side_effect = create_invalid_rule_type_side_effect(
        mocker
    )
    result = runner.invoke(
        cli,
        ["alert-rules", "remove-user", "--rule-id", TEST_RULE_ID, "-u", TEST_USERNAME],
        obj=cli_state,
    )

    assert result.exit_code == 1
    assert (
        "Unable to find or access Rule with ID 'rule-id'. You might be trying to access a system rule."
        in result.output
    )


def test_list_gets_alert_rules(runner, cli_state):
    runner.invoke(cli, ["alert-rules", "list"], obj=cli_state)
    assert cli_state.sdk.alerts.rules.get_all.call_count == 1


def test_list_when_no_rules_prints_no_rules_message(runner, cli_state):
    cli_state.sdk.alerts.rules.get_all.return_value = [TEST_EMPTY_RULE_RESPONSE]
    result = runner.invoke(cli, ["alert-rules", "list"], obj=cli_state)
    assert "No alert rules found" in result.output


def test_show_rule_calls_correct_rule_property(runner, cli_state):
    cli_state.sdk.alerts.rules.get_by_observer_id.return_value = (
        TEST_GET_ALL_RESPONSE_EXFILTRATION
    )
    runner.invoke(cli, ["alert-rules", "show", TEST_RULE_ID], obj=cli_state)
    cli_state.sdk.alerts.rules.exfiltration.get.assert_called_once_with(TEST_RULE_ID)


def test_show_rule_calls_correct_rule_property_cloud_share(runner, cli_state):
    cli_state.sdk.alerts.rules.get_by_observer_id.return_value = (
        TEST_GET_ALL_RESPONSE_CLOUD_SHARE
    )
    runner.invoke(cli, ["alert-rules", "show", TEST_RULE_ID], obj=cli_state)
    cli_state.sdk.alerts.rules.cloudshare.get.assert_called_once_with(TEST_RULE_ID)


def test_show_rule_calls_correct_rule_property_file_type_mismatch(runner, cli_state):
    cli_state.sdk.alerts.rules.get_by_observer_id.return_value = (
        TEST_GET_ALL_RESPONSE_FILE_TYPE_MISMATCH
    )
    runner.invoke(cli, ["alert-rules", "show", TEST_RULE_ID], obj=cli_state)
    cli_state.sdk.alerts.rules.filetypemismatch.get.assert_called_once_with(
        TEST_RULE_ID
    )


def test_show_rule_when_no_matching_rule_prints_no_rule_message(runner, cli_state):
    cli_state.sdk.alerts.rules.get_by_observer_id.return_value = (
        TEST_EMPTY_RULE_RESPONSE
    )
    result = runner.invoke(cli, ["alert-rules", "show", TEST_RULE_ID], obj=cli_state)
    msg = "No alert rules with RuleId {} found".format(TEST_RULE_ID)
    assert msg in result.output


def test_add_bulk_users_uses_expected_arguments(runner, mocker, cli_state):
    bulk_processor = mocker.patch("code42cli.cmds.alert_rules.run_bulk_process")
    with runner.isolated_filesystem():
        with open("test_add.csv", "w") as csv:
            csv.writelines(["rule_id,username\n", "test,value\n"])
        runner.invoke(
            cli, ["alert-rules", "bulk", "add", "test_add.csv"], obj=cli_state
        )
    assert bulk_processor.call_args[0][1] == [{"rule_id": "test", "username": "value"}]


def test_remove_bulk_users_uses_expected_arguments(runner, mocker, cli_state):
    bulk_processor = mocker.patch("code42cli.cmds.alert_rules.run_bulk_process")
    with runner.isolated_filesystem():
        with open("test_remove.csv", "w") as csv:
            csv.writelines(["rule_id,username\n", "test,value\n"])
        runner.invoke(
            cli, ["alert-rules", "bulk", "add", "test_remove.csv"], obj=cli_state
        )
    assert bulk_processor.call_args[0][1] == [{"rule_id": "test", "username": "value"}]


def test_list_cmd_prints_no_rules_found_when_f_is_passed_and_response_is_empty(
    runner, cli_state
):
    cli_state.sdk.alerts.rules.get_all.return_value = [TEST_EMPTY_RULE_RESPONSE]
    result = runner.invoke(cli, ["alert-rules", "list", "-f", "csv"], obj=cli_state)
    assert cli_state.sdk.alerts.rules.get_all.call_count == 1
    assert "No alert rules found" in result.output


def test_list_cmd_formats_to_csv_when_format_is_passed(runner, cli_state):
    cli_state.sdk.alerts.rules.get_all.return_value = [TEST_RULE_RESPONSE]
    result = runner.invoke(cli, ["alert-rules", "list", "-f", "csv"], obj=cli_state)
    assert cli_state.sdk.alerts.rules.get_all.call_count == 1
    assert "observerRuleId" in result.output
    assert "type" in result.output
    assert "isEnabled" in result.output
    assert "ruleSource" in result.output
    assert "name" in result.output
    assert "severity" in result.output
