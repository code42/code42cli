import pytest

from code42cli.cmds.alerts.rules.user_rule import (
    add_user, remove_user, bulk_update, get_rules
)

TEST_RULE_ID = u"rule-id"
TEST_USER_ID = u"test-user-id"


def test_add_user_adds_user_list_to_alert_rules(alert_rules_sdk):
    add_user(alert_rules_sdk, TEST_RULE_ID, TEST_USER_ID)
    alert_rules_sdk.alerts.rules.add_user.assert_called_once_with(TEST_RULE_ID, TEST_USER_ID)


def test_remove_user_removes_user_list_from_alert_rules(alert_rules_sdk):
    remove_user(alert_rules_sdk, TEST_RULE_ID, TEST_USER_ID)
    alert_rules_sdk.alerts.rules.remove_user.assert_called_once_with(TEST_RULE_ID, TEST_USER_ID)
    remove_user(alert_rules_sdk, TEST_RULE_ID)
    alert_rules_sdk.alerts.rules.remove_all_users.assert_called_once_with(TEST_RULE_ID)


def test_get_rules_gets_alert_rules(alert_rules_sdk):
    get_rules(alert_rules_sdk, "exfiltration", TEST_RULE_ID)
    alert_rules_sdk.alerts.rules.exfiltration.get.assert_called_once_with(TEST_RULE_ID)
    get_rules(alert_rules_sdk, "cloudshare", TEST_RULE_ID)
    alert_rules_sdk.alerts.rules.cloudshare.get.assert_called_once_with(TEST_RULE_ID)
    get_rules(alert_rules_sdk, "filetypemismatch", TEST_RULE_ID)
    alert_rules_sdk.alerts.rules.filetypemismatch.get.assert_called_once_with(TEST_RULE_ID)
    get_rules(alert_rules_sdk)
    alert_rules_sdk.alerts.rules.get_all.assert_called_once()

