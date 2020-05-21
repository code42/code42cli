import pytest
from requests import Response, HTTPError

from py42.exceptions import Py42InternalServerError
from code42cli.errors import InvalidRuleTypeError
from code42cli.cmds.alerts.rules.user_rule import add_user, remove_user, get_rules, show_rule

import logging

TEST_RULE_ID = u"rule-id"
TEST_USER_ID = u"test-user-id"
TEST_USERNAME = "test@code42.com"

TEST_EMPTY_RULE_RESPONSE = {u"ruleMetadata": []}

TEST_SYSTEM_RULE_REPONSE = {
    u"ruleMetadata": [
        {
            u"observerRuleId": TEST_RULE_ID,
            u"type": u"FED_FILE_TYPE_MISMATCH",
            u"isSystem": True,
            u"ruleSource": "NOTVALID",
        }
    ]
}

TEST_USER_RULE_REPONSE = {
    u"ruleMetadata": [
        {
            u"observerRuleId": TEST_RULE_ID,
            u"type": u"FED_FILE_TYPE_MISMATCH",
            u"isSystem": False,
            u"ruleSource": "Testing",
        }
    ]
}

TEST_GET_ALL_RESPONSE_EXFILTRATION = {
    u"ruleMetadata": [{u"observerRuleId": TEST_RULE_ID, u"type": u"FED_ENDPOINT_EXFILTRATION"}]
}
TEST_GET_ALL_RESPONSE_CLOUD_SHARE = {
    u"ruleMetadata": [{u"observerRuleId": TEST_RULE_ID, u"type": u"FED_CLOUD_SHARE_PERMISSIONS"}]
}
TEST_GET_ALL_RESPONSE_FILE_TYPE_MISMATCH = {
    u"ruleMetadata": [{u"observerRuleId": TEST_RULE_ID, u"type": u"FED_FILE_TYPE_MISMATCH"}]
}


@pytest.fixture
def mock_server_error(mocker):
    base_err = HTTPError()
    mock_response = mocker.MagicMock(spec=Response)
    base_err.response = mock_response
    return Py42InternalServerError(base_err)


def test_add_user_adds_user_list_to_alert_rules(alert_rules_sdk, profile):
    alert_rules_sdk.users.get_by_username.return_value = {u"users": [{u"userUid": TEST_USER_ID}]}
    add_user(alert_rules_sdk, profile, TEST_RULE_ID, TEST_USERNAME)
    alert_rules_sdk.alerts.rules.add_user.assert_called_once_with(TEST_RULE_ID, TEST_USER_ID)


def test_add_user_when_non_existent_alert_prints_no_rules_message(alert_rules_sdk, profile, caplog):
    with caplog.at_level(logging.INFO):
        alert_rules_sdk.alerts.rules.get_by_observer_id.return_value = TEST_EMPTY_RULE_RESPONSE
        add_user(alert_rules_sdk, profile, TEST_RULE_ID, TEST_USERNAME)
        msg = u"No alert rules with RuleId {} found".format(TEST_RULE_ID)
        assert msg in caplog.text


def test_add_user_when_returns_500_and_system_rule_raises_InvalidRuleTypeError(
    alert_rules_sdk, profile, mock_server_error, caplog
):
    with caplog.at_level(logging.INFO):
        alert_rules_sdk.alerts.rules.get_by_observer_id.return_value = TEST_SYSTEM_RULE_REPONSE
        alert_rules_sdk.alerts.rules.add_user.side_effect = mock_server_error
        with pytest.raises(InvalidRuleTypeError):
            add_user(alert_rules_sdk, profile, TEST_RULE_ID, TEST_USERNAME)


def test_add_user_when_returns_500_and_not_system_rule_raises_Py42InternalServerError(
    alert_rules_sdk, profile, mock_server_error, caplog
):
    with caplog.at_level(logging.INFO):
        alert_rules_sdk.alerts.rules.get_by_observer_id.return_value = TEST_USER_RULE_REPONSE
        alert_rules_sdk.alerts.rules.add_user.side_effect = mock_server_error
        with pytest.raises(Py42InternalServerError):
            add_user(alert_rules_sdk, profile, TEST_RULE_ID, TEST_USERNAME)


def test_remove_user_removes_user_list_from_alert_rules(alert_rules_sdk, profile):
    alert_rules_sdk.users.get_by_username.return_value = {u"users": [{u"userUid": TEST_USER_ID}]}
    remove_user(alert_rules_sdk, profile, TEST_RULE_ID, TEST_USERNAME)
    alert_rules_sdk.alerts.rules.remove_user.assert_called_once_with(TEST_RULE_ID, TEST_USER_ID)


def test_remove_user_when_non_existent_alert_prints_no_rules_message(
    alert_rules_sdk, profile, caplog
):
    with caplog.at_level(logging.INFO):
        alert_rules_sdk.alerts.rules.get_by_observer_id.return_value = TEST_EMPTY_RULE_RESPONSE
        remove_user(alert_rules_sdk, profile, TEST_RULE_ID, TEST_USERNAME)
        msg = u"No alert rules with RuleId {} found".format(TEST_RULE_ID)
        assert msg in caplog.text


def test_remove_user_when_returns_500_and_system_rule_raises_InvalidRuleTypeError(
    alert_rules_sdk, profile, mock_server_error, caplog
):
    with caplog.at_level(logging.INFO):
        alert_rules_sdk.alerts.rules.get_by_observer_id.return_value = TEST_SYSTEM_RULE_REPONSE
        alert_rules_sdk.alerts.rules.remove_user.side_effect = mock_server_error
        with pytest.raises(InvalidRuleTypeError):
            remove_user(alert_rules_sdk, profile, TEST_RULE_ID, TEST_USERNAME)


def test_remove_user_when_returns_500_and_not_system_rule_raises_Py42InternalServerError(
    alert_rules_sdk, profile, mock_server_error, caplog
):
    with caplog.at_level(logging.INFO):
        alert_rules_sdk.alerts.rules.get_by_observer_id.return_value = TEST_USER_RULE_REPONSE
        alert_rules_sdk.alerts.rules.remove_user.side_effect = mock_server_error
        with pytest.raises(Py42InternalServerError):
            remove_user(alert_rules_sdk, profile, TEST_RULE_ID, TEST_USERNAME)


def test_get_rules_gets_alert_rules(alert_rules_sdk, profile):
    get_rules(alert_rules_sdk, profile)
    assert alert_rules_sdk.alerts.rules.get_all.call_count == 1


def test_get_rules_when_no_rules_prints_no_rules_message(alert_rules_sdk, profile, caplog):
    with caplog.at_level(logging.INFO):
        alert_rules_sdk.alerts.rules.get_all.return_value = [TEST_EMPTY_RULE_RESPONSE]
        get_rules(alert_rules_sdk, profile)
        msg = u"No alert rules found".format(TEST_RULE_ID)
        assert msg in caplog.text


def test_show_rule_calls_correct_rule_property(alert_rules_sdk, profile):
    alert_rules_sdk.alerts.rules.get_by_observer_id.return_value = (
        TEST_GET_ALL_RESPONSE_EXFILTRATION
    )
    show_rule(alert_rules_sdk, profile, TEST_RULE_ID)
    alert_rules_sdk.alerts.rules.exfiltration.get.assert_called_once_with(TEST_RULE_ID)


def test_show_rule_calls_correct_rule_property_cloud_share(alert_rules_sdk, profile):
    alert_rules_sdk.alerts.rules.get_by_observer_id.return_value = TEST_GET_ALL_RESPONSE_CLOUD_SHARE
    show_rule(alert_rules_sdk, profile, TEST_RULE_ID)
    alert_rules_sdk.alerts.rules.cloudshare.get.assert_called_once_with(TEST_RULE_ID)


def test_show_rule_calls_correct_rule_property_file_type_mismatch(alert_rules_sdk, profile):
    alert_rules_sdk.alerts.rules.get_by_observer_id.return_value = (
        TEST_GET_ALL_RESPONSE_FILE_TYPE_MISMATCH
    )
    show_rule(alert_rules_sdk, profile, TEST_RULE_ID)
    alert_rules_sdk.alerts.rules.filetypemismatch.get.assert_called_once_with(TEST_RULE_ID)


def test_show_rule_when_no_matching_rule_prints_no_rule_message(alert_rules_sdk, profile, caplog):
    with caplog.at_level(logging.INFO):
        alert_rules_sdk.alerts.rules.get_by_observer_id.return_value = TEST_EMPTY_RULE_RESPONSE
        show_rule(alert_rules_sdk, profile, TEST_RULE_ID)
        msg = u"No alert rules with RuleId {} found".format(TEST_RULE_ID)
        assert msg in caplog.text
