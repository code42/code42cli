import pytest


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
