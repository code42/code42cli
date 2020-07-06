import pytest
from requests import Request, Response, HTTPError

from click.testing import CliRunner

from py42.exceptions import Py42InternalServerError
from code42cli.main import cli
from code42cli.errors import InvalidRuleTypeError

import logging

TEST_RULE_ID = "rule-id"
TEST_USER_ID = "test-user-id"
TEST_USERNAME = "test@code42.com"

TEST_EMPTY_RULE_RESPONSE = {"ruleMetadata": []}

TEST_SYSTEM_RULE_RESPONSE = {
    "ruleMetadata": [
        {
            u"observerRuleId": TEST_RULE_ID,
            "type": u"FED_FILE_TYPE_MISMATCH",
            "isSystem": True,
            "ruleSource": "NOTVALID",
        }
    ]
}

TEST_USER_RULE_RESPONSE = {
    "ruleMetadata": [
        {
            "observerRuleId": TEST_RULE_ID,
            "type": "FED_FILE_TYPE_MISMATCH",
            "isSystem": False,
            "ruleSource": "Testing",
        }
    ]
}

TEST_GET_ALL_RESPONSE_EXFILTRATION = {
    "ruleMetadata": [{"observerRuleId": TEST_RULE_ID, "type": "FED_ENDPOINT_EXFILTRATION"}]
}
TEST_GET_ALL_RESPONSE_CLOUD_SHARE = {
    "ruleMetadata": [{"observerRuleId": TEST_RULE_ID, "type": "FED_CLOUD_SHARE_PERMISSIONS"}]
}
TEST_GET_ALL_RESPONSE_FILE_TYPE_MISMATCH = {
    "ruleMetadata": [{"observerRuleId": TEST_RULE_ID, "type": "FED_FILE_TYPE_MISMATCH"}]
}


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


@pytest.fixture
def mock_server_error(mocker):
    base_err = HTTPError()
    mock_response = mocker.MagicMock(spec=Response)
    base_err.response = mock_response
    request = mocker.MagicMock(spec=Request)
    request.body = '{"test":"body"}'
    base_err.response.request = request

    return Py42InternalServerError(base_err)


def test_add_user_adds_user_list_to_alert_rules(cli_state):
    cli_state.sdk.users.get_by_username.return_value = {"users": [{"userUid": TEST_USER_ID}]}
    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["alert-rules", "add-user", "--rule-id", TEST_RULE_ID, "-u", TEST_USERNAME],
        obj=cli_state,
    )
    cli_state.sdk.alerts.rules.add_user.assert_called_once_with(TEST_RULE_ID, TEST_USER_ID)


def test_add_user_when_non_existent_alert_prints_no_rules_message(cli_state):
    cli_state.sdk.alerts.rules.get_by_observer_id.return_value = TEST_EMPTY_RULE_RESPONSE
    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["alert-rules", "add-user", "--rule-id", TEST_RULE_ID, "-u", TEST_USERNAME],
        obj=cli_state,
    )
    msg = "No alert rules with RuleId {} found".format(TEST_RULE_ID)
    assert msg in result.output


def test_add_user_when_returns_500_and_system_rule_exits_with_InvalidRuleTypeError(
    cli_state, mock_server_error
):
    cli_state.sdk.alerts.rules.get_by_observer_id.return_value = TEST_SYSTEM_RULE_RESPONSE
    cli_state.sdk.alerts.rules.add_user.side_effect = mock_server_error
    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["alert-rules", "add-user", "--rule-id", TEST_RULE_ID, "-u", TEST_USERNAME],
        obj=cli_state,
    )
    assert result.exit_code == 1
    assert (
        "Only alert rules with a source of 'Alerting' can be targeted by this command."
        in result.output
    )


def test_add_user_when_returns_500_and_not_system_rule_raises_Py42InternalServerError(
    cli_state, mock_server_error, caplog
):
    cli_state.sdk.alerts.rules.get_by_observer_id.return_value = TEST_USER_RULE_RESPONSE
    cli_state.sdk.alerts.rules.add_user.side_effect = mock_server_error
    with caplog.at_level(logging.ERROR):
        runner = CliRunner()
        result = runner.invoke(
            cli,
            ["alert-rules", "add-user", "--rule-id", TEST_RULE_ID, "-u", TEST_USERNAME],
            obj=cli_state,
        )
        assert result.exit_code == 1
        assert "Py42InternalServerError" in caplog.text


def test_remove_user_removes_user_list_from_alert_rules(cli_state):
    cli_state.sdk.users.get_by_username.return_value = {"users": [{"userUid": TEST_USER_ID}]}
    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["alert-rules", "remove-user", "--rule-id", TEST_RULE_ID, "-u", TEST_USERNAME],
        obj=cli_state,
    )
    cli_state.sdk.alerts.rules.remove_user.assert_called_once_with(TEST_RULE_ID, TEST_USER_ID)


def test_remove_user_when_non_existent_alert_prints_no_rules_message(cli_state):
    cli_state.sdk.alerts.rules.get_by_observer_id.return_value = TEST_EMPTY_RULE_RESPONSE
    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["alert-rules", "remove-user", "--rule-id", TEST_RULE_ID, "-u", TEST_USERNAME],
        obj=cli_state,
    )
    msg = "No alert rules with RuleId {} found".format(TEST_RULE_ID)
    assert msg in result.output


def test_remove_user_when_returns_500_and_system_rule_raises_InvalidRuleTypeError(
    cli_state, mock_server_error
):
    cli_state.sdk.alerts.rules.get_by_observer_id.return_value = TEST_SYSTEM_RULE_RESPONSE
    cli_state.sdk.alerts.rules.remove_user.side_effect = mock_server_error
    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["alert-rules", "remove-user", "--rule-id", TEST_RULE_ID, "-u", TEST_USERNAME],
        obj=cli_state,
    )
    assert result.exit_code == 1
    assert (
        "Only alert rules with a source of 'Alerting' can be targeted by this command."
        in result.output
    )


def test_remove_user_when_returns_500_and_not_system_rule_raises_Py42InternalServerError(
    cli_state, mock_server_error, caplog
):
    cli_state.sdk.alerts.rules.get_by_observer_id.return_value = TEST_USER_RULE_RESPONSE
    cli_state.sdk.alerts.rules.remove_user.side_effect = mock_server_error
    with caplog.at_level(logging.ERROR):
        runner = CliRunner()
        result = runner.invoke(
            cli,
            ["alert-rules", "remove-user", "--rule-id", TEST_RULE_ID, "-u", TEST_USERNAME],
            obj=cli_state,
        )
        assert result.exit_code == 1
        assert "Py42InternalServerError" in caplog.text


def test_list_gets_alert_rules(cli_state):
    runner = CliRunner()
    result = runner.invoke(cli, ["alert-rules", "list"], obj=cli_state)
    assert cli_state.sdk.alerts.rules.get_all.call_count == 1


def test_list_when_no_rules_prints_no_rules_message(cli_state):
    cli_state.sdk.alerts.rules.get_all.return_value = [TEST_EMPTY_RULE_RESPONSE]
    runner = CliRunner()
    result = runner.invoke(cli, ["alert-rules", "list"], obj=cli_state)
    assert "No alert rules found" in result.output


def test_show_rule_calls_correct_rule_property(cli_state):
    cli_state.sdk.alerts.rules.get_by_observer_id.return_value = TEST_GET_ALL_RESPONSE_EXFILTRATION
    runner = CliRunner()
    result = runner.invoke(cli, ["alert-rules", "show", TEST_RULE_ID], obj=cli_state)
    cli_state.sdk.alerts.rules.exfiltration.get.assert_called_once_with(TEST_RULE_ID)


def test_show_rule_calls_correct_rule_property_cloud_share(cli_state):
    cli_state.sdk.alerts.rules.get_by_observer_id.return_value = TEST_GET_ALL_RESPONSE_CLOUD_SHARE
    runner = CliRunner()
    result = runner.invoke(cli, ["alert-rules", "show", TEST_RULE_ID], obj=cli_state)
    cli_state.sdk.alerts.rules.cloudshare.get.assert_called_once_with(TEST_RULE_ID)


def test_show_rule_calls_correct_rule_property_file_type_mismatch(cli_state):
    cli_state.sdk.alerts.rules.get_by_observer_id.return_value = (
        TEST_GET_ALL_RESPONSE_FILE_TYPE_MISMATCH
    )
    runner = CliRunner()
    result = runner.invoke(cli, ["alert-rules", "show", TEST_RULE_ID], obj=cli_state)
    cli_state.sdk.alerts.rules.filetypemismatch.get.assert_called_once_with(TEST_RULE_ID)


def test_show_rule_when_no_matching_rule_prints_no_rule_message(cli_state, caplog):
    cli_state.sdk.alerts.rules.get_by_observer_id.return_value = TEST_EMPTY_RULE_RESPONSE
    runner = CliRunner()
    result = runner.invoke(cli, ["alert-rules", "show", TEST_RULE_ID], obj=cli_state)
    msg = "No alert rules with RuleId {} found".format(TEST_RULE_ID)
    assert msg in result.output
