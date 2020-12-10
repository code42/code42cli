import pytest
from integration import run_command

LEGAL_HOLD_COMMAND = "code42 legal-hold"


@pytest.mark.parametrize(
    "command",
    [
        "{} list".format(LEGAL_HOLD_COMMAND),
        "{} show 984140047896012577".format(LEGAL_HOLD_COMMAND),
        "{} list -f CSV".format(LEGAL_HOLD_COMMAND),
        "{} list -f TABLE".format(LEGAL_HOLD_COMMAND),
        "{} list -f RAW-JSON".format(LEGAL_HOLD_COMMAND),
        "{} list -f JSON".format(LEGAL_HOLD_COMMAND),
        "{} list --format CSV".format(LEGAL_HOLD_COMMAND),
        "{} list --format TABLE".format(LEGAL_HOLD_COMMAND),
        "{} list --format JSON".format(LEGAL_HOLD_COMMAND),
        "{} list --format RAW-JSON".format(LEGAL_HOLD_COMMAND),
    ],
)
def test_alert_rules_command_returns_success_return_code(command):
    return_code, response = run_command(command)
    assert return_code == 0


@pytest.mark.parametrize(
    "command, error_msg",
    [
        (
            "{} add-user --matter-id test-matter-id".format(LEGAL_HOLD_COMMAND),
            "Missing option '-u' / '--username'.",
        ),
        (
            "{} remove-user --matter-id test-matter-id".format(LEGAL_HOLD_COMMAND),
            "Missing option '-u' / '--username'.",
        ),
        (
            "{} add-user".format(LEGAL_HOLD_COMMAND),
            "Missing option '-m' / '--matter-id'.",
        ),
        (
            "{} remove-user".format(LEGAL_HOLD_COMMAND),
            "Missing option '-m' / '--matter-id'.",
        ),
        ("{} show".format(LEGAL_HOLD_COMMAND), "Missing argument 'MATTER_ID'."),
        (
            "{} bulk add".format(LEGAL_HOLD_COMMAND),
            "Error: Missing argument 'CSV_FILE'.",
        ),
        (
            "{} bulk remove".format(LEGAL_HOLD_COMMAND),
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
