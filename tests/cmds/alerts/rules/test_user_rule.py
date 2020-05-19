import pytest

from code42cli.cmds.alerts.rules.user_rule import add_user, remove_user, get_rules, show_rule

TEST_RULE_ID = u"rule-id"
TEST_USER_ID = u"test-user-id"
TEST_USERNAME = "test@code42.com"

TEST_GET_ALL_RESPONSE_EXFILTRATION = {
    u"ruleMetadata": [{u"observerRuleId": TEST_RULE_ID, u"type": u"FED_ENDPOINT_EXFILTRATION"}]
}
TEST_GET_ALL_RESPONSE_CLOUD_SHARE = {
    u"ruleMetadata": [{u"observerRuleId": TEST_RULE_ID, u"type": u"FED_CLOUD_SHARE_PERMISSIONS"}]
}
TEST_GET_ALL_RESPONSE_FILE_TYPE_MISMATCH = {
    u"ruleMetadata": [{u"observerRuleId": TEST_RULE_ID, u"type": u"FED_FILE_TYPE_MISMATCH"}]
}


def test_add_user_adds_user_list_to_alert_rules(alert_rules_sdk, profile):
    alert_rules_sdk.users.get_by_username.return_value = {u"users": [{u"userUid": TEST_USER_ID}]}
    add_user(alert_rules_sdk, profile, TEST_RULE_ID, TEST_USERNAME)
    alert_rules_sdk.alerts.rules.add_user.assert_called_once_with(TEST_RULE_ID, TEST_USER_ID)


def test_remove_user_removes_user_list_from_alert_rules(alert_rules_sdk, profile):
    alert_rules_sdk.users.get_by_username.return_value = {u"users": [{u"userUid": TEST_USER_ID}]}
    remove_user(alert_rules_sdk, profile, TEST_RULE_ID, TEST_USERNAME)
    alert_rules_sdk.alerts.rules.remove_user.assert_called_once_with(TEST_RULE_ID, TEST_USER_ID)


def test_get_rules_gets_alert_rules(alert_rules_sdk, profile):
    get_rules(alert_rules_sdk, profile)
    assert alert_rules_sdk.alerts.rules.get_all.call_count == 1


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
