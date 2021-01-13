import pytest
from integration import run_command

ALERT_RULES_COMMAND = "code42 alert-rules"


@pytest.mark.integration
@pytest.mark.parametrize(
    "command",
    [
        "{} list".format(ALERT_RULES_COMMAND),
        "{} show test-rule-id".format(ALERT_RULES_COMMAND),
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
def test_alert_rules_command_returns_success_return_code(command):
    return_code, response = run_command(command)
    assert return_code == 0
