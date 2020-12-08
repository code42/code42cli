import pytest
from integration import run_command

LEGAL_HOLD_COMMAND = "code42 legal-hold"

@pytest.mark.parametrize(
    "command",
    [
        f"{LEGAL_HOLD_COMMAND} list",
        f"{LEGAL_HOLD_COMMAND} show test-matter-id",
        f"{LEGAL_HOLD_COMMAND} list -f CSV",
        f"{LEGAL_HOLD_COMMAND} list -f TABLE",
        f"{LEGAL_HOLD_COMMAND} list -f RAW-JSON",
        f"{LEGAL_HOLD_COMMAND} list -f JSON",
        f"{LEGAL_HOLD_COMMAND} list --format CSV",
        f"{LEGAL_HOLD_COMMAND} list --format TABLE",
        f"{LEGAL_HOLD_COMMAND} list --format JSON",
        f"{LEGAL_HOLD_COMMAND} list --format RAW-JSON",

    ]
)
def test_alert_rules_command_returns_success_return_code(command):
    return_code, response = run_command(command)
    assert return_code == 0


@pytest.mark.parametrize(
    "command, error_msg",
    [
        (f"{LEGAL_HOLD_COMMAND} add-user --matter-id test-matter-id", 
         "Missing option '-u' / '--username'."),
        (f"{LEGAL_HOLD_COMMAND} remove-user --matter-id test-matter-id", 
         "Missing option '-u' / '--username'."),
        (f"{LEGAL_HOLD_COMMAND} add-user", "Missing option '-m' / '--matter-id'."),
        (f"{LEGAL_HOLD_COMMAND} remove-user", "Missing option '-m' / '--matter-id'."),
        (f"{LEGAL_HOLD_COMMAND} show", "Missing argument 'MATTER_ID'."),
        (f"{LEGAL_HOLD_COMMAND} bulk add", "Error: Missing argument 'CSV_FILE'."),
        (f"{LEGAL_HOLD_COMMAND} bulk remove", "Error: Missing argument 'CSV_FILE'."),
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
