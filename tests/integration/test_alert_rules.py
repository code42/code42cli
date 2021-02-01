import pytest
from tests.integration.conftest import append_profile
from tests.integration.util import assert_test_is_successful

ALERT_RULES_COMMAND = "alert-rules"


@pytest.mark.integration
@pytest.mark.parametrize(
    "command",
    [
        "{} list".format(ALERT_RULES_COMMAND),
        "{} list -f CSV".format(ALERT_RULES_COMMAND),
        "{} list -f TABLE".format(ALERT_RULES_COMMAND),
        "{} list -f RAW-JSON".format(ALERT_RULES_COMMAND),
        "{} list -f JSON".format(ALERT_RULES_COMMAND),
        "{} list --format CSV".format(ALERT_RULES_COMMAND),
        "{} list --format TABLE".format(ALERT_RULES_COMMAND),
        "{} list --format JSON".format(ALERT_RULES_COMMAND),
        "{} list --format RAW-JSON".format(ALERT_RULES_COMMAND),
    ],
)
def test_alert_rules_list_command_returns_success_return_code(
    runner, integration_test_profile, command
):
    assert_test_is_successful(runner, integration_test_profile, append_profile(command))


@pytest.mark.integration
def test_alert_rules_show_command_returns_success_return_code(
    runner, integration_test_profile
):
    command = ("{} show test-rule-id".format(ALERT_RULES_COMMAND),)
    assert_test_is_successful(runner, integration_test_profile, append_profile(command))
