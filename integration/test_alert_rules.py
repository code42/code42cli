import pytest
from integration import run_command

ALERT_RULES_COMMAND = "code42 alert-rules"

@pytest.mark.parametrize(
    "command",
    [
        f"{ALERT_RULES_COMMAND} list",
        f"{ALERT_RULES_COMMAND} show test-rule-id",
        f"{ALERT_RULES_COMMAND} list -f CSV",
        f"{ALERT_RULES_COMMAND} list -f TABLE",
        f"{ALERT_RULES_COMMAND} list -f RAW-JSON",
        f"{ALERT_RULES_COMMAND} list -f JSON",
        f"{ALERT_RULES_COMMAND} list --format CSV",
        f"{ALERT_RULES_COMMAND} list --format TABLE",
        f"{ALERT_RULES_COMMAND} list --format JSON",
        f"{ALERT_RULES_COMMAND} list --format RAW-JSON",

    ]
)
def test_alert_rules_command_returns_success_return_code(command):
    return_code, response = run_command(command)
    assert return_code == 0


@pytest.mark.parametrize(
    "command, error_msg",
    [
        (f"{ALERT_RULES_COMMAND} add-user --rule-id test-rule-id", 
         "Missing option '-u' / '--username'."),
        (f"{ALERT_RULES_COMMAND} remove-user --rule-id test-rule-id", 
         "Missing option '-u' / '--username'."),
        (f"{ALERT_RULES_COMMAND} add-user", "Missing option '--rule-id'."),
        (f"{ALERT_RULES_COMMAND} remove-user", "Missing option '--rule-id'."),
        (f"{ALERT_RULES_COMMAND} show", "Missing argument 'RULE_ID'."),
        (f"{ALERT_RULES_COMMAND} bulk add", "Error: Missing argument 'CSV_FILE'."),
        (f"{ALERT_RULES_COMMAND} bulk remove", "Error: Missing argument 'CSV_FILE'."),
    ]
)
def test_alert_rules_command_returns_error_exit_status_when_missing_required_parameters(
    command, error_msg
):
    return_code, response = run_command(command)
    assert return_code == 2
    assert error_msg in "".join(response)


"""
def test_alert_rules_add_user_command(command):
    pass


def test_alert_rules_remove_user_command(command):
    pass


def test_alert_rules_bulk_command(command):
    pass
"""
