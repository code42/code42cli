import pytest
from integration import run_command

ALERT_RULES_COMMAND = "code42 alert-rules"


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


@pytest.mark.parametrize(
    "command, error_msg",
    [
        (
            "{} add-user --rule-id test-rule-id".format(ALERT_RULES_COMMAND),
            "Missing option '-u' / '--username'.",
        ),
        (
            "{} remove-user --rule-id test-rule-id".format(ALERT_RULES_COMMAND),
            "Missing option '-u' / '--username'.",
        ),
        ("{} add-user".format(ALERT_RULES_COMMAND), "Missing option '--rule-id'."),
        ("{} remove-user".format(ALERT_RULES_COMMAND), "Missing option '--rule-id'."),
        ("{} show".format(ALERT_RULES_COMMAND), "Missing argument 'RULE_ID'."),
        (
            "{} bulk add".format(ALERT_RULES_COMMAND),
            "Error: Missing argument 'CSV_FILE'.",
        ),
        (
            "{} bulk remove".format(ALERT_RULES_COMMAND),
            "Error: Missing argument 'CSV_FILE'.",
        ),
    ],
)
def test_alert_rules_command_returns_error_exit_status_when_missing_required_parameters(
    command, error_msg
):
    return_code, response = run_command(command)
    assert return_code == 2
    assert error_msg in "".join(response)
